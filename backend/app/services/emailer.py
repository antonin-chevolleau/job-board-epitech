"""Application notification emails (optional, SMTP configured through env)."""

import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Advertisement, JobApplication

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str, reply_to: str | None = None) -> bool:
    """Send one email. Returns False (and logs) when SMTP is not configured or fails."""
    if not settings.smtp_host:
        logger.info("SMTP not configured, email to %s not sent", to)
        return False
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Could not send email to %s", to)
        return False
    return True


def notify_new_application(application_id: int) -> None:
    """Email the ad owner about an application and record `email_sent_at`.

    Runs as a background task, so it opens its own database session.
    """
    with SessionLocal() as db:
        application = db.get(JobApplication, application_id)
        if application is None:
            return
        ad = db.get(
            Advertisement,
            application.advertisement_id,
            options=[joinedload(Advertisement.company), joinedload(Advertisement.user)],
        )
        if ad is None:
            return
        recipient = ad.user.email if ad.user else ad.company.email
        body = (
            f"New application for \"{ad.title}\" ({ad.company.name})\n\n"
            f"Name:  {application.applicant_name}\n"
            f"Email: {application.applicant_email}\n"
            f"Phone: {application.applicant_phone}\n\n"
            f"{application.message}\n"
        )
        sent = send_email(
            recipient,
            f"[Job Board] New application: {ad.title}",
            body,
            reply_to=application.applicant_email,
        )
        if sent:
            application.email_sent_at = func.now()
            db.commit()
