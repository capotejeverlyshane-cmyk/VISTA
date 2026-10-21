import json
from typing import Dict, Any
from supabase_client import supabase
import pandas as pd
import os

# Global caches
ANSWERS: Dict[str, Any] = {}
OFFICES: list = []

def refresh_answers_cache():
    """Loads all intent answers directly from data/intents.csv."""
    global ANSWERS
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    csv_path = os.path.join(data_dir, "intents.csv")
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            new_answers = {}
            for _, row in df.iterrows():
                name = str(row.get("intent_name", "")).strip()
                if name:
                    new_answers[name] = {
                        "id": row.get("id"),
                        "department": str(row.get("department", "General")),
                        "answers": {
                            "en": str(row.get("en_answer", "") or ""),
                            "tl": str(row.get("tl_answer", "") or ""),
                            "bis": str(row.get("bis_answer", "") or "")
                        }
                    }
            ANSWERS.clear()
            ANSWERS.update(new_answers)
            print(f"[INFO] Loaded {len(ANSWERS)} intent answers directly from data/intents.csv!")
            return
    except Exception as e:
        print(f"[ERROR] Failed to load data/intents.csv: {e}")

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
