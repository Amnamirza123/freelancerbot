from fastapi import APIRouter
from app.services import developers as developers_service

router = APIRouter(prefix="/developers", tags=["developers"])


@router.get("")
def list_developers():
    return developers_service.list_developers(active_only=False)
