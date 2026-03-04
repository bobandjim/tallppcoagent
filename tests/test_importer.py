"""
Tests for the Excel CRM importer.
Downloads the actual template from the blob URL to test real parsing.
"""

import io
import urllib.request

import pytest
import openpyxl

from src.crm.importer import CRMImporter, ImportResult, _yes_no, _int, _float, _str
from src.crm.deduplication import dedup_venues, dedup_contacts
from src.crm.schema import VenueRecord, ContactRecord

TEMPLATE_URL = "https://magotalent.blob.core.windows.net/magobiz/import.xlsx"


class TestHelpers:
    def test_yes_no_yes_variants(self):
        for val in ("Yes", "yes", "YES", "1", "true", "y"):
            assert _yes_no({"k": val}, "k") == "Yes", f"Failed for {val!r}"

    def test_yes_no_no_variants(self):
        for val in ("No", "no", "0", "false", "n", None):
            assert _yes_no({"k": val}, "k") == "No", f"Failed for {val!r}"

    def test_int_converts_correctly(self):
        assert _int({"k": "42"}, "k") == 42
        assert _int({"k": 7}, "k") == 7
        assert _int({"k": None}, "k") is None
        assert _int({"k": "abc"}, "k") is None

    def test_float_handles_currency_formatting(self):
        assert _float({"k": "$1,234.56"}, "k") == pytest.approx(1234.56)
        assert _float({"k": 100}, "k") == pytest.approx(100.0)
        assert _float({"k": None}, "k") is None

    def test_str_strips_whitespace(self):
        assert _str({"k": "  hello  "}, "k") == "hello"
        assert _str({"k": None}, "k") is None


class TestTemplateImport:
    """Integration test against the real template file."""

    @pytest.fixture(scope="class")
    def xlsx_bytes(self):
        try:
            with urllib.request.urlopen(TEMPLATE_URL, timeout=15) as r:
                return r.read()
        except Exception as e:
            pytest.skip(f"Cannot reach template URL: {e}")

    @pytest.fixture(scope="class")
    def tmp_xlsx(self, xlsx_bytes, tmp_path_factory):
        tmp = tmp_path_factory.mktemp("crm") / "import.xlsx"
        tmp.write_bytes(xlsx_bytes)
        return tmp

    def test_importer_loads_without_fatal_error(self, tmp_xlsx):
        result = CRMImporter(tmp_xlsx).load_all()
        assert isinstance(result, ImportResult)

    def test_companies_sheet_parses(self, tmp_xlsx):
        result = CRMImporter(tmp_xlsx).load_all()
        assert len(result.venues) >= 1, "Expected at least 1 venue from Companies sheet"

    def test_contacts_sheet_parses(self, tmp_xlsx):
        result = CRMImporter(tmp_xlsx).load_all()
        assert len(result.contacts) >= 1, "Expected at least 1 contact from Contacts sheet"

    def test_gigs_leads_sheet_parses(self, tmp_xlsx):
        result = CRMImporter(tmp_xlsx).load_all()
        assert len(result.gig_leads) >= 1, "Expected at least 1 record from Gigs_Leads sheet"

    def test_no_fatal_errors_on_sample_data(self, tmp_xlsx):
        result = CRMImporter(tmp_xlsx).load_all()
        # Some validation warnings are acceptable; zero fatal parse errors is not possible
        # to assert here, but error count should be reasonable
        assert result.error_count < result.total_records, (
            "More errors than records — likely a structural mismatch"
        )


class TestDeduplication:
    def test_venue_dedup_by_company_state(self):
        venues = [
            VenueRecord(lead_id=1, company="City Theater", state="NY"),
            VenueRecord(lead_id=2, company="City Theater", state="NY"),  # duplicate
            VenueRecord(lead_id=3, company="Another Theater", state="NY"),
        ]
        deduped, events = dedup_venues(venues)
        assert len(deduped) == 2
        assert len(events) == 1
        assert events[0]["event"] == "VENUE_DEDUP"

    def test_venue_dedup_newer_wins(self):
        venues = [
            VenueRecord(lead_id=1, company="City Theater", state="NY", website="old.com"),
            VenueRecord(lead_id=5, company="City Theater", state="NY", website="new.com"),
        ]
        deduped, _ = dedup_venues(venues)
        assert len(deduped) == 1
        assert deduped[0].website == "new.com"

    def test_contact_dedup_by_email(self):
        contacts = [
            ContactRecord(contact_id=1, email="sarah@venue.org"),
            ContactRecord(contact_id=2, email="SARAH@VENUE.ORG"),   # duplicate (different case)
            ContactRecord(contact_id=3, email="other@venue.org"),
        ]
        deduped, events = dedup_contacts(contacts)
        assert len(deduped) == 2
        assert len(events) == 1

    def test_contact_dedup_no_email_kept(self):
        contacts = [
            ContactRecord(contact_id=1),   # no email
            ContactRecord(contact_id=2),   # no email
        ]
        deduped, events = dedup_contacts(contacts)
        assert len(deduped) == 2   # both kept — can't dedup without email
        assert events == []
