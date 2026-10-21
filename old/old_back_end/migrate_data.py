import json
import sqlite3
import os
from database import DB_PATH, get_db

def migrate_data():
    if not os.path.exists(DB_PATH):
        print("SQLite database not found. Run init_db() first.")
        return

    # Migrate chat logs
    try:
        with open('data/chat_logs.json', 'r', encoding='utf-8') as f:
            chat_logs = json.load(f)
            if chat_logs:
                with get_db() as conn:
                    cursor = conn.cursor()
                    for log in chat_logs:
                        cursor.execute(
                            "INSERT INTO chat_logs (question, intent, language, confidence, created_at) VALUES (?, ?, ?, ?, ?)",
                            (log.get('question', ''), log.get('intent', ''), log.get('language', ''), log.get('confidence', 0.0), log.get('created_at'))
                        )
                    conn.commit()
                print(f"Migrated {len(chat_logs)} chat logs.")
    except Exception as e:
        print(f"Chat logs migration error: {e}")

    # Migrate feedback
    try:
        with open('data/feedback.json', 'r', encoding='utf-8') as f:
            feedback = json.load(f)
            if feedback:
                with get_db() as conn:
                    cursor = conn.cursor()
                    for fb in feedback:
                        cursor.execute(
                            "INSERT INTO feedback (question, answer, intent, helpful, language, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (fb.get('question', ''), fb.get('answer', ''), fb.get('intent', ''), fb.get('helpful', False), fb.get('language', ''), fb.get('created_at'))
                        )
                    conn.commit()
                print(f"Migrated {len(feedback)} feedback entries.")
    except Exception as e:
        print(f"Feedback migration error: {e}")

    # Migrate unresolved queries
    try:
        with open('data/unresolved_questions.json', 'r', encoding='utf-8') as f:
            unresolved = json.load(f)
            if unresolved:
                with get_db() as conn:
                    cursor = conn.cursor()
                    for unres in unresolved:
                        cursor.execute(
                            "INSERT INTO unresolved_queries (question, predicted_intent, confidence, created_at) VALUES (?, ?, ?, ?)",
                            (unres.get('question', ''), unres.get('predicted_intent', ''), unres.get('confidence', 0.0), unres.get('created_at'))
                        )
                    conn.commit()
                print(f"Migrated {len(unresolved)} unresolved queries.")
    except Exception as e:
        print(f"Unresolved queries migration error: {e}")

if __name__ == '__main__':
    migrate_data()
