"""Tests for CRM Pydantic schema validation."""

import pytest
from pydantic import ValidationError

from src.crm.schema import (
    ContactRecord,
    GigLeadRecord,
    LeadRowFlat,
    NoteRecord,
    VenueRecord,
)


class TestVenueRecord:
    def test_basic_creation(self):
        v = VenueRecord(lead_id=1, company="Test Theater")
        assert v.company == "Test Theater"
        assert v.lead_id == 1

    def test_state_normalized_to_uppercase(self):
        v = VenueRecord(lead_id=1, company="X", state="ny")
        assert v.state == "NY"

    def test_company_whitespace_stripped(self):
        v = VenueRecord(lead_id=1, company="  Riverside Theater  ")
        assert v.company == "Riverside Theater"

    def test_dedup_key_is_lowercase_composite(self):
        v = VenueRecord(lead_id=1, company="City Theater", state="NY")
        assert v.dedup_key() == "city theater|ny"

    def test_dedup_key_no_state(self):
        v = VenueRecord(lead_id=1, company="Arts Center")
        assert v.dedup_key() == "arts center|"

    def test_optional_fields_default_none(self):
        v = VenueRecord(lead_id=1, company="X")
        assert v.website is None
        assert v.city is None
        assert v.seating_capacity_tier is None


class TestContactRecord:
    def test_basic_creation(self):
        c = ContactRecord(contact_id=1, first_name="Sarah", last_name="Jones", email="sarah@venue.org")
        assert c.full_name == "Sarah Jones"

    def test_email_normalized_to_lowercase(self):
        c = ContactRecord(contact_id=1, email="SARAH@Venue.ORG")
        assert c.email == "sarah@venue.org"

    def test_dedup_key_is_email(self):
        c = ContactRecord(contact_id=1, email="Test@Example.com")
        assert c.dedup_key() == "test@example.com"

    def test_dedup_key_no_email_is_empty(self):
        c = ContactRecord(contact_id=1)
        assert c.dedup_key() == ""

    def test_is_suppressed_when_opt_out_yes(self):
        c = ContactRecord(contact_id=1, email="x@y.com", email_opt_out="Yes")
        assert c.is_suppressed() is True

    def test_is_not_suppressed_by_default(self):
        c = ContactRecord(contact_id=1, email="x@y.com")
        assert c.is_suppressed() is False

    def test_full_name_first_only(self):
        c = ContactRecord(contact_id=1, first_name="Mary")
        assert c.full_name == "Mary"

    def test_full_name_empty_when_no_name(self):
        c = ContactRecord(contact_id=1)
        assert c.full_name == ""


class TestGigLeadRecord:
    def test_basic_creation(self):
        g = GigLeadRecord(gig_lead_id=1, status="Lead", venue_name="City Theater")
        assert g.venue_name == "City Theater"

    def test_is_booked_when_status_gig(self):
        g = GigLeadRecord(gig_lead_id=1, status="Gig")
        assert g.is_booked is True

    def test_is_booked_when_show_booked_yes(self):
        g = GigLeadRecord(gig_lead_id=1, status="Lead", show_booked="Yes")
        assert g.is_booked is True

    def test_not_booked_when_lead(self):
        g = GigLeadRecord(gig_lead_id=1, status="Lead")
        assert g.is_booked is False

    def test_meeting_booked_defaults_no(self):
        g = GigLeadRecord(gig_lead_id=1)
        assert g.meeting_booked == "No"


class TestLeadRowFlat:
    def test_from_records_builds_correctly(self):
        venue = VenueRecord(
            lead_id=10,
            company="Riverside Arts Center",
            city="Albany",
            state="NY",
            segment="Performing Arts Center",
        )
        contact = ContactRecord(
            contact_id=20,
            first_name="Sarah",
            last_name="Director",
            company_id=10,
            email="sarah@riverside.org",
            title="Programming Director",
            sequence_id="theater_outreach_v1",
            step_number=1,
        )
        gig = GigLeadRecord(
            gig_lead_id=30,
            company_id=10,
            contact_id=20,
            status="Lead",
            venue_name="Riverside Arts Center",
            projected_fee=2500.0,
        )

        flat = LeadRowFlat.from_records(venue, contact, gig)
        assert flat.lead_id == 30
        assert flat.company == "Riverside Arts Center"
        assert flat.contact_name == "Sarah Director"
        assert flat.email == "sarah@riverside.org"
        assert flat.city == "Albany"
        assert flat.state == "NY"
        assert flat.segment == "Performing Arts Center"
        assert flat.sequence_id == "theater_outreach_v1"
        assert flat.step_number == 1
        assert flat.projected_fee == 2500.0
        assert flat.show_booked == "No"
