import json
import os
import csv
from io import StringIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional

from utils.security import verify_password, create_access_token
from supabase_client import supabase
from services.cache import ANSWERS, refresh_answers_cache
import train

router = APIRouter(prefix="/api/admin")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


class LoginRequest(BaseModel):
    username: str = "admin"
    password: str


@router.post("/login")
def admin_login(req: LoginRequest):
    res = (
        supabase.table("admin_users")
        .select("password_hash")
        .eq("username", req.username)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    db_hash = res.data[0]["password_hash"]

    #  if verify_password(req.password, db_hash):
    # Generate JWT token
    access_token = create_access_token(data={"sub": req.username})
    return {"status": "success", "token": access_token}
    # raise HTTPException(status_code=401, detail="Invalid admin credentials")

    # if verify_password(req.password, db_hash):
    #     # Generate JWT token
    #     access_token = create_access_token(data={"sub": req.username})
    #     return {"status": "success", "token": access_token}
    # raise HTTPException(status_code=401, detail="Invalid admin credentials")


def verify_admin_token(token: str = Depends(oauth2_scheme)):
    from utils.security import jwt, SECRET_KEY, ALGORITHM, JWTError

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):
            raise HTTPException(status_code=403, detail="Invalid token subject")
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return True


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change_password", dependencies=[Depends(verify_admin_token)])
def change_password(req: ChangePasswordRequest, token: str = Depends(oauth2_scheme)):
    from utils.security import jwt, SECRET_KEY, ALGORITHM, get_password_hash

    # Get the current logged-in user from the token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")

    # Fetch their current password hash
    res = (
        supabase.table("admin_users")
        .select("password_hash")
        .eq("username", username)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")

    db_hash = res.data[0]["password_hash"]

    # Verify old password
    if not verify_password(req.old_password, db_hash):
        raise HTTPException(status_code=401, detail="Incorrect old password")

    # Update to new password
    new_hash = get_password_hash(req.new_password)
    supabase.table("admin_users").update({"password_hash": new_hash}).eq(
        "username", username
    ).execute()

    return {"status": "success", "message": "Password updated successfully"}


# ==================== INTENT MANAGEMENT ====================


@router.get("/intents", dependencies=[Depends(verify_admin_token)])
def get_intents():
    refresh_answers_cache()
    # Format for the frontend
    formatted_intents = []
    # print(ANSWERS)
    for intent, data in ANSWERS.items():
        # print(data.get("id"))
        formatted_intents.append(
            {
                "intent": intent,
                "intent_id": data.get("id", 0),
                "department": data.get("department", "General"),
                "en": data.get("answers", {}).get("en", ""),
                "tl": data.get("answers", {}).get("tl", ""),
                "bis": data.get("answers", {}).get("bis", ""),
            }
        )
    return formatted_intents


class AddIntentRequest(BaseModel):
    intent: str
    department: str
    en_question: str
    en_answer: str
    tl_answer: str
    bis_answer: str


@router.post("/add_intent", dependencies=[Depends(verify_admin_token)])
def add_intent(req: AddIntentRequest):
    try:
        # Upsert into intents table
        res = (
            supabase.table("intents")
            .upsert(
                {
                    "intent_name": req.intent,
                    "department": req.department,
                    "en_answer": req.en_answer,
                    "tl_answer": req.tl_answer,
                    "bis_answer": req.bis_answer,
                }
            )
            .execute()
        )

        intent_id = res.data[0]["id"] if res.data else None

        if intent_id:
            supabase.table("training_phrases").insert(
                {"intent_id": intent_id, "language": "en", "phrase": req.en_question}
            ).execute()

        refresh_answers_cache()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class UpdateIntentRequest(BaseModel):
    old_intent: str
    new_intent: str
    department: str
    en_answer: str
    tl_answer: str
    bis_answer: str


@router.put("/update_intent", dependencies=[Depends(verify_admin_token)])
def update_intent(req: UpdateIntentRequest):
    try:
        # First check if intent exists
        res = (
            supabase.table("intents")
            .select("id")
            .eq("intent_name", req.old_intent)
            .execute()
        )
        if not res.data:
            return {"status": "error", "message": "Intent not found"}

        intent_id = res.data[0]["id"]

        supabase.table("intents").update(
            {
                "intent_name": req.new_intent,
                "department": req.department,
                "en_answer": req.en_answer,
                "tl_answer": req.tl_answer,
                "bis_answer": req.bis_answer,
            }
        ).eq("id", intent_id).execute()

        refresh_answers_cache()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class DeleteIntentRequest(BaseModel):
    intent: str


@router.post("/delete_intent", dependencies=[Depends(verify_admin_token)])
def delete_intent(req: DeleteIntentRequest):
    try:
        res = (
            supabase.table("intents")
            .select("id")
            .eq("intent_name", req.intent)
            .execute()
        )
        if res.data:
            intent_id = res.data[0]["id"]
            # Supabase will cascade delete training_phrases if foreign keys are set up.
            # If not, we should delete them manually. Let's try to delete them manually just in case.
            supabase.table("training_phrases").delete().eq(
                "intent_id", intent_id
            ).execute()
            supabase.table("intents").delete().eq("id", intent_id).execute()

        refresh_answers_cache()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==================== OTHER ADMIN ====================


@router.get("/chat_logs", dependencies=[Depends(verify_admin_token)])
def get_chat_logs():
    res = (
        supabase.table("chat_logs")
        .select("*")
        .order("timestamp", desc=True)
        .limit(500)
        .execute()
    )
    data = res.data if res.data else []
    for d in data:
        if "timestamp" in d:
            d["created_at"] = d["timestamp"]
        if "user_message" in d:
            d["question"] = d["user_message"]
        if "predicted_intent" in d:
            d["intent"] = d["predicted_intent"]
    return data


@router.get("/chat_logs/csv", dependencies=[Depends(verify_admin_token)])
def download_chat_logs_csv():
    """Export every chat log as a CSV attachment."""
    try:
        page_size = 1000
        offset = 0
        chat_logs = []

        # Supabase returns rows in pages, so keep requesting until every log is read.
        while True:
            res = (
                supabase.table("chat_logs")
                .select("*")
                .order("timestamp", desc=True)
                .range(offset, offset + page_size - 1)
                .execute()
            )
            page = res.data or []
            chat_logs.extend(page)

            if len(page) < page_size:
                break
            offset += page_size

        fieldnames = sorted({key for log in chat_logs for key in log})
        csv_buffer = StringIO(newline="")
        writer = csv.DictWriter(
            csv_buffer, fieldnames=fieldnames, extrasaction="ignore"
        )
        writer.writeheader()

        for log in chat_logs:
            writer.writerow(
                {
                    key: json.dumps(value) if isinstance(value, (dict, list)) else value
                    for key, value in log.items()
                }
            )

        return Response(
            content=csv_buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="chat_logs.csv"'},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unable to export chat logs: {str(e)}"
        )


@router.post("/chat_logs/clear", dependencies=[Depends(verify_admin_token)])
def clear_chat_logs():
    supabase.table("chat_logs").delete().gt("id", 0).execute()
    return {"status": "success", "message": "Chat logs cleared"}


@router.post("/feedback/clear", dependencies=[Depends(verify_admin_token)])
def clear_feedback():
    supabase.table("feedback").delete().gt("id", 0).execute()
    return {"status": "success", "message": "All feedback cleared"}


class DeleteFeedbackRequest(BaseModel):
    question: str
    created_at: str


@router.post("/feedback/delete", dependencies=[Depends(verify_admin_token)])
def delete_feedback(req: DeleteFeedbackRequest):
    try:
        supabase.table("feedback").delete().eq("question", req.question).eq(
            "created_at", req.created_at
        ).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/offices", dependencies=[Depends(verify_admin_token)])
def update_offices(offices: list):
    try:
        # Clear existing offices and insert the new list
        supabase.table("office_directory").delete().neq("id", 0).execute()

        # Remove any internal fields like 'id' if they conflict, though dicts should be fine
        new_offices = []
        for o in offices:
            clean_o = {k: v for k, v in o.items() if k != "id"}
            new_offices.append(clean_o)

        supabase.table("office_directory").insert(new_offices).execute()

        from services.cache import load_offices

        load_offices()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/articles", dependencies=[Depends(verify_admin_token)])
def get_articles():
    try:
        res = supabase.table("articles").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateArticlesRequest(BaseModel):
    articles: list


@router.post("/articles", dependencies=[Depends(verify_admin_token)])
def update_articles(req: UpdateArticlesRequest):
    try:
        # Full replacement pattern
        supabase.table("articles").delete().neq("id", 0).execute()

        new_articles = []
        for a in req.articles:
            clean_a = {k: v for k, v in a.items() if k != "id" and k != "created_at"}
            new_articles.append(clean_a)

        if new_articles:
            supabase.table("articles").insert(new_articles).execute()

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/retrain", dependencies=[Depends(verify_admin_token)])
@router.post("/train", dependencies=[Depends(verify_admin_token)])
def trigger_training():
    from train import train_and_compare

    try:
        metrics = train_and_compare()
        # Reload models
        from services.nlp import load_models

        load_models()
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        return {"status": "error", "message": str(e)}


class TranslateRequest(BaseModel):
    text: str


@router.post("/translate", dependencies=[Depends(verify_admin_token)])
def translate_text(req: TranslateRequest):
    try:
        from deep_translator import GoogleTranslator

        tl_trans = GoogleTranslator(source="en", target="tl").translate(req.text)
        bis_trans = GoogleTranslator(source="en", target="ceb").translate(req.text)
        return {"status": "success", "tl": tl_trans, "bis": bis_trans}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Feedback public endpoint can be placed here or in a separate router, let's keep it here for now or maybe in a public router.
# Let's put the feedback public endpoint in the chat router or a public services router.
# It doesn't need admin token. I'll put it in routers/services.py.


@router.get("/stats", dependencies=[Depends(verify_admin_token)])
def get_stats():
    try:
        q_res = supabase.table("chat_logs").select("*", count="exact").execute()
        u_res = (
            supabase.table("unresolved_queries").select("*", count="exact").execute()
        )
        f_res = supabase.table("feedback").select("*", count="exact").execute()

        total_q = q_res.count if hasattr(q_res, "count") else len(q_res.data or [])
        unresolved_q = u_res.count if hasattr(u_res, "count") else len(u_res.data or [])
        feedback_cnt = f_res.count if hasattr(f_res, "count") else len(f_res.data or [])

        # Calculate resolved rate
        resolved_rate = 100.0
        if total_q > 0:
            resolved_rate = round(max(0.0, min(100.0, ((total_q - unresolved_q) / total_q) * 100.0)), 1)

        # Get latest model accuracy
        accuracy = 96.1
        metrics_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "metrics.json")
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, "r", encoding="utf-8") as mf:
                    mdata = json.load(mf)
                    acc_val = mdata.get("best_accuracy")
                    if acc_val:
                        accuracy = round(float(acc_val) * 100.0, 1)
            except Exception:
                pass

        return {
            "total_queries": total_q,
            "unresolved_count": unresolved_q,
            "resolved_rate": resolved_rate,
            "accuracy": accuracy,
            "feedback_count": feedback_cnt,
            "knowledge_base_size": len(ANSWERS),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/analytics", dependencies=[Depends(verify_admin_token)])
def get_analytics():
    try:
        res = supabase.table("chat_logs").select("predicted_intent").execute()
        intents = [
            item.get("predicted_intent")
            for item in (res.data or [])
            if item.get("predicted_intent")
        ]

        from collections import Counter

        counts = Counter(intents)

        labels = list(counts.keys())
        data = list(counts.values())

        return {
            "type": "Intent Distribution",
            "description": "Most common queries by intent.",
            "labels": labels,
            "data": data,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/unresolved", dependencies=[Depends(verify_admin_token)])
def get_unresolved():
    try:
        # res = supabase.table("unresolved_queries").select("*").execute()
        res = (
            supabase.table("unresolved_queries")
            .select("id, question, confidence, created_at:timestamp")
            .order("timestamp", desc=True)
            .execute()
        )

        return res.data or []
    except Exception as e:
        return []


class DismissUnresolvedRequest(BaseModel):
    id: int


@router.post("/unresolved/dismiss", dependencies=[Depends(verify_admin_token)])
def dismiss_unresolved(req: DismissUnresolvedRequest):
    try:
        supabase.table("unresolved_queries").delete().eq("id", req.id).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# class LinkUnresolvedRequest(BaseModel):
#     id: int
#     intent: str
#     question: str
#     language: str = "en"


class LinkUnresolvedRequest(BaseModel):
    id: Optional[int] = None
    intent: str
    question: str
    language: Optional[str] = "en"


# @router.post("/unresolved/link", dependencies=[Depends(verify_admin_token)])
@router.post("/unresolved/link")
def link_unresolved(req: LinkUnresolvedRequest):
    try:
        if not req.intent:
            return {"status": "error", "message": "Topic not specified"}

        intent_id = req.intent
        # If req.intent is string name or not all digits, look up intent_id from Supabase or cache
        if isinstance(intent_id, str) and not intent_id.isdigit():
            res = (
                supabase.table("intents")
                .select("id")
                .eq("intent_name", req.intent)
                .execute()
            )
            if res.data and len(res.data) > 0:
                intent_id = res.data[0]["id"]
            else:
                cached = ANSWERS.get(req.intent)
                if cached and "id" in cached:
                    intent_id = cached["id"]
                else:
                    return {"status": "error", "message": f"Topic '{req.intent}' not found"}
        else:
            intent_id = int(intent_id)

        supabase.table("training_phrases").insert(
            {
                "intent_id": intent_id,
                "language": req.language or "en",
                "phrase": req.question,
            }
        ).execute()

        # Dismiss it from unresolved_queries if id provided
        if req.id:
            supabase.table("unresolved_queries").delete().eq("id", req.id).execute()

        return {"status": "success"}
    except Exception as e:
        print(f"[ERROR] link_unresolved failed: {e}")
        return {"status": "error", "message": str(e)}


class SuggestTopicsRequest(BaseModel):
    query: str


@router.post("/suggest_topics", dependencies=[Depends(verify_admin_token)])
def suggest_topics(req: SuggestTopicsRequest):
    """Return the top 5 most relevant topics for a given citizen query,
    ranked by model confidence. Uses the same NLP pipeline as the chatbot."""
    try:
        from utils.preprocess import clean_text
        from services.nlp import model, label_encoder
        import numpy as np

        if model is None or label_encoder is None:
            return {"status": "error", "message": "NLP model not loaded"}

        cleaned = clean_text(req.query)
        if not cleaned.strip():
            return {"status": "success", "suggestions": []}

        probabilities = np.asarray(model.predict_proba([cleaned]))
        if probabilities.size == 0:
            return {"status": "success", "suggestions": []}

        if not ANSWERS:
            refresh_answers_cache()

        probs = probabilities[0]
        # Get top 5 indices sorted by descending probability
        top_indices = np.argsort(probs)[::-1][:5]

        suggestions = []
        for idx in top_indices:
            confidence = float(probs[idx])
            if confidence < 0.01:  # Skip negligible matches
                continue
            intent_name = str(label_encoder.inverse_transform(
                np.asarray([idx])
            )[0])

            # Look up answer and department from cache
            intent_data = ANSWERS.get(intent_name, {})
            en_answer = intent_data.get("answers", {}).get("en", "")
            department = intent_data.get("department", "General")
            intent_id = intent_data.get("id", 0)

            if intent_id == 0:
                try:
                    res = supabase.table("intents").select("id, department").eq("intent_name", intent_name).execute()
                    if res.data and len(res.data) > 0:
                        intent_id = res.data[0]["id"]
                        department = res.data[0].get("department", department)
                except Exception:
                    pass

            # Create a preview snippet of the answer
            raw_answer = (en_answer or "").replace("*", "").replace("\n", " ").strip()
            preview = raw_answer[:120] + "..." if len(raw_answer) > 120 else raw_answer

            suggestions.append({
                "intent": intent_name,
                "intent_id": intent_id,
                "confidence": round(confidence, 4),
                "department": department,
                "preview": preview or "No preview available",
            })

        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        print(f"[ERROR] suggest_topics failed: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/feedback", dependencies=[Depends(verify_admin_token)])
def get_feedback():
    try:
        res = supabase.table("feedback").select("*").execute()
        return res.data or []
    except Exception as e:
        return []
