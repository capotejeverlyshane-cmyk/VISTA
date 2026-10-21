import csv
from pathlib import Path
from typing import Dict, Any
from supabase_client import supabase

# Global caches
ANSWERS: Dict[str, Any] = {}
OFFICES: list = []
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
                        "bis": row.get("bis_answer", "")
                    }
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
    except Exception as e:
        print(f"[ERROR] Failed to load offices from Supabase: {e}")
        OFFICES = []

# Initial load
def init_cache():
    refresh_answers_cache()
    load_offices()
