"""
LangChain-style tool functions the agent can call. Each tool wraps a
deterministic service function — the LLM decides WHEN to call a tool and
WITH WHAT arguments, but never decides the tool's actual output (pricing,
availability, etc. always come from the database/service layer).
"""
from datetime import date, time
from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app.rag.retriever import retrieve, build_context
from app.services import leads as leads_service
from app.services import developers as developers_service
from app.services import appointments as appointments_service
from app.services import escalations as escalations_service
from app.services import proposals as proposals_service
from app.services import requests_service
from app.services import callers as callers_service
from app.prompts.prompts import PROPOSAL_PROMPT_V1


@tool
def search_services(query: str) -> str:
    """Search the knowledge base for information about our services. Use this when the
    caller asks what services we offer or how something works."""
    chunks = retrieve(query)
    context = build_context(chunks)
    return context or "NO_MATCHING_INFORMATION"


@tool
def get_pricing(query: str) -> str:
    """Search the knowledge base for pricing information. Use this when the caller asks
    about cost, price, or packages."""
    chunks = retrieve(query, match_count=3)
    context = build_context(chunks)
    return context or "NO_MATCHING_INFORMATION"


@tool
def create_lead(caller_id: str, project_description: str, service: str) -> dict:
    """Create a lead record once the caller has described what they need. Use this once
    per call, after the project requirement is clear."""
    return leads_service.create_lead(caller_id, project_description, service)


@tool
def find_specialist(technology: str) -> dict:
    """Find a developer whose specialty matches the requested technology or project type.
    Call this BEFORE check_availability or book_meeting — you need a developer_id first."""
    developer = developers_service.find_specialist(technology)
    return developer or {"error": "No active developer found"}


@tool
def check_availability(check_date: str, start_time: str, end_time: str) -> dict:
    """Check whether at least one active developer is available at a specific date/time.
    Dates are YYYY-MM-DD, times are HH:MM. Never guess availability — always call this tool."""
    is_free = appointments_service.is_any_slot_free(
        date.fromisoformat(check_date),
        time.fromisoformat(start_time),
        time.fromisoformat(end_time),
    )
    return {"available": is_free}

@tool
def find_alternative_slots(developer_id: str, check_date: str) -> list[dict]:
    """Find up to 3 available time slots for a developer on a given date (YYYY-MM-DD)."""
    return appointments_service.find_available_slots(developer_id, date.fromisoformat(check_date))


@tool
def book_meeting(developer_id: str, check_date: str, start_time: str, end_time: str,
                  state: Annotated[dict, InjectedState]) -> dict:
    """Propose a meeting slot with a developer, after check_availability confirmed it's free.
    This creates a PROPOSED meeting — it is NOT confirmed until the developer accepts. Never
    tell the caller the meeting is booked/confirmed; tell them it's pending developer confirmation."""
    caller_id = state.get("caller_id")
    call_id = state.get("call_id")
    if not caller_id:
        return {"error": "No caller_id in state — cannot book a meeting."}

    request = requests_service.create_request(
        caller_id=caller_id,
        call_id=call_id,
        request_type="meeting",
        project_requirements=None,
    )
    requests_service.transition_status(request["id"], "processing")
    requests_service.transition_status(request["id"], "waiting_for_developer")
    requests_service.assign_developer(request["id"], developer_id)

    try:
        appointment = appointments_service.propose_appointment(
            developer_id=developer_id,
            caller_id=caller_id,
            call_id=call_id,
            check_date=date.fromisoformat(check_date),
            start_time=time.fromisoformat(start_time),
            end_time=time.fromisoformat(end_time),
        )
    except ValueError as e:
        return {"error": str(e)}

    return {
        "status": "proposed_pending_developer_confirmation",
        "appointment_id": appointment["id"],
        "request_id": request["id"],
        "message": "The meeting slot has been proposed to the developer and is awaiting their confirmation.",
    }

