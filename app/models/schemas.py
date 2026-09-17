"""
Pydantic schemas shared across the API layer.

These mirror the Supabase tables (see migrations/001_init_schema.sql) but
are intentionally kept separate from raw DB rows so the API can validate
input/output independently of storage details.
"""

from __future__ import annotations
from datetime import date, time, datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


RequestStatus = Literal[
    "new_call", "processing", "needs_approval", "waiting_for_developer",
    "proposal_sent", "meeting_booked", "closed", "escalated", "rejected",
]
RequestType = Literal["pricing", "proposal", "meeting", "escalation", "general"]
ApprovalStatus = Literal["pending_approval", "approved", "rejected", "sent"]
AppointmentStatus = Literal["proposed", "confirmed", "declined", "cancelled"]
Priority = Literal["low", "normal", "high", "urgent"]


class CallerCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class LeadCreate(BaseModel):
    caller_id: str
    project_description: Optional[str] = None
    service: Optional[str] = None


class RequestCreate(BaseModel):
    caller_id: str
    call_id: Optional[str] = None
    request_type: RequestType
    project_requirements: Optional[str] = None
    priority: Priority = "normal"


class RequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    assigned_developer: Optional[str] = None
    project_requirements: Optional[str] = None


class ProposalCreate(BaseModel):
    request_id: str
    recipient_email: EmailStr
    draft_content: str


class ProposalDecision(BaseModel):
    approved_by: str


class AppointmentCreate(BaseModel):
    developer_id: str
    caller_id: Optional[str] = None
    call_id: Optional[str] = None
    date: date
    start_time: time
    end_time: time


class AvailabilityCheck(BaseModel):
    developer_id: str
    date: date
    start_time: time
    end_time: time


class EscalationCreate(BaseModel):
    request_id: str
    reason: str
    priority: Priority = "normal"


class CallSummaryCreate(BaseModel):
    call_id: str
    summary: str


class VapiWebhookPayload(BaseModel):
    """Loose schema — Vapi's webhook payload has many fields; we only
    validate the ones we actually use, and keep the rest available via
    the raw dict in the route handler."""
    type: Optional[str] = None
    call: Optional[dict] = None
