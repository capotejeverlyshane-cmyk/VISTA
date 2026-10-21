import re
import os

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace imports
content = content.replace('from database import get_db', 'from supabase_client import supabase')

# Replace unresolved_queries insert
old_unresolved = '''        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO unresolved_queries (question, predicted_intent, confidence) VALUES (?, ?, ?)",
                (user_text, intent, confidence)
            )
            conn.commit()'''

new_unresolved = '''        try:
            supabase.table("unresolved_queries").insert({
                "question": user_text,
                "confidence": confidence
            }).execute()
        except Exception as e:
            print("Supabase insert error:", e)'''
content = content.replace(old_unresolved, new_unresolved)

# Replace chat_logs insert
old_chat = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (question, intent, language, confidence) VALUES (?, ?, ?, ?)",
            (user_text, intent, language, confidence)
        )
        conn.commit()'''

new_chat = '''    try:
        supabase.table("chat_logs").insert({
            "user_message": user_text,
            "predicted_intent": intent,
            "language": language,
            "confidence": confidence
        }).execute()
    except Exception as e:
        print("Supabase insert error:", e)'''
content = content.replace(old_chat, new_chat)

# Replace feedback insert
old_feed = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (question, answer, intent, helpful, language, comment) VALUES (?, ?, ?, ?, ?, ?)",
            (req.question, req.answer, req.intent, req.helpful, req.language, req.comment)
        )
        conn.commit()'''

new_feed = '''    try:
        supabase.table("feedback").insert({
            "question": req.question,
            "answer": req.answer,
            "intent": req.intent,
            "helpful": req.helpful,
            "comment": req.comment
        }).execute()
    except Exception as e:
        print("Supabase insert error:", e)'''
content = content.replace(old_feed, new_feed)

# Replace get_stats
old_stats = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_logs")
        total_queries = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM unresolved_queries")
        unresolved_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM feedback")
        feedback_count = cursor.fetchone()[0]'''

new_stats = '''    try:
        res_chat = supabase.table("chat_logs").select("id", count="exact").execute()
        total_queries = res_chat.count if res_chat.count else 0
        res_unres = supabase.table("unresolved_queries").select("id", count="exact").execute()
        unresolved_count = res_unres.count if res_unres.count else 0
        res_feed = supabase.table("feedback").select("id", count="exact").execute()
        feedback_count = res_feed.count if res_feed.count else 0
    except:
        total_queries = unresolved_count = feedback_count = 0'''
content = content.replace(old_stats, new_stats)

# Replace analytics
old_analytics = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT intent, COUNT(*) as count FROM chat_logs GROUP BY intent ORDER BY count DESC LIMIT 10")
        rows = cursor.fetchall()
        
    labels = [row['intent'] if row['intent'] else 'unknown' for row in rows]
    data = [row['count'] for row in rows]'''

new_analytics = '''    labels = []
    data = []
    try:
        # Note: Supabase JS has RPC, for Python we might need to fetch all or use RPC. 
        # For simplicity, we fetch all and aggregate if no RPC exists.
        res = supabase.table("chat_logs").select("predicted_intent").execute()
        if res.data:
            from collections import Counter
            counts = Counter([r.get("predicted_intent", "unknown") for r in res.data])
            top_10 = counts.most_common(10)
            labels = [k if k else 'unknown' for k, v in top_10]
            data = [v for k, v in top_10]
    except Exception as e:
        print("Analytics error:", e)'''
content = content.replace(old_analytics, new_analytics)

# Replace get_unresolved
old_get_unresolved = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM unresolved_queries ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]'''

new_get_unresolved = '''    res = supabase.table("unresolved_queries").select("*").order("timestamp", desc=True).execute()
    return res.data if res.data else []'''
content = content.replace(old_get_unresolved, new_get_unresolved)

# Replace get_feedback
old_get_feedback = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]'''

new_get_feedback = '''    res = supabase.table("feedback").select("*").order("created_at", desc=True).execute()
    return res.data if res.data else []'''
content = content.replace(old_get_feedback, new_get_feedback)

# Replace dismiss_unresolved
old_dismiss_unresolved = '''        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unresolved_queries WHERE question = ?", (req.question,))
            conn.commit()'''

new_dismiss_unresolved = '''        supabase.table("unresolved_queries").delete().eq("question", req.question).execute()'''
content = content.replace(old_dismiss_unresolved, new_dismiss_unresolved)

# Replace link_unresolved delete
old_link_unresolved_delete = '''        # Remove from unresolved
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unresolved_queries WHERE question = ?", (req.question,))
            conn.commit()'''
new_link_unresolved_delete = '''        # Remove from unresolved
        supabase.table("unresolved_queries").delete().eq("question", req.question).execute()'''
content = content.replace(old_link_unresolved_delete, new_link_unresolved_delete)

# Replace add_intent delete
old_add_intent_delete = '''    # Also delete the resolved question from unresolved_queries
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unresolved_queries WHERE question = ?", (req.en_question,))
            conn.commit()
    except:
        pass'''
new_add_intent_delete = '''    # Also delete the resolved question from unresolved_queries
    try:
        supabase.table("unresolved_queries").delete().eq("question", req.en_question).execute()
    except:
        pass'''
content = content.replace(old_add_intent_delete, new_add_intent_delete)

# Replace get_chat_logs
old_get_chat = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_logs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]'''

new_get_chat = '''    res = supabase.table("chat_logs").select("*").order("timestamp", desc=True).limit(500).execute()
    # rename timestamp to created_at for frontend compatibility
    data = res.data if res.data else []
    for d in data:
        if "timestamp" in d:
            d["created_at"] = d["timestamp"]
        if "user_message" in d:
            d["question"] = d["user_message"]
        if "predicted_intent" in d:
            d["intent"] = d["predicted_intent"]
    return data'''
content = content.replace(old_get_chat, new_get_chat)

# Replace clear_chat_logs
old_clear_chat = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_logs")
        conn.commit()'''
new_clear_chat = '''    # Note: Supabase delete requires a filter. To delete all, filter where id > 0
    supabase.table("chat_logs").delete().gt("id", 0).execute()'''
content = content.replace(old_clear_chat, new_clear_chat)

# Replace clear_feedback
old_clear_feed = '''    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback")
        conn.commit()'''
new_clear_feed = '''    supabase.table("feedback").delete().gt("id", 0).execute()'''
content = content.replace(old_clear_feed, new_clear_feed)

# Replace delete_feedback
old_del_feed = '''        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE question = ? AND created_at = ?", (req.question, req.created_at))
            conn.commit()'''
new_del_feed = '''        supabase.table("feedback").delete().eq("question", req.question).eq("created_at", req.created_at).execute()'''
content = content.replace(old_del_feed, new_del_feed)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated app.py")
