from fastapi import APIRouter, HTTPException
from app.models.schemas import ProposalCreate, ProposalDecision
from app.services import proposals as proposals_service
from app.services.base import db

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.get("")
def list_pending():
    return proposals_service.list_pending_proposals()


@router.post("")
def create_proposal(payload: ProposalCreate):
    return proposals_service.create_proposal(
        payload.request_id, payload.recipient_email, payload.draft_content
    )


@router.post("/{proposal_id}/approve")
def approve_and_send(proposal_id: str, approved_by: str = "developer") -> dict:
    from datetime import datetime, timezone
    from app.services.email_sender import send_email, EmailSendError
    from app.services import requests_service

    proposal = proposals_service.get_proposal(proposal_id)
    if not proposal:
        raise ValueError(f"Proposal {proposal_id} not found")

    try:
        send_email(
            to_address=proposal["recipient_email"],
            subject="Your Proposal from D'Vorbis",
            body=proposal["draft_content"],
        )
    except EmailSendError:
        raise

    result = db().table("proposals").update({
        "approval_status": "sent",
        "approved_by": approved_by,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", proposal_id).execute()

    requests_service.transition_status(proposal["request_id"], "proposal_sent")

    return result.data[0] if result.data else {}


@router.post("/{proposal_id}/reject")
def reject(proposal_id: str, payload: ProposalDecision) -> dict:
    from app.services import requests_service

    proposal = proposals_service.get_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    result = proposals_service.reject(proposal_id, payload.approved_by)

    requests_service.transition_status(
        proposal["request_id"],
        "rejected"
    )

    return result