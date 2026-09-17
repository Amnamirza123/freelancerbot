"""
CRUD + status-transition logic for `requests` — the central record tying
a call to whatever the client actually needed (pricing info, a proposal,
a meeting, an escalation).

Status transitions are validated here so no other layer can push a
request into an invalid state (rule from the brief: "Do not allow
invalid state transitions").
"""
from app.services.base import db

VALID_TRANSITIONS: dict[str, set[str]] = {
    "new_call": {"processing", "escalated"},
    "processing": {"needs_approval", "waiting_for_developer", "closed", "escalated"},
    "needs_approval": {"proposal_sent", "rejected", "escalated"},
    "waiting_for_developer": {"meeting_booked", "waiting_for_developer", "escalated"},
    "proposal_sent": {"closed", "escalated"},
    "meeting_booked": {"closed", "escalated"},
    "closed": set(),
    "escalated": {"processing", "closed"},
    "rejected": {"processing", "closed"},
}


def create_request(caller_id: str, call_id: str | None, request_type: str,
                    project_requirements: str | None, priority: str = "normal") -> dict:
    result = db().table("requests").insert({
        "caller_id": caller_id,
        "call_id": call_id,
        "request_type": request_type,
        "project_requirements": project_requirements,
        "priority": priority,
        "status": "new_call",
    }).execute()
    return result.data[0]


def get_request(request_id: str) -> dict | None:
    result = db().table("requests").select(
        "*, callers(*), developers(*), proposals(*)"
    ).eq("id", request_id).execute()
    return result.data[0] if result.data else None


def list_requests(status: str | None = None) -> list[dict]:
    query = db().table("requests").select(
    "*, callers(*), developers(*), proposals(*)"
).order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    return query.execute().data


def transition_status(request_id: str, new_status: str) -> dict:
    current = get_request(request_id)
    if not current:
        raise ValueError(f"Request {request_id} not found")
    current_status = current["status"]
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if new_status not in allowed and new_status != current_status:
        raise ValueError(
            f"Invalid transition: {current_status} -> {new_status}. "
            f"Allowed from {current_status}: {sorted(allowed)}"
        )
    result = db().table("requests").update({"status": new_status}).eq("id", request_id).execute()
    return result.data[0] if result.data else {}


def assign_developer(request_id: str, developer_id: str) -> dict:
    result = db().table("requests").update(
        {"assigned_developer": developer_id}
    ).eq("id", request_id).execute()
    return result.data[0] if result.data else {}