@tool
def draft_email(project_requirements: str, recipient_email: str,
                 state: Annotated[dict, InjectedState]) -> dict:
    """Draft a proposal email grounded in retrieved services/pricing context, and save it
    for human approval. Ask the caller for their email address first if you don't have it.
    Does NOT send anything — always requires human approval before sending."""
    from app.agent.graph import _get_llm

    caller_id = state.get("caller_id")
    call_id = state.get("call_id")

    if not caller_id:
        return {
            "error": "No caller_id in state — cannot create a request/proposal."
        }

    recipient_email = recipient_email.strip()

    if "@" not in recipient_email or "." not in recipient_email.split("@")[-1]:
        return {
            "status": "invalid_email",
            "message": "The email address does not appear to be valid. Ask the caller to provide their full email address again, including the @ symbol.",
        }

    try:
        print("[DRAFT EMAIL] Starting proposal draft...")
        print(f"[DRAFT EMAIL] recipient_email={recipient_email}")
        print(f"[DRAFT EMAIL] caller_id={caller_id}")
        print(f"[DRAFT EMAIL] project_requirements={project_requirements}")

        # Retrieve grounded company information.
        chunks = retrieve(project_requirements)
        context = build_context(chunks)

        if not context:
            context = "No specific pricing found — keep the draft general."

        print("[DRAFT EMAIL] Knowledge base retrieval successful.")

        prompt = PROPOSAL_PROMPT_V1.format(
            project_requirements=project_requirements,
            context=context,
        )

        # Generate the proposal body.
        llm = _get_llm()

        print("[DRAFT EMAIL] Generating proposal with LLM...")
        response = llm.invoke(prompt)

        drafted_body = str(response.content).strip()

        if not drafted_body:
            print("[DRAFT EMAIL] LLM returned an empty draft.")
            return {
                "error": "Failed to generate the email draft."
            }

        print("[DRAFT EMAIL] Proposal draft generated successfully.")

        # Create the request only after the draft was successfully generated.
        request = requests_service.create_request(
            caller_id=caller_id,
            call_id=call_id,
            request_type="proposal",
            project_requirements=project_requirements,
        )

        print(f"[DRAFT EMAIL] Request created: {request['id']}")

        requests_service.transition_status(
            request["id"],
            "processing",
        )

        requests_service.transition_status(
            request["id"],
            "needs_approval",
        )

        print("[DRAFT EMAIL] Request moved to needs_approval.")

        # Save the proposal for human approval.
        proposal = proposals_service.create_proposal(
            request_id=request["id"],
            recipient_email=recipient_email,
            draft_content=drafted_body,
        )

        print(f"[DRAFT EMAIL] Proposal created: {proposal['id']}")

        return {
            "status": "drafted_pending_approval",
            "proposal_id": proposal["id"],
            "message": "Your proposal has been drafted and is waiting for approval before it's sent.",
        }

    except Exception as exc:
        print(f"[DRAFT EMAIL ERROR] {type(exc).__name__}: {exc}")

        return {
            "status": "failed",
            "error": "I could not create the proposal draft.",
            "message": "The proposal draft could not be created. Do not claim that the email was sent.",
        }
@tool
def escalate_to_human(reason: str, state: Annotated[dict, InjectedState]) -> dict:
    """Escalate the caller's request to a human. The tool creates the request automatically."""
    caller_id = state.get("caller_id")
    call_id = state.get("call_id")

    if not caller_id:
        return {"error": "No caller_id in state — cannot create an escalation request."}

    request = requests_service.create_request(
        caller_id=caller_id,
        call_id=call_id,
        request_type="escalation",
        project_requirements=reason,
    )

    requests_service.transition_status(request["id"], "processing")

    return {
        "status": "escalated",
        "request_id": request["id"],
        "message": "The request has been escalated to a human.",
    }
@tool
def save_caller_name(name: str, state: Annotated[dict, InjectedState]) -> dict:
    """Save the caller's name once they provide it. Call this as soon as they tell you their name."""
    caller_id = state.get("caller_id")
    if not caller_id:
        return {"error": "No caller_id in state"}
    callers_service.update_caller_name(caller_id, name)
    return {"status": "saved"}


@tool
def book_meeting_fast(
    check_date: str,
    start_time: str,
    end_time: str,
    state: Annotated[dict, InjectedState],
) -> dict:
    """Create a technical meeting request for the requested time without assigning a developer.
    The request is visible to all developers, and the developer who accepts it is assigned later."""
    caller_id = state.get("caller_id")
    call_id = state.get("call_id")

    if not caller_id:
        return {"error": "No caller_id in state."}

    d = date.fromisoformat(check_date)
    s = time.fromisoformat(start_time)
    e = time.fromisoformat(end_time)

    try:
        appointment = appointments_service.propose_unassigned_appointment(
            caller_id=caller_id,
            call_id=call_id,
            check_date=d,
            start_time=s,
            end_time=e,
        )
    except ValueError as exc:
        return {"error": str(exc)}

    request = requests_service.create_request(
        caller_id=caller_id,
        call_id=call_id,
        request_type="meeting",
        project_requirements=None,
    )

    requests_service.transition_status(request["id"], "processing")
    requests_service.transition_status(request["id"], "waiting_for_developer")

    return {
        "status": "proposed_pending_developer_confirmation",
        "appointment_id": appointment["id"],
        "request_id": request["id"],
        "date": check_date,
        "start_time": start_time,
        "end_time": end_time,
        "message": "The meeting request has been created and is awaiting developer confirmation.",
    }

ALL_TOOLS = [
    search_services,
    get_pricing,
    create_lead,
    draft_email,
    escalate_to_human,
    save_caller_name,
    book_meeting_fast,
]