#!/usr/bin/env python3
"""
run_sequence.py — Princess Peigh Adventures Outbound Sequence Runner

CLI entry point for executing the outbound email sequence.

Usage:
    # STEP 1 — Review all email templates before any live sends (MANDATORY)
    python3 run_sequence.py --review-mode

    # Dry run (renders templates, skips actual send)
    python3 run_sequence.py --dry-run

    # Test mode (sends to seed list only, not real contacts)
    python3 run_sequence.py --test-mode --seed-file data/seed_lists/seed_list.csv

    # Live run (sends to real contacts per throttle config)
    # Requires: template_approved: true in config/settings.yaml
    python3 run_sequence.py --live

    # Show stats only (no sends)
    python3 run_sequence.py --stats

Options:
    --review-mode    Render all 4 templates with sample data; print to stdout; no sends
    --dry-run        Render templates and check compliance; do not send
    --test-mode      Send to seed addresses only
    --live           Send to real contacts (requires template_approved: true in settings)
    --stats          Print CRM and audit stats; exit
    --config PATH    Path to settings.yaml (default: config/settings.yaml)
    --crm PATH       Path to leads.xlsx (overrides config)
    --step INT       Only run this specific step (1-4); default: next pending step
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load .env before importing modules that read env vars
load_dotenv()

from src.crm.deduplication import dedup_contacts, dedup_venues
from src.crm.exporter import CRMExporter, ExportPayload
from src.crm.importer import CRMImporter
from src.crm.schema import ContactRecord, GigLeadRecord, VenueRecord
from src.email.deliverability import ComplianceError, DailyLimitReached, DeliverabilityGuard, TemplateNotApproved
from src.email.sequence_builder import SequenceBuilder
from src.email.zoho_sender import ZohoSender
from src.utils.audit import AuditLog
from src.utils.compliance import CANSPAMChecker, SuppressionList
from src.utils.logger import get_logger

logger = get_logger("run_sequence")


SAMPLE_VENUE = {
    "contact_name": "Sarah",
    "venue_name": "Riverside Community Theater",
    "city": "Springfield",
    "state": "NY",
    "seating_capacity_tier": "medium (201-400 seats)",
    "programming_focus": "family series and community productions",
    "mission_excerpt": "bringing accessible, enriching theater to families in our region",
    "next_season": "the 2025-2026 season",
}


def review_mode(config: dict) -> None:
    """
    Render all 4 email templates with sample venue data and print to stdout.
    No network calls. No CRM writes. No audit log entries.

    After reviewing, set `template_approved: true` in config/settings.yaml.
    """
    templates_dir = config["sequences"]["templates_dir"]
    sender_name = config["brand"]["sender_name"]
    physical_address = config["brand"]["physical_address"]
    unsubscribe_url = config["brand"].get("unsubscribe_url", "[UNSUBSCRIBE_URL]")
    reply_to = "[your@email.com]"

    builder = SequenceBuilder(templates_dir)

    context = {
        **SAMPLE_VENUE,
        "sender_name": sender_name,
        "physical_address": physical_address,
        "unsubscribe_url": unsubscribe_url,
        "reply_to_email": reply_to,
        "show_name": config["brand"]["show_name"],
    }

    delays = config["sequences"]["delays_days"]
    step_labels = [
        f"Step 1 — Day {delays[0]}: Initial Outreach",
        f"Step 2 — Day {delays[1]}: Follow-Up 1",
        f"Step 3 — Day {delays[2]}: Follow-Up 2",
        f"Step 4 — Day {delays[3]}: Breakup / Final Touch",
    ]

    print("\n" + "=" * 70)
    print("TEMPLATE REVIEW MODE — Princess Peigh Adventures")
    print("No emails will be sent. This is for human review only.")
    print("=" * 70)
    print("\nSample venue context used for rendering:")
    for k, v in SAMPLE_VENUE.items():
        print(f"  [{k}] = {v!r}")
    print()

    for step in range(1, 5):
        token_errors = builder.check_tokens(step, context)
        subject, body = builder.render(step, context)

        print("─" * 70)
        print(f"  {step_labels[step - 1]}")
        print("─" * 70)
        if token_errors:
            print(f"  ⚠  TOKEN ERRORS: {token_errors}")
        print(f"  SUBJECT: {subject}")
        print()
        print(body)
        print()

    print("=" * 70)
    print("REVIEW COMPLETE")
    print()
    print("If templates look correct, set in config/settings.yaml:")
    print("  template_approved: true")
    print()
    print("Then run live sends with:")
    print("  python3 run_sequence.py --live")
    print("=" * 70 + "\n")


def load_config(path: str = "config/settings.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def print_stats(config: dict, crm_path: str, audit_db: str) -> None:
    importer = CRMImporter(crm_path)
    result = importer.load_all()
    audit = AuditLog(audit_db)

    print(f"\n{'='*50}")
    print("SYSTEM STATUS — Princess Peigh Adventures")
    print(f"{'='*50}")
    print(f"CRM file: {crm_path}")
    print(f"\nCRM Records:")
    print(f"  Venues:    {len(result.venues)}")
    print(f"  Contacts:  {len(result.contacts)}")
    print(f"  Gig Leads: {len(result.gig_leads)}")
    print(f"  Import errors: {result.error_count}")

    suppression = SuppressionList(config["crm"]["suppression_file"])
    print(f"\nSuppression list: {suppression.count()} addresses")

    print(f"\nAudit log ({audit_db}):")
    for event_type in ["LEAD_CREATED", "EMAIL_SENT", "REPLY_RECEIVED", "OPT_OUT", "BOUNCE", "MEETING_BOOKED", "SHOW_BOOKED"]:
        count = audit.event_count(event_type)
        if count:
            print(f"  {event_type}: {count}")

    # Sequence progress
    eligible = [c for c in result.contacts if c.sequence_id and (c.step_number or 0) < 4 and not c.is_suppressed()]
    print(f"\nSequence status:")
    print(f"  Contacts enrolled in a sequence: {len([c for c in result.contacts if c.sequence_id])}")
    print(f"  Eligible for next step: {len(eligible)}")
    print(f"  Completed sequence (step 4): {len([c for c in result.contacts if (c.step_number or 0) >= 4])}")
    print(f"{'='*50}\n")


def get_venue(venues: list[VenueRecord], company_id: int | None) -> VenueRecord | None:
    if company_id is None:
        return None
    return next((v for v in venues if v.lead_id == company_id), None)


def get_gig(gig_leads: list[GigLeadRecord], contact_id: int) -> GigLeadRecord | None:
    return next((g for g in gig_leads if g.contact_id == contact_id), None)


def build_context(contact: ContactRecord, venue: VenueRecord, gig: GigLeadRecord | None) -> dict:
    return {
        "contact_name": contact.first_name or contact.full_name or "Hello",
        "venue_name": (gig.venue_name if gig else None) or venue.venue_name or venue.company,
        "city": venue.city or "",
        "state": venue.state or "",
        "seating_capacity_tier": venue.seating_capacity_tier,
        "mission_excerpt": venue.mission_excerpt,
        "programming_focus": venue.programming_focus,
        "next_season": "the upcoming season",  # TODO: make configurable
    }


def run(args: argparse.Namespace, config: dict) -> None:
    crm_path = args.crm or config["crm"]["leads_file"]
    audit_db = config["crm"]["audit_db"]
    suppression_file = config["crm"]["suppression_file"]
    templates_dir = config["sequences"]["templates_dir"]

    sender_name = config["brand"]["sender_name"]
    physical_address = config["brand"]["physical_address"]
    unsubscribe_url = config["brand"].get("unsubscribe_url", "")

    if args.review_mode:
        review_mode(config)
        return

    if args.stats:
        print_stats(config, crm_path, audit_db)
        return

    # Template approval gate — block live/test sends before human review
    if args.live or args.test_mode:
        template_approved = config.get("template_approved", False)
        if not template_approved:
            print(
                "\nBLOCKED: Templates have not been approved.\n"
                "Run `python3 run_sequence.py --review-mode` to preview all 4 templates,\n"
                "then set `template_approved: true` in config/settings.yaml.\n"
            )
            sys.exit(1)

    # Load CRM
    logger.info("Loading CRM", extra={"path": crm_path})
    importer = CRMImporter(crm_path)
    crm = importer.load_all()

    if crm.error_count:
        logger.warning("CRM import had errors", extra={"count": crm.error_count})
        for err in crm.errors[:5]:
            logger.warning("Import error", extra=err)

    venues, _ = dedup_venues(crm.venues)
    contacts, _ = dedup_contacts(crm.contacts)

    suppression = SuppressionList(suppression_file)
    checker = CANSPAMChecker(physical_address, unsubscribe_url, sender_name)
    builder = SequenceBuilder(templates_dir)
    audit = AuditLog(audit_db)

    # Setup sender (skip for dry-run)
    if args.dry_run:
        sender = None
        guard = None
    else:
        sender = ZohoSender(sender_name=sender_name)
        guard = DeliverabilityGuard(
            sender=sender,
            suppression=suppression,
            checker=checker,
            audit=audit,
            max_per_day=config["deliverability"]["max_sends_per_day"],
            delay_seconds=config["deliverability"]["delay_between_sends_seconds"],
            template_approved=config.get("template_approved", False),
        )

    # Find eligible contacts
    eligible = []
    for contact in contacts:
        if not contact.sequence_id:
            continue
        if contact.is_suppressed():
            continue
        if (contact.step_number or 0) >= 4:
            continue
        if suppression.is_suppressed(contact.email or ""):
            continue
        eligible.append(contact)

    if args.step:
        eligible = [c for c in eligible if (c.step_number or 0) + 1 == args.step]

    logger.info("Eligible contacts", extra={"count": len(eligible)})

    # Test mode: override contacts list with seed addresses
    if args.test_mode:
        logger.info("TEST MODE: replacing contacts with seed list", extra={"seed_file": args.seed_file})
        seed_contacts = []
        with open(args.seed_file, newline="") as f:
            for row in csv.DictReader(line for line in f if not line.strip().startswith("#")):
                email = row.get("email", "").strip()
                if email:
                    seed_contacts.append(ContactRecord(
                        contact_id=9000 + len(seed_contacts),
                        first_name="Seed",
                        last_name=row.get("label", "Test"),
                        email=email,
                        sequence_id="theater_outreach_v1",
                        step_number=0,
                    ))
        eligible = seed_contacts
        logger.info("Seed contacts loaded", extra={"count": len(eligible)})

    sent = 0
    skipped = 0
    errors = 0

    for contact in eligible:
        venue = get_venue(venues, contact.company_id) or VenueRecord(lead_id=0, company="Unknown Venue")
        gig = get_gig(crm.gig_leads, contact.contact_id)
        step = (contact.step_number or 0) + 1

        context = build_context(contact, venue, gig)
        context.update({
            "sender_name": sender_name,
            "physical_address": physical_address,
            "unsubscribe_url": unsubscribe_url,
            "reply_to_email": os.environ.get("ZOHO_REPLY_TO", ""),
        })

        # Check for template errors
        token_errors = builder.check_tokens(step, context)
        if token_errors:
            logger.warning("Template token error", extra={"email": contact.email, "step": step, "errors": token_errors})
            errors += 1
            continue

        subject, body = builder.render(step, context)

        # CAN-SPAM pre-check
        is_ok, warnings = checker.validate(subject, body)
        if not is_ok:
            logger.error("Compliance failure — skipping", extra={"email": contact.email, "warnings": warnings})
            skipped += 1
            continue

        if args.dry_run:
            print(f"\n[DRY RUN] Step {step} → {contact.email}")
            print(f"  Subject: {subject}")
            print(f"  Body preview: {body[:80]}...")
            sent += 1
            continue

        # Send
        try:
            result = guard.send_step(
                contact=contact,
                venue=venue,
                step=step,
                subject=subject,
                body_text=body,
                lead_id=venue.lead_id,
            )
            if result.success:
                # Update CRM in-memory
                contact.step_number = step
                contact.last_updated = datetime.now(timezone.utc).isoformat()
                if gig:
                    gig.send_time = contact.last_updated
                sent += 1
                logger.info("Sent", extra={"email": contact.email, "step": step})
            else:
                logger.warning("Send failed", extra={"email": contact.email, "error": result.error})
                if result.error == "suppressed":
                    skipped += 1
                else:
                    errors += 1
        except DailyLimitReached:
            logger.info("Daily limit reached — stopping run")
            break
        except ComplianceError as e:
            logger.error("Compliance error", extra={"error": str(e)})
            skipped += 1

    # Save updated CRM
    if not args.dry_run and (sent > 0):
        logger.info("Saving updated CRM", extra={"path": crm_path})
        exporter = CRMExporter(crm_path)
        exporter.write(ExportPayload(
            venues=venues,
            contacts=contacts,
            gig_leads=crm.gig_leads,
            calls=crm.calls,
            notes=crm.notes,
        ))

    print(f"\nRun complete: {sent} sent, {skipped} skipped, {errors} errors")


def main() -> None:
    parser = argparse.ArgumentParser(description="Princess Peigh Adventures — Outbound Sequence Runner")
    parser.add_argument("--review-mode", action="store_true", help="Render all templates with sample data; print to stdout; no sends or CRM writes")
    parser.add_argument("--dry-run", action="store_true", help="Render and validate; do not send")
    parser.add_argument("--test-mode", action="store_true", help="Send to seed list only")
    parser.add_argument("--live", action="store_true", help="Send to real contacts")
    parser.add_argument("--stats", action="store_true", help="Show stats and exit")
    parser.add_argument("--config", default="config/settings.yaml", help="Path to settings.yaml")
    parser.add_argument("--crm", default=None, help="Path to leads.xlsx (overrides config)")
    parser.add_argument("--seed-file", default="data/seed_lists/seed_list.csv")
    parser.add_argument("--step", type=int, default=None, help="Run specific step only (1-4)")
    args = parser.parse_args()

    if not args.review_mode and not args.dry_run and not args.test_mode and not args.live and not args.stats:
        print("ERROR: Specify one of --dry-run, --test-mode, --live, or --stats")
        parser.print_help()
        sys.exit(1)

    config = load_config(args.config)
    run(args, config)


if __name__ == "__main__":
    main()
