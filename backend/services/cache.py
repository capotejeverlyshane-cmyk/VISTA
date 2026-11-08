import csv
from pathlib import Path
from typing import Dict, Any
from supabase_client import supabase
from utils.preprocess import clean_text

# Global caches
ANSWERS: Dict[str, Any] = {}
OFFICES: list = []
TRAINING_PHRASES: Dict[str, str] = {}
LOCAL_INTENTS_PATH = Path(__file__).resolve().parent.parent / "intents.csv"


def load_local_answers():
    """Read intent names and multilingual answers from the training export."""
    with LOCAL_INTENTS_PATH.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required_columns = {"intent_name", "en_answer", "tl_answer", "bis_answer"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("Local intents CSV is missing required answer columns.")
        return {
            row["intent_name"]: {
                "id": row.get("id"),
                "department": row.get("department", "General"),
                "answers": {
                    language: row.get(f"{language}_answer", "")
                    for language in ("en", "tl", "bis")
                },
            }
            for row in reader
            if row.get("intent_name")
        }


def refresh_answers_cache():
    """Fetches all intents from Supabase and rebuilds the ANSWERS dictionary."""
    global ANSWERS
    try:
        res = supabase.table("intents").select("*").execute()
        new_answers = {}
        for row in res.data:
            intent_name = row.get("intent_name")
            if intent_name:
                new_answers[intent_name] = {
                    "id": row.get("id"),
                    "department": row.get("department", "General"),
                    "answers": {
                        "en": row.get("en_answer", ""),
                        "tl": row.get("tl_answer", ""),
                        "bis": row.get("bis_answer", ""),
                    },
                }
        if not new_answers:
            raise ValueError("Supabase returned no knowledge-base intents.")
        ANSWERS.clear()
        ANSWERS.update(new_answers)
        print(f"[INFO] Cache refreshed: Loaded {len(ANSWERS)} intents from Supabase.")
    except Exception as e:
        print(f"[ERROR] Failed to refresh answers cache from Supabase: {e}")
        try:
            local_answers = load_local_answers()
            if not local_answers:
                raise ValueError("Local intents CSV contains no answers.")
            ANSWERS.clear()
            ANSWERS.update(local_answers)
            print(f"[INFO] Fallback: Loaded {len(ANSWERS)} intents from local CSV.")
        except (OSError, ValueError, csv.Error) as local_e:
            print(f"[ERROR] Fallback failed: {local_e}")
            raise RuntimeError("Unable to load the knowledge base.") from local_e


def load_offices():
    """Loads offices directory data from Supabase."""
    global OFFICES
    try:
        res = supabase.table("office_directory").select("*").execute()
        OFFICES = res.data

        print(f"[INFO] Loaded {len(OFFICES)} offices from Supabase.")
        return OFFICES

    except Exception as e:
        print(f"[ERROR] Failed to load offices from Supabase: {e}")
        OFFICES = []


def refresh_training_phrases():
    """Cache unambiguous, admin-managed examples for exact-match resolution."""
    try:
        intent_names = {}
        page_size = 1000
        start = 0
        while True:
            result = (
                supabase.table("intents")
                .select("id, intent_name")
                .range(start, start + page_size - 1)
                .execute()
            )
            batch = result.data or []
            for row in batch:
                if row.get("id") is not None and row.get("intent_name"):
                    intent_names[str(row["id"])] = row["intent_name"]
            if len(batch) < page_size:
                break
            start += page_size

        phrase_intents = {}
        ambiguous_phrases = set()
        start = 0
        while True:
            result = (
                supabase.table("training_phrases")
                .select("intent_id, phrase")
                .range(start, start + page_size - 1)
                .execute()
            )
            batch = result.data or []
            for row in batch:
                phrase = clean_text(str(row.get("phrase") or ""))
                intent_name = intent_names.get(str(row.get("intent_id")))
                if not phrase or not intent_name or phrase in ambiguous_phrases:
                    continue
                existing_intent = phrase_intents.get(phrase)
                if existing_intent and existing_intent != intent_name:
                    phrase_intents.pop(phrase)
                    ambiguous_phrases.add(phrase)
                else:
                    phrase_intents[phrase] = intent_name
            if len(batch) < page_size:
                break
            start += page_size

        TRAINING_PHRASES.clear()
        TRAINING_PHRASES.update(phrase_intents)
        print(f"[INFO] Cached {len(TRAINING_PHRASES)} unambiguous training phrases.")
    except Exception as e:
        print(f"[WARNING] Failed to refresh training phrase cache: {e}")


def add_training_phrase(phrase: str, intent_name: str):
    """Make a newly admin-linked phrase available without waiting for retraining."""
    normalized_phrase = clean_text(phrase)
    if normalized_phrase and intent_name:
        TRAINING_PHRASES[normalized_phrase] = intent_name


# Initial load
def init_cache():
    refresh_answers_cache()
    load_offices()
    refresh_training_phrases()
