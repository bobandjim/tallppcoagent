# Outbound Automation Plan — Princess Peigh Adventures
## Implementation Roadmap: 10 Phases

**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Target:** Community theaters, performing arts centers, libraries, municipal cultural venues
**Geography:** Regional (1-3 states), 100-400 seat venues
**CRM:** Excel/CSV 6-sheet format
**Email:** Zoho Mail SMTP
**Branch:** `claude/complete-system-build-crm-jrfpP`

---

## Goal

Book paid performances of Princess Peigh's Sword Fighting Tea Party at regional venues (100-400 seats) by running a compliant, personalized, auditable outbound email system. Target: $1,500 profit/show, growing toward 36 booked weeks/year within 3 years.

---

## Strict Scope and Constraints

- **Geography:** 1-3 states (regional); no national expansion without explicit decision
- **Venue size:** 100-400 seats only
- **CRM:** Excel/CSV only; no SaaS CRM subscription
- **Email platform:** Zoho Mail SMTP; no platform changes without approval
- **Personalization:** Real only; no fabricated venue references
- **Compliance:** CAN-SPAM defaults enforced; no purchased lists without review
- **Automation:** Human approval required for all reply responses; no auto-reply

---

## Primary Inputs

- `/home/user/tallppcoagent/docs/Princess Peigh Positioning Document.txt` — brand voice, show specs, differentiators
- `https://magotalent.blob.core.windows.net/magobiz/import.xlsx` — Excel CRM template (6 sheets)
- `config/settings.yaml` — Zoho credentials (via env vars), throttle limits, geography config
- `config/suppression_list.csv` — opt-outs and bounces
- Venue research (per Lead_Sourcing documentation)
- Social media: `@PrincessPeighadventures` — brand voice reference

---

## Continuous Iteration Policy

This system **never declares complete.** Every phase produces:
1. Updated documentation in the relevant sub-module
2. New items in the **Continuation Backlog** below
3. An updated **Current Wave Log** entry

System improvement is ongoing. Any operator can add to the backlog without waiting for a phase review.

---

## Success Criteria / Definition of Done

| Metric | Threshold |
|--------|-----------|
| Inbox placement (seed test) | ≥ 80% landing in primary inbox |
| Open rate (first 30 sends) | ≥ 25% |
| Reply rate (4-step sequence) | ≥ 3% |
| Bookings per 50 leads contacted | ≥ 1 |
| Audit trail completeness | 100% of sends have EMAIL_SENT event |
| Suppression compliance | 100% opt-outs honored within 24h |
| CRM round-trip accuracy | 0 data loss on Excel import/export |

---

## Current Wave Log

| Wave | Date | Description | Artifacts |
|------|------|-------------|-----------|
| 1 | 2026-03-04 | Initial system build: full codebase, documentation, 4-step sequence, test suite | All files in this repository |

---

---

# Phase 1 — Strategy Definition

## Objectives
Define booking targets, success metrics, offer framing, and operational constraints before any outbound begins.

## Tasks
- [x] Read and internalize brand positioning document
- [x] Define target venue profile (100-400 seats, regional, community-focused)
- [x] Define target contact titles (Programming Director, Executive Director, Family Series Coordinator)
- [x] Set revenue target ($1,500 profit/show)
- [x] Set touring season window (confirm with Melissa and Zachary)
- [ ] Define 3 target states with list of 10 venue names each as starting seed list
- [ ] Confirm Zoho sending domain and Sender Identity with Zachary
- [ ] Review and approve email sequence tone with Melissa

## Inputs Required
- Touring availability calendar (dates unavailable, geography preference)
- Zoho account credentials (for settings.yaml)
- Confirmation of physical mailing address for CAN-SPAM footer

## Deliverables
- `config/settings.yaml` — complete with states list, Zoho config
- `/Process/00_system_overview.md` — finalized
- Initial list of 10 target venues per state in a staging CSV

