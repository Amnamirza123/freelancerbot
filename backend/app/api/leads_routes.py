from fastapi import APIRouter
from app.services import leads as leads_service

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("")
def list_leads():
    return leads_service.list_leads()
