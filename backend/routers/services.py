import re
from fastapi import APIRouter
from pydantic import BaseModel
from services.cache import ANSWERS, OFFICES
from supabase_client import supabase
import time

router = APIRouter(prefix="/api")

@router.get("/services")
def get_services():
    """Returns a lightweight list of all services grouped by department for the citizen portal."""
    services_map = {}
    for intent_name, data in ANSWERS.items():
        # Strip sub-intent suffixes to get base service name
        base = re.sub(r'_(fee|process|requirements|location|cost)$', '', intent_name)
        if base in services_map:
            continue
        dept = data.get("department", "General")
        # Convert intent_id to human-readable name
        display = base.replace("cmo_", "").replace("_", " ").title()
        services_map[base] = {
            "intent": base,
            "department": dept,
            "display_name": display
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
    return OFFICES

class FeedbackRequest(BaseModel):
    question: str
    predicted_intent: str
    feedback: str
    language: str

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    try:
        supabase.table("feedback").insert({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "question": req.question,
            "predicted_intent": req.predicted_intent,
            "feedback_type": req.feedback,
            "language": req.language
        }).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