## Validation Steps
1. Run: `python3 -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"` — no errors
2. Verify sender identity in Zoho admin panel matches `ZOHO_EMAIL` env var
3. Confirm 3 target states are populated in `settings.yaml` under `targeting.geography.states`

## Evidence / Traceability
- Every config decision documented in `/Process/00_system_overview.md`
- Touring calendar stored as artifact in `/Process/` folder
- Approved email tone documented in `/Sequences/DROP_IN_REUSABILITY.md`

---

# Phase 2 — Offer Positioning for Theaters

## Objectives
Finalize the specific value proposition for each venue tier (PAC, community theater, library) and confirm differentiators vs. competing family shows.

## Tasks
- [x] Document differentiators vs. princess party acts, magicians, generic family shows
- [x] Define 3 pricing models (flat fee, ticket split, guarantee + percentage)
- [x] Define workshop upsell positioning (post-show sword fighting add-on)
- [ ] Draft 2-3 subject line A/B variants per email step
- [ ] Confirm "social proof" quotes approved for use in email copy
- [ ] Define Tier A / Tier B / Tier C venue offer framing

## Inputs Required
- Approved testimonial quotes from programmers (e.g., Irvington Theater)
- Pricing floor and ceiling for each model
- Workshop pricing

## Deliverables
- `/Sequences/sequence_01_initial_outreach.md` through `sequence_04_breakup.md` — approved
- Subject line A/B test variants documented in `/Testing/`

## Validation Steps
1. Read templates/email/initial_outreach.j2 — verify venue-specific personalization tokens present
2. Test-render Step 1 with sample data: `python3 -c "from src.email.sequence_builder import SequenceBuilder; s=SequenceBuilder(); print(s.render(1, {'contact_name':'Sarah','venue_name':'City Theater','city':'Albany','state':'NY','seating_capacity_tier':'Mid','mission_excerpt':None,'next_season':'Fall 2026','physical_address':'123 Main St','unsubscribe_url':'https://example.com/unsub','reply_to_email':'z@example.com'}))"`
3. Verify output contains no `{{` artifacts

## Evidence / Traceability
- Positioning decisions documented in `/Sequences/DROP_IN_REUSABILITY.md`
- Approved testimonials stored as artifact file (not committed if contains PII)

---

# Phase 3 — Lead Sourcing + Qualification

## Objectives
Build initial venue list of 50-150 qualified leads across target states before any outreach begins.

## Tasks
- [ ] Run venue research per `/Lead_Sourcing/data_sources.md`
- [ ] Apply qualification criteria per `/Lead_Sourcing/venue_qualification_criteria.md`
- [ ] Score and tier each venue (Tier A / B / C)
- [ ] Find correct contact name, title, and email for each venue
- [ ] Enter into Companies + Contacts sheets in Excel CRM
- [ ] Create Gigs_Leads row (Status=Lead) for each venue
- [ ] Run deduplication: `python3 -c "from src.crm.importer import CRMImporter; from src.crm.deduplication import dedup_venues, dedup_contacts; r = CRMImporter('data/crm/leads.xlsx').load_all(); v,ve = dedup_venues(r.venues); c,ce = dedup_contacts(r.contacts); print(f'{len(ve)} venue dups, {len(ce)} contact dups')"`
- [ ] Verify 0 duplicate emails in Contacts sheet

## Inputs Required
- Target state list (from Phase 1)
- Research time: expect 5-10 minutes per venue for full qualification
- Access to venue websites, social media, arts council directories

## Deliverables
- `data/crm/leads.xlsx` — populated with 50-150 qualified leads
- Tier distribution documented (target: ≥ 30% Tier A)

## Validation Steps
1. Import CRM: `python3 -c "from src.crm.importer import CRMImporter; r = CRMImporter('data/crm/leads.xlsx').load_all(); print(f'{len(r.venues)} venues, {len(r.contacts)} contacts, {r.error_count} errors')"`
2. Verify error_count < 5
3. Verify every Contacts row has: email, first_name or last_name, company_id, sequence_id

