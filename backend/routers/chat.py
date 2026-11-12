import logging
import re
import time
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field, field_validator
from services.cache import ANSWERS, TRAINING_PHRASES
from services.nlp import (
    DISAMBIGUATION_RULES,
    LANGUAGE_ALIASES,
    get_confidence,
    normalize_language,
    predict_intent,
    resolve_language,
    summarize_text,
)
from utils.preprocess import clean_text
from supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)
MAX_CHAT_MESSAGE_LENGTH = 500

GREETING_PHRASES = {
    "hi",
    "hi there",
    "hello",
    "hey",
    "hey there",
    "hello there",
    "greetings",
    "good morning",
    "good afternoon",
    "good evening",
}
NORMALIZED_GREETING_PHRASES = {
    re.sub(r"(.)\1+", r"\1", phrase) for phrase in GREETING_PHRASES
}

# Selections supply missing query context; the trained model still chooses the intent.
FOLLOW_UP_QUERIES = {
    "awaiting_business_permit_type": (
        ("new business permit", ("new", "bago", "bag-o", "bagong", "bag-ong")),
        ("renew business permit", ("renew", "renewal")),
        ("retirement of business permit", ("retire", "retirement", "sarado", "close")),
        ("change location business permit", ("transfer", "change location")),
    ),
    "awaiting_mtop_type": (
        ("new MTOP franchise", ("new", "bago", "bag-o", "bagong", "bag-ong")),
        ("renewal of MTOP franchise", ("renew", "renewal")),
        ("annual MTOP mayor's permit", ("annual",)),
        ("dropping of MTOP franchise", ("drop", "dropping")),
        ("substitution of MTOP unit", ("substitute", "substitution")),
        ("transfer of MTOP ownership", ("transfer",)),
    ),
}


def fallback_reply(lang: str, kind: str) -> str:
    messages = {
        "unresolved": {
            "en": (
                "I'm sorry, I couldn't find a direct answer to your question. "
                "For direct assistance, you may check our **Office Directory** to find "
                "the responsible department, office location, contact channels, and operating hours."
            ),
            "tl": (
                "Pasensya na, hindi ko mahanap ang tiyak na sagot sa inyong tanong. "
                "Para sa direktang tulong, maaari ninyong tingnan ang aming **Office Directory** "
                "upang malaman ang kaukulang departamento, lokasyon ng opisina, contact channels, at oras ng operasyon."
            ),
            "bis": (
                "Pasayloa ko, wala nako makita ang direktang tubag sa imong pangutana. "
                "Para sa direktang tabang, mahimo nimong tan-awon ang atong **Office Directory** "
                "aron makita ang responsableng departamento, lokasyon sa opisina, contact details, ug oras sa operasyon."
            ),
        },
        "missing_intent": {
            "en": "No specific information is available for this intent yet. Please refer to the Office Directory for assistance.",
            "tl": "Wala pang tiyak na impormasyon para sa katanungang ito. Maaari pong sumangguni sa Office Directory para sa tulong.",
            "bis": "Wala pay klarong impormasyon bahin niini. Palihug tan-awa ang Office Directory para sa tabang.",
        },
    }
    return messages[kind][normalize_language(lang)]


def context_error_reply(lang: str, context: str) -> str:
    messages = {
        "awaiting_business_permit_type": {
            "en": "I couldn't recognize that type. Please reply with 1, 2, 3, or 4.",
            "tl": "Hindi ko nakilala ang uri na iyon. Paki-reply ng 1, 2, 3, o 4.",
            "bis": "Wala nako mailhi kana nga klase. Palihug reply og 1, 2, 3, o 4.",
        },
        "awaiting_mtop_type": {
            "en": "I couldn't recognize that type. Please reply with 1 to 6.",
            "tl": "Hindi ko nakilala ang uri na iyon. Paki-reply ng numero 1 hanggang 6.",
            "bis": "Wala nako mailhi kana nga klase. Palihug reply og numero 1 hangtod 6.",
        },
    }
    return messages[context][normalize_language(lang)]


def answer_for_intent(
    intent: str, lang: str, default_answer: str = "No answer found."
) -> str:
    intent_data = ANSWERS.get(intent)
    if not intent_data:
        return default_answer

    answer = intent_data.get("answers", {}).get(normalize_language(lang))
    return (
        answer.strip() if isinstance(answer, str) and answer.strip() else default_answer
    )


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_CHAT_MESSAGE_LENGTH)
    language: str = "auto"
    context: str | None = None
    context_language: str | None = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, message: str) -> str:
        message = message.strip()
        if not message or not any(character.isalnum() for character in message):
            raise ValueError("Message must contain letters or numbers.")
        return message

    @field_validator("language", "context_language")
    @classmethod
    def validate_language(cls, language: str | None) -> str | None:
        if language is None:
            return None
        value = language.strip().lower()
        if value != "auto" and value not in LANGUAGE_ALIASES:
            raise ValueError("Language must be auto, English, Tagalog, or Bisaya.")
        return value


def make_reply(reply: str, lang: str, intent: str, context: str | None = None) -> dict:
    return {
        "reply": reply,
        "summary": "",
        "context": context,
        "intent": intent,
        "language": lang,
    }


