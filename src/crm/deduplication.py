"""
Deduplication logic for venues and contacts.

Rules:
  - VenueRecord dedup key: normalized company name + state (case-insensitive)
  - ContactRecord dedup key: normalized email address (case-insensitive)
  - On conflict: record with the higher UniqueId (assumed more recent) wins
  - Merge strategy: newer record's non-null fields override older record's fields
  - All dedup events are logged via the audit module
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from .schema import ContactRecord, VenueRecord

logger = logging.getLogger(__name__)


def _newer(a_id: int, b_id: int) -> bool:
    """Return True if b is newer than a (higher UniqueId = more recently added)."""
    return b_id > a_id


def dedup_venues(venues: list[VenueRecord]) -> tuple[list[VenueRecord], list[dict]]:
    """
    Dedup a list of VenueRecords.

    Returns:
        (deduplicated list, list of dedup event dicts for audit logging)
    """
    seen: dict[str, VenueRecord] = {}
    events: list[dict] = []

    for venue in venues:
        key = venue.dedup_key()
        if key in seen:
            existing = seen[key]
            if _newer(existing.lead_id, venue.lead_id):
                # Incoming record is newer — merge non-null fields on top
                merged = _merge_venue(existing, venue)
                seen[key] = merged
                events.append({
                    "event": "VENUE_DEDUP",
                    "kept_id": venue.lead_id,
                    "dropped_id": existing.lead_id,
                    "key": key,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                logger.debug("Dedup: kept venue %d over %d (key=%s)", venue.lead_id, existing.lead_id, key)
            else:
                events.append({
                    "event": "VENUE_DEDUP_SKIPPED",
                    "kept_id": existing.lead_id,
                    "dropped_id": venue.lead_id,
                    "key": key,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        else:
            seen[key] = venue

    return list(seen.values()), events


def dedup_contacts(contacts: list[ContactRecord]) -> tuple[list[ContactRecord], list[dict]]:
    """
    Dedup a list of ContactRecords by email.

    Returns:
        (deduplicated list, list of dedup event dicts for audit logging)
    """
    seen: dict[str, ContactRecord] = {}
    events: list[dict] = []

    for contact in contacts:
        key = contact.dedup_key()
        if not key:
            # No email — keep as-is (cannot dedup without key)
            seen[f"_noemail_{contact.contact_id}"] = contact
            continue

        if key in seen:
            existing = seen[key]
            if _newer(existing.contact_id, contact.contact_id):
                merged = _merge_contact(existing, contact)
                seen[key] = merged
                events.append({
                    "event": "CONTACT_DEDUP",
                    "kept_id": contact.contact_id,
                    "dropped_id": existing.contact_id,
                    "email": key,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                logger.debug("Dedup: kept contact %d over %d (email=%s)", contact.contact_id, existing.contact_id, key)
            else:
                events.append({
                    "event": "CONTACT_DEDUP_SKIPPED",
                    "kept_id": existing.contact_id,
                    "dropped_id": contact.contact_id,
                    "email": key,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        else:
            seen[key] = contact

    return list(seen.values()), events


def _merge_venue(older: VenueRecord, newer: VenueRecord) -> VenueRecord:
    """Merge two VenueRecords: newer's non-None fields overwrite older's."""
    data = older.model_dump()
    for k, v in newer.model_dump().items():
        if v is not None:
            data[k] = v
    return VenueRecord(**data)


def _merge_contact(older: ContactRecord, newer: ContactRecord) -> ContactRecord:
    """Merge two ContactRecords: newer's non-None fields overwrite older's."""
    data = older.model_dump()
    for k, v in newer.model_dump().items():
        if v is not None:
            data[k] = v
    return ContactRecord(**data)
