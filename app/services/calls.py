"""CRUD for calls + call_summaries."""
from app.services.base import db


def create_call(caller_id: str | None, vapi_call_id: str | None) -> dict:
    result = db().table("calls").insert({
        "caller_id": caller_id, "vapi_call_id": vapi_call_id, "status": "in_progress",
    }).execute()
    return result.data[0]


def end_call(call_id: str, transcript: str | None) -> dict:
    result = db().table("calls").update({
        "status": "completed", "transcript": transcript,
    }).eq("id", call_id).execute()
    return result.data[0] if result.data else {}


def get_call(call_id: str) -> dict | None:
    result = db().table("calls").select("*").eq("id", call_id).execute()
    return result.data[0] if result.data else None


def save_summary(call_id: str, summary: str) -> dict:
    result = db().table("call_summaries").upsert({
        "call_id": call_id, "summary": summary,
    }, on_conflict="call_id").execute()
    return result.data[0] if result.data else {}
