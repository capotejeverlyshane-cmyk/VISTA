
@router.get("/stats", dependencies=[Depends(verify_admin_token)])
def get_stats():
    try:
        q_res = supabase.table("chat_logs").select("*", count="exact").execute()
        u_res = supabase.table("unresolved_queries").select("*", count="exact").execute()
        f_res = supabase.table("feedback").select("*", count="exact").execute()
        
        return {
            "total_queries": q_res.count if hasattr(q_res, 'count') else len(q_res.data or []),
            "unresolved_count": u_res.count if hasattr(u_res, 'count') else len(u_res.data or []),
            "feedback_count": f_res.count if hasattr(f_res, 'count') else len(f_res.data or []),
            "knowledge_base_size": len(ANSWERS)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/analytics", dependencies=[Depends(verify_admin_token)])
def get_analytics():
    try:
        res = supabase.table("chat_logs").select("predicted_intent").execute()
        intents = [item.get("predicted_intent") for item in (res.data or []) if item.get("predicted_intent")]
        
        from collections import Counter
        counts = Counter(intents)
        
        labels = list(counts.keys())
        data = list(counts.values())
        
        return {
            "type": "Intent Distribution",
            "description": "Most common queries by intent.",
            "labels": labels,
            "data": data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/unresolved", dependencies=[Depends(verify_admin_token)])
def get_unresolved():
    try:
        res = supabase.table("unresolved_queries").select("*").execute()
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

class LinkUnresolvedRequest(BaseModel):
    id: int
    intent: str
    question: str
    language: str = "en"

@router.post("/unresolved/link", dependencies=[Depends(verify_admin_token)])
def link_unresolved(req: LinkUnresolvedRequest):
    try:
        res = supabase.table("intents").select("id").eq("intent_name", req.intent).execute()
        if res.data:
            intent_id = res.data[0]["id"]
            supabase.table("training_phrases").insert({
                "intent_id": intent_id,
                "language": req.language,
                "phrase": req.question
            }).execute()
            
            # Dismiss it
            supabase.table("unresolved_queries").delete().eq("id", req.id).execute()
            
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Intent not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/feedback", dependencies=[Depends(verify_admin_token)])
def get_feedback():
    try:
        res = supabase.table("feedback").select("*").execute()
        return res.data or []
    except Exception as e:
        return []
