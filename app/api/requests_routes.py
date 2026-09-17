from fastapi import APIRouter, HTTPException
from app.models.schemas import RequestCreate, RequestUpdate
from app.services import requests_service

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("")
def list_requests(status: str | None = None):
    return requests_service.list_requests(status)


@router.get("/{request_id}")
def get_request(request_id: str):
    result = requests_service.get_request(request_id)
    if not result:
        raise HTTPException(404, "Request not found")
    return result


@router.post("")
def create_request(payload: RequestCreate):
    return requests_service.create_request(
        payload.caller_id, payload.call_id, payload.request_type,
        payload.project_requirements, payload.priority,
    )


@router.patch("/{request_id}")
def update_request(request_id: str, payload: RequestUpdate):
    try:
        if payload.status:
            requests_service.transition_status(request_id, payload.status)
        if payload.assigned_developer:
            requests_service.assign_developer(request_id, payload.assigned_developer)
        return requests_service.get_request(request_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
