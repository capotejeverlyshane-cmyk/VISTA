import re
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.cache import ANSWERS, OFFICES,load_offices

from supabase_client import supabase
import time

router = APIRouter(prefix="/api")


@router.get("/services")
def get_services():
    """Returns a lightweight list of all services grouped by department for the citizen portal."""
    services_map = {}
    for intent_name, data in ANSWERS.items():
        # Strip sub-intent suffixes to get base service name
        base = re.sub(r"_(fee|process|requirements|location|cost)$", "", intent_name)
        if base in services_map:
            continue
        dept = data.get("department", "General")
        # Convert intent_id to human-readable name
        display = base.replace("cmo_", "").replace("_", " ").title()
        services_map[base] = {
            "intent": base,
            "department": dept,
            "display_name": display,
        }

    # Group by department
    dept_groups = {}
    for svc in services_map.values():
        dept = svc["department"]
        if dept not in dept_groups:
            dept_groups[dept] = []
        dept_groups[dept].append(svc)

    return {"departments": dept_groups}


@router.get("/departments")
def get_departments():
    """Returns unique departments with service counts for the Office Directory."""
    dept_info = {}
    for intent_name, data in ANSWERS.items():
        dept = data.get("department", "General")
        if dept not in dept_info:
            dept_info[dept] = {"name": dept, "service_count": 0, "sample_services": []}
        dept_info[dept]["service_count"] += 1
        if len(dept_info[dept]["sample_services"]) < 3:
            display = intent_name.replace("cmo_", "").replace("_", " ").title()
            dept_info[dept]["sample_services"].append(display)
    return list(dept_info.values())


@router.get("/offices")
def get_offices():
    """Returns the logistical information for LGU offices from offices.json."""
    load_offices()
    
    return load_offices() #OFFICES


class FeedbackRequest(BaseModel):
    question: str
    answer: Optional[str] = ""
    intent: Optional[str] = ""
    predicted_intent: Optional[str] = None
    helpful: Optional[bool] = None
    feedback: Optional[str] = None
    comment: Optional[str] = None
    language: Optional[str] = "en"


@router.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    try:
        resolved_intent = req.intent or req.predicted_intent or "unknown"
        is_helpful = req.helpful if req.helpful is not None else (req.feedback in ["positive", "helpful", "true"])
        
        insert_payload = {
            "question": req.question,
            "answer": req.answer or "",
            "intent": resolved_intent,
            "helpful": is_helpful,
            "comment": req.comment or "",
        }
        res = supabase.table("feedback").insert(insert_payload).execute()
        return {"status": "success", "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")
