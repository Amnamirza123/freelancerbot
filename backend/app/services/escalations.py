"""Human escalation records."""
from app.services.base import db


def create_escalation(request_id: str, reason: str, priority: str = "normal") -> dict:
    result = db().table("escalations").insert({
        "request_id": request_id, "reason": reason, "priority": priority, "status": "open",
    }).execute()
    return result.data[0]


def list_escalations(status: str | None = None) -> list[dict]:
    query = db().table("escalations").select("*, requests(*)").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    return query.execute().data


def resolve_escalation(escalation_id: str, assigned_human: str) -> dict:
    result = db().table("escalations").update({
        "status": "resolved", "assigned_human": assigned_human,
    }).eq("id", escalation_id).execute()
    return result.data[0] if result.data else {}
