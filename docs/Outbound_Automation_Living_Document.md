# Outbound Automation Living Document
## Tall People Performing Company — Touring Show Booking System

**Status:** Active | **Wave:** 1 — Initial Build (Princess Peigh Adventures)
**Last Updated:** 2026-03-04
**Project:** Princess Peigh's Sword Fighting Tea Party — Regional Theater Outreach

---

> **About this document:** This is a living document designed for reuse on any future booking automation project for any touring show, entertainment act, or performing arts organization. Everything here is written to be directly applied to a new project with minimal adaptation. Update the "Lessons Learned" section after each deployment wave.

---

## 1. System Architecture Overview

The outbound booking automation system is built on a 5-layer stack:

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: LEAD RESEARCH & SOURCING                      │
│  Manual venue list building + qualification rubric      │
│  → Outputs: venue_list.csv with enrichment fields       │
├─────────────────────────────────────────────────────────┤
│  LAYER 2: CRM (Excel/CSV)                               │
│  6-sheet relational Excel workbook (import.xlsx)        │
│  Companies | Contacts | Gigs_Leads | Calls | Notes      │
│  → Pydantic-validated import/export via openpyxl        │
├─────────────────────────────────────────────────────────┤
│  LAYER 3: COMPLIANCE & SUPPRESSION                      │
│  CAN-SPAM checker | Suppression list manager            │
│  Opt-out handling | Bounce classification               │
│  → Every send gated through CANSPAMChecker + SuppressionList │
├─────────────────────────────────────────────────────────┤
│  LAYER 4: EMAIL TEMPLATES & PERSONALIZATION             │
│  4-step Jinja2 sequence (Day 0/5/9/14)                  │
│  Tokens: venue_name, city, mission_excerpt, capacity    │
│  → Human review gate (--review-mode) before any sends  │
├─────────────────────────────────────────────────────────┤
│  LAYER 5: DELIVERY & AUDIT                              │
│  Zoho Mail SMTP | Throttle guard | Daily cap            │
│  SQLite audit trail (append-only, 8 event types)        │
│  → Every action logged with audit_trail_id              │
└─────────────────────────────────────────────────────────┘
```

### Why These Technology Choices

**Excel/CSV as CRM (not SaaS):**
- No monthly subscription cost — critical for touring shows with variable revenue
- Portable — travels with the company, no vendor lock-in
- Import format is a real industry-standard template (6-sheet relational structure)
- Can be opened and edited by non-technical team members
- Python (openpyxl/pandas) reads and writes it reliably

**Zoho Mail for sending:**
- Low cost for regional touring operations
- STARTTLS SMTP available (port 587) — standard and secure
- Built-in domain warming tools and SPF/DKIM/DMARC configuration
- Regional sending volumes (100/day max) fit within free/starter tiers

**Python + Pydantic + Jinja2:**
- Type-safe data models that catch import errors before they corrupt the CRM
- Jinja2 is industry standard for email templating with token injection
- No framework overhead — all logic is transparent and auditable

**SQLite for audit trail:**
- Zero infrastructure requirements (file-based)
- Append-only enforcement prevents audit log tampering
- Queryable with standard SQL for reporting

---

## 2. Reusable Module Inventory

For each module: path, purpose, key interface, adaptation notes.

---

### `src/crm/schema.py`
**Purpose:** Pydantic v2 models for all 6 sheets of the Excel CRM template.

**Key classes:**
- `VenueRecord` — Companies sheet. Fields: lead_id, company, website, segment, phone, city, state, notes, seating_capacity_tier, mission_excerpt, programming_focus, venue_name
- `ContactRecord` — Contacts sheet. Fields: contact_id, first_name, last_name, company_id, email, phone, title, sequence_id, step_number, email_open, email_click, email_reply, reply_category, audit_trail_id
- `GigLeadRecord` — Gigs_Leads sheet. Fields: gig_lead_id, name, status, company_id, contact_id, venue_name, fee, projected_fee, outcome, meeting_booked, show_booked, send_time
- `CallRecord` — Calls sheet. Log of outbound call attempts.
- `NoteRecord` — Notes sheet. Free-form notes attached to companies, contacts, or gigs.
- `LeadRowFlat` — Denormalized 27-field view joining all sheets for reporting.

**Adapt for new project:**
- Rename `seating_capacity_tier`, `mission_excerpt`, `programming_focus` in `VenueRecord` to fields relevant to your new venue type
- Update `segment` field values in the qualification criteria doc
- The 6-sheet structure is fixed by the Excel template — do not add new sheets

---

### `src/crm/importer.py`
**Purpose:** Load and validate the Excel workbook → return typed Pydantic records.

**Key interface:**
```python
from src.crm.importer import CRMImporter
importer = CRMImporter("data/crm/leads.xlsx")
result = importer.load_all()
# result.venues: List[VenueRecord]
# result.contacts: List[ContactRecord]
# result.gig_leads: List[GigLeadRecord]
# result.errors: List[dict]  # Non-fatal validation errors
```

**Adapt for new project:**
- `column_map` in `config/settings.yaml` drives all field-to-column mapping
- If the Excel template's column names change, update the column_map only — no code changes needed
- The `_safe()`, `_str()`, `_int()`, `_float()`, `_yes_no()` helpers handle messy data gracefully

---

### `src/crm/exporter.py`
**Purpose:** Write updated Pydantic records back to Excel, preserving the exact column structure.

**Key interface:**
```python
from src.crm.exporter import CRMExporter, ExportPayload
exporter = CRMExporter("data/crm/leads.xlsx")
exporter.write(ExportPayload(venues=..., contacts=..., gig_leads=..., calls=..., notes=...))
```

**Adapt for new project:** No changes needed unless column headers change in the Excel template.

---

### `src/crm/deduplication.py`
**Purpose:** Remove duplicate venues and contacts using normalized composite keys.

**Dedup rules:**
- Venues: key = `(normalized_company_name, normalized_state)` — case-insensitive, stripped
- Contacts: key = `normalized_email` — lowercase
- Merge strategy: highest UniqueId (most recently imported) wins on conflicts

**Key interface:**
```python
from src.crm.deduplication import dedup_venues, dedup_contacts
unique_venues, dedup_events = dedup_venues(venues)
unique_contacts, dedup_events = dedup_contacts(contacts)
```

**Adapt for new project:** The dedup keys are appropriate for any venue-based CRM. No changes needed.

---

### `src/utils/audit.py`
**Purpose:** Append-only SQLite audit trail. Every system action leaves a record.

**Supported event types:**
`LEAD_CREATED`, `LEAD_UPDATED`, `EMAIL_SENT`, `REPLY_RECEIVED`, `OPT_OUT`, `BOUNCE`, `MEETING_BOOKED`, `SHOW_BOOKED`, `DEDUP`, `SUPPRESSED`, `IMPORT`

**Key interface:**
```python
from src.utils.audit import AuditLog
audit = AuditLog("data/audit.db")
audit_id = audit.log("EMAIL_SENT", lead_id=123, payload={"email": "...", "step": 1})
events = audit.get_events(lead_id=123)
count = audit.event_count("EMAIL_SENT")
```

**Adapt for new project:** Drop-in reusable. Update `audit_db` path in `settings.yaml`. The event types are fixed.

---

### `src/utils/logger.py`
**Purpose:** Structured JSON logging to stdout. Every log line is a parseable JSON object.

**Key interface:**
```python
from src.utils.logger import get_logger
logger = get_logger("my_module")
logger.info("Action taken", extra={"key": "value"})
```

**Adapt for new project:** Drop-in reusable with no changes.

---

### `src/utils/compliance.py`
**Purpose:** CAN-SPAM validation and suppression list management.

**Key classes:**
- `SuppressionList` — reads/writes `config/suppression_list.csv`. Methods: `is_suppressed(email)`, `add(email, reason)`, `count()`
- `CANSPAMChecker` — validates email subject + body. Checks: physical address present, unsubscribe link present, sender name present, subject not empty, no spam trigger phrases in subject.

**Key interface:**
```python
from src.utils.compliance import CANSPAMChecker, SuppressionList
suppression = SuppressionList("config/suppression_list.csv")
checker = CANSPAMChecker(physical_address="...", unsubscribe_url="...", sender_name="...")
is_ok, warnings = checker.validate(subject, body_text)
```

**Adapt for new project:**
- Update `physical_address`, `sender_name` in `settings.yaml`
- Add show-specific spam trigger words to `CANSPAMChecker.SPAM_TRIGGERS` if needed
- The suppression_list.csv format is fixed: `email,reason,suppressed_at`

---

### `src/email/sequence_builder.py`
**Purpose:** Render Jinja2 email templates with personalization tokens.

**Key interface:**
```python
from src.email.sequence_builder import SequenceBuilder
builder = SequenceBuilder("templates/email")
subject, body = builder.render(step=1, context={"venue_name": "...", "contact_name": "...", ...})
errors = builder.check_tokens(step=1, context=context)  # dry-run validation
```

**Required context keys:**
`contact_name`, `venue_name`, `city`, `state`, `seating_capacity_tier`, `programming_focus`, `mission_excerpt`, `sender_name`, `physical_address`, `unsubscribe_url`, `reply_to_email`, `next_season`

**Adapt for new project:**
- Replace templates in `templates/email/` with new show's brand voice
- Add or remove context keys based on what's available in your venue research
- Templates map to steps 1→`initial_outreach.j2`, 2→`followup_1.j2`, 3→`followup_2.j2`, 4→`breakup.j2`

---

### `src/email/zoho_sender.py`
**Purpose:** Send email via Zoho Mail SMTP (smtp.zoho.com:587, STARTTLS).

**Key interface:**
```python
from src.email.zoho_sender import ZohoSender
sender = ZohoSender(sender_name="Your Name")
result = sender.send(to_email="...", to_name="...", subject="...", body_text="...")
# result.success: bool
# result.error: Optional[str]
# result.message_id: Optional[str]
```

**Credentials:** Set via environment variables: `ZOHO_EMAIL`, `ZOHO_PASSWORD`, `ZOHO_REPLY_TO`

**Adapt for new project:**
- For a different email platform: update `SMTP_HOST`, `SMTP_PORT`, and auth logic
- Never hardcode credentials — always use `.env` + `python-dotenv`

---

### `src/email/deliverability.py`
**Purpose:** Guard wrapper around ZohoSender. Enforces: throttle, suppression, compliance, template approval, audit logging.

**Key interface:**
```python
from src.email.deliverability import DeliverabilityGuard, TemplateNotApproved
guard = DeliverabilityGuard(sender, suppression, checker, audit,
                            max_per_day=50, delay_seconds=90,
                            template_approved=config["template_approved"])
