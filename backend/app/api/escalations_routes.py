from fastapi import APIRouter
from app.models.schemas import EscalationCreate
from app.services import escalations as escalations_service

router = APIRouter(prefix="/escalations", tags=["escalations"])


@router.get("")
def list_escalations(status: str | None = None):
    return escalations_service.list_escalations(status)


@router.post("")
def create_escalation(payload: EscalationCreate):
    return escalations_service.create_escalation(
        payload.request_id, payload.reason, payload.priority
    )


@router.post("/{escalation_id}/resolve")
def resolve_escalation(escalation_id: str, assigned_human: str):
    return escalations_service.resolve_escalation(escalation_id, assigned_human)
