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
from sklearn.calibration import CalibratedClassifierCV
from sklearn.neural_network import MLPClassifier

from utils.preprocess import clean_text

# from services.nlp import SpaCyVectorTransformer
from supabase_client import supabase

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


import pandas as pd


def load_data():
    print("[INFO] Loading training data from Supabase and local CSV...")

    data = []

    # --------------------------------------------------
    # 1. Load intents from Supabase (paginated)
    # --------------------------------------------------
    supabase_intent_map = {}
    page_size = 1000
    start = 0
    while True:
        intents_res = (
            supabase.table("intents")
            .select("id, intent_name")
            .range(start, start + page_size - 1)
            .execute()
        )
        batch = intents_res.data or []
        for row in batch:
            if row.get("id") is not None and row.get("intent_name"):
                supabase_intent_map[str(row["id"])] = row["intent_name"]
        if len(batch) < page_size:
            break
        start += page_size

    # --------------------------------------------------
    # 2. Load training phrases from Supabase (paginated)
    # --------------------------------------------------
    all_phrases = []
    start = 0
    while True:
        phrases_res = (
            supabase.table("training_phrases")
            .select("intent_id, phrase")
            .range(start, start + page_size - 1)
            .execute()
        )
        batch = phrases_res.data or []
        all_phrases.extend(batch)
        if len(batch) < page_size:
            break
        start += page_size

    for row in all_phrases:
        intent_name = supabase_intent_map.get(str(row.get("intent_id")))
        phrase = row.get("phrase")

        if intent_name and phrase is not None and str(phrase).strip():
            data.append(
                {
                    "question": str(phrase).strip(),
                    "intent": intent_name,
                    "source": "supabase",
                }
            )

    print(
        f"[INFO] Supabase samples: "
        f"{sum(1 for row in data if row['source'] == 'supabase')}"
    )

    # --------------------------------------------------
    # 3. Load local CSV files
    # --------------------------------------------------
    print("[INFO] Loading local CSV files...")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    intents_path = os.path.join(base_dir, "intents.csv")
    phrases_path = os.path.join(base_dir, "training_phrases_augmented.csv")

    intents_df = (
        pd.read_csv(intents_path)
        if os.path.exists(intents_path)
        else pd.DataFrame(columns=["id", "intent_name"])
    )
    phrases_df = (
        pd.read_csv(phrases_path)
        if os.path.exists(phrases_path)
        else pd.DataFrame(columns=["intent_id", "phrase"])
    )

    # Normalize ID types to prevent int/string mismatches
    local_intent_map = {
        str(int(row["id"]))
        if pd.notna(row["id"]) and str(row["id"]).replace(".", "", 1).isdigit()
        else str(row["id"]).strip(): str(row["intent_name"]).strip()
        for _, row in intents_df.iterrows()
        if pd.notna(row["id"])
        and pd.notna(row["intent_name"])
        and str(row["intent_name"]).strip()
    }

    for _, row in phrases_df.iterrows():
        raw_intent_id = row.get("intent_id")
        phrase = row.get("phrase")

        if pd.isna(raw_intent_id) or pd.isna(phrase):
            continue

        # Handle integer IDs stored as floats, e.g. 12.0
        try:
            intent_id = str(int(raw_intent_id))
        except (ValueError, TypeError, OverflowError):
            intent_id = str(raw_intent_id).strip()

        intent_name = local_intent_map.get(intent_id)

        if intent_name and str(phrase).strip():
            data.append(
                {
                    "question": str(phrase).strip(),
                    "intent": intent_name,
                    "source": "csv",
                }
            )

    print(f"[INFO] CSV samples: {sum(1 for row in data if row['source'] == 'csv')}")

    # --------------------------------------------------
    # 4. Combine and validate
    # --------------------------------------------------
    df = pd.DataFrame(data)

    if df.empty:
        raise ValueError("No valid training data found.")

    df["question"] = df["question"].astype(str).apply(clean_text)

    df["intent"] = df["intent"].astype(str).str.strip()

    # Remove empty cleaned questions and invalid labels
    df = df[
        df["question"].notna()
        & df["question"].str.strip().ne("")
        & df["intent"].str.strip().ne("")
    ].copy()

    # Remove duplicate question-intent pairs across both sources
    before_dedup = len(df)

    df = df.drop_duplicates(subset=["question", "intent"]).reset_index(drop=True)

    print(f"[INFO] Removed {before_dedup - len(df)} duplicate question-intent pairs.")

    # --------------------------------------------------
    # 5. Check class distribution
    # --------------------------------------------------
    intent_counts = df["intent"].value_counts()
    rare_intents = intent_counts[intent_counts < 2]

    if not rare_intents.empty:
        print("\n[WARNING] Intents with fewer than 2 samples:")

        for intent, count in rare_intents.items():
            print(f"  - {intent}: {count} sample(s)")

    print(f"\n[INFO] Total training samples: {len(df)}")
    print(f"[INFO] Number of intents: {df['intent'].nunique()}")
    print("\n[INFO] Samples by source:")
    print(df["source"].value_counts().to_string())

    # Return only the columns required for model training
    return df[["question", "intent"]]