## Evidence / Traceability
- Research sources documented per venue in Companies.Notes column
- Tier assigned in Companies.Custom1 (seating_capacity_tier)

---

# Phase 4 — Data Enrichment

## Objectives
Enrich each venue record with mission statement excerpt, programming focus, and seating capacity tier before personalization can fire correctly.

## Tasks
- [ ] For each venue: visit website and note mission statement excerpt (1 phrase, <100 chars)
- [ ] Classify programming focus (Family, Education, Community, Arts, Mixed)
- [ ] Verify or assign seating capacity tier (Small/Mid/Large)
- [ ] Enter seating_capacity_tier in Companies.Custom1
- [ ] Enter mission_excerpt in Companies.Custom2
- [ ] Enter programming_focus in Companies.Custom3
- [ ] Run template render test for 5 sample venues (check personalization fires correctly)

## Inputs Required
- `data/crm/leads.xlsx` from Phase 3
- Time for website research per venue (~2 min each)

## Deliverables
- Updated `data/crm/leads.xlsx` with Custom1-3 populated for all venues
- `/Lead_Sourcing/enrichment_checklist.md` — per-venue enrichment checklist artifact

## Validation Steps
1. Render Step 1 for 5 random contacts from CRM — verify `mission_excerpt` block renders or is skipped cleanly
2. Verify no `{{ }}` artifacts in any rendered output
3. Confirm seating_capacity_tier renders as "Small (100-199 seats)" / "Mid (200-299 seats)" / "Large (300-400 seats)"

## Evidence / Traceability
- Enrichment logged in Companies.Notes ("Enriched: [date]")

---

# Phase 5 — CRM Architecture + Import Validation

## Objectives
Verify the Excel CRM round-trips correctly (import → validate → export → re-import), all 27 required fields work, and dedup logic is clean.

## Tasks
- [x] Define all Pydantic models (schema.py)
- [x] Build importer (importer.py)
- [x] Build exporter (exporter.py)
- [x] Build deduplication (deduplication.py)
- [x] Build audit log (audit.py)
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify round-trip: import leads.xlsx → export to leads_roundtrip.xlsx → re-import → compare record counts
- [ ] Verify audit log records LEAD_CREATED events on import

## Inputs Required
- `data/crm/leads.xlsx` with at least 5 populated records (from Phase 3)

## Deliverables
- All tests passing with 0 failures
- Round-trip verification log (save output to /Testing/)

## Validation Steps
1. `pytest tests/test_crm_schema.py tests/test_importer.py -v` — all pass
2. Import → export → re-import: record counts match
3. Dedup test: add 2 duplicate emails manually, verify dedup_contacts() returns 1
4. Audit test: `pytest tests/test_compliance.py::TestAuditLog -v` — all pass

## Evidence / Traceability
- Test run output saved to `/Testing/test_run_phase5.txt`
- Schema field definitions documented in `/CRM_Schema/crm_field_definitions.md`

---

# Phase 6 — Deliverability Infrastructure Setup

## Objectives
Configure Zoho Mail for outbound, verify DNS authentication, and complete domain warm-up schedule setup before first live send.

## Tasks
- [ ] Set up Zoho Mail account with sending domain (not a free Zoho address)
- [ ] Add SPF record to DNS per `/Deliverability/spf_dkim_dmarc_checklist.md`
- [ ] Generate and add DKIM key in Zoho admin
- [ ] Set DMARC policy (start at p=none)
- [ ] Verify all three: `nslookup -type=TXT yourdomain.com` (SPF + DKIM + DMARC)
- [ ] Populate `config/seed_list.csv` with 25 seed addresses
- [ ] Send test email to all 25 seeds; check inbox placement
- [ ] Document inbox placement results in `/Testing/inbox_placement_protocol.md`
- [ ] Confirm warm-up schedule: start at Week 1 (10/day)
- [ ] Set `deliverability.current_week: 1` in `config/settings.yaml`

