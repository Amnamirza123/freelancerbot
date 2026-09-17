"""
SMTP email sending via Gmail. Uses Python's built-in smtplib — no extra
dependency needed. Called only from proposals.approve_and_send(), never
directly by the agent (email always requires human approval first).
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


class EmailSendError(Exception):
    """Raised when SMTP sending fails, so callers can avoid marking a proposal as sent."""
    pass


def send_email(to_address: str, subject: str, body: str) -> None:
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        raise EmailSendError("SMTP_USERNAME/SMTP_PASSWORD not configured in .env")

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_FROM_ADDRESS or settings.SMTP_USERNAME
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        raise EmailSendError(f"Failed to send email: {exc}") from exc