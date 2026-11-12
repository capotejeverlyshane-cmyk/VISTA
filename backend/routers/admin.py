import json
import os
import csv
from datetime import datetime
from io import StringIO
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional

from utils.security import verify_password, create_access_token
from supabase_client import supabase
from services.cache import (
    ANSWERS,
    add_training_phrase,
    init_cache,
    refresh_answers_cache,
    refresh_training_phrases,
)
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

    if not verify_password(req.password, db_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    # Generate JWT token
    access_token = create_access_token(data={"sub": req.username})
    return {"status": "success", "token": access_token}


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
        refresh_training_phrases()
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
        refresh_training_phrases()
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
        refresh_training_phrases()
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
def update_offices(offices: list = Body(...)):
    try:
        if not all(isinstance(office, dict) for office in offices):
            raise ValueError("Each office must be an object.")

        new_offices = []
        office_ids = set()
        for o in offices:
            clean_o = {
                k: v
                for k, v in o.items()
                if k
                in (
                    "office_id",
                    "name",
                    "head_of_office",
                    "contact",
                    "location",
                    "operating_hours",
                )
            }
            office_id = clean_o.get("office_id")
            if not isinstance(office_id, str) or not office_id.strip():
                raise ValueError("Each office must have a non-empty office_id.")
            office_id = office_id.strip()
            clean_o["office_id"] = office_id
            if office_id in office_ids:
                raise ValueError(f"Duplicate office_id: {office_id}")
            office_ids.add(office_id)
            name = clean_o.get("name")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"Office {office_id} must have a non-empty name.")
            clean_o["name"] = name.strip()

            for field in ("head_of_office", "contact", "location", "operating_hours"):
                value = clean_o.get(field)
                if value is not None and not isinstance(value, dict):
                    raise ValueError(f"Office {office_id}: {field} must be an object.")

            new_offices.append(clean_o)

        table = supabase.table("office_directory")
        existing_response = table.select("office_id").execute()
        existing_ids = {
            office["office_id"]
            for office in (existing_response.data or [])
            if office.get("office_id")
        }

        if new_offices:
            table.upsert(new_offices, on_conflict="office_id").execute()

        removed_ids = existing_ids - office_ids
        if removed_ids:
            table.delete().in_("office_id", list(removed_ids)).execute()

        from services.cache import load_offices

        load_offices()
        return {"status": "success", "count": len(new_offices)}
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


@router.post("/refresh_cache", dependencies=[Depends(verify_admin_token)])
def refresh_cache_endpoint():
    try:
        init_cache()
        return {"status": "success", "message": "All caches reloaded successfully"}
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

        return {
            "total_queries": q_res.count
            if hasattr(q_res, "count")
            else len(q_res.data or []),
            "unresolved_count": u_res.count
            if hasattr(u_res, "count")
            else len(u_res.data or []),
            "feedback_count": f_res.count
            if hasattr(f_res, "count")
            else len(f_res.data or []),
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


class SuggestTopicsRequest(BaseModel):
    query: str


@router.post("/suggest_topics", dependencies=[Depends(verify_admin_token)])
def suggest_topics(req: SuggestTopicsRequest):
    try:
        import numpy as np
        from services.nlp import label_encoder, model
        from utils.preprocess import clean_text

        if model is None or label_encoder is None:
            return {"status": "error", "message": "NLP model is not loaded"}

        cleaned = clean_text(req.query)
        if not cleaned.strip():
            return {"status": "success", "suggestions": []}

        probabilities = np.asarray(model.predict_proba([cleaned]))
        if probabilities.size == 0:
            return {"status": "success", "suggestions": []}

        if not ANSWERS:
            refresh_answers_cache()

        suggestions = []
        for index in np.argsort(probabilities[0])[::-1][:5]:
            confidence = float(probabilities[0][index])
            if confidence < 0.01:
                continue

            intent_name = str(label_encoder.inverse_transform(np.asarray([index]))[0])
            intent_data = ANSWERS.get(intent_name, {})
            intent_id = intent_data.get("id", 0)
            department = intent_data.get("department", "General")

            if not intent_id:
                result = (
                    supabase.table("intents")
                    .select("id, department")
                    .eq("intent_name", intent_name)
                    .execute()
                )
                if result.data:
                    intent_id = result.data[0]["id"]
                    department = result.data[0].get("department") or department

            answer = intent_data.get("answers", {}).get("en", "")
            preview = " ".join((answer or "").replace("*", "").split())
            if len(preview) > 120:
                preview = preview[:120].rstrip() + "..."

            suggestions.append(
                {
                    "intent": intent_name,
                    "intent_id": intent_id,
                    "confidence": round(confidence, 4),
                    "department": department,
                    "preview": preview or "No preview available",
                }
            )

        return {"status": "success", "suggestions": suggestions}
    except Exception as e:
        print(f"[ERROR] suggest_topics failed: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/unresolved/link", dependencies=[Depends(verify_admin_token)])
def link_unresolved(req: LinkUnresolvedRequest):
    try:
        if not req.intent or not req.question.strip():
            return {"status": "error", "message": "Topic and query are required"}

        lookup = supabase.table("intents").select("id, intent_name")
        if req.intent.isdigit():
            lookup = lookup.eq("id", int(req.intent))
        else:
            lookup = lookup.eq("intent_name", req.intent)
        result = lookup.execute()
        if not result.data:
            return {"status": "error", "message": f"Topic '{req.intent}' not found"}

        intent_id = result.data[0]["id"]
        intent_name = result.data[0]["intent_name"]

        supabase.table("training_phrases").insert(
            {
                "intent_id": intent_id,
                "language": req.language or "en",
                "phrase": req.question.strip(),
            }
        ).execute()
        add_training_phrase(req.question, intent_name)

        if req.id is not None:
            supabase.table("unresolved_queries").delete().eq("id", req.id).execute()

        return {"status": "success"}
    except Exception as e:
        print(f"[ERROR] link_unresolved failed: {e}")
        return {"status": "error", "message": str(e)}



@router.get("/feedback", dependencies=[Depends(verify_admin_token)])
def get_feedback():
    try:
        res = supabase.table("feedback").select("*").execute()
        return res.data or []
    except Exception as e:
        return []


@router.post("/retrain", dependencies=[Depends(verify_admin_token)])
def retrain():
    metrics = train.train_and_compare()
    from services.nlp import load_models

    load_models()
    return {"status": "success", "metrics": metrics}


@router.get("/health")
def get_health():
    metrics_path = os.path.join(train.MODEL_DIR, "metrics.json")
    model_path = os.path.join(train.MODEL_DIR, "best_model.pkl")
    intent_count = len(ANSWERS) if ANSWERS else None
    model_loaded = os.path.isfile(model_path)

    if not os.path.isfile(metrics_path):
        return {
            "status": "ok",
            "model_loaded": model_loaded,
            "accuracy": None,
            "intent_count": intent_count,
            "last_trained": None,
        }

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    best_accuracy = metrics.get("best_accuracy")
    accuracy = (
        round(float(best_accuracy) * 100, 1)
        if isinstance(best_accuracy, (int, float))
        else None
    )
    last_trained = (
        datetime.fromtimestamp(os.path.getmtime(metrics_path)).astimezone().isoformat(
            timespec="seconds"
        )
        if os.path.isfile(metrics_path)
        else None
    )

    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "accuracy": accuracy,
        "intent_count": intent_count,
        "last_trained": last_trained,
    }