result = guard.send_step(contact, venue, step=1, subject="...", body_text="...")
```

**Raises:** `DailyLimitReached`, `ComplianceError`, `TemplateNotApproved`

**Adapt for new project:** Update throttle settings in `settings.yaml`. The guard logic itself is drop-in reusable.

---

### `run_sequence.py`
**Purpose:** CLI entry point. Orchestrates the full sequence run.

**Modes:**
- `--review-mode` — render all 4 templates with sample data; print to stdout; no sends; no CRM writes
- `--dry-run` — render templates, check compliance, validate; no sends
- `--test-mode --seed-file data/seed_lists/seed_list.csv` — send to seed addresses only
- `--live` — live send mode (requires `template_approved: true` in settings.yaml)
- `--stats` — print CRM record counts and audit summary

**Adapt for new project:** Update `SAMPLE_VENUE` dict at the top to use a representative venue for your target market.

---

## 3. CRM Field Schema Template (Generic — 27 Fields)

This table defines the canonical outbound CRM schema. Rename fields for each project as noted.

| Field | Type | Source Sheet | Purpose | Rename Notes |
|-------|------|-------------|---------|--------------|
| lead_id | int | Companies.UniqueId | Primary key for venue record | — |
| company | str | Companies.Name | Legal company name | — |
| venue_name | str | Gigs_Leads.Venue Name | Performing venue (may differ from company) | — |
| contact_name | str | Contacts.First+Last Name | Decision maker full name | — |
| title | str | Contacts.Title | Job title at venue | — |
| email | str | Contacts.Email | Primary outreach email | — |
| phone | str | Contacts.Work Phone | Phone number | — |
| website | str | Companies.Website | Venue website | — |
| city | str | Companies.Billing City | City for geographic targeting | — |
| state | str | Companies.Billing State | State (2-char) for regional filtering | — |
| source | str | Contacts.Lead Source | How we found this lead (manual/web/referral) | — |
| segment | str | Companies.Record Type | Venue category | e.g. "community_theater", "pac", "library" |
| sequence_id | str | Contacts.Custom1 | Which sequence enrolled in | e.g. "theater_outreach_v1" |
| step_number | int | Contacts.Custom2 | Last completed step (0-4) | — |
| send_time | str | Contacts.Custom4 | ISO 8601 timestamp of last send | — |
| open | bool | Contacts.Custom3 | Email opened (YES/NO) | Requires open tracking pixel |
| click | bool | Contacts.Custom4 | Link clicked | Requires click tracking |
| reply | bool | Contacts.Custom5 | Reply received | — |
| reply_category | str | Contacts.Custom6 | Classified reply type | See reply_categories.md |
| meeting_booked | bool | Gigs_Leads.Custom2 | Discovery call scheduled | — |
| show_booked | bool | Gigs_Leads.Custom1 | Performance booked (YES/NO) | — |
| projected_fee | float | Gigs_Leads.Quote1 | Expected performance fee | Rename to projected_fee per show type |
| final_fee | float | Gigs_Leads.Fee | Confirmed booking fee | — |
| outcome | str | Gigs_Leads.Status | Pipeline status | e.g. "Lead", "Interested", "Booked", "Not a Fit" |
| notes | str | Companies.Notes | Free-form notes | — |
| last_updated | str | Contacts.Custom7 | ISO 8601 timestamp | — |
| audit_trail_id | str | Contacts.Custom8 | UUID4 linking to audit.db | — |

**Custom field assignments (Companies sheet):**
- Custom1 → segment
- Custom9 → audit_trail_id

**Custom field assignments (Contacts sheet):**
- Custom1 → sequence_id
- Custom2 → step_number
- Custom3 → email_open
- Custom4 → email_click
- Custom5 → email_reply
- Custom6 → reply_category
- Custom7 → last_updated
- Custom8 → audit_trail_id

**Custom field assignments (Gigs_Leads sheet):**
- Custom1 → show_booked
- Custom2 → meeting_booked

---

## 4. Excel Import Format Reference

**Template URL:** `https://magotalent.blob.core.windows.net/magobiz/import.xlsx`

