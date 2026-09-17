"""Aggregate counts for the dashboard overview page."""
from app.services.base import db


def get_stats() -> dict:
    client = db()
    total_calls = client.table("calls").select("id", count="exact").execute().count or 0
    pending_approvals = client.table("proposals").select("id", count="exact").eq(
        "approval_status", "pending_approval"
    ).execute().count or 0
    meetings_booked = client.table("appointments").select("id", count="exact").eq(
        "status", "confirmed"
    ).execute().count or 0
    open_escalations = client.table("escalations").select("id", count="exact").eq(
        "status", "open"
    ).execute().count or 0
    total_leads = client.table("leads").select("id", count="exact").execute().count or 0

    return {
        "total_calls": total_calls,
        "pending_approvals": pending_approvals,
        "meetings_booked": meetings_booked,
        "open_escalations": open_escalations,
        "total_leads": total_leads,
    }
