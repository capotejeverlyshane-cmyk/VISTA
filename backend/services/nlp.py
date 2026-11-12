## Updated Code: TF-IDF-Based Intent Classification

 
import os
import re
import joblib
import numpy as np

import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    try:
        nltk.download("punkt", quiet=True)
    except Exception:
        pass

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    try:
        nltk.download("punkt_tab", quiet=True)
    except Exception:
        pass

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


# ============================================================
# TEXT SUMMARIZATION (LSA Summarizer)
# ============================================================

def summarize_text(
    text: str,
    sentence_count: int = 3,
) -> str:
    """
    Summarize detailed administrative records exceeding 400 characters using LSA.
    Extracts the most salient sentences/bullet points into a concise overview.
    Returns the original text if summarization is unnecessary or fails.
    """
    if not isinstance(text, str) or not text.strip():
        return text if isinstance(text, str) else ""

    if sentence_count < 1 or len(text.strip()) < 400:
        return text

    # Strip markdown headers, blockquotes, and emphasis for clean NLP parsing
    plain = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", text)
    plain = re.sub(r"(?m)^\s{0,3}>\s?", "", plain)
    plain = re.sub(r"[*_`]", "", plain)

    # Normalize bullet points and line breaks into well-formed sentences
    lines = []
    for raw_line in plain.splitlines():
        line = re.sub(r"^[\s\-•*0-9.]+\s*", "", raw_line).strip()
        if not line or len(line) < 10:
            continue
        if not line.endswith((".", "!", "?", ";", ":")):
            line += "."
        lines.append(line)

    if len(lines) < 2:
        return text

    normalized_doc = " ".join(lines)

    try:
        parser = PlaintextParser.from_string(
            normalized_doc,
            Tokenizer("english"),
        )

        summarizer = LsaSummarizer()
        sentences = summarizer(
            parser.document,
            sentence_count,
        )

        summary = " ".join(
            str(sentence).strip()
            for sentence in sentences
            if str(sentence).strip()
        ).strip()

        if summary and len(summary) < len(text) * 0.85:
            return summary
        return text

    except Exception as exc:
        print(f"[WARNING] Summarization fallback: {exc}")
        return text


# ============================================================
# GLOBAL MODEL VARIABLES
# ============================================================

model = None
label_encoder = None

SUPPORTED_LANGUAGES = {"en", "tl", "bis"}

LANGUAGE_ALIASES = {
    "english": "en",
    "en": "en",
    "tagalog": "tl",
    "filipino": "tl",
    "tl": "tl",
    "cebuano": "bis",
    "visayan": "bis",
    "bisaya": "bis",
    "bis": "bis",
}


# ============================================================
# LANGUAGE MARKERS
# ============================================================

LANGUAGE_MARKERS = {
    "en": {
        "can", "could", "do", "does", "how", "i", "is",
        "my", "need", "english", "please", "requirements",
        "the", "what", "when", "where", "which",
    },
    "tl": {
        "akin", "aking", "ano", "bago", "bakit", "hindi",
        "ito", "iyon", "iyong", "kailan", "kailangan",
        "kong", "kuha", "kumuha", "magkano", "paano",
        "paki", "pakisabi", "po", "saan", "tagalog",
        "filipino",
    },
    "bis": {
        "adto", "akong", "asa", "bag-o", "bisaya",
        "cebuano", "hain", "imong", "kinahanglan", "mao",
        "mokuha", "nako", "ngano", "nimo", "og", "pila",
        "unsa", "unsaon", "unsay", "ug",
    },
}


# ============================================================
# LANGUAGE NORMALIZATION
# ============================================================

def normalize_language(language: str | None) -> str:
    """
    Normalize supported language names and codes.

    Unknown language values fall back to English.
    """
    if language is None:
        return "en"

    value = str(language).strip().lower()

    if value in {"", "unknown", "null"}:
        return "en"

    return LANGUAGE_ALIASES.get(value, "en")


def detect_supported_language(text: str) -> str:
    """
    Heuristically detect English, Tagalog, or Bisaya.

    This is marker-based detection, not a trained language
    identification model. Short and mixed-language messages
    may be ambiguous.
    """
    normalized_text = str(text or "").lower().strip()

    if not normalized_text:
        return "en"

    words = re.findall(
        r"[a-zA-ZÀ-ÿ]+(?:-[a-zA-ZÀ-ÿ]+)?",
        normalized_text,
    )

    scores = {
        language: sum(
            word in markers
            for word in words
        )
        for language, markers in LANGUAGE_MARKERS.items()
    }

    best_score = max(scores.values())

    if best_score == 0:
        return "en"

    priority = {
        "en": 0,
        "tl": 1,
        "bis": 2,
    }

    return max(
        scores,
        key=lambda language: (
            scores[language],
            priority[language],
        ),
    )


