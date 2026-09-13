import re
import joblib
import os
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
import spacy

# Load spaCy model for inference
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("[INFO] Downloading spaCy model en_core_web_md (this might take a while if not cached)...")
    from spacy.cli import download
    download("en_core_web_md")
    nlp = spacy.load("en_core_web_md")

class SpaCyVectorTransformer(BaseEstimator, TransformerMixin):
    """
    Custom scikit-learn transformer that converts text into SpaCy
    semantic word vectors. This captures the MEANING of sentences,
    not just keyword frequency like TF-IDF.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.array([nlp(text).vector for text in X])

# Backward compatibility hack for old models trained when this was in __main__
import sys
setattr(sys.modules["__main__"], "SpaCyVectorTransformer", SpaCyVectorTransformer)

# Summarization imports
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def summarize_text(text: str, sentence_count: int = 3) -> str:
    """
    Summarize long answer text using LSA (Latent Semantic Analysis).
    Only summarizes if the text is longer than 400 characters.
    """
    plain = re.sub(r'[#*_\-`>]', '', text).strip()
    if len(plain) < 400:
        return text

    try:
        parser = PlaintextParser.from_string(plain, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, sentence_count)
        summary = " ".join(str(s) for s in summary_sentences)
        return summary if summary.strip() else text
    except Exception:
        return text

# Global Model variables
model = None
label_encoder = None

def load_models():
    """Loads the trained ML models."""
    global model, label_encoder
    try:
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "best_model.pkl")
        le_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "label_encoder.pkl")
        model = joblib.load(model_path)
        label_encoder = joblib.load(le_path)
        print("[INFO] Models loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to load models: {e}")

def get_confidence(text: str, cleaned_text: str) -> float:
    """Calculates prediction confidence."""
    if not model:
        return 0.0
    
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([cleaned_text])
        return float(probabilities.max())
    elif hasattr(model, "decision_function"):
        scores = model.decision_function([cleaned_text])
        if len(scores.shape) == 1:
            max_score = float(scores[0])
        else:
            max_score = float(scores.max())
        confidence = min(max((max_score + 1) / 2, 0), 1)
        return confidence
    return 0.75

def predict_intent(cleaned_text: str):
    """Predicts the intent from cleaned text."""
    if not model or not label_encoder:
        return None, 0.0
    pred_encoded = model.predict([cleaned_text])[0]
    intent = label_encoder.inverse_transform([pred_encoded])[0]
    return intent

DISAMBIGUATION_RULES = {
    "business_permit": {
        "trigger_words": ["business permit", "permit sa negosyo", "permit ng negosyo", "business permit requirements", "negosyo permit"],
        "exclude_words": ["new", "bago", "bag-o", "renew", "renewal", "retire", "retirement", "sarado", "closing", "close", "transfer", "change location", "online"],
        "response": {
            "en": "I'd be happy to help with your **Business Permit**! To give you the correct information, could you please clarify:\n\n1️⃣ **New Business Permit** – If you are registering a brand new business.\n2️⃣ **Renewal of Business Permit** – If you are renewing an existing permit.\n3️⃣ **Retirement of Business Permit** – If you are closing your business.\n4️⃣ **Transfer of Ownership / Change Location** – If you are transferring or relocating.\n\nPlease reply with the number or type (e.g., \"new\" or \"renewal\").",
            "tl": "Tutulong ako sa iyong **Business Permit**! Para maibigay ko ang tamang impormasyon, pakisabi po:\n\n1️⃣ **Bagong Business Permit** – Kung bago kang magrerehistro ng negosyo.\n2️⃣ **Renewal ng Business Permit** – Kung magre-renew ka ng permit.\n3️⃣ **Retirement ng Business Permit** – Kung isasara mo ang negosyo.\n4️⃣ **Transfer of Ownership / Change Location** – Kung ililipat mo.\n\nPaki-reply ng numero o klase (halimbawa: \"bago\" o \"renewal\").",
            "bis": "Motabang ko nimo sa imong **Business Permit**! Para mahatag nako ang sakto nga impormasyon, palihug isulti:\n\n1️⃣ **Bag-ong Business Permit** – Kung bag-o kang mag-rehistro og negosyo.\n2️⃣ **Renewal sa Business Permit** – Kung mag-renew ka sa permit.\n3️⃣ **Retirement sa Business Permit** – Kung manira na ka sa negosyo.\n4️⃣ **Transfer of Ownership / Change Location** – Kung ibalhin nimo.\n\nPalihug reply sa numero o klase (pananglitan: \"bag-o\" o \"renewal\")."
        },
        "context": "awaiting_business_permit_type"
    },
    "mtop": {
        "trigger_words": ["mtop", "prangkisa", "franchise", "tricycle permit", "tricycle franchise"],
        "exclude_words": ["new", "bago", "bag-o", "renew", "renewal", "drop", "substitut", "transfer", "annual", "mayor's permit", "id card", "driver"],
        "response": {
            "en": "I can help with your **MTOP / Tricycle Franchise**! Which one do you need?\n\n1️⃣ **New MTOP Franchise** – Applying for a brand new franchise.\n2️⃣ **Renewal of MTOP Franchise** – Renewing your existing franchise.\n3️⃣ **Annual MTOP Mayor's Permit** – Yearly permit renewal.\n4️⃣ **Dropping of Franchise** – Surrendering your franchise.\n5️⃣ **Substitution of Unit** – Replacing your tricycle unit.\n6️⃣ **Transfer of Ownership** – Transferring franchise to someone else.\n\nPlease reply with the number or type.",
            "tl": "Matutulungan kita sa iyong **MTOP / Prangkisa sa Tricycle**! Alin ang kailangan mo?\n\n1️⃣ **Bagong MTOP Franchise** – Pag-apply ng bagong prangkisa.\n2️⃣ **Renewal ng MTOP** – Pag-renew ng prangkisa.\n3️⃣ **Annual MTOP Mayor's Permit** – Taon-taong permit.\n4️⃣ **Dropping ng Franchise** – Pag-surrender ng prangkisa.\n5️⃣ **Substitution ng Unit** – Pagpalit ng tricycle unit.\n6️⃣ **Transfer of Ownership** – Paglipat ng prangkisa.\n\nPaki-reply ng numero o klase.",
            "bis": "Motabang ko nimo sa imong **MTOP / Prangkisa sa Tricycle**! Hain ang imong kinahanglan?\n\n1️⃣ **Bag-ong MTOP Franchise** – Mag-apply og bag-ong prangkisa.\n2️⃣ **Renewal sa MTOP** – Mag-renew sa prangkisa.\n3️⃣ **Annual MTOP Mayor's Permit** – Tinuig nga permit.\n4️⃣ **Dropping sa Franchise** – Pagsurrender sa prangkisa.\n5️⃣ **Substitution sa Unit** – Pagpuli sa tricycle unit.\n6️⃣ **Transfer of Ownership** – Pagbalhin sa prangkisa.\n\nPalihug reply sa numero o klase."
        },
        "context": "awaiting_mtop_type"
    }
}
