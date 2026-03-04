# System Overview: Outbound Theater Booking Automation
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## 1. Problem This System Solves

Tall People Performing Company produces *Princess Peigh's Sword Fighting Tea Party*, a touring family theater show targeting community theaters, performing arts centers, libraries, and municipal cultural venues with 100–400 seats across a 1–3 state regional footprint.

Outbound booking for a touring show is a high-volume, relationship-sensitive communication task. Without automation:

- Contacts slip through the cracks between research and first outreach
- Follow-up sequences are inconsistent — some venues receive one email, others receive none
- There is no audit trail to confirm what was sent, to whom, and when
- Compliance risks (CAN-SPAM opt-outs, bounce handling) are handled ad hoc or not at all
- Small teams like Melissa Neufer and Zachary Gartrell spend most of their time on manual logistics rather than relationship work

This system replaces ad hoc outreach with a structured, repeatable process. It automates the mechanical steps — sequencing, rendering, sending, logging — while keeping humans in control of all relationship decisions (reply drafting, follow-up strategy, booking negotiations). The result is a consistent, auditable, compliant outbound campaign that scales with the team's capacity rather than against it.

---

## 2. Target Venue Profile

| Attribute | Value |
|---|---|
| Venue types | Community theaters, performing arts centers, libraries, municipal cultural venues |
| Seat capacity | 100–400 seats |
| Geographic scope | 1–3 state regional targeting |
| Decision makers | Programming Director, Executive Director, Family Series Coordinator |
| Programming style | Family series, children's programming, community events |

---

## 3. Who Operates This System

| Person | Role |
|---|---|
| **Melissa Neufer** | Lead researcher, CRM data entry, reply triage, escalation recipient for Interested replies |
| **Zachary Gartrell** | Sequence oversight, reply drafting (Budget/Programming Window), new lead creation from Referrals, escalation recipient for Interested replies |

Both operators share access to the CRM Excel file and the audit log. Neither has unilateral authority to send replies — all outbound reply drafts require human approval before sending.

---

## 4. Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| CRM data layer | Microsoft Excel (.xlsx) via openpyxl and pandas |
| Data validation | Pydantic (VenueRecord, ContactRecord, GigLeadRecord models) |
| Email templating | Jinja2 |
| Email delivery | Zoho Mail SMTP |
| Audit logging | SQLite (audit_log.db) |
| Configuration | YAML (config/settings.yaml) |
| Suppression list | CSV (config/suppression_list.csv) |

---

## 5. The 6 Subsystems and How They Interact

The system is structured as a linear pipeline with feedback loops. Each subsystem has a defined input and output. Data flows forward through the pipeline; errors and opt-outs flow backward into the suppression and audit systems.

```
┌─────────────────────┐
│   1. LEAD SOURCING  │  Research venues, find contacts, qualify
└────────┬────────────┘
         │ VenueRecord, ContactRecord, GigLeadRecord written to CRM Excel
         ▼
┌─────────────────────┐
│   2. CRM (Excel)    │  Companies, Contacts, Gigs_Leads sheets
│                     │  Custom fields: sequence_id, step_number,
│                     │  send_time, reply_category, audit_trail_id
└────────┬────────────┘
         │ importer.py reads eligible contacts
         ▼
┌─────────────────────┐
│   3. SEQUENCE       │  SequenceBuilder: loads YAML steps, renders
│      BUILDER        │  Jinja2 templates per contact
└────────┬────────────┘
         │ Rendered email payload
         ▼
┌─────────────────────┐
│   4. ZOHO SEND      │  DeliverabilityGuard: compliance check,
│      (SMTP)         │  suppression check, throttle check, SMTP send
└────────┬────────────┘
         │ SMTP response / bounce signal
         ▼
┌─────────────────────┐
│   5. REPLY          │  Inbox monitoring, reply classification,
│      HANDLING       │  CRM update, human escalation routing
└────────┬────────────┘
         │ All events (sends, bounces, replies, opt-outs)
         ▼
┌─────────────────────┐
│   6. AUDIT LOG      │  SQLite audit_log.db — append-only event log
│      (SQLite)       │  for every system action
└─────────────────────┘
```

### Subsystem Descriptions

#### 5.1 Lead Sourcing
Melissa Neufer researches venues using the qualification criteria (see `01_lead_intake_workflow.md`). Qualified venues and their primary contacts are entered into the CRM Excel file. Each new contact receives a `sequence_id`, an initial `step_number = 0`, and a UUID4 `audit_trail_id`. A `LEAD_CREATED` event is written to the audit log.

#### 5.2 CRM (Excel/CSV)
The CRM is a structured Excel workbook with three primary sheets:

- **Companies:** One row per venue (VenueRecord)
- **Contacts:** One row per person (ContactRecord), linked to Companies by `company_unique_id`
- **Gigs_Leads:** One row per booking opportunity (GigLeadRecord), linking a venue and a primary contact with a `status` field