# def train_and_compare():
#     df = load_data()

#     X = df["question"]
#     y = df["intent"]

#     label_encoder = LabelEncoder()
#     y_encoded = label_encoder.fit_transform(y)

#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y_encoded, test_size=0.2, random_state=42
#     )

#     # Hybrid feature extraction: TF-IDF (keyword frequency) + SpaCy (semantic meaning)
#     # Added max_features=3000 to prevent MemoryError on standard laptops
#     hybrid_features = FeatureUnion([
#         ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000)),
#         ("spacy_vectors", SpaCyVectorTransformer()),
#     ], transformer_weights={
#         "tfidf": 1.0,
#         "spacy_vectors": 0.5
#     })

#     models = {
#         "logistic_regression": LogisticRegression(max_iter=2000, random_state=42),
#         "svm": LinearSVC(max_iter=2000),
#         "neural_network": MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=2000, random_state=42)
#     }

#     results = {}
#     best_name = None
#     best_score = 0
#     best_pipeline = None

#     for name, clf in models.items():
#         pipeline = Pipeline([
#             ("features", hybrid_features),
#             ("clf", clf)
#         ])

#         pipeline.fit(X_train, y_train)
#         y_pred = pipeline.predict(X_test)
#         acc = accuracy_score(y_test, y_pred)

#         results[name] = {
#             "accuracy": acc,
#             "report": classification_report(
#                 y_test,
#                 y_pred,
#                 labels=range(len(label_encoder.classes_)),
#                 target_names=label_encoder.classes_,
#                 output_dict=True,
#                 zero_division=0
#             )
#         }

#         print(f"{name}: {acc:.4f}")

#         if acc > best_score:
#             best_score = acc
#             best_name = name
#             best_pipeline = pipeline

#     joblib.dump(best_pipeline, os.path.join(MODEL_DIR, "best_model.pkl"))
#     joblib.dump(label_encoder, os.path.join(MODEL_DIR, "label_encoder.pkl"))

#     metrics_data = {
#         "best_model": best_name,
#         "best_accuracy": best_score,
#         "all_results": results
#     }

#     with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
#         json.dump(metrics_data, f, indent=2)

#     # print("[INFO] Pushing training metrics to Supabase...")

#     # try:
#     #     metrics_batch = []
#     #     for model_key, model_info in results.items():
#     #         supabase.table("nlp_models").upsert({
#     #             "model_name": model_key,
#     #             "model_file": f"{model_key}.pkl",
#     #             "accuracy": model_info.get("accuracy", 0.0)
#     #         }).execute()

#     #         report = model_info.get("report", {})
#     #         for intent_name, scores in report.items():
#     #             if isinstance(scores, dict) and "precision" in scores:
#     #                 metrics_batch.append({
#     #                     "model_name": model_key,
#     #                     "intent_name": intent_name,
#     #                     "precision": scores.get("precision", 0.0),
#     #                     "recall": scores.get("recall", 0.0),
#     #                     "f1_score": scores.get("f1-score", 0.0),
#     #                     "support": int(scores.get("support", 0.0))
#     #                 })

#     #     chunk_size = 100
#     #     for i in range(0, len(metrics_batch), chunk_size):
#     #         chunk = metrics_batch[i:i+chunk_size]
#     #         supabase.table("training_metrics").insert(chunk).execute()
#     #     print(f"[INFO] Successfully uploaded {len(metrics_batch)} metrics to Supabase.")
#     # except Exception as e:
#     #     print(f"[ERROR] Failed to push metrics to Supabase: {e}")