The template has 6 sheets. All column headers below are exact matches to the actual template.

### Companies Sheet (venue records)
`UniqueId, Name, Website, Record Type, Principal, Phone, Fax, Rating, Size, Custom1–10, Billing Street/City/State/Postcode/Country, Alt Street/City/State/Postcode/Country, Notes`

### Contacts Sheet (individual contacts)
`UniqueId, First Name, Last Name, Company UniqueId, Lead Source, Work Phone, Extension, Mobile Phone, Home Phone, Other Phone, Fax, Email, Phone Opt Out, Email Opt Out, Primary Street/City/State/Postcode/Country, Alt Street/City/State/Postcode/Country, Notes, Tag1/2/3, Prefix, Salutation, Title, Birthdate, AltEmail, Custom1–10`

### Gigs_Leads Sheet (opportunities/bookings)
`UniqueId, Name, Status, Company UniqueId, Primary Contact UniqueId, Secondary Contact UniqueId, Lead Source, GigID, Sponsor, Show Date, Show Time, Show Duration, Event Type, Guest Age Range, Event Size, Audience Type, Guest of Honor, Guest of Honor Age, Upsell Quantity, Alternate Showtimes, Show Details, Venue Address, Site Contact, Venue Name, Travel Info, Taxable Miles, Billable Miles, Mileage Rate, Fee, Deposit, Balance Paid, Deposit Paid, Gratuity Received, Contract sent, Contract Received, Other Sales, Coupon Code, Next Step, Decision Maker, Decision Date, Best time to contact, Client Comment, Quote1/2/3, Description1/2/3, Upsell Price, Upsell Description, Deposit Percentage, Custom1–15`

