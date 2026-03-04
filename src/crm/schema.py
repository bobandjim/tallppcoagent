"""
CRM schema definitions — maps directly to the 6-sheet Excel import format.

Sheet structure (from import.xlsx):
  Companies   → VenueRecord      (venues/organizations)
  Contacts    → ContactRecord    (people at venues)
  Gigs_Leads  → GigLeadRecord    (leads and booked shows)
  Calls       → CallRecord       (call log)
  Notes       → NoteRecord       (notes log)
  Lookups     → reference values (not modeled as Pydantic)

All 27 required outbound tracking fields are distributed across these models.
Custom1–CustomN columns in the Excel are repurposed for outbound tracking fields.
"""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Lookup values (from Lookups sheet)
# ---------------------------------------------------------------------------

YES_NO = Literal["Yes", "No"]
CALL_STATUS = Literal["Held", "Planned", "Not Held"]
GIG_STATUS = Literal["Gig", "Lead"]

REPLY_CATEGORIES = Literal[
    "Interested",
    "Budget Question",
    "Programming Window Question",
    "Referral",
    "Not a Fit",
    "Opt-Out",
    "Out of Office",
    "Bounce",
    "",
]

OUTCOMES = Literal[
    "In Progress",
    "Interested",
    "Not a Fit",
    "Booked",
    "Lost",
    "Bounced",
    "Suppressed",
    "",
]

SEGMENTS = Literal[
    "Community Theater",
    "Performing Arts Center",
    "Municipal Cultural Venue",
    "Library",
    "Arts Nonprofit",
    "Other",
    "Agent",
    "Organization",
]

SOURCES = Literal[
    "Manual Research",
    "Referral",
    "Website",
    "Cold Call",
    "Social Media",
    "Existing Customer",
    "Conference",
    "Directory",
    "Other",
]


# ---------------------------------------------------------------------------
# Companies sheet → VenueRecord
# Outbound tracking fields: segment, city, state, website, phone
# ---------------------------------------------------------------------------

class VenueRecord(BaseModel):
    """Maps to Companies sheet. Represents a venue/organization."""

    lead_id: int = Field(..., description="UniqueId column — primary key")
    company: str = Field(..., description="Name column — venue/organization name")
    website: Optional[str] = Field(None, description="Website column")
    segment: Optional[str] = Field(None, description="Record Type column — venue category")
    phone: Optional[str] = Field(None, description="Phone column")
    city: Optional[str] = Field(None, description="Billing City column")
    state: Optional[str] = Field(None, description="Billing State column — 2-char code")
    notes: Optional[str] = Field(None, description="Notes column")

    # Derived/enrichment fields (stored in Custom1–Custom4 in Excel)
    seating_capacity_tier: Optional[str] = Field(
        None, description="Custom1 — Small (100-199) | Mid (200-299) | Large (300-400)"
    )
    mission_excerpt: Optional[str] = Field(None, description="Custom2 — scraped mission snippet")
    programming_focus: Optional[str] = Field(None, description="Custom3 — e.g. Family, Education")
    venue_name: Optional[str] = Field(None, description="Custom4 — display name if different from company")

    @field_validator("state")
    @classmethod
    def normalize_state(cls, v: Optional[str]) -> Optional[str]:
        return v.upper().strip() if v else v

    @field_validator("company")
    @classmethod
    def normalize_company(cls, v: str) -> str:
        return v.strip()

    def dedup_key(self) -> str:
        """Composite dedup key: normalized company name + state."""
        return f"{self.company.lower().strip()}|{(self.state or '').lower()}"


# ---------------------------------------------------------------------------
# Contacts sheet → ContactRecord
# Outbound tracking fields: sequence_id, step_number, open, click, reply,
#   reply_category, last_updated, audit_trail_id
# ---------------------------------------------------------------------------

class ContactRecord(BaseModel):
    """Maps to Contacts sheet. Represents a person at a venue."""

    contact_id: int = Field(..., description="UniqueId column — primary key")
    first_name: Optional[str] = Field(None, description="First Name column")
    last_name: Optional[str] = Field(None, description="Last Name column")
    company_id: Optional[int] = Field(None, description="Company UniqueId — FK to VenueRecord")
    source: Optional[str] = Field(None, description="Lead Source column")
    phone: Optional[str] = Field(None, description="Work Phone column")
    email: Optional[str] = Field(None, description="Email column")
    email_opt_out: YES_NO = Field("No", description="Email Opt Out column")
    title: Optional[str] = Field(None, description="Title column")

    # Outbound sequence tracking (stored in Custom1–Custom8 in Excel)
    sequence_id: Optional[str] = Field(None, description="Custom1 — e.g. theater_outreach_v1")
    step_number: Optional[int] = Field(None, description="Custom2 — current step 1-4")
    email_open: YES_NO = Field("No", description="Custom3 — opened most recent email")
    email_click: YES_NO = Field("No", description="Custom4 — clicked link in email")
    email_reply: YES_NO = Field("No", description="Custom5 — replied to sequence")
    reply_category: Optional[str] = Field(None, description="Custom6 — reply classification")
    last_updated: Optional[str] = Field(None, description="Custom7 — ISO 8601 timestamp")
    audit_trail_id: Optional[str] = Field(None, description="Custom8 — UUID4 for audit linkage")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: Optional[str]) -> Optional[str]:
        return v.lower().strip() if v else v

    @property
    def full_name(self) -> str:
        parts = [p for p in [self.first_name, self.last_name] if p]
        return " ".join(parts)

    def dedup_key(self) -> str:
        """Composite dedup key: normalized email."""
        return (self.email or "").lower().strip()

    def is_suppressed(self) -> bool:
        return self.email_opt_out == "Yes"


