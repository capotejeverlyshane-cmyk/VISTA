import re

with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
content = content.replace(
    "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware",
    "from fastapi import FastAPI, Depends, HTTPException, Header\nfrom fastapi.middleware.cors import CORSMiddleware"
)
content = content.replace(
    "from train import train_and_compare",
    "from train import train_and_compare\nfrom database import get_db"
)

# 2. Dependency
dep_code = """
app = FastAPI(title="VISTA API")

def verify_admin_token(x_admin_token: str = Header(None)):
    if x_admin_token != "vista_admin_2026":
        raise HTTPException(status_code=401, detail="Unauthorized")
"""
content = content.replace('app = FastAPI(title="VISTA API")', dep_code)

# 3. Add dependencies=[Depends(verify_admin_token)] to all admin routes
content = re.sub(r'@app\.(get|post|put|delete)\("/api/admin/([^\"]*)"\)', r'@app.\1("/api/admin/\2", dependencies=[Depends(verify_admin_token)])', content)

# 4. Chat function
old_unresolved = """    if confidence < 0.35:
        append_json(UNRESOLVED_PATH, {
            "question": user_text,
            "predicted_intent": intent,
            "confidence": confidence,
            "created_at": datetime.now().isoformat()
        })"""
new_unresolved = """    if confidence < 0.35:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO unresolved_queries (question, predicted_intent, confidence) VALUES (?, ?, ?)",
                (user_text, intent, confidence)
            )
            conn.commit()"""
content = content.replace(old_unresolved, new_unresolved)

old_chat_log = """    append_json(CHAT_LOGS_PATH, {
        "question": user_text,
        "intent": intent,
        "language": language,
        "confidence": confidence,
        "created_at": datetime.now().isoformat()
    })"""
new_chat_log = """    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_logs (question, intent, language, confidence) VALUES (?, ?, ?, ?)",
            (user_text, intent, language, confidence)
        )
        conn.commit()"""
content = content.replace(old_chat_log, new_chat_log)

# 5. Feedback function
old_feedback = """@app.post("/feedback")
def feedback(req: FeedbackRequest):
    append_json(FEEDBACK_PATH, {
        "question": req.question,
        "answer": req.answer,
        "intent": req.intent,
        "helpful": req.helpful,
        "language": req.language,
        "created_at": datetime.now().isoformat()
    })
    return {"status": "saved"}"""
new_feedback = """@app.post("/feedback")
def feedback(req: FeedbackRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (question, answer, intent, helpful, language) VALUES (?, ?, ?, ?, ?)",
            (req.question, req.answer, req.intent, req.helpful, req.language)
        )
        conn.commit()
    return {"status": "saved"}"""
content = content.replace(old_feedback, new_feedback)

# 6. Admin stats
old_stats = """@app.get("/api/admin/stats", dependencies=[Depends(verify_admin_token)])
def get_stats():
    try:
        with open(UNRESOLVED_PATH, "r", encoding="utf-8") as f:
            unresolved = json.load(f)
    except:
        unresolved = []
        
    try:
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            feedback = json.load(f)
    except:
        feedback = []
        
    try:
        with open(CHAT_LOGS_PATH, "r", encoding="utf-8") as f:
            chat_logs = json.load(f)
        total_queries = len(chat_logs)
    except:
        total_queries = len(unresolved) + len(feedback)
    
    return {
        "total_queries": total_queries,
        "unresolved_count": len(unresolved),
        "feedback_count": len(feedback)
    }"""
new_stats = """@app.get("/api/admin/stats", dependencies=[Depends(verify_admin_token)])
def get_stats():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chat_logs")
        total_queries = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM unresolved_queries")
        unresolved_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM feedback")
        feedback_count = cursor.fetchone()[0]
        
    return {
        "total_queries": total_queries,
        "unresolved_count": unresolved_count,
        "feedback_count": feedback_count
    }"""
content = content.replace(old_stats, new_stats)

# 7. Admin analytics
old_analytics = """@app.get("/api/admin/analytics", dependencies=[Depends(verify_admin_token)])
def get_analytics():
    try:
        with open(CHAT_LOGS_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []

    intent_counts = {}
    for log in logs:
        intent = log.get("intent", "unknown")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    # Sort and get top 10
    sorted_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    labels = [x[0] for x in sorted_intents]
    data = [x[1] for x in sorted_intents]

    return {
        "labels": labels,
        "data": data,
        "type": "Descriptive Analytics",
        "description": "This chart uses Descriptive Analytics to visualize historical citizen inquiry trends based on actual system chat logs."
    }"""
new_analytics = """@app.get("/api/admin/analytics", dependencies=[Depends(verify_admin_token)])
def get_analytics():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT intent, COUNT(*) as count FROM chat_logs GROUP BY intent ORDER BY count DESC LIMIT 10")
        rows = cursor.fetchall()
        
    labels = [row['intent'] if row['intent'] else 'unknown' for row in rows]
    data = [row['count'] for row in rows]

    return {
        "labels": labels,
        "data": data,
        "type": "Descriptive Analytics",
        "description": "This chart uses Descriptive Analytics to visualize historical citizen inquiry trends based on actual system chat logs."
    }"""
content = content.replace(old_analytics, new_analytics)

# 8. Admin unresolved
old_unresolved_get = """@app.get("/api/admin/unresolved", dependencies=[Depends(verify_admin_token)])
def get_unresolved():
    try:
        with open(UNRESOLVED_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []"""
