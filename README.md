# Princess Peigh Adventures — Outbound Booking Automation System

**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company

A production-ready outbound booking automation system for a regional touring family theatrical production. Targets community theaters, performing arts centers, libraries, and municipal cultural venues (100-400 seats, 1-3 states).

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env: add your Zoho email and password
```

### 3. Configure settings

Edit `config/settings.yaml`:
- Set `targeting.geography.states` to your target states
- Set `brand.physical_address` to your actual mailing address
- Set `brand.website` and update `unsubscribe_url` once your unsubscribe page is live
- Confirm `deliverability.current_week: 1` for domain warm-up

### 4. Run system validation

```bash
pytest tests/ -v
```

### 5. Run a dry run (no actual emails sent)

```bash
python3 run_sequence.py --dry-run
```

---

## System Overview

```
Lead Research → Excel CRM → Python Validator → Jinja2 Templates →
Zoho SMTP (throttled, compliant) → SQLite Audit Trail → Human Reply Review
```

### CRM Structure

The CRM uses a standard 6-sheet Excel format (matching the [import template](https://magotalent.blob.core.windows.net/magobiz/import.xlsx)):

| Sheet | Purpose |
|-------|---------|
| Companies | Venues/organizations |
| Contacts | Individual contacts at venues |
| Gigs_Leads | Booking pipeline (Status: Lead or Gig) |
| Calls | Call log |
| Notes | Notes |
| Lookups | Dropdown values |

Outbound tracking fields are stored in `Custom1`-`Custom8` columns in Companies and Contacts sheets.

---

## Project Structure

```
tallppcoagent/
├── Outbound_Theater_Automation_System/   # Living documentation
│   ├── PLAN.md                           # 10-phase implementation roadmap
│   ├── Knowledge_Base.md                 # Master evolving document
│   ├── Process/                          # Workflow docs
│   ├── Deliverability/                   # DNS, warm-up, throttling
│   ├── Sequences/                        # Email step docs
│   ├── CRM_Schema/                       # Field definitions, dedup rules
│   ├── Lead_Sourcing/                    # Qualification, research sources
│   ├── Testing/                          # QA checklists, seed protocols
│   ├── Compliance/                       # CAN-SPAM, suppression
│   └── Reply_Handling/                   # Categories, escalation rules
├── src/
│   ├── crm/                              # Schema, importer, exporter, dedup
│   ├── email/                            # Sequence builder, Zoho sender, guard
│   └── utils/                            # Logger, audit, compliance
├── templates/email/                      # Jinja2 email templates (4 steps)
├── config/
│   ├── settings.yaml                     # System configuration
│   └── suppression_list.csv              # Opt-outs and bounces
├── data/
│   ├── crm/leads.xlsx                    # CRM data (NOT committed to git)
│   └── seed_lists/seed_list.csv          # Seed addresses for inbox testing
├── tests/                                # pytest test suite
├── run_sequence.py                       # CLI entry point
└── .env.example                          # Credentials template
```

---

## Email Sequence

4-step sequence over 14 days targeting programming directors and executive directors at venues:

| Step | Day | Theme | Subject |
|------|-----|-------|---------|
| 1 | 0 | Warm intro | "A show your {city} families will still be talking about" |
| 2 | 5 | Social proof | "Quick follow-up: Princess Peigh at {venue_name}" |
| 3 | 9 | Logistics ease | "No technical riders, no headaches — just great theater" |
| 4 | 14 | Gracious exit | "Leaving the door open for {next_season}" |

All emails are personalized with venue name, city, seating tier, and optional mission reference. All include CAN-SPAM-required sender identity, physical address, and unsubscribe link.

---

## Compliance

- **CAN-SPAM:** Physical address + unsubscribe link in every email; compliant sender identity
- **Opt-out:** Honored immediately (same-day suppression); stored in `config/suppression_list.csv`
- **No purchased lists:** Only manually researched contacts
- **Honest subject lines:** No deceptive language; pre-send spam-trigger check
- See `Outbound_Theater_Automation_System/Compliance/` for full documentation

---

## Running the Sequence

```bash
# Show current stats (no sends)
python3 run_sequence.py --stats

# Dry run — renders templates, validates compliance, does not send
python3 run_sequence.py --dry-run

# Test mode — sends to seed addresses only
python3 run_sequence.py --test-mode --seed-file data/seed_lists/seed_list.csv

# Live run — sends to real contacts per throttle config
python3 run_sequence.py --live

# Run a specific step only
python3 run_sequence.py --live --step 1
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_crm_schema.py -v
pytest tests/test_importer.py -v
pytest tests/test_compliance.py -v
```

---

## Before First Live Send — Required Checklist

- [ ] Zoho sending domain configured (not free zoho.com subdomain)
- [ ] SPF, DKIM, DMARC DNS records verified
- [ ] Domain warm-up started at Week 1 (10/day cap)
- [ ] 25-seed inbox placement test completed (≥80% inbox)
- [ ] Physical mailing address set in `config/settings.yaml`
- [ ] Unsubscribe URL set and functional
- [ ] Email copy approved by Melissa Neufer and Zachary Gartrell
- [ ] `data/crm/leads.xlsx` populated with first batch of qualified venues
- [ ] Suppression list verified empty (no pre-existing opt-outs to carry over)

See `Outbound_Theater_Automation_System/PLAN.md` Phase 6-9 for the full pre-launch checklist.

---

## Implementation Roadmap

See [`Outbound_Theater_Automation_System/PLAN.md`](Outbound_Theater_Automation_System/PLAN.md) for the 10-phase implementation roadmap.

**Current phase:** Wave 1 — system build complete; awaiting operational setup (Zoho config, DNS, venue research)

---

## Audit Trail

Every system event is logged to `data/audit.db` (SQLite):

```python
from src.utils.audit import AuditLog
audit = AuditLog("data/audit.db")
events = audit.get_events(event_type="EMAIL_SENT", limit=50)
```

Event types: `LEAD_CREATED`, `LEAD_UPDATED`, `EMAIL_SENT`, `REPLY_RECEIVED`, `OPT_OUT`, `BOUNCE`, `MEETING_BOOKED`, `SHOW_BOOKED`
