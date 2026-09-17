
"""
Appointment creation + deterministic availability checking.

CRITICAL: this is the ONLY place availability is decided. The LLM/agent
must call `check_availability`/`find_available_slots` below — it must
never guess whether a developer is free.
"""
from datetime import date, time, datetime, timedelta
from app.services.base import db
from app.services.developers import get_developer, list_developers
from app.services.callers import get_caller
from app.services.email_sender import send_email

def _to_minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def is_slot_free(developer_id: str, check_date: date, start_time: time, end_time: time) -> bool:
    developer = get_developer(developer_id)
    if not developer or not developer.get("active"):
        return False

    weekday = check_date.strftime("%a").lower()[:3]  # 'mon', 'tue', ...
    if weekday not in [d.lower() for d in developer.get("working_days", [])]:
        return False

    work_start = datetime.strptime(developer["working_start"], "%H:%M:%S").time() \
        if isinstance(developer["working_start"], str) else developer["working_start"]
    work_end = datetime.strptime(developer["working_end"], "%H:%M:%S").time() \
        if isinstance(developer["working_end"], str) else developer["working_end"]

    if _to_minutes(start_time) < _to_minutes(work_start) or _to_minutes(end_time) > _to_minutes(work_end):
        return False

    existing = db().table("appointments").select("*").eq(
        "developer_id", developer_id
    ).eq("date", check_date.isoformat()).in_(
        "status", ["proposed", "confirmed"]
    ).execute().data

    requested_start, requested_end = _to_minutes(start_time), _to_minutes(end_time)
    for appt in existing:
        appt_start = _to_minutes(datetime.strptime(appt["start_time"], "%H:%M:%S").time())
        appt_end = _to_minutes(datetime.strptime(appt["end_time"], "%H:%M:%S").time())
        if requested_start < appt_end and requested_end > appt_start:
            return False  # overlap

    return True


def is_any_slot_free(check_date: date, start_time: time, end_time: time) -> bool:
    developers = list_developers(active_only=True)

    for developer in developers:
        if is_slot_free(
            developer["id"],
            check_date,
            start_time,
            end_time,
        ):
            return True

    return False


def find_available_slots(developer_id: str, check_date: date, slot_minutes: int = 60,
                          max_slots: int = 3) -> list[dict]:
    developer = get_developer(developer_id)
    if not developer:
        return []

    work_start = datetime.strptime(developer["working_start"], "%H:%M:%S").time() \
        if isinstance(developer["working_start"], str) else developer["working_start"]
    work_end = datetime.strptime(developer["working_end"], "%H:%M:%S").time() \
        if isinstance(developer["working_end"], str) else developer["working_end"]

    slots = []
    cursor = datetime.combine(check_date, work_start)
    day_end = datetime.combine(check_date, work_end)
    while cursor + timedelta(minutes=slot_minutes) <= day_end and len(slots) < max_slots:
        slot_start, slot_end = cursor.time(), (cursor + timedelta(minutes=slot_minutes)).time()
        if is_slot_free(developer_id, check_date, slot_start, slot_end):
            slots.append({"date": check_date.isoformat(), "start_time": slot_start.isoformat(),
                           "end_time": slot_end.isoformat()})
        cursor += timedelta(minutes=slot_minutes)
    return slots


def propose_appointment(developer_id: str, caller_id: str | None, call_id: str | None,
                         check_date: date, start_time: time, end_time: time) -> dict:
    if not is_slot_free(developer_id, check_date, start_time, end_time):
        raise ValueError("Requested slot is not available")
    result = db().table("appointments").insert({
        "developer_id": developer_id, "caller_id": caller_id, "call_id": call_id,
        "date": check_date.isoformat(), "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(), "status": "proposed",
    }).execute()
    return result.data[0]



def confirm_appointment(appointment_id: str, developer_id: str) -> dict:
    """Developer confirms. Assigns the meeting and its request to the developer who approved it."""
    appt = db().table("appointments").select("*").eq("id", appointment_id).execute().data
    if not appt:
        raise ValueError("Appointment not found")

    appointment = appt[0]

    if appointment.get("developer_id") and appointment["developer_id"] != developer_id:
        raise ValueError("This meeting is already assigned to another developer")

    if not is_slot_free(
        developer_id,
        date.fromisoformat(appointment["date"]),
        time.fromisoformat(appointment["start_time"]),
        time.fromisoformat(appointment["end_time"]),
    ):
        raise ValueError("The requested slot is no longer available for this developer")

    result = db().table("appointments").update({
        "developer_id": developer_id,
        "status": "confirmed",
    }).eq("id", appointment_id).execute()

    confirmed = result.data[0] if result.data else {}

    if appointment.get("call_id"):
        request_result = db().table("requests").select("id").eq(
            "call_id", appointment["call_id"]
        ).eq(
            "request_type", "meeting"
        ).order("created_at", desc=True).limit(1).execute()

        if request_result.data:
            db().table("requests").update({
                "assigned_developer": developer_id,
                "status": "meeting_booked",
            }).eq("id", request_result.data[0]["id"]).execute()

    caller = get_caller(appointment["caller_id"]) if appointment.get("caller_id") else None

    if caller and caller.get("email"):
        subject = "Your DevOrbis meeting has been confirmed"
        body = f"""Hi {caller.get("name") or "there"},

Your meeting with DevOrbis has been confirmed.

Date: {appointment["date"]}
Time: {appointment["start_time"]} - {appointment["end_time"]}

We look forward to speaking with you.

Best regards,
DevOrbis
"""
        send_email(caller["email"], subject, body)

    return confirmed



def decline_appointment(appointment_id: str) -> dict:
    result = db().table("appointments").update({"status": "declined"}).eq("id", appointment_id).execute()
    return result.data[0] if result.data else {}


def propose_unassigned_appointment(
    caller_id: str | None,
    call_id: str | None,
    check_date: date,
    start_time: time,
    end_time: time,
) -> dict:
    """Create a proposed meeting without assigning a developer yet."""

    developers = db().table("developers").select("id").eq("active", True).execute().data

    if not developers:
        raise ValueError("No active developers are available")

    if not is_any_slot_free(check_date, start_time, end_time):
        raise ValueError("No active developer is available at the requested time")

    result = db().table("appointments").insert({
        "developer_id": None,
        "caller_id": caller_id,
        "call_id": call_id,
        "date": check_date.isoformat(),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "status": "proposed",
    }).execute()

    return result.data[0]
