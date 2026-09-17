"""
Proposal drafts. IMPORTANT: nothing here ever sends an email. Creation
always lands in `pending_approval`; only an explicit human approve action
(via the dashboard/API) is allowed to move it toward `sent`.
"""
from app.services.base import db


def create_proposal(request_id: str, recipient_email: str, draft_content: str) -> dict:
    result = db().table("proposals").insert({
        "request_id": request_id,
        "recipient_email": recipient_email,
        "draft_content": draft_content,
        "approval_status": "pending_approval",
    }).execute()
    return result.data[0]


def list_pending_proposals() -> list[dict]:
    return db().table("proposals").select("*, requests(*)").eq(
        "approval_status", "pending_approval"
    ).order("created_at", desc=True).execute().data


def get_proposal(proposal_id: str) -> dict | None:
    result = db().table("proposals").select("*").eq("id", proposal_id).execute()
    return result.data[0] if result.data else None


def approve_and_send(proposal_id: str, approved_by: str) -> dict:
    """
    Marks approved + sent — but only after the email is actually delivered
    via SMTP. If sending fails, the proposal stays in its current state
    and the error propagates so the API layer can report it.
    """
    from datetime import datetime, timezone
    from app.services.email_sender import send_email, EmailSendError

    proposal = get_proposal(proposal_id)
    if not proposal:
        raise ValueError(f"Proposal {proposal_id} not found")

    try:
        send_email(
            to_address=proposal["recipient_email"],
            subject="Your Proposal from D'Vorbis",
            body=proposal["draft_content"],
        )
    except EmailSendError:
        # Don't mark as sent if delivery actually failed — re-raise so the
        # route layer can return a proper error instead of a false success.
        raise

    result = db().table("proposals").update({
        "approval_status": "sent",
        "approved_by": approved_by,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", proposal_id).execute()
    return result.data[0] if result.data else {}

def reject(proposal_id: str, approved_by: str) -> dict:
    result = db().table("proposals").update({
        "approval_status": "rejected", "approved_by": approved_by,
    }).eq("id", proposal_id).execute()
    return result.data[0] if result.data else {}
