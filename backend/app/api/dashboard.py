from fastapi import APIRouter
from app.services.dashboard_stats import get_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats():
    return get_stats()