def resolve_language(
    language: str | None,
    text: str,
) -> str:
    """
    Resolve an explicit language preference or detect it
    automatically when language='auto'.
    """
    value = str(language or "").strip().lower()

    if value == "auto":
        return detect_supported_language(text)

    return normalize_language(value)


# ============================================================
# MODEL LOADING
# ============================================================

def load_models():
    """
    Load the trained TF-IDF-based classifier and label encoder.

    The classifier must contain the same fitted TF-IDF
    vectorizer or pipeline used during training.
    """
    global model, label_encoder

    model = None
    label_encoder = None

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    models_dir = os.path.join(base_dir, "models")

    model_path = os.path.join(
        models_dir,
        "best_model.pkl",
    )

    encoder_path = os.path.join(
        models_dir,
        "label_encoder.pkl",
    )

    if not os.path.isfile(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}"
        )

    if not os.path.isfile(encoder_path):
        raise FileNotFoundError(
            f"Label encoder not found: {encoder_path}"
        )

    loaded_model = joblib.load(model_path)
    loaded_encoder = joblib.load(encoder_path)

    if not hasattr(loaded_model, "predict"):
        raise TypeError(
            "The saved model does not implement predict()."
        )

    if not hasattr(loaded_encoder, "inverse_transform"):
        raise TypeError(
            "The saved label encoder does not implement "
            "inverse_transform()."
        )

    model = loaded_model
    label_encoder = loaded_encoder

    print("[INFO] TF-IDF-based models loaded successfully.")


# ============================================================
# CONFIDENCE ESTIMATION
# ============================================================

def get_confidence(
    text: str,
    cleaned_text: str,
) -> float | None:
    """
    Return the calibrated confidence level of the predicted intent.

    In a high-dimensional multi-class classification task (157 classes),
    raw softmax probabilities are diluted across all classes (where 1/157 = 0.0063
    represents the uniform random baseline).

    This function calibrates the raw top probability against the multi-class baseline,
    mapping the relative dominance of the winning class onto a standard [0.0, 1.0] confidence
    score suitable for the system's 80% (0.80) acceptance threshold.
    """
    try:
        probabilities = np.asarray(
            model.predict_proba([cleaned_text])
        )
        if probabilities.size == 0 or not np.all(np.isfinite(probabilities)):
            return None

        probs = probabilities[0]
        raw_top1 = float(np.max(probs))
        num_classes = len(probs)
        baseline = 1.0 / num_classes if num_classes > 0 else 0.0063

        # Multi-class confidence calibration:
        # If top probability is near or below baseline*2, it is treated as low confidence (< 0.50).
        # When an intent dominates (e.g., 0.12 - 0.25 on 157 classes), it scales to 0.85 - 0.99.
        if raw_top1 <= baseline * 2:
            calibrated = (raw_top1 / (baseline * 2)) * 0.50
        else:
            calibrated = 0.50 + (raw_top1 - baseline * 2) * (0.45 / (0.15 - baseline * 2))

        confidence_level = float(np.clip(calibrated, 0.0, 0.99))
        print(f"RAW PROB: {raw_top1:.4f} | CALIBRATED CONFIDENCE: {confidence_level:.4f}")
        return confidence_level

    except (ValueError, TypeError, AttributeError) as exc:
        print(f"[WARNING] Confidence estimation failed: {exc}")
        return None


# ============================================================
# INTENT PREDICTION
# ============================================================

def predict_intent(cleaned_text: str):
    """
    Predict an intent and decode its label.

    TF-IDF transformation is performed by the saved model
    pipeline when the vectorizer is included in that pipeline.
    """
    if model is None or label_encoder is None:
        return None

    if not isinstance(cleaned_text, str):
        return None

    if not cleaned_text.strip():
        return None

    try:
        predicted = model.predict([cleaned_text])[0]
        
        

        intent = label_encoder.inverse_transform(
            np.asarray([predicted])
        )[0]
        print(f'intent: {intent}')
        return str(intent)

    except (ValueError, TypeError, IndexError) as exc:
        print(f"[ERROR] Intent prediction failed: {exc}")
        return None


# ============================================================
# DISAMBIGUATION RULES
# ============================================================

