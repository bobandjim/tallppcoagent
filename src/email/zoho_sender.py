"""
Zoho Mail SMTP sender.

Connects to smtp.zoho.com:587 via STARTTLS.
Credentials are read from environment variables — never hardcoded.

Usage:
    from src.email.zoho_sender import ZohoSender
    sender = ZohoSender()
    result = sender.send(
        to_email="contact@venue.org",
        to_name="Sarah Director",
        subject="A show your families will remember",
        body_text="...",
    )
"""

from __future__ import annotations

import os
import smtplib
import time
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)

SMTP_HOST = "smtp.zoho.com"
SMTP_PORT = 587


@dataclass
class SendResult:
    success: bool
    to_email: str
    error: Optional[str] = None
    message_id: Optional[str] = None


class ZohoSender:
    """
    Sends individual emails via Zoho Mail SMTP.
    Throttling and suppression checks happen in deliverability.py (the caller).
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        reply_to: Optional[str] = None,
        sender_name: Optional[str] = None,
    ):
        self.email = email or os.environ.get("ZOHO_EMAIL")
        self.password = password or os.environ.get("ZOHO_PASSWORD")
        self.reply_to = reply_to or os.environ.get("ZOHO_REPLY_TO") or self.email
        self.sender_name = sender_name or "Zachary Gartrell"

        if not self.email or not self.password:
            raise EnvironmentError(
                "ZOHO_EMAIL and ZOHO_PASSWORD must be set as environment variables."
            )

    def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
    ) -> SendResult:
        """
        Send one email. Returns SendResult with success/failure details.
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.email}>"
        msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email
        msg["Reply-To"] = self.reply_to

        msg.attach(MIMEText(body_text, "plain", "utf-8"))
        if body_html:
            msg.attach(MIMEText(body_html, "html", "utf-8"))

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.email, self.password)
                server.sendmail(self.email, [to_email], msg.as_string())

            message_id = msg.get("Message-ID", "")
            logger.info(
                "Email sent",
                extra={"to": to_email, "subject": subject, "message_id": message_id},
            )
            return SendResult(success=True, to_email=to_email, message_id=message_id)

        except smtplib.SMTPRecipientsRefused as e:
            error = f"Recipient refused: {e}"
            logger.warning("Send failed — hard bounce", extra={"to": to_email, "error": error})
            return SendResult(success=False, to_email=to_email, error=error)

        except smtplib.SMTPException as e:
            error = f"SMTP error: {e}"
            logger.error("Send failed — SMTP error", extra={"to": to_email, "error": error})
            return SendResult(success=False, to_email=to_email, error=error)

        except Exception as e:
            error = f"Unexpected error: {e}"
            logger.error("Send failed — unexpected", extra={"to": to_email, "error": error})
            return SendResult(success=False, to_email=to_email, error=error)
