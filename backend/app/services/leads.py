"""CRUD for leads."""
from app.services.base import db


def create_lead(caller_id: str, project_description: str | None, service: str | None) -> dict:
    result = db().table("leads").insert({
        "caller_id": caller_id,
        "project_description": project_description,
        "service": service,
        "status": "new",
    }).execute()
    return result.data[0]


def list_leads() -> list[dict]:
    return db().table("leads").select("*, callers(*)").order("created_at", desc=True).execute().data


def update_lead_status(lead_id: str, status: str) -> dict:
    result = db().table("leads").update({"status": status}).eq("id", lead_id).execute()
    return result.data[0] if result.data else {}


def create_call_lead(caller_id: str) -> dict:
    return create_lead(
        caller_id=caller_id,
        project_description=None,
        service=None,
    )