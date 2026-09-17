"""Shared state that flows through every node of the LangGraph agent."""
from __future__ import annotations
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    call_id: Optional[str]
    caller_id: Optional[str]
    caller_name: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    messages: Annotated[list, add_messages]

    detected_intent: Optional[str]          # pricing | proposal | meeting | escalation | general
    project_requirements: Optional[str]
    assigned_developer: Optional[str]
    preferred_meeting_times: Optional[str]
    retrieved_context: Optional[str]

    request_id: Optional[str]
    request_status: Optional[str]
    proposal_status: Optional[str]
    escalation_status: Optional[str]
