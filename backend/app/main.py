"""
FreelancerBot backend entrypoint.

Wires together the database health check plus every API router: requests,
proposals, meetings/appointments, escalations, leads, developers, calls,
dashboard stats, and the Vapi/n8n webhooks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.client import get_supabase

from app.api import (
    dashboard, requests_routes, proposals_routes, meetings_routes,
    escalations_routes, leads_routes, developers_routes, calls_routes,
    webhooks_routes,knowledge_base_routes,
)

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Client Acquisition, Support & Scheduling Automation System",
    version="0.2.0",
)

# Wide-open CORS for local dev only. Tightened in Phase 14 (Security Hardening)
# to an explicit allow-list (e.g. the deployed Vercel frontend URL).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://freelancerbot-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(requests_routes.router)
app.include_router(proposals_routes.router)
app.include_router(meetings_routes.router)
app.include_router(escalations_routes.router)
app.include_router(leads_routes.router)
app.include_router(developers_routes.router)
app.include_router(calls_routes.router)
app.include_router(webhooks_routes.router)
app.include_router(knowledge_base_routes.router)


@app.get("/health")
def health_check():
    """
    Liveness check + database connectivity report. Vapi, n8n, and uptime
    monitors all hit this. If Supabase isn't configured yet, we say so
    instead of crashing.
    """
    db_status = "not_configured"
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            client = get_supabase()
            client.table("callers").select("id", count="exact").limit(1).execute()
            db_status = "connected"
        except Exception as exc:  # noqa: BLE001 - surface any DB error directly
            db_status = f"error: {exc}"

    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} backend is running. See /docs for the API."}