#     print(f"\nBest model: {best_name} ({best_score:.4f})")
#     return metrics_data
def train_and_compare():
    df = load_data()

    print(f"[INFO] Dataset: {len(df)} samples")
    print(f"[INFO] Intents: {df['intent'].nunique()}")

    # ---------------------------------------------------------
    # Check minimum samples per intent and satisfy stratification
    # ---------------------------------------------------------
    intent_counts = df["intent"].value_counts()
    print("\n[INFO] Samples per intent:")
    print(intent_counts)

    rare_intents = intent_counts[intent_counts < 2].index
    if not rare_intents.empty:
        print(f"\n[INFO] Auto-duplicating {len(rare_intents)} single-sample intent(s) to satisfy stratified split: {list(rare_intents)}")
        rare_subset = df[df["intent"].isin(rare_intents)].copy()
        df = pd.concat([df, rare_subset], ignore_index=True)

    X = df["question"].astype(str)
    y = df["intent"].astype(str)

    # ---------------------------------------------------------
    # Encode labels
    # ---------------------------------------------------------

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # ---------------------------------------------------------
    # Hold out test set
    # ---------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )

    print(f"\n[INFO] Training samples: {len(X_train)}")
    print(f"[INFO] Testing samples: {len(X_test)}")

    # =========================================================
    # WORD + CHARACTER TF-IDF (Optimized for Memory & Speed)
    # =========================================================

    word_tfidf = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        sublinear_tf=True,
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.98,
        max_features=5000,
        norm="l2",
    )

    char_tfidf = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=1,
        max_features=5000,
        sublinear_tf=True,
        norm="l2",
    )

    features = FeatureUnion(
        [
            ("word", word_tfidf),
            ("char", char_tfidf),
        ]
    )

    # =========================================================
    # MODELS TO COMPARE (Objective 3: LR, SVM, MLP)
    # =========================================================

    models = {
        "logistic_regression": Pipeline(
            [
                ("features", features),
                (
                    "classifier",
                    LogisticRegression(
                        C=2.0,
                        class_weight="balanced",
                        max_iter=1000,
                        solver="lbfgs",
                        random_state=42,
                    ),
                ),
            ]
        ),
        "linear_svm": Pipeline(
            [
                ("features", features),
                (
                    "classifier",
                    CalibratedClassifierCV(
                        LinearSVC(
                            C=1.5, class_weight="balanced", max_iter=3000, random_state=42
                        ),
                        cv=2,
                    ),
                ),
            ]
        ),
        # -----------------------------------------------------
        # Neural Network - MLP
        # -----------------------------------------------------
        "mlp": Pipeline(
            [
                ("features", features),
                (
                    "classifier",
                    MLPClassifier(
                        hidden_layer_sizes=(64, 32),
                        activation="relu",
                        solver="adam",
                        alpha=0.0001,
                        batch_size=64,
                        learning_rate_init=0.001,
                        max_iter=60,
                        early_stopping=True,
                        validation_fraction=0.10,
                        n_iter_no_change=5,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }

    results = {}

    best_name = None
    best_score = -1
    best_pipeline = None

    # =========================================================
    # TRAIN
    # =========================================================

    for name, pipeline in models.items():
        print(f"\n{'=' * 60}")
        print(f"[INFO] Training: {name}")
        print(f"{'=' * 60}")

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)

        report = classification_report(
            y_test,
            y_pred,
            labels=range(len(label_encoder.classes_)),
            target_names=label_encoder.classes_,
            output_dict=True,
            zero_division=0,
        )

        macro_f1 = report["macro avg"]["f1-score"]
        weighted_f1 = report["weighted avg"]["f1-score"]

        results[name] = {
            "accuracy": float(accuracy),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "report": report,
        }

        print(f"Accuracy:     {accuracy:.4f}")
        print(f"Macro F1:     {macro_f1:.4f}")
        print(f"Weighted F1:  {weighted_f1:.4f}")

        # Select based on macro F1
        if macro_f1 > best_score:
            best_score = macro_f1
            best_name = name
            best_pipeline = pipeline

    # =========================================================
    # SAVE BEST MODEL
    # =========================================================

    if best_pipeline is None:
        raise RuntimeError("No model was successfully trained.")

    # joblib.dump(best_pipeline, os.path.join(MODEL_DIR, "best_model_augmented.pkl"))
    # joblib.dump(label_encoder, os.path.join(MODEL_DIR, "label_encoder_augmented.pkl"))

    joblib.dump(best_pipeline, os.path.join(MODEL_DIR, "best_model.pkl"))
    joblib.dump(label_encoder, os.path.join(MODEL_DIR, "label_encoder.pkl"))

    # =========================================================
    # SAVE METRICS
    # =========================================================

    best_result = results[best_name]

    metrics_data = {
        "best_model": best_name,
        "best_accuracy": best_result["accuracy"],
        "best_macro_f1": best_result["macro_f1"],
        "best_weighted_f1": best_result["weighted_f1"],
        "all_results": results,
    }

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)

    # =========================================================
    # FINAL RESULT
    # =========================================================

    print("\n" + "=" * 60)
    print("BEST MODEL")
    print("=" * 60)

    print(f"Model:        {best_name}")
    print(f"Accuracy:     {best_result['accuracy']:.4f}")
    print(f"Macro F1:     {best_result['macro_f1']:.4f}")
    print(f"Weighted F1:  {best_result['weighted_f1']:.4f}")

    print(
        f"\n[INFO] Model saved to: {os.path.join(MODEL_DIR, 'best_model_augmented.pkl')}"
    )

    return metrics_data


if __name__ == "__main__":
    load_data()
    # train_and_compare()