## Inputs Required
- Sending domain (not zoho.com subdomain)
- Zoho Mail admin access
- 25 seed email addresses (minimum 1 Gmail, 1 Outlook, 1 Yahoo)

## Deliverables
- SPF/DKIM/DMARC all verified green
- Seed inbox placement report: ≥ 80% in primary inbox
- Warm-up schedule active (Week 1: 10/day cap)

## Validation Steps
1. MXToolbox SPF check: `mxtoolbox.com/spf.aspx` — PASS
2. DKIM check via MXToolbox — PASS
3. DMARC check — PASS
4. Test send to all 25 seeds — check inbox vs spam placement manually
5. Confirm `max_sends_per_day: 10` in settings.yaml (Week 1)

## Evidence / Traceability
- Seed test results documented in `/Testing/inbox_placement_protocol.md`
- DNS verification screenshots saved as artifacts

---

# Phase 7 — Sequence Development

## Objectives
Finalize all 4 email sequence steps: templates verified, subject lines approved, compliance check passing for all steps.

## Tasks
- [x] Write templates/email/initial_outreach.j2 (Step 1 — Day 0)
- [x] Write templates/email/followup_1.j2 (Step 2 — Day 5)
- [x] Write templates/email/followup_2.j2 (Step 3 — Day 9)
- [x] Write templates/email/breakup.j2 (Step 4 — Day 14)
- [ ] Run CAN-SPAM validation on all 4 steps with sample data
- [ ] Run spam-trigger phrase check on all 4 subject lines
- [ ] Get Melissa + Zachary to approve all email copy (tone review)
- [ ] Document approved sequence in `/Sequences/sequence_01_initial_outreach.md` etc.

## Inputs Required
- Brand voice: theatrical, whimsical, family-forward — not corporate
- Approved testimonials and social proof
- Final mailing address and unsubscribe URL

## Deliverables
- All 4 templates rendering correctly with test data
- All 4 templates passing CAN-SPAM validation
- Sequence approved by Melissa and Zachary

## Validation Steps
1. `pytest tests/test_compliance.py::TestSequenceBuilder -v` — all pass
2. CAN-SPAM check on each step: `from src.utils.compliance import CANSPAMChecker` — 0 warnings
3. Unsubscribe URL present in every rendered body
4. Physical address present in every rendered body

## Evidence / Traceability
- Approval emails/messages from Melissa and Zachary stored as artifact
- Final template files committed to repository

---

# Phase 8 — Automation Build

## Objectives
Wire all modules into an executable send pipeline that can be run from command line.

## Tasks
- [x] Build sequence_builder.py
- [x] Build zoho_sender.py
- [x] Build deliverability.py (with throttle, suppression, compliance, audit integration)
- [ ] Write a simple `run_sequence.py` CLI entry point that:
  - Loads CRM
  - Filters eligible contacts
  - Renders templates
  - Calls DeliverabilityGuard.send_step()
  - Updates CRM after each send
  - Exports updated Excel
- [ ] Test run against 3 seed addresses (not real venue contacts)

## Inputs Required
- Verified Zoho credentials in `.env`
- `data/crm/leads.xlsx` with 3+ test records pointing to seed addresses

## Deliverables
- `run_sequence.py` — working end-to-end pipeline script
- Successful test run against 3 seed addresses logged in audit.db

## Validation Steps
1. Run `python3 run_sequence.py --dry-run` — renders templates, skips actual send
2. Run `python3 run_sequence.py --test-mode` — sends to seeds only
3. Check audit.db: 3 EMAIL_SENT events written
4. Check CRM: step_number incremented for test contacts

## Evidence / Traceability
- Dry-run output saved to `/Testing/dry_run_phase8.txt`
- Test-mode audit log exported

---

# Phase 9 — Testing + Validation

## Objectives
Full end-to-end test before any live venue contacts are sent to. Verify compliance, deliverability, CRM, and audit trail.

