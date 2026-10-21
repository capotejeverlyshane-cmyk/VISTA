import os

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

supabase_insert_intent = """
    # Also push to Supabase
    try:
        res = supabase.table("intents").upsert({
            "intent_name": req.intent,
            "department": req.department,
            "en_answer": req.en_answer,
            "tl_answer": req.tl_answer,
            "bis_answer": req.bis_answer
        }).execute()
        if res.data:
            intent_id = res.data[0]['id']
            supabase.table("training_phrases").insert({
                "intent_id": intent_id, "language": "en", "phrase": req.en_question
            }).execute()
            supabase.table("training_phrases").insert({
                "intent_id": intent_id, "language": "tl", "phrase": req.tl_question
            }).execute()
            supabase.table("training_phrases").insert({
                "intent_id": intent_id, "language": "bis", "phrase": req.bis_question
            }).execute()
    except Exception as e:
        print("Supabase insert error:", e)
"""

old_add_intent = '    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)\n    df.to_csv("data/intents.csv", index=False)'
content = content.replace(old_add_intent, old_add_intent + supabase_insert_intent)

old_update_intent = '    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)\n    df.to_csv("data/intents.csv", index=False)'
content = content.replace(old_update_intent, old_update_intent + supabase_insert_intent)

supabase_delete = """
    try:
        supabase.table("intents").delete().eq("intent_name", intent_id).execute()
    except Exception as e:
        print("Supabase delete error:", e)
"""
old_delete_intent = '        df.to_csv("data/intents.csv", index=False, encoding="utf-8")\n    except Exception as e:\n        print("Error deleting intent:", e)'
content = content.replace(old_delete_intent, old_delete_intent + supabase_delete)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated app.py with intent syncing")
