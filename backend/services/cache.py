import json
from typing import Dict, Any
from supabase_client import supabase

# Global caches
ANSWERS: Dict[str, Any] = {}
OFFICES: list = []

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
        ANSWERS.clear()
        ANSWERS.update(new_answers)
        print(f"[INFO] Cache refreshed: Loaded {len(ANSWERS)} intents from Supabase.")
    except Exception as e:
        print(f"[ERROR] Failed to refresh answers cache from Supabase: {e}")
        # Fallback to local if Supabase fails (optional, but good for safety)
        try:
            with open("data/answers.json", "r", encoding="utf-8") as f:
                local_answers = json.load(f)
                ANSWERS.clear()
                ANSWERS.update(local_answers)
                print("[INFO] Fallback: Loaded answers from local JSON.")
        except Exception as local_e:
            print(f"[ERROR] Fallback failed: {local_e}")

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