## Tasks
- [ ] Run `pytest tests/ -v --tb=short` — all tests pass
- [ ] Run 25-seed inbox placement test per `/Testing/seed_list_25_protocol.md`
- [ ] Verify inbox placement ≥ 80%
- [ ] Complete manual QA checklist per `/Testing/manual_qa_checklist.md`
- [ ] Complete CRM audit checklist per `/Testing/crm_audit_checklist.md`
- [ ] Simulate opt-out: add test address to suppression, verify next run skips it
- [ ] Simulate hard bounce: verify HARD_BOUNCE audit event written and suppression added
- [ ] Verify dedup: import file with duplicates, verify dedup events in audit log

## Inputs Required
- 25-address seed list in `data/seed_lists/seed_list.csv`
- All prior phases complete

## Deliverables
- All tests passing
- Inbox placement ≥ 80%
- Manual QA checklist completed and filed in `/Testing/`
- CRM audit checklist completed and filed in `/Testing/`

## Validation Steps
1. `pytest tests/ -v` — 0 failures
2. Seed test: count addresses landing in primary inbox (target ≥ 20/25)
3. Suppression test: suppressed address does NOT appear in send log
4. Audit log test: `SELECT event_type, COUNT(*) FROM audit_log GROUP BY event_type` shows expected event types

## Evidence / Traceability
- Test run output saved to `/Testing/test_run_phase9.txt`
- Seed placement results saved to `/Testing/seed_placement_phase9.csv`

---

# Phase 10 — Optimization + Scaling

## Objectives
After first 50 sends, analyze results and iterate. Expand to full regional list. Document learnings.

## Tasks
- [ ] Review: open rate, reply rate, reply categories
- [ ] A/B test subject line variants (document in `/Testing/`)
- [ ] Update `current_week` in settings.yaml to increase daily cap per warm-up schedule
- [ ] Interview Interested replies — identify pattern in venues that respond
- [ ] Refine targeting: if Tier A responds better, shift sourcing toward Tier A
- [ ] Document sequence performance in `/Knowledge_Base.md`
- [ ] Plan expansion: additional states, additional venue segments (school matinee market)
- [ ] Update `Continuation Backlog` below

## Inputs Required
- First 50 sends complete
- Audit log data
- Reply data from Zoho inbox

## Deliverables
- Phase 10 performance report in `/Knowledge_Base.md`
- Updated targeting criteria (if changes made)
- Updated sequence (if subject line changes approved)

## Validation Steps
1. Export flat report: join audit_log + CRM → verify all 27 fields populated correctly
2. Reply rate ≥ 3% — if not, identify and address before scaling
3. Any suppression rate > 5%: investigate and pause before scaling

## Evidence / Traceability
- Performance report committed to repo
- All CRM updates exported to Excel and backed up

---

## Reproducible Validation Steps

Run in order to verify the full system is operational:

```bash
# 1. Verify Python dependencies installed
pip install -r requirements.txt

# 2. Run full test suite
pytest tests/ -v --tb=short

# 3. Verify config loads
python3 -c "import yaml; c = yaml.safe_load(open('config/settings.yaml')); print('Config OK:', c['brand']['show_name'])"

# 4. Verify CRM import (template file)
python3 -c "
import urllib.request, io, openpyxl
url = 'https://magotalent.blob.core.windows.net/magobiz/import.xlsx'
with urllib.request.urlopen(url) as r:
    data = io.BytesIO(r.read())
wb = openpyxl.load_workbook(data)
print('Sheets:', wb.sheetnames)
print('Template OK')
"

# 5. Test sequence render
python3 -c "
from src.email.sequence_builder import SequenceBuilder
s = SequenceBuilder('templates/email')
ctx = {
    'contact_name': 'Sarah',
    'venue_name': 'City Theater',
    'city': 'Albany',
    'state': 'NY',
    'seating_capacity_tier': 'Mid',
    'mission_excerpt': None,
    'next_season': 'Fall 2026',
    'physical_address': '123 Main St, Albany NY',
    'unsubscribe_url': 'https://example.com/unsub',
    'reply_to_email': 'z@example.com',
}
for r in s.render_all(ctx):
    print(f'Step {r[\"step\"]}: {r[\"subject\"]}')
print('Templates OK')
"

# 6. Verify audit log
python3 -c "
from src.utils.audit import AuditLog
a = AuditLog('data/audit.db')
trail = a.log('LEAD_CREATED', lead_id=999, payload={'test': True})
print('Audit trail ID:', trail)
print('Audit log OK')
"
```

