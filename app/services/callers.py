"""CRUD for callers — created on first contact (Vapi webhook) or manually."""
from app.services.base import db


def get_or_create_caller(phone: str | None, name: str | None = None, email: str | None = None) -> dict:
    client = db()
    if phone:
        existing = client.table("callers").select("*").eq("phone", phone).execute()
        if existing.data:
            return existing.data[0]
    result = client.table("callers").insert({
        "name": name, "phone": phone, "email": email,
    }).execute()
    return result.data[0]


def get_caller(caller_id: str) -> dict | None:
    result = db().table("callers").select("*").eq("id", caller_id).execute()
    return result.data[0] if result.data else None


def update_caller_name(caller_id: str, name: str) -> dict:
    result = db().table("callers").update({"name": name}).eq("id", caller_id).execute()
    return result.data[0] if result.data else {}