def matches_disambiguation_query(message: str, rule: dict) -> bool:
    normalized = re.sub(r"[^\w\s]", " ", message.casefold())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    topic_matches = any(
        re.search(rf"(?<!\w){re.escape(trigger.casefold())}(?!\w)", normalized)
        for trigger in rule["trigger_words"]
    )
    if not topic_matches:
        return False

    if any(
        re.search(rf"(?<!\w){re.escape(exclusion.casefold())}(?!\w)", normalized)
        for exclusion in rule["exclude_words"]
    ):
        return False

    return bool(
        re.search(
            r"\b(?:apply|applies|applying|application|applications|get|getting|"
            r"obtain|obtaining|secure|securing|register|registering|"
            r"process|procedure|procedures|steps?|"
            r"require|requires|requirement|requirements|requirment|requirments|requiement|requiements|reqs?|"
            r"document|documents|dokumento|"
            r"kailangan|pangangailangan|kinahanglan|rekisito|requisito|"
            r"kuha|kumuha|mokuha|pagkuha|magkuha|unsaon|paano|how|"
            r"bayad|magkano|pila|fee|fees|cost|costs|price|payment)\b",
            normalized,
        )
    )



@router.post("/chat")
async def chat(request: ChatRequest, req: Request):
    user_msg = request.message
    context = request.context
    lang = resolve_language(request.language, user_msg)
    model_input = user_msg
    user_lower = user_msg.casefold().strip().rstrip(".!?")

    if context in FOLLOW_UP_QUERIES:
        choices = FOLLOW_UP_QUERIES[context]
        selection = re.fullmatch(r"(?:option\s+)?([0-9]+)", user_lower)
        matched_query = None
        choice_number = None
        if selection:
            number = int(selection[1])
            if 1 <= number <= len(choices):
                matched_query = choices[number - 1][0]
        else:
            for query, aliases in choices:
                if user_lower in aliases:
                    matched_query = query
                    break

        # A bare selection has no reliable language of its own.
        if (
            (selection or matched_query)
            and request.language == "auto"
            and request.context_language
            and request.context_language != "auto"
        ):
            lang = normalize_language(request.context_language)

        if selection and matched_query is None:
            return make_reply(
                context_error_reply(lang, context), lang, "disambiguation", context
            )
        if matched_query:
            model_input = matched_query
        # Other messages are fresh questions, not forced into the old menu.

    # Clarify broad business-permit application questions before classification.
    if model_input == user_msg:
        for rule in DISAMBIGUATION_RULES.values():
            if user_lower in rule["trigger_words"] or matches_disambiguation_query(
                user_msg, rule
            ):
                return make_reply(
                    rule["response"][lang], lang, "disambiguation", rule["context"]
                )

    print(f"MODEL INPUT: {model_input}")

    cleaned = clean_text(model_input)
    print(f"CLEANED: {cleaned}")

    normalized_greeting = re.sub(r"(.)\1+", r"\1", user_lower)
    is_greeting = (
        model_input == user_msg
        and normalized_greeting in NORMALIZED_GREETING_PHRASES
    )
    approved_intent = (
        TRAINING_PHRASES.get(cleaned) if model_input == user_msg else None
    )
    intent = (
        "greetings"
        if is_greeting
        else approved_intent or predict_intent(cleaned)
    )
    print(f"INTENT: {intent}")

    confidence = (
        1.0
        if is_greeting or approved_intent
        else get_confidence(model_input, cleaned)
    )
    print(f"CL: {confidence}")

    logger.info(
        "Chat prediction: intent=%s language=%s confidence=%s", intent, lang, confidence
    )
    ip = req.client.host if req.client else None

    # if not intent or (confidence is not None and confidence < 0.8):
    if confidence < 0.8:
        print(f"LOW CL: {confidence}")
        log_unresolved_chat(model_input, confidence)

        log_chat(user_msg, intent or "unresolved", ip, False, confidence)
        # log_chat(user_msg, intent or "unresolved", ip, False, confidence)

        return make_reply(fallback_reply(lang, "unresolved"), lang, "unresolved")

    answer = answer_for_intent(intent, lang, "")
    if not answer:
        logger.warning(
            "Missing knowledge-base answer: intent=%s language=%s", intent, lang
        )
        log_chat(user_msg, intent, ip, False, confidence)
        return make_reply(fallback_reply(lang, "missing_intent"), lang, intent)

    response = make_reply(answer, lang, intent)
    # Extractive summarization via LsaSummarizer for detailed responses
    response["summary"] = summarize_text(answer)
    log_chat(user_msg, intent, ip, True, confidence)
    return response


def log_unresolved_chat(question, confidence):

    try:
        supabase.table("unresolved_queries").insert(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "question": question,
                "confidence": confidence,
                # "resolved": resolved,
            }
        ).execute()

    except Exception as e:
        print(f"[ERROR] Failed to log chat: {e}")


def log_chat(msg, intent, ip, resolved, confidence=0.0):

    try:
        supabase.table("chat_logs").insert(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "user_message": msg,
                "predicted_intent": intent,
                "confidence": confidence,
                # "resolved": resolved,
            }
        ).execute()
        logger.info(
            "Chat handled: intent=%s ip=%s resolved=%s confidence=%s",
            intent,
            ip,
            resolved,
            confidence,
        )
    except Exception as e:
        print(f"[ERROR] Failed to log chat: {e}")
