import time
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from deep_translator import GoogleTranslator
from services.nlp import get_confidence, predict_intent, summarize_text, DISAMBIGUATION_RULES
from services.cache import ANSWERS, OFFICES
from supabase_client import supabase
from utils.preprocess import clean_text

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    language: str
    context: Optional[str] = None  # To handle follow-up disambiguation context

@router.post("/chat")
async def chat(request: ChatRequest, req: Request):
    user_msg = request.message
    lang = request.language
    context = request.context
    
    # 1. Handle Active Context (Follow-ups)
    if context:
        if context == "awaiting_business_permit_type":
            type_mapping = {
                "1": "cmo_business_permit_new", "new": "cmo_business_permit_new", "bago": "cmo_business_permit_new", "bag-o": "cmo_business_permit_new",
                "2": "cmo_business_permit_renewal", "renew": "cmo_business_permit_renewal", "renewal": "cmo_business_permit_renewal",
                "3": "cmo_business_permit_retirement", "retire": "cmo_business_permit_retirement", "retirement": "cmo_business_permit_retirement", "sarado": "cmo_business_permit_retirement", "close": "cmo_business_permit_retirement",
                "4": "cmo_business_permit_transfer", "transfer": "cmo_business_permit_transfer", "change location": "cmo_business_permit_transfer"
            }
            user_lower = user_msg.lower().strip()
            matched_intent = None
            for key, intent_val in type_mapping.items():
                if key in user_lower:
                    matched_intent = intent_val
                    break
            if matched_intent:
                ans = ANSWERS.get(matched_intent, {}).get("answers", {}).get(lang, "Information not available yet.")
                summary = summarize_text(ans)
                log_chat(user_msg, matched_intent, req.client.host, True, confidence=1.0)
                return {"reply": ans, "summary": summary, "context": None, "intent": matched_intent}
            else:
                return {"reply": "I couldn't recognize that type. Please reply with 1, 2, 3, or 4.", "context": "awaiting_business_permit_type"}
                
        elif context == "awaiting_mtop_type":
            type_mapping = {
                "1": "cmo_mtop_new", "new": "cmo_mtop_new", "bago": "cmo_mtop_new", "bag-o": "cmo_mtop_new",
                "2": "cmo_mtop_renewal", "renew": "cmo_mtop_renewal", "renewal": "cmo_mtop_renewal",
                "3": "cmo_mtop_annual", "annual": "cmo_mtop_annual",
                "4": "cmo_mtop_dropping", "drop": "cmo_mtop_dropping", "dropping": "cmo_mtop_dropping",
                "5": "cmo_mtop_substitution", "substitute": "cmo_mtop_substitution", "substitution": "cmo_mtop_substitution",
                "6": "cmo_mtop_transfer", "transfer": "cmo_mtop_transfer"
            }
            user_lower = user_msg.lower().strip()
            matched_intent = None
            for key, intent_val in type_mapping.items():
                if key in user_lower:
                    matched_intent = intent_val
                    break
            if matched_intent:
                ans = ANSWERS.get(matched_intent, {}).get("answers", {}).get(lang, "Information not available yet.")
                summary = summarize_text(ans)
                log_chat(user_msg, matched_intent, req.client.host, True, confidence=1.0)
                return {"reply": ans, "summary": summary, "context": None, "intent": matched_intent}
            else:
                return {"reply": "I couldn't recognize that type. Please reply with 1 to 6.", "context": "awaiting_mtop_type"}

    # 2. Check Disambiguation Rules
    user_lower = user_msg.lower()
    for rule_name, rule_data in DISAMBIGUATION_RULES.items():
        has_trigger = any(trigger in user_lower for trigger in rule_data["trigger_words"])
        has_exclude = any(exclude in user_lower for exclude in rule_data["exclude_words"])
        
        if has_trigger and not has_exclude:
            # Trigger disambiguation
            reply_text = rule_data["response"].get(lang, rule_data["response"]["en"])
            return {"reply": reply_text, "summary": "", "context": rule_data["context"], "intent": "disambiguation"}

    # 3. Translation to English for the model (if necessary)
    en_msg = user_msg
    if lang != "en":
        try:
            translator = GoogleTranslator(source=lang, target='en')
            en_msg = translator.translate(user_msg)
        except Exception as e:
            print(f"[WARN] Translation failed: {e}")
            en_msg = user_msg

    # 4. Process text and predict intent
    cleaned = clean_text(en_msg)
    intent = predict_intent(cleaned)
    confidence = get_confidence(en_msg, cleaned)
    print(f"[INFO] Message: '{user_msg}' -> EN: '{en_msg}' -> Intent: {intent} (Conf: {confidence:.2f})")

    # 5. Fetch Answer
    if confidence < 0.35: # Changed threshold to 0.35
        # Fallback answers
        if lang == "tl":
            ans = "Pasensya na, hindi ko naiintindihan ang inyong tanong. Maaari po bang linawin?"
        elif lang == "bis":
            ans = "Pasayloa ko, wala ko makasabot sa imong pangutana. Mahimo ba nimong klaruhon?"
        else:
            ans = "I'm sorry, I didn't understand that. Could you rephrase your question?"
        log_chat(user_msg, "unresolved", req.client.host, False, confidence=confidence)
        supabase.table("unresolved_queries").insert({"question": user_msg, "language": lang}).execute()
        return {"reply": ans, "summary": "", "context": None, "intent": "unresolved"}
    else:
        ans_data = ANSWERS.get(intent)
        if ans_data:
            ans = ans_data.get("answers", {}).get(lang, ans_data.get("answers", {}).get("en", "No answer found."))
            summary = summarize_text(ans)
            log_chat(user_msg, intent, req.client.host, True, confidence=confidence)
            return {"reply": ans, "summary": summary, "context": None, "intent": intent}
        else:
            if lang == "tl":
                ans = "Wala pang impormasyon para sa katanungang ito."
            elif lang == "bis":
                ans = "Wala pay impormasyon bahin niini."
            else:
                ans = "No information available for this intent yet."
            log_chat(user_msg, intent, req.client.host, False, confidence=confidence)
            return {"reply": ans, "summary": "", "context": None, "intent": intent}

def log_chat(msg, intent, ip, resolved, confidence=0.0):
    try:
        supabase.table("chat_logs").insert({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "user_message": msg,
            "predicted_intent": intent,
            "confidence": confidence,
            "resolved": resolved
        }).execute()
    except Exception as e:
        print(f"[ERROR] Failed to log chat: {e}")