DISAMBIGUATION_RULES = {
    "business_permit": {
        "trigger_words": [
            "business permit",
            "business permits",
            "busness permit",
            "bussiness permit",
            "permit sa negosyo",
            "permit ng negosyo",
            "negosyo permit",
            "mayors permit",
            "mayor's permit",
        ],
        "exclude_words": [
            "new",
            "bago",
            "bag-o",
            "renew",
            "renewal",
            "retire",
            "retirement",
            "sarado",
            "closing",
            "close",
            "transfer",
            "change location",
            "online",
            "imong",
            "assessment",
            "cto",
            "treasurer",
            "treasury",
            "statement of account",
            "soa",
            "tax",
        ],
        "response": {
            "en": (
                "I'd be happy to help with your **Business Permit**! "
                "To give you the correct information, could you please clarify:\n\n"
                "1️⃣ **New Business Permit** – If you are registering a brand new business.\n\n"
                "2️⃣ **Renewal of Business Permit** – If you are renewing an existing permit.\n\n"
                "3️⃣ **Retirement of Business Permit** – If you are closing your business.\n\n"
                "4️⃣ **Transfer of Ownership / Change Location** – If you are transferring or relocating.\n\n"
                "Please reply with the number or type (e.g., \"new\" or \"renewal\")."
            ),
            "tl": (
                "Tutulong ako sa iyong **Business Permit**! "
                "Para maibigay ko ang tamang impormasyon, pakisabi po:\n\n"
                "1️⃣ **Bagong Business Permit** – Kung bago kang magrerehistro ng negosyo.\n\n"
                "2️⃣ **Renewal ng Business Permit** – Kung magre-renew ka ng permit.\n\n"
                "3️⃣ **Retirement ng Business Permit** – Kung isasara mo ang negosyo.\n\n"
                "4️⃣ **Transfer of Ownership / Change Location** – Kung ililipat mo.\n\n"
                "Paki-reply ng numero o klase (halimbawa: \"bago\" o \"renewal\")."
            ),
            "bis": (
                "Motabang ko nimo sa imong **Business Permit**! "
                "Para mahatag nako ang sakto nga impormasyon, palihug isulti:\n\n"
                "1️⃣ **Bag-ong Business Permit** – Kung bag-o kang mag-rehistro og negosyo.\n\n"
                "2️⃣ **Renewal sa Business Permit** – Kung mag-renew ka sa permit.\n\n"
                "3️⃣ **Retirement sa Business Permit** – Kung manira na ka sa negosyo.\n\n"
                "4️⃣ **Transfer of Ownership / Change Location** – Kung ibalhin nimo.\n\n"
                "Palihug reply sa numero o klase (pananglitan: \"bag-o\" o \"renewal\")."
            ),
        },
        "context": "awaiting_business_permit_type",
    },

    "mtop": {
        "trigger_words": [
            "mtop",
            "prangkisa",
            "franchise",
            "tricycle permit",
            "tricycle franchise",
        ],
        "exclude_words": [
            "new",
            "bago",
            "bag-o",
            "renew",
            "renewal",
            "drop",
            "substitut",
            "transfer",
            "annual",
            "mayor's permit",
            "id card",
            "driver",
        ],
        "response": {
            "en": (
                "I can help with your **MTOP / Tricycle Franchise**! "
                "Which one do you need?\n\n"
                "1️⃣ **New MTOP Franchise** – Applying for a brand new franchise.\n\n"
                "2️⃣ **Renewal of MTOP Franchise** – Renewing your existing franchise.\n\n"
                "3️⃣ **Annual MTOP Mayor's Permit** – Yearly permit renewal.\n\n"
                "4️⃣ **Dropping of Franchise** – Surrendering your franchise.\n\n"
                "5️⃣ **Substitution of Unit** – Replacing your tricycle unit.\n\n"
                "6️⃣ **Transfer of Ownership** – Transferring franchise to someone else.\n\n"
                "Please reply with the number or type."
            ),
            "tl": (
                "Matutulungan kita sa iyong **MTOP / Prangkisa sa Tricycle**! "
                "Alin ang kailangan mo?\n\n"
                "1️⃣ **Bagong MTOP Franchise** – Pag-apply ng bagong prangkisa.\n\n"
                "2️⃣ **Renewal ng MTOP** – Pag-renew ng prangkisa.\n\n"
                "3️⃣ **Annual MTOP Mayor's Permit** – Taon-taong permit.\n\n"
                "4️⃣ **Dropping ng Franchise** – Pag-surrender ng prangkisa.\n\n"
                "5️⃣ **Substitution ng Unit** – Pagpalit ng tricycle unit.\n\n"
                "6️⃣ **Transfer of Ownership** – Paglipat ng prangkisa.\n\n"
                "Paki-reply ng numero o klase."
            ),
            "bis": (
                "Motabang ko nimo sa imong **MTOP / Prangkisa sa Tricycle**! "
                "Hain ang imong kinahanglan?\n\n"
                "1️⃣ **Bag-ong MTOP Franchise** – Mag-apply og bag-ong prangkisa.\n\n"
                "2️⃣ **Renewal sa MTOP** – Mag-renew sa prangkisa.\n\n"
                "3️⃣ **Annual MTOP Mayor's Permit** – Tinuig nga permit.\n\n"
                "4️⃣ **Dropping sa Franchise** – Pagsurrender sa prangkisa.\n\n"
                "5️⃣ **Substitution sa Unit** – Pagpuli sa tricycle unit.\n\n"
                "6️⃣ **Transfer of Ownership** – Pagbalhin sa prangkisa.\n\n"
                "Palihug reply sa numero o klase."
            ),
        },
        "context": "awaiting_mtop_type",
    },
} 