Custom fields on the Contacts sheet drive the automation engine:

| Field | Purpose |
|---|---|
| `Custom1` (sequence_id) | Which outreach sequence to run |
| `Custom2` (step_number) | How many steps have been sent (0 = not yet started) |
| `Custom3` (send_time) | Timestamp of last send |
| `Custom4` (reply_category) | How the most recent reply was classified |
| `Custom5` (email_opt_out) | Yes/No opt-out flag |
| `Custom8` (audit_trail_id) | UUID4 linking all events for this contact |

#### 5.3 Sequence Builder
`SequenceBuilder` (in `sequence_builder.py`) reads the YAML sequence definition (`sequences/theater_outreach_v1.yaml`). For each eligible contact, it determines the next step, loads the appropriate Jinja2 template, and renders the email body and subject line with contact-specific merge fields. Output is a structured email payload object validated by Pydantic.

#### 5.4 Zoho Send (SMTP)
`DeliverabilityGuard` (in `deliverability.py`) is the final gate before any email leaves the system. Before each send it:

1. Runs `CANSPAMChecker.validate()` to confirm required fields are present
2. Checks `suppression_list.csv` for the recipient address
3. Checks the daily send counter against `max_sends_per_day` from config
4. Submits the email via Zoho Mail SMTP
5. Records the SMTP response code

After a successful send, it updates `step_number` and `send_time` in the CRM and writes an `EMAIL_SENT` event to the audit log.

#### 5.5 Reply Handling
Replies are classified into 8 categories (see `reply_categories.md`). Classification can be assisted by keyword detection, but a human reviews every reply before any CRM update is finalized or any response is drafted. No auto-responses are sent. Escalation routing follows the rules in `escalation_rules.md`.

#### 5.6 Audit Log (SQLite)
`audit_log.db` is an append-only SQLite database. Every system action — lead creation, email send, bounce, opt-out, reply classification — is written as a timestamped event row. The audit log is the authoritative record for compliance and troubleshooting. It is never edited or deleted from. Exports for compliance review use the read-only query interface in `audit.py`.

---

## 6. Data Flow Summary

```
Research → Excel CRM entry → importer.py reads eligible contacts
→ SequenceBuilder renders step → DeliverabilityGuard validates + sends
→ CRM updated (step_number++, send_time) → audit_log.db event written
→ Inbox monitored for replies → reply classified by human
→ CRM updated (reply_category, opt_out if applicable)
→ audit_log.db reply event written → escalation routed per rules
```

---

## 7. Configuration Reference

All tunable parameters live in `config/settings.yaml`. Key fields:

```yaml
zoho_smtp:
  host: smtp.zoho.com
  port: 587
  username: "bookings@yourdomainhere.com"

sequence:
  default_sequence_id: theater_outreach_v1
  delay_between_sends_seconds: 90
  max_sends_per_day: 50        # adjust per warming schedule week

warming:
  current_week: 3              # increment each week during warm-up

compliance:
  sender_name: "Tall People Performing Company"
  physical_address: "123 Main St, City, State, ZIP"
  unsubscribe_url: "https://yourdomainhere.com/unsubscribe"
```

---

## 8. Failure Modes and Safe Defaults

| Failure | System behavior |
|---|---|
| SMTP connection failure | Log error, skip contact, retry on next run |
| Daily throttle reached | Stop run, log THROTTLE_HIT event, resume next day |
| Suppression list hit | Skip contact silently, log SUPPRESSED event |
| CAN-SPAM check fails | Abort send, log COMPLIANCE_BLOCK event, alert operator |
| Hard bounce received | Immediately add to suppression, log HARD_BOUNCE event |
| Soft bounce (1st or 2nd) | Log SOFT_BOUNCE, retry within 7 days |
| Soft bounce (3rd) | Add to suppression, log SOFT_BOUNCE_MAX event |
| Reply received | Flag for human review, no automated response sent |

---

## Drop-In Reusability Notes

This system overview is designed to be reusable as a template for any outbound theatrical booking automation project. To adapt it for a new show or company:

1. **Replace show/company identity** in the header block and Section 1. The problem statement language is generic enough to require only minor edits.
2. **Update the venue profile table** (Section 2) with the new show's target venue type, seat range, and geography.
3. **Update operator names** (Section 3) with the new project's team members.
4. **The technology stack** (Section 4) is fully reusable without changes unless the new project changes tools.
5. **The 6-subsystem pipeline diagram** (Section 5) is architecture-level and reusable for any sequence-based outbound email system.
6. **Configuration reference** (Section 7): update SMTP credentials, sender identity, and physical address in `settings.yaml` — the config structure itself does not change.
7. **Failure modes table** (Section 8) is fully reusable without modification.

The core insight this document encodes — that a small team can run a compliant, auditable outbound campaign by automating the mechanical steps while keeping humans in control of relationship decisions — applies to any touring performing arts organization.
