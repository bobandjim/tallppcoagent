"""
Compliance utilities — CAN-SPAM safe defaults + suppression list enforcement.

This module does NOT provide legal advice. It implements technical safe defaults
that align with CAN-SPAM Act requirements and common deliverability best practices.

Responsibilities:
  1. Check email address against suppression list before any send
  2. Add suppression entries (opt-out, hard bounce, soft bounce, manual)
  3. Validate that required CAN-SPAM fields are present in email payload
  4. Flag potential spam-trigger phrases in subject lines
"""

from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Phrases that commonly trigger spam filters — not exhaustive, but covers the worst offenders
SPAM_TRIGGER_PATTERNS = [
    r"\bfree\b",
    r"\bact now\b",
    r"\blimited time\b",
    r"\bguaranteed\b",
    r"\bno obligation\b",
    r"\bunsubscribe\b",  # ok in body footer, NOT subject
    r"\bmake money\b",
    r"\bcash\b",
    r"\bwin\b",
    r"!!!",
    r"\$\$\$",
    r"\b100%\b",
    r"\bnow or never\b",
    r"\burgent\b",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in SPAM_TRIGGER_PATTERNS]


class SuppressionList:
    """
    Manages the suppression list CSV.
    Format: email,reason,suppressed_at
    Reasons: OPT_OUT | HARD_BOUNCE | SOFT_BOUNCE | MANUAL
    """

    VALID_REASONS = frozenset({"OPT_OUT", "HARD_BOUNCE", "SOFT_BOUNCE", "MANUAL"})

    def __init__(self, path: str | Path = "config/suppression_list.csv"):
        self.path = Path(path)
        self._cache: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        self._cache.clear()
        if not self.path.exists():
            return
        with open(self.path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(
                (line for line in f if not line.strip().startswith("#"))
            ):
                email = row.get("email", "").lower().strip()
                if email:
                    self._cache[email] = row

    def is_suppressed(self, email: str) -> bool:
        return email.lower().strip() in self._cache

    def add(self, email: str, reason: str) -> None:
        if reason not in self.VALID_REASONS:
            raise ValueError(f"Invalid suppression reason: {reason!r}")
        email = email.lower().strip()
        row = {
            "email": email,
            "reason": reason,
            "suppressed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._cache[email] = row
        self._persist(row)

    def _persist(self, row: dict) -> None:
        """Append a new suppression entry to the CSV."""
        write_header = not self.path.exists() or self.path.stat().st_size == 0
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["email", "reason", "suppressed_at"])
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def all_suppressed(self) -> list[str]:
        return list(self._cache.keys())

    def count(self) -> int:
        return len(self._cache)


class CANSPAMChecker:
    """
    Validates outbound email payloads against CAN-SPAM safe defaults.
    Not legal advice — these are technical checkpoints.
    """

    REQUIRED_FOOTER_FIELDS = ["physical_address", "unsubscribe_url", "sender_name"]

    def __init__(self, physical_address: str, unsubscribe_url: str, sender_name: str):
        self.physical_address = physical_address
        self.unsubscribe_url = unsubscribe_url
        self.sender_name = sender_name

    def check_subject(self, subject: str) -> list[str]:
        """Return list of compliance warnings for the subject line."""
        warnings = []
        if not subject or not subject.strip():
            warnings.append("Subject line is empty.")
        if len(subject) > 150:
            warnings.append("Subject line is unusually long (>150 chars).")
        for pattern in COMPILED_PATTERNS:
            if pattern.search(subject):
                warnings.append(f"Possible spam-trigger phrase in subject: matched /{pattern.pattern}/")
        return warnings

    def check_body(self, body: str) -> list[str]:
        """Return list of compliance warnings for the email body."""
        warnings = []
        if self.physical_address.lower() not in body.lower():
            warnings.append("Physical mailing address not found in email body (CAN-SPAM required).")
        if self.unsubscribe_url.lower() not in body.lower():
            warnings.append("Unsubscribe URL not found in email body (CAN-SPAM required).")
        if self.sender_name.lower() not in body.lower():
            warnings.append("Sender name not found in email body.")
        return warnings

    def validate(self, subject: str, body: str) -> tuple[bool, list[str]]:
        """
        Full CAN-SPAM validation.
        Returns (is_compliant, list_of_warnings).
        Any warning = not compliant.
        """
        warnings = self.check_subject(subject) + self.check_body(body)
        return (len(warnings) == 0), warnings