### Calls Sheet
`UniqueId, Subject, CallDateTime, Call Status, Call Notes, Related Gig, Related Contact, Related Company`

### Notes Sheet
`UniqueId, Subject, Date, Notes, Related Gig, Related Contact, Related Company`

### Lookups Sheet (reference data)
`YesNo, Call, Gig`

---

## 5. Email Sequence Design Pattern

### The 4-Step Day 0/5/9/14 Cadence

| Step | Day | Template File | Arc | Subject Pattern |
|------|-----|--------------|-----|-----------------|
| 1 | 0 | initial_outreach.j2 | Warm intro — who we are, why this venue | "A show your [city] families will still be talking about" |
| 2 | 5 | followup_1.j2 | Social proof + specifics — add credentials, testimonials | "Quick follow-up: [show_name] at [venue_name]" |
| 3 | 9 | followup_2.j2 | Practical angle — address logistics concerns, low barrier | "No technical riders, no headaches — just great theater" |
| 4 | 14 | breakup.j2 | Last touch — graceful exit, door left open | "Leaving the door open for [next_season]" |

**Why these delays:** Day 0/5 is tight enough to maintain momentum. Day 9 catches people who saw the first two but needed more info. Day 14 is the last touch that respects the prospect's time without over-pestering. Total cadence is 14 days — short enough for a seasonal booking window.

