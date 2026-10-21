import time
import os
import csv
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

def check_disambiguation(user_msg: str, lang: str, client_host: str) -> Optional[dict]:
    user_lower = user_msg.lower()
    for rule_name, rule_data in DISAMBIGUATION_RULES.items():
        matched_trigger = next((t for t in rule_data["trigger_words"] if t in user_lower), None)
        has_exclude = any(exclude in user_lower for exclude in rule_data["exclude_words"])
        
        if matched_trigger and not has_exclude:
            # Trigger disambiguation without overkill fallback
            reply_text = rule_data["response"].get(lang, rule_data["response"].get("en", "Please clarify your request."))
            
            # Log the event so the Admin Interface has a basis!
            intent_label = f"disambiguation_{rule_name}"
            log_chat(user_msg, intent_label, client_host, True, confidence=1.0)
            
            return {"reply": reply_text, "summary": "", "context": rule_data["context"], "intent": intent_label}
    return None

def translate_to_english(user_msg: str, lang: str) -> Optional[str]:
    # Enforce limit to avoid translation errors
    if len(user_msg) > 500:
        user_msg = user_msg[:500]
        
    if lang == "en":
        return user_msg
        
    try:
        translator = GoogleTranslator(source=lang, target='en')
        return translator.translate(user_msg)
    except Exception as e:
        print(f"[WARN] Translation failed: {e}")
        # Return None instead of raw non-English text to prevent NLP errors
        return user_msg  # Fallback to original message so local model can process it

def process_and_fetch_answer(en_msg: str, user_msg: str, lang: str, client_host: str) -> dict:
    cleaned = clean_text(en_msg)
    intent = predict_intent(cleaned)
    confidence = get_confidence(en_msg, cleaned)
    print(f"CL: {confidence:.4f} | Intent: {intent} | Query: '{user_msg}'")
    # Reject if confidence is below 0.85 (target 0.90) or intent is missing
    if not intent or (confidence is not None and confidence < 0.85):
        if lang == "tl":
            ans = "Pasensya na, hindi ko naiintindihan ang inyong tanong. Maaari po bang linawin?"
        elif lang == "bis":
            ans = "Pasayloa ko, wala ko makasabot sa imong pangutana. Mahimo ba nimong klaruhon?"
        else:
            ans = "I'm sorry, I didn't understand that. Could you rephrase your question?"
        log_chat(user_msg, "unresolved", client_host, False, confidence=confidence)
        try:
            supabase.table("unresolved_queries").insert({"question": user_msg, "language": lang}).execute()
        except Exception as e:
            print(f"[ERROR] Failed to log unresolved to Supabase: {e}")
            
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
            os.makedirs(data_dir, exist_ok=True)
            local_unresolved = os.path.join(data_dir, "local_unresolved.csv")
            file_exists = os.path.isfile(local_unresolved)
            with open(local_unresolved, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["question", "language", "timestamp"])
                writer.writerow([user_msg, lang, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])
        except Exception as e:
            print(f"[ERROR] Failed to log unresolved locally: {e}")
            
        return {"reply": ans, "summary": "", "context": None, "intent": "unresolved"}
    else:
        ans_data = ANSWERS.get(intent)
        if ans_data:
            # Fallback to English if lang is 'auto' or not found
            answers_dict = ans_data.get("answers", {})
            ans = answers_dict.get(lang) or answers_dict.get("en") or "No answer found."
            summary = summarize_text(ans)
            log_chat(user_msg, intent, client_host, True, confidence=confidence)
            return {"reply": ans, "summary": summary, "context": None, "intent": intent}
        else:
            if lang == "tl":
                ans = "Wala pang impormasyon para sa katanungang ito."
            elif lang == "bis":
                ans = "Wala pay impormasyon bahin niini."
            else:
                ans = "No information available for this intent yet."
            log_chat(user_msg, intent, client_host, False, confidence=confidence)
            return {"reply": ans, "summary": "", "context": None, "intent": intent}

def handle_active_context(context: str, user_msg: str, lang: str, client_host: str) -> Optional[dict]:
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
            answers_dict = ANSWERS.get(matched_intent, {}).get("answers", {})
            ans = answers_dict.get(lang) or answers_dict.get("en") or "Information not available yet."
            summary = summarize_text(ans)
            log_chat(user_msg, matched_intent, client_host, True, confidence=1.0)
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
            answers_dict = ANSWERS.get(matched_intent, {}).get("answers", {})
            ans = answers_dict.get(lang) or answers_dict.get("en") or "Information not available yet."
            summary = summarize_text(ans)
            log_chat(user_msg, matched_intent, client_host, True, confidence=1.0)
            return {"reply": ans, "summary": summary, "context": None, "intent": matched_intent}
        else:
            return {"reply": "I couldn't recognize that type. Please reply with 1, 2, 3, 4, 5, or 6.", "context": "awaiting_mtop_type"}
    else:
        # Panelist Fix: Proper termination for unknown contexts
        return {"reply": "I'm sorry, I lost track of our conversation. How can I help you again?", "context": None, "intent": "unknown"}
    return None

@router.post("/chat")
async def chat(request: ChatRequest, req: Request):
    user_msg = request.message
    lang = request.language
    context = request.context
    
    # 1. Handle Active Context (Follow-ups)
    if context:
        context_response = handle_active_context(context, user_msg, lang, req.client.host)
        if context_response:
            return context_response

    # 2. Check Disambiguation Rules
    disambiguation_response = check_disambiguation(user_msg, lang, req.client.host)
    if disambiguation_response:
        return disambiguation_response

    # 3. Translation to English for the model (if necessary)
    en_msg = translate_to_english(user_msg, lang)
    if en_msg is None:
        # Halt execution if translation fails (don't feed non-English to model)
        error_msg = "Our translation service is currently unavailable. Please try asking in English."
        if lang == "tl": error_msg = "Pansamantalang hindi magamit ang aming translation service. Maaari po bang magtanong sa Ingles?"
        if lang == "bis": error_msg = "Kadiyot nga wala ang among translation service. Palihug pagsulay og pangutana sa English."
        return {"reply": error_msg, "summary": "", "context": None, "intent": "translation_error"}

    # 4 & 5. Process text and predict intent, then Fetch Answer
    return process_and_fetch_answer(en_msg, user_msg, lang, req.client.host)

def log_chat(msg, intent, ip, resolved, confidence=0.0):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # 1. Log to Supabase (for Admin Dashboard)
    try:
        supabase.table("chat_logs").insert({
            "timestamp": timestamp,
            "user_message": msg,
            "predicted_intent": intent,
            "confidence": confidence,
            "resolved": resolved
        }).execute()
    except Exception as e:
        print(f"[ERROR] Failed to log chat to Supabase: {e}")
        
    # 2. Log to Local CSV (for ML Retraining)
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        local_log_path = os.path.join(data_dir, "local_chat_logs.csv")
        file_exists = os.path.isfile(local_log_path)
        
        with open(local_log_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "user_message", "predicted_intent", "confidence", "resolved"])
            writer.writerow([timestamp, msg, intent, confidence, resolved])
    except Exception as e:
        print(f"[ERROR] Failed to log chat locally: {e}")
