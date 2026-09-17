from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AppointmentCreate, AvailabilityCheck
from app.services import appointments as appointments_service
from app.services import developers as developers_service
from app.auth.dependencies import get_current_user


router = APIRouter(tags=["meetings"])


@router.get("/appointments")
def list_appointments():
    from app.services.base import db
    return db().table("appointments").select("*, developers(*), callers(*)").order(
        "date", desc=True
    ).execute().data


@router.post("/appointments/check-availability")
def check_availability(payload: AvailabilityCheck):
    is_free = appointments_service.is_slot_free(
        payload.developer_id, payload.date, payload.start_time, payload.end_time
    )
    return {"available": is_free}


@router.post("/appointments")
def propose_appointment(payload: AppointmentCreate):
    try:
        return appointments_service.propose_appointment(
            payload.developer_id, payload.caller_id, payload.call_id,
            payload.date, payload.start_time, payload.end_time,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.post("/meetings/{appointment_id}/confirm")
def confirm_meeting(
    appointment_id: str,
    current_user: dict = Depends(get_current_user),
):
    developer = developers_service.get_developer_by_email(current_user["email"])

    if not developer:
        raise HTTPException(
            status_code=403,
            detail="No developer account is linked to this user",
        )

    try:
        return appointments_service.confirm_appointment(
            appointment_id,
            developer["id"],
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.post("/meetings/{appointment_id}/decline")
def decline_meeting(appointment_id: str):
    return appointments_service.decline_appointment(appointment_id)