### Personalization Tokens

Every template must include these tokens (Jinja2 double-brace syntax):
```
{{ contact_name }}         - First name of contact
{{ venue_name }}           - Name of the performing venue
{{ city }}                 - Venue city
{{ state }}                - Venue state
{{ seating_capacity_tier }} - e.g. "small (100-200 seats)", "medium (201-400 seats)"
{{ programming_focus }}    - e.g. "family series and community productions"
{{ mission_excerpt }}      - Short excerpt from venue's stated mission
{{ sender_name }}          - Outreach sender's name
{{ show_name }}            - Full show title
{{ physical_address }}     - CAN-SPAM required physical mailing address
{{ unsubscribe_url }}      - CAN-SPAM required unsubscribe link/instruction
{{ reply_to_email }}       - Reply-to address
{{ next_season }}          - e.g. "the 2025-2026 season"
```

**Populating tokens from venue research:**
- `mission_excerpt`: Copy 1-2 sentences from venue's "About" page — shows you did the homework
- `programming_focus`: Extract from their current season or programming page
- `seating_capacity_tier`: Assign based on stated capacity: small (100-200), medium (201-400)
- `contact_name`: First name only — more conversational than full name

### Brand Voice Adaptation Guide

| Context | Tone Adjustment |
|---------|----------------|
| Community theater | Peer-to-peer, arts-focused, "we both care about the community" |
| Performing arts center | More formal, emphasize production quality and credentials |
| Library / municipal | Mission-aligned, emphasize educational and family access value |
| Arts nonprofit | Lead with impact, not revenue |
| School / education | Safety, curriculum alignment, age-appropriateness |

**What NOT to do:**
- Fake personalization (copy-pasted generic text labeled as personal)
- Deceptive subject lines ("Re: your inquiry" when there was no prior contact)
- Spam trigger words: free, act now, limited time, guaranteed, win, !!!, $$$
- Preaching or over-explaining the show's values — trust the content to do the work
- Corporate tone in arts outreach — it signals you don't understand the sector

---

## 6. Deliverability Runbook

### Domain Warm-Up Schedule

| Week | Max Sends/Day | Notes |
|------|--------------|-------|
| 1 | 10 | New domain — send to highest-quality addresses only |
| 2 | 25 | Add more recipients, monitor bounce rate |
| 3 | 50 | Scale if bounce rate < 2% and no spam flags |
| 4+ | 100 | Full production volume (capped at 100 for regional outreach) |

Update `deliverability.current_week` in `config/settings.yaml` each week. Update `max_sends_per_day` to match the week's cap.

### DNS Setup Checklist for Zoho Mail

