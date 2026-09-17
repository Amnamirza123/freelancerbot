from fastapi import APIRouter
from app.services import calls as calls_service

router = APIRouter(prefix="/calls", tags=["calls"])


@router.get("/{call_id}")
def get_call(call_id: str):
    return calls_service.get_call(call_id)
