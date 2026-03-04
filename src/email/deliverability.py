"""
Deliverability guard — enforces throttling, suppression checks, and
CAN-SPAM validation before every send.

Usage:
    from src.email.deliverability import DeliverabilityGuard
    from src.email.zoho_sender import ZohoSender
    from src.utils.compliance import SuppressionList, CANSPAMChecker
    from src.utils.audit import AuditLog

    guard = DeliverabilityGuard(
        sender=ZohoSender(),
        suppression=SuppressionList(),
        checker=CANSPAMChecker(...),
        audit=AuditLog(),
        max_per_day=50,
        delay_seconds=90,
    )
    guard.send_step(contact, venue, step, subject, body)
"""

from __future__ import annotations

import time
from datetime import date, datetime, timezone
from typing import Optional

from ..crm.schema import ContactRecord, VenueRecord
from ..utils.audit import AuditLog
from ..utils.compliance import CANSPAMChecker, SuppressionList
from ..utils.logger import get_logger
from .zoho_sender import SendResult, ZohoSender

logger = get_logger(__name__)


class DailyLimitReached(Exception):
    pass


class ComplianceError(Exception):
    pass


class TemplateNotApproved(Exception):
    """Raised when template_approved is not set to true in settings.yaml."""
    pass


class DeliverabilityGuard:
    """
    Wraps ZohoSender with:
      - Daily send count enforcement
      - Per-send delay throttling
      - Suppression list check (pre-send)
      - CAN-SPAM compliance validation
      - Audit logging for every send attempt
    """

    def __init__(
        self,
        sender: ZohoSender,
        suppression: SuppressionList,
        checker: CANSPAMChecker,
        audit: AuditLog,
        max_per_day: int = 50,
        delay_seconds: int = 90,
        template_approved: bool = False,
    ):
        self.sender = sender
        self.suppression = suppression
        self.checker = checker
        self.audit = audit
        self.max_per_day = max_per_day
        self.delay_seconds = delay_seconds
        self.template_approved = template_approved

        self._send_date: Optional[date] = None
        self._sends_today: int = 0

    def _reset_if_new_day(self) -> None:
        today = date.today()
        if self._send_date != today:
            self._send_date = today
            self._sends_today = 0

    def _check_throttle(self) -> None:
        self._reset_if_new_day()
        if self._sends_today >= self.max_per_day:
            raise DailyLimitReached(
                f"Daily send limit reached: {self._sends_today}/{self.max_per_day}"
            )

    def send_step(
        self,
        contact: ContactRecord,
        venue: VenueRecord,
        step: int,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        lead_id: Optional[int] = None,
    ) -> SendResult:
        """
        Execute one sequence step send with full guard logic.
        Raises DailyLimitReached or ComplianceError if guards trip.
        """
        email = contact.email or ""

        # 0. Template approval gate
        if not self.template_approved:
            raise TemplateNotApproved(
                "BLOCKED: Templates have not been reviewed and approved. "
                "Run `python3 run_sequence.py --review-mode` to preview all templates, "
                "then set `template_approved: true` in config/settings.yaml."
            )

        # 1. Suppression check
        if self.suppression.is_suppressed(email):
            logger.info("Send skipped — suppressed", extra={"email": email, "step": step})
            self.audit.log(
                "SUPPRESSED",
                lead_id=lead_id or venue.lead_id,
                payload={"email": email, "reason": "suppression_list", "step": step},
            )
            return SendResult(success=False, to_email=email, error="suppressed")

        # 2. Opt-out check
        if contact.is_suppressed():
            logger.info("Send skipped — email opt-out flag", extra={"email": email})
            return SendResult(success=False, to_email=email, error="email_opt_out")

        # 3. CAN-SPAM compliance check
        is_ok, warnings = self.checker.validate(subject, body_text)
        if not is_ok:
            raise ComplianceError(
                f"CAN-SPAM compliance failure for {email}: " + "; ".join(warnings)
            )

        # 4. Daily throttle check
        self._check_throttle()

        # 5. Send
        result = self.sender.send(
            to_email=email,
            to_name=contact.full_name,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
        )

        # 6. Audit + accounting
        event_type = "EMAIL_SENT" if result.success else "BOUNCE"
        self.audit.log(
            event_type,
            lead_id=lead_id or venue.lead_id,
            audit_trail_id=contact.audit_trail_id,
            payload={
                "email": email,
                "step": step,
                "subject": subject,
                "success": result.success,
                "error": result.error,
            },
        )

        if result.success:
            self._sends_today += 1
            logger.info(
                "Step sent",
                extra={"email": email, "step": step, "sends_today": self._sends_today},
            )
            # Throttle delay between sends
            if self.delay_seconds > 0:
                time.sleep(self.delay_seconds)

        elif result.error and "refused" in (result.error or "").lower():
            # Hard bounce — add to suppression
            self.suppression.add(email, "HARD_BOUNCE")
            logger.warning("Hard bounce suppressed", extra={"email": email})

        return result

    @property
    def sends_today(self) -> int:
        self._reset_if_new_day()
        return self._sends_today