1. Log into Zoho Mail → Settings → Email Authentication
2. Copy the SPF TXT record → add to your domain's DNS
3. Copy the DKIM TXT record → add to your domain's DNS
4. Add DMARC TXT record: `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
5. Wait 24-48 hours for DNS propagation
6. Verify at mxtoolbox.com: SPF ✓, DKIM ✓, DMARC ✓

### Throttle Settings

The 90-second delay between sends (`delay_between_sends_seconds: 90`) prevents:
- Rate limiting by the receiving server
- Pattern detection by spam filters (bulk send behavior)
- IP reputation damage from sending too fast

Do not reduce below 60 seconds. For very conservative warm-up, use 120-180 seconds.

### Bounce Classification

| Bounce Type | Definition | Action |
|-------------|------------|--------|
| Hard bounce | 5xx permanent failure (invalid address, domain blocked) | Immediate suppression; log BOUNCE event |
| Soft bounce | 4xx temporary failure (mailbox full, server unavailable) | Retry up to 3x; then suppress; log SOFT_BOUNCED |
| Out-of-office | Auto-reply with return date | Re-queue to return date; no suppression |

Bounce rate target: < 2%. Above 5% is a danger signal for sender reputation.

### Seed List Inbox Placement Test (25-Inbox Protocol)

Before any live sends on a new domain or new sequence:
1. Collect 25 test inboxes across: Gmail (5), Outlook (5), Yahoo (5), Apple Mail (5), other (5)
2. Add all 25 to `data/seed_lists/seed_list.csv`
3. Run: `python3 run_sequence.py --test-mode`
4. Check each inbox manually: inbox (not spam), rendering, unsubscribe link works
5. Record: # in inbox, # in spam, # not delivered
6. Target: ≥ 20/25 in inbox (80% placement rate)
7. If < 80%: do NOT proceed to live sends. Debug DNS, template content, or sending domain.

---

## 7. Compliance Defaults Checklist

Run through this checklist before first live send on any new project.

### CAN-SPAM Requirements (US Law — Not Legal Advice)
- [ ] Every email includes sender's physical mailing address
- [ ] Every email includes a clear and conspicuous opt-out mechanism
- [ ] Subject lines are not deceptive or misleading
- [ ] From name clearly identifies the sender
- [ ] Opt-out requests honored within 10 business days (this system: immediate)
- [ ] No purchased or harvested email lists

### GDPR / UK PECR Awareness
- [ ] International contacts (EU, UK) flagged in CRM notes field
- [ ] B2B outreach to business email addresses at arts organizations is generally permitted under legitimate interest — document this rationale
- [ ] Any EU/UK contacts who opt out are removed immediately and permanently
- [ ] No personal data stored beyond what's needed for outreach

### Suppression List Management
- File: `config/suppression_list.csv`
- Format: `email,reason,suppressed_at`
- Valid reasons: `OPT_OUT`, `HARD_BOUNCE`, `SOFT_BOUNCE`, `MANUAL`
- Checked before EVERY send (enforced in `deliverability.py`)
- Never delete from this list — only add
- Back up this file regularly

### Spam Trigger Words to Avoid in Subject Lines
free, act now, limited time, guaranteed, make money, win, click here, urgent, !!!, $$$, 100%, no obligation, once in a lifetime, special promotion, buy now, best price, congratulations

---

## 8. "Adapt for New Project" — 10-Step Setup Guide

Use this checklist to spin up this system for any new touring show.

- [ ] **Step 1 — Clone the repository**
  ```bash
  git clone <repo_url> new-project-name
  cd new-project-name
  pip install -r requirements.txt
  ```

- [ ] **Step 2 — Update `config/settings.yaml` with new show details**
  - `brand.show_name`, `brand.brand_name`, `brand.company_name`
  - `brand.sender_name` (who is doing the outreach)
  - `brand.physical_address` (required for CAN-SPAM)
  - `targeting.geography.states` (target states list)
  - `targeting.venue.seat_min` and `seat_max`
  - `zoho.email` and `zoho.password` (via `.env` file — never in settings.yaml)

- [ ] **Step 3 — Download and inspect the CRM Excel template**
  ```bash
  python3 -c "
  import openpyxl, urllib.request, io
  url = 'https://magotalent.blob.core.windows.net/magobiz/import.xlsx'
  with urllib.request.urlopen(url) as r:
      wb = openpyxl.load_workbook(io.BytesIO(r.read()))
  for sheet in wb.sheetnames:
      print(sheet, [c.value for c in next(wb[sheet].iter_rows(max_row=1))][:10])
  "
  ```

- [ ] **Step 4 — Verify `column_map` in settings.yaml matches actual column headers**
  Update any column names that differ from the default mapping.

- [ ] **Step 5 — Replace email templates with new show's brand voice**
  Edit: `templates/email/initial_outreach.j2`, `followup_1.j2`, `followup_2.j2`, `breakup.j2`
  Keep all token references (`{{ venue_name }}`, etc.) — only change the prose.

- [ ] **Step 6 — Run `--review-mode` and get human approval**
  ```bash
  python3 run_sequence.py --review-mode
  ```
  After reviewing all 4 rendered templates, set `template_approved: true` in settings.yaml.

- [ ] **Step 7 — Build the initial venue list**
  Research 50-100 venues matching your criteria. Populate the Companies and Contacts sheets of your leads.xlsx following the Excel schema. Import to verify:
  ```bash
  python3 run_sequence.py --stats
  ```

- [ ] **Step 8 — Complete DNS setup and warm-up**
  Follow `Outbound_Theater_Automation_System/Deliverability/spf_dkim_dmarc_checklist.md`. Start at week_1 = 10 sends/day.

- [ ] **Step 9 — Run seed inbox test**
  ```bash
  python3 run_sequence.py --test-mode --seed-file data/seed_lists/seed_list.csv
  ```
  Target: >80% inbox placement. Do not proceed to live sends until this passes.

- [ ] **Step 10 — Begin live outbound**
  ```bash
  python3 run_sequence.py --live
  ```
  Monitor bounce rate, reply rate, and audit log daily. Advance `current_week` in settings.yaml each week.

---

## 9. Lessons Learned + Pitfalls

*This section is append-only. Add new lessons after each deployment wave.*

### Wave 1 — Initial Build (Princess Peigh Adventures, March 2026)

**1. Always inspect actual Excel column headers before writing import code.**
The template URL (`import.xlsx`) was provided but could not be parsed from its binary format via WebFetch. The actual column names (especially in Gigs_Leads with 60+ columns) differ significantly from what you might assume. Downloading and inspecting with openpyxl is the only reliable approach.

**2. The `template_approved` gate prevents a costly mistake.**
Without the gate, a new system operator could accidentally send 50 emails with un-reviewed templates (wrong tone, broken tokens, missing CAN-SPAM footer). Adding `template_approved: false` as a hard block, checked before CRM load, ensures this never happens. This should be in every future project.

**3. Pydantic field name shadowing is a subtle bug source.**
Naming a Pydantic model field `date` when `from datetime import date` creates a schema generation error in Pydantic v2. Field names must not shadow imported type names. The fix was renaming the field to `note_date` in `NoteRecord`. Watch for this with field names like `time`, `date`, `list`, `type`, `id`.

**4. Suppression list must be checked before EVERY send, not just at sequence start.**
An address may be added to the suppression list mid-run (e.g., from a bounce response while the send loop is running). The `deliverability.py` guard re-checks for each send individually. Do not optimize this away.

**5. Deduplication must run on both email AND venue name composite.**
The same venue can appear multiple times in a raw import (once from a state association list, once from a city directory). Email alone isn't sufficient — the same contact email can appear across multiple venue records. Use both the venue dedup (company+state) AND contact dedup (email) in sequence.

**6. Brand tone drives response rate more than sequence timing.**
Generic sales language in theater outreach produces much lower response rates than language that reflects genuine familiarity with the venue's programming. Invest time in the mission_excerpt and programming_focus fields — they make the difference between a cold email and a warm introduction.

**7. Map each Custom field explicitly in settings.yaml — never rely on positional column order.**
The Excel template has 10 Custom fields in Companies and 10 in Contacts. Relying on position (Custom1 is always segment) is fragile. The `column_map` in settings.yaml makes every assignment explicit and auditable.

*[APPEND NEW LESSONS HERE after each deployment wave]*

---

## Continuation Backlog

Items deferred from Wave 1 for future waves:

- **Social media research ingestion:** Pull content from `@PrincessPeighadventures` to inform personalization tokens and brand voice updates
- **Calendar integration:** Connect scheduling tool (Calendly/Google Calendar) for `meeting_booked` tracking and auto-logging to CRM
- **Proposal tracking:** After `meeting_booked = YES`, track proposal sent, negotiation stage, contract sent
- **Post-call recap auto-log:** After discovery call, auto-generate a note in the Notes sheet
- **School matinee segment expansion:** Separate sequence and qualification rubric for school daytime bookings
- **Open/click tracking:** Currently `email_open` and `email_click` are manually tracked. Add a simple tracking pixel endpoint or integrate with Zoho Campaigns API for automated tracking
- **Reply handling automation:** Currently all reply categorization is manual. Add keyword-based auto-classification writing to `reply_category` field in CRM
- **Multi-state geographic expansion:** Extend the states list in targeting config and build venue lists for second and third states
- **Fringe Festival sequence:** Separate 2-step sequence for festival programmers with different value proposition

---

*Document version: 1.0 | Created: 2026-03-04 | Next review: End of Wave 1 (first 50 outbound contacts)*
