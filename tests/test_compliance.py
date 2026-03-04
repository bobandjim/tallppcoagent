"""Tests for compliance utilities — CAN-SPAM checker and suppression list."""

import csv
import pytest
from pathlib import Path

from src.utils.compliance import CANSPAMChecker, SuppressionList


class TestSuppressionList:
    @pytest.fixture
    def suppression_csv(self, tmp_path) -> Path:
        p = tmp_path / "suppression.csv"
        p.write_text("email,reason,suppressed_at\n")
        return p

    def test_empty_list_not_suppressed(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        assert sl.is_suppressed("anyone@example.com") is False

    def test_add_then_check(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        sl.add("test@theater.org", "OPT_OUT")
        assert sl.is_suppressed("test@theater.org") is True

    def test_case_insensitive_check(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        sl.add("director@venue.org", "HARD_BOUNCE")
        assert sl.is_suppressed("DIRECTOR@VENUE.ORG") is True

    def test_add_invalid_reason_raises(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        with pytest.raises(ValueError, match="Invalid suppression reason"):
            sl.add("x@y.com", "INVALID")

    def test_persists_to_csv(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        sl.add("sarah@venue.org", "OPT_OUT")
        # Re-load from disk
        sl2 = SuppressionList(suppression_csv)
        assert sl2.is_suppressed("sarah@venue.org") is True

    def test_count(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        sl.add("a@b.com", "MANUAL")
        sl.add("c@d.com", "MANUAL")
        assert sl.count() == 2

    def test_all_suppressed_list(self, suppression_csv):
        sl = SuppressionList(suppression_csv)
        sl.add("a@b.com", "OPT_OUT")
        sl.add("c@d.com", "HARD_BOUNCE")
        assert set(sl.all_suppressed()) == {"a@b.com", "c@d.com"}


class TestCANSPAMChecker:
    @pytest.fixture
    def checker(self):
        return CANSPAMChecker(
            physical_address="123 Theater Lane, Albany, NY 12201",
            unsubscribe_url="https://example.com/unsubscribe",
            sender_name="Zachary Gartrell",
        )

    def test_valid_email_passes(self, checker):
        body = (
            "Hello,\n\nGreat show for your venue.\n\n"
            "Zachary Gartrell\n\n"
            "123 Theater Lane, Albany, NY 12201\n"
            "https://example.com/unsubscribe"
        )
        ok, warnings = checker.validate("A show for your community", body)
        assert ok is True
        assert warnings == []

    def test_missing_physical_address_flagged(self, checker):
        body = "Hello.\n\nhttps://example.com/unsubscribe\nZachary Gartrell"
        ok, warnings = checker.validate("Good subject", body)
        assert ok is False
        assert any("Physical mailing address" in w for w in warnings)

    def test_missing_unsubscribe_flagged(self, checker):
        body = "Hello.\n\n123 Theater Lane, Albany, NY 12201\nZachary Gartrell"
        ok, warnings = checker.validate("Good subject", body)
        assert ok is False
        assert any("Unsubscribe URL" in w for w in warnings)

    def test_spam_trigger_in_subject_flagged(self, checker):
        body = (
            "Hello.\n\nZachary Gartrell\n"
            "123 Theater Lane, Albany, NY 12201\n"
            "https://example.com/unsubscribe"
        )
        ok, warnings = checker.validate("FREE shows for your venue!!!", body)
        assert ok is False
        assert any("spam-trigger" in w.lower() for w in warnings)

    def test_empty_subject_flagged(self, checker):
        body = (
            "Zachary Gartrell\n"
            "123 Theater Lane, Albany, NY 12201\n"
            "https://example.com/unsubscribe"
        )
        ok, warnings = checker.validate("", body)
        assert ok is False
        assert any("empty" in w.lower() for w in warnings)


class TestAuditLog:
    def test_audit_log_records_events(self, tmp_path):
        from src.utils.audit import AuditLog
        audit = AuditLog(tmp_path / "audit.db")
        trail_id = audit.log("LEAD_CREATED", lead_id=1, payload={"company": "City Theater"})
        assert trail_id is not None
        events = audit.get_events(lead_id=1)
        assert len(events) == 1
        assert events[0]["event_type"] == "LEAD_CREATED"

    def test_audit_log_rejects_unknown_event(self, tmp_path):
        from src.utils.audit import AuditLog
        audit = AuditLog(tmp_path / "audit.db")
        with pytest.raises(ValueError, match="Unknown event type"):
            audit.log("FAKE_EVENT", lead_id=1)

    def test_full_event_sequence(self, tmp_path):
        from src.utils.audit import AuditLog
        audit = AuditLog(tmp_path / "audit.db")
        trail = audit.log("LEAD_CREATED", lead_id=5)
        audit.log("EMAIL_SENT", lead_id=5, audit_trail_id=trail, payload={"step": 1})
        audit.log("OPT_OUT", lead_id=5, audit_trail_id=trail)
        assert audit.event_count() == 3
        events = audit.get_events(lead_id=5)
        types = [e["event_type"] for e in events]
        assert "LEAD_CREATED" in types
        assert "EMAIL_SENT" in types
        assert "OPT_OUT" in types


class TestSequenceBuilder:
    @pytest.fixture
    def builder(self):
        from src.email.sequence_builder import SequenceBuilder
        return SequenceBuilder("templates/email")

    def test_step_1_renders(self, builder):
        subject, body = builder.render(1, {
            "contact_name": "Sarah",
            "venue_name": "City Theater",
            "city": "Albany",
            "state": "NY",
            "seating_capacity_tier": "Mid",
            "mission_excerpt": None,
            "next_season": "Spring 2027",
            "physical_address": "123 Main St",
            "unsubscribe_url": "https://example.com/unsub",
            "reply_to_email": "z@example.com",
        })
        assert "Princess Peigh" in body or "Albany" in subject or "Albany" in body
        assert subject != ""

    def test_all_4_steps_render(self, builder):
        ctx = {
            "contact_name": "Sarah",
            "venue_name": "City Theater",
            "city": "Albany",
            "state": "NY",
            "seating_capacity_tier": "Small",
            "mission_excerpt": None,
            "next_season": "Fall 2026",
            "physical_address": "123 Main St",
            "unsubscribe_url": "https://example.com/unsub",
            "reply_to_email": "z@example.com",
        }
        results = builder.render_all(ctx)
        assert len(results) == 4
        for r in results:
            assert r["subject"]
            assert r["body"]

    def test_invalid_step_raises(self, builder):
        with pytest.raises(ValueError):
            builder.render(99, {})

    def test_unsubscribe_url_present_in_all_steps(self, builder):
        ctx = {
            "contact_name": "Sarah",
            "venue_name": "City Theater",
            "city": "Albany",
            "state": "NY",
            "seating_capacity_tier": None,
            "mission_excerpt": None,
            "next_season": "Fall 2026",
            "physical_address": "123 Main St",
            "unsubscribe_url": "https://example.com/unsub",
            "reply_to_email": "z@example.com",
        }
        for step in range(1, 5):
            _, body = builder.render(step, ctx)
            assert "https://example.com/unsub" in body, f"Step {step} missing unsubscribe URL"
