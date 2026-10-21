import json
import joblib
import numpy as np
import pandas as pd
import os

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier

from utils.preprocess import clean_text
from services.nlp import SpaCyVectorTransformer
from supabase_client import supabase

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data():
    print("[INFO] Fetching training data from Supabase...")
    # Fetch intents to map intent_id to intent_name
    intents_res = supabase.table("intents").select("id, intent_name").execute()
    intent_map = {row["id"]: row["intent_name"] for row in intents_res.data}
    
    # Fetch training phrases
    phrases_res = supabase.table("training_phrases").select("intent_id, phrase").execute()
    
    data = []
    for row in phrases_res.data:
        intent_name = intent_map.get(row.get("intent_id"))
        if intent_name and row.get("phrase"):
            data.append({
                "question": row["phrase"],
                "intent": intent_name
            })
            
    df = pd.DataFrame(data)
    df["question"] = df["question"].astype(str).apply(clean_text)
    print(f"[INFO] Loaded {len(df)} training samples.")
    return df

def train_and_compare():
    df = load_data()

    X = df["question"]
    y = df["intent"]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    # Hybrid feature extraction: TF-IDF (keyword frequency) + SpaCy (semantic meaning)
    # Added max_features=3000 to prevent MemoryError on standard laptops
    hybrid_features = FeatureUnion([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000)),
        ("spacy_vectors", SpaCyVectorTransformer()),
    ], transformer_weights={
        "tfidf": 1.0,
        "spacy_vectors": 0.5
    })

    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, random_state=42),
        "svm": LinearSVC(max_iter=2000),
        "neural_network": MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=2000, random_state=42)
    }

    results = {}
    best_name = None
    best_score = 0
    best_pipeline = None

    for name, clf in models.items():
        pipeline = Pipeline([
            ("features", hybrid_features),
            ("clf", clf)
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        results[name] = {
            "accuracy": acc,
            "report": classification_report(
                y_test,
                y_pred,
                labels=range(len(label_encoder.classes_)),
                target_names=label_encoder.classes_,
                output_dict=True,
                zero_division=0
            )
        }

        print(f"{name}: {acc:.4f}")

        if acc > best_score:
            best_score = acc
            best_name = name
            best_pipeline = pipeline

    joblib.dump(best_pipeline, os.path.join(MODEL_DIR, "best_model.pkl"))
    joblib.dump(label_encoder, os.path.join(MODEL_DIR, "label_encoder.pkl"))

    metrics_data = {
        "best_model": best_name,
        "best_accuracy": best_score,
        "all_results": results
    }

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)

    print("[INFO] Pushing training metrics to Supabase...")
    try:
        metrics_batch = []
        for model_key, model_info in results.items():
            supabase.table("nlp_models").upsert({
                "model_name": model_key,
                "model_file": f"{model_key}.pkl",
                "accuracy": model_info.get("accuracy", 0.0)
            }).execute()
            
            report = model_info.get("report", {})
            for intent_name, scores in report.items():
                if isinstance(scores, dict) and "precision" in scores:
                    metrics_batch.append({
                        "model_name": model_key,
                        "intent_name": intent_name,
                        "precision": scores.get("precision", 0.0),
                        "recall": scores.get("recall", 0.0),
                        "f1_score": scores.get("f1-score", 0.0),
                        "support": int(scores.get("support", 0.0))
                    })
                    
        chunk_size = 100
        for i in range(0, len(metrics_batch), chunk_size):
            chunk = metrics_batch[i:i+chunk_size]
            supabase.table("training_metrics").insert(chunk).execute()
        print(f"[INFO] Successfully uploaded {len(metrics_batch)} metrics to Supabase.")
    except Exception as e:
        print(f"[ERROR] Failed to push metrics to Supabase: {e}")

    print(f"\nBest model: {best_name} ({best_score:.4f})")
    return metrics_data

if __name__ == "__main__":
    train_and_compare()