# ---------------------------------------------------------------------------
# Gigs_Leads sheet → GigLeadRecord
# Outbound tracking fields: meeting_booked, show_booked, projected_fee,
#   final_fee, outcome, send_time
# ---------------------------------------------------------------------------

class GigLeadRecord(BaseModel):
    """Maps to Gigs_Leads sheet. Tracks both pipeline leads and booked shows."""

    gig_lead_id: int = Field(..., description="UniqueId column — primary key")
    name: Optional[str] = Field(None, description="Name column — descriptive label")
    status: Optional[str] = Field(None, description="Status column — 'Gig' or 'Lead'")
    company_id: Optional[int] = Field(None, description="Company UniqueId — FK to VenueRecord")
    contact_id: Optional[int] = Field(None, description="Primary Contact UniqueId — FK to ContactRecord")
    source: Optional[str] = Field(None, description="Lead Source column")
    show_date: Optional[datetime] = Field(None, description="Show Date column")
    venue_name: Optional[str] = Field(None, description="Venue Name column")
    final_fee: Optional[float] = Field(None, description="Fee column — agreed final fee (USD)")
    projected_fee: Optional[float] = Field(None, description="Quote1 column — initial estimate (USD)")
    deposit: Optional[float] = Field(None, description="Deposit column")
    contract_sent: Optional[str] = Field(None, description="Contract sent column")
    contract_received: Optional[str] = Field(None, description="Contract Received column")

    # Outbound tracking (stored in Custom1–Custom4 in Gigs_Leads)
    outcome: Optional[str] = Field(None, description="Custom1 — outcome classification")
    meeting_booked: YES_NO = Field("No", description="Custom2 — call/meeting scheduled")
    show_booked: YES_NO = Field("No", description="Custom3 — show confirmed and contracted")
    send_time: Optional[str] = Field(None, description="Custom4 — ISO 8601 timestamp of last email send")

    @property
    def is_booked(self) -> bool:
        return self.status == "Gig" or self.show_booked == "Yes"


# ---------------------------------------------------------------------------
# Calls sheet → CallRecord
# ---------------------------------------------------------------------------

class CallRecord(BaseModel):
    """Maps to Calls sheet. Represents a logged call."""

    call_id: int = Field(..., description="UniqueId column")
    subject: Optional[str] = Field(None, description="Subject column")
    call_datetime: Optional[datetime] = Field(None, description="CallDateTime column")
    status: Optional[str] = Field(None, description="Call Status column — Held | Planned | Not Held")
    notes: Optional[str] = Field(None, description="Call Notes column")
    gig_id: Optional[int] = Field(None, description="Related Gig — FK to GigLeadRecord")
    contact_id: Optional[int] = Field(None, description="Related Contact — FK to ContactRecord")
    company_id: Optional[int] = Field(None, description="Related Company — FK to VenueRecord")


# ---------------------------------------------------------------------------
# Notes sheet → NoteRecord
# ---------------------------------------------------------------------------

class NoteRecord(BaseModel):
    """Maps to Notes sheet. Represents a general note."""

    note_id: int = Field(..., description="UniqueId column")
    subject: Optional[str] = Field(None, description="Subject column")
    note_date: Optional[date] = Field(None, description="Date column")
    notes: Optional[str] = Field(None, description="Notes column")
    gig_id: Optional[int] = Field(None, description="Related Gig — FK to GigLeadRecord")
    contact_id: Optional[int] = Field(None, description="Related Contact — FK to ContactRecord")
    company_id: Optional[int] = Field(None, description="Related Company — FK to VenueRecord")


# ---------------------------------------------------------------------------
# Flat view for reporting (joins all sheets into one row)
# ---------------------------------------------------------------------------

class LeadRowFlat(BaseModel):
    """
    Flat denormalized view of one outbound lead — all 27 required CRM fields.
    Used for reporting, dashboards, and audit views. Not directly imported/exported
    to Excel; synthesized by joining VenueRecord + ContactRecord + GigLeadRecord.
    """

    lead_id: int
    company: Optional[str] = None
    venue_name: Optional[str] = None
    contact_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    source: Optional[str] = None
    segment: Optional[str] = None
    sequence_id: Optional[str] = None
    step_number: Optional[int] = None
    send_time: Optional[str] = None
    open: YES_NO = "No"
    click: YES_NO = "No"
    reply: YES_NO = "No"
    reply_category: Optional[str] = None
    meeting_booked: YES_NO = "No"
    show_booked: YES_NO = "No"
    projected_fee: Optional[float] = None
    final_fee: Optional[float] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    last_updated: Optional[str] = None
    audit_trail_id: Optional[str] = None

    @classmethod
    def from_records(
        cls,
        venue: VenueRecord,
        contact: ContactRecord,
        gig: GigLeadRecord,
    ) -> "LeadRowFlat":
        return cls(
            lead_id=gig.gig_lead_id,
            company=venue.company,
            venue_name=gig.venue_name or venue.venue_name or venue.company,
            contact_name=contact.full_name,
            title=contact.title,
            email=contact.email,
            phone=contact.phone or venue.phone,
            website=venue.website,
            city=venue.city,
            state=venue.state,
            source=contact.source or gig.source,
            segment=venue.segment,
            sequence_id=contact.sequence_id,
            step_number=contact.step_number,
            send_time=gig.send_time,
            open=contact.email_open,
            click=contact.email_click,
            reply=contact.email_reply,
            reply_category=contact.reply_category,
            meeting_booked=gig.meeting_booked,
            show_booked=gig.show_booked,
            projected_fee=gig.projected_fee,
            final_fee=gig.final_fee,
            outcome=gig.outcome,
            notes=venue.notes,
            last_updated=contact.last_updated,
            audit_trail_id=contact.audit_trail_id,
        )