---

## Continuation Backlog

Items to address in future waves:

- [ ] **Social media research ingestion** — scrape @PrincessPeighadventures content to auto-update brand voice reference in Knowledge_Base.md
- [ ] **Calendar integration** — connect Zoho Calendar or Calendly to auto-log meetings booked
- [ ] **Proposal tracking** — template for post-call proposal PDF, log send to Gigs_Leads.Next Step
- [ ] **School matinee segment** — separate sequence targeting school program directors
- [ ] **Festival circuit** — Fringe Festival showcase outreach sequence
- [ ] **Library consortium targeting** — library networks often book as packages, need different pitch
- [ ] **Reply classification automation** — keyword-based Python classifier to pre-categorize replies (human still approves)
- [ ] **Multi-sequence management** — handle venues that have been in multiple waves without re-sending
- [ ] **Open/click tracking** — Zoho Campaigns API for tracking pixel vs SMTP-only
- [ ] **Reporting dashboard** — simple Python script that generates a flat CSV report from audit.db

---

## Deliverables Checklist

- [x] `requirements.txt` — Python dependencies
- [x] `.gitignore` — with .env and live data excluded
- [x] `config/settings.yaml` — full system configuration
- [x] `.env.example` — credentials template
- [x] `config/suppression_list.csv` — suppression list (initially empty)
- [x] `data/seed_lists/seed_list.csv` — 25-seed list template
- [x] `src/crm/schema.py` — Pydantic models for all 6 sheets
- [x] `src/crm/importer.py` — Excel → validated records
- [x] `src/crm/exporter.py` — records → Excel
- [x] `src/crm/deduplication.py` — venue + contact dedup
- [x] `src/utils/logger.py` — structured JSON logger
- [x] `src/utils/audit.py` — SQLite audit trail
- [x] `src/utils/compliance.py` — CAN-SPAM checker + suppression list
- [x] `src/email/sequence_builder.py` — Jinja2 template renderer
- [x] `src/email/zoho_sender.py` — Zoho SMTP sender
- [x] `src/email/deliverability.py` — throttle + suppression + compliance guard
- [x] `templates/email/initial_outreach.j2` — Step 1 template
- [x] `templates/email/followup_1.j2` — Step 2 template
- [x] `templates/email/followup_2.j2` — Step 3 template
- [x] `templates/email/breakup.j2` — Step 4 template
- [x] `tests/test_crm_schema.py`
- [x] `tests/test_importer.py`
- [x] `tests/test_compliance.py`
- [x] Documentation: `/Outbound_Theater_Automation_System/` — full sub-module structure
- [x] `Outbound_Theater_Automation_System/PLAN.md` — this document
- [x] `Outbound_Theater_Automation_System/Knowledge_Base.md`

---

## Acceptance Criteria

System is accepted when:

1. `pytest tests/ -v` runs with 0 failures
2. Excel import/export round-trip is lossless (0 field loss on 5 test records)
3. All 4 email templates render with no missing token errors on sample venue data
4. Suppression list check fires before every send (verified by test)
5. CAN-SPAM validation blocks any email missing physical address or unsubscribe URL
6. Audit trail records all 8 event types correctly
7. Seed inbox placement ≥ 80% (verified before first live wave)
8. All documentation files present in `Outbound_Theater_Automation_System/`
9. Code committed and pushed to `claude/complete-system-build-crm-jrfpP`