new_unresolved_get = """@app.get("/api/admin/unresolved", dependencies=[Depends(verify_admin_token)])
def get_unresolved():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM unresolved_queries ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]"""
content = content.replace(old_unresolved_get, new_unresolved_get)

# 9. Admin feedback
old_feedback_get = """@app.get("/api/admin/feedback", dependencies=[Depends(verify_admin_token)])
def get_feedback():
    try:
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []"""
new_feedback_get = """@app.get("/api/admin/feedback", dependencies=[Depends(verify_admin_token)])
def get_feedback():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]"""
content = content.replace(old_feedback_get, new_feedback_get)

# 10. Admin dismiss
old_dismiss = """@app.post("/api/admin/unresolved/dismiss", dependencies=[Depends(verify_admin_token)])
def dismiss_unresolved(req: DismissQueryRequest):
    try:
        with open(UNRESOLVED_PATH, "r", encoding="utf-8") as f:
            unresolved = json.load(f)
        
        # Filter out the dismissed question
        unresolved = [u for u in unresolved if u.get("question") != req.question]
        
        with open(UNRESOLVED_PATH, "w", encoding="utf-8") as f:
            json.dump(unresolved, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "message": "Query dismissed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}"""
new_dismiss = """@app.post("/api/admin/unresolved/dismiss", dependencies=[Depends(verify_admin_token)])
def dismiss_unresolved(req: DismissQueryRequest):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unresolved_queries WHERE question = ?", (req.question,))
            conn.commit()
        return {"status": "success", "message": "Query dismissed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}"""
content = content.replace(old_dismiss, new_dismiss)

# 11. Admin link remove unresolved json part
old_link_unresolved = """        # Remove from unresolved
        with open(UNRESOLVED_PATH, "r", encoding="utf-8") as f:
            unresolved = json.load(f)
        unresolved = [u for u in unresolved if u.get("question") != req.question]
        with open(UNRESOLVED_PATH, "w", encoding="utf-8") as f:
            json.dump(unresolved, f, indent=2, ensure_ascii=False)"""
new_link_unresolved = """        # Remove from unresolved
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unresolved_queries WHERE question = ?", (req.question,))
            conn.commit()"""
content = content.replace(old_link_unresolved, new_link_unresolved)

# 12. Add Intent remove unresolved json part
old_add_intent_unres = """    # Also delete the resolved question from unresolved_questions.json if it matches the en_question
    try:
        with open(UNRESOLVED_PATH, "r", encoding="utf-8") as f:
            unresolved = json.load(f)
        unresolved = [u for u in unresolved if u.get("question") != req.en_question]
        with open(UNRESOLVED_PATH, "w", encoding="utf-8") as f:
            json.dump(unresolved, f, indent=2, ensure_ascii=False)
    except:
        pass"""
new_add_intent_unres = """    # Also delete the resolved question from unresolved_queries
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unresolved_queries WHERE question = ?", (req.en_question,))
            conn.commit()
    except:
        pass"""
content = content.replace(old_add_intent_unres, new_add_intent_unres)

# 13. Chat Logs Get
old_chatlogs_get = """@app.get("/api/admin/chat_logs", dependencies=[Depends(verify_admin_token)])
def get_chat_logs():
    try:
        with open(CHAT_LOGS_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
        logs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return logs
    except:
        return []"""
new_chatlogs_get = """@app.get("/api/admin/chat_logs", dependencies=[Depends(verify_admin_token)])
def get_chat_logs():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_logs ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]"""
content = content.replace(old_chatlogs_get, new_chatlogs_get)

# 14. Chat Logs Clear
old_chatlogs_clear = """@app.post("/api/admin/chat_logs/clear", dependencies=[Depends(verify_admin_token)])
def clear_chat_logs():
    with open(CHAT_LOGS_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)
    return {"status": "success", "message": "Chat logs cleared"}"""
new_chatlogs_clear = """@app.post("/api/admin/chat_logs/clear", dependencies=[Depends(verify_admin_token)])
def clear_chat_logs():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_logs")
        conn.commit()
    return {"status": "success", "message": "Chat logs cleared"}"""
content = content.replace(old_chatlogs_clear, new_chatlogs_clear)

# 15. Feedback Clear
old_fb_clear = """@app.post("/api/admin/feedback/clear", dependencies=[Depends(verify_admin_token)])
def clear_feedback():
    with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)
    return {"status": "success", "message": "All feedback cleared"}"""
new_fb_clear = """@app.post("/api/admin/feedback/clear", dependencies=[Depends(verify_admin_token)])
def clear_feedback():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback")
        conn.commit()
    return {"status": "success", "message": "All feedback cleared"}"""
content = content.replace(old_fb_clear, new_fb_clear)

# 16. Feedback Delete
old_fb_del = """@app.post("/api/admin/feedback/delete", dependencies=[Depends(verify_admin_token)])
def delete_feedback(req: DeleteFeedbackRequest):
    try:
        with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
            feedback_list = json.load(f)
        feedback_list = [
            f for f in feedback_list
            if not (f.get("question") == req.question and f.get("created_at") == req.created_at)
        ]
        with open(FEEDBACK_PATH, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}"""
new_fb_del = """@app.post("/api/admin/feedback/delete", dependencies=[Depends(verify_admin_token)])
def delete_feedback(req: DeleteFeedbackRequest):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE question = ? AND created_at = ?", (req.question, req.created_at))
            conn.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}"""
content = content.replace(old_fb_del, new_fb_del)

with open('backend/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
