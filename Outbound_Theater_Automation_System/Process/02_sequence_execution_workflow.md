# Sequence Execution Workflow
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Overview

The sequence execution workflow is the automated core of the outbound booking system. Once contacts are entered into the CRM (see `01_lead_intake_workflow.md`), this workflow handles all outbound email steps without requiring manual sends. It runs on a scheduled basis (typically once per day) and processes all eligible contacts in sequence order, subject to compliance, suppression, and daily throttle checks.

The workflow is implemented primarily in:
- `importer.py` — CRM data loading and contact filtering
- `sequence_builder.py` — Step resolution and template rendering
- `deliverability.py` — Compliance, suppression, throttle checks, and SMTP send
- `audit.py` — Audit log writing

---

## Sequence Definition: theater_outreach_v1

The sequence is defined in `sequences/theater_outreach_v1.yaml`. It consists of 4 steps sent over approximately 3 weeks:

| Step | Timing | Purpose |
|---|---|---|
| Step 1 | Day 1 | Initial introduction — show overview, audience description, booking inquiry |
| Step 2 | Day 5–7 | Follow-up — value focus, testimonial or press quote if available |
| Step 3 | Day 12–14 | Resource email — link to video clip, one-sheet PDF, or season planning frame |
| Step 4 | Day 18–21 | Closing step — final outreach, clear next step CTA |

After Step 4, the contact is considered "sequence complete." No further automated emails are sent. Human follow-up may continue outside the system.

**Step number meaning:**

| `step_number` value | State |
|---|---|
| `0` | Enrolled, no emails sent yet |
| `1` | Step 1 sent |
| `2` | Step 2 sent |
| `3` | Step 3 sent |
| `4` | Step 4 sent — sequence complete |

The automation engine only sends to contacts where `step_number < 4`. Contacts with `step_number = 4` are never re-enrolled automatically.

---

## Step-by-Step Execution Workflow

### Step 1: Load CRM Excel

**Module:** `importer.py`

The automation run begins by loading the CRM Excel workbook from the path specified in `config/settings.yaml` → `crm.file_path`.

```python
from importer import CRMImporter

importer = CRMImporter(config)
contacts = importer.load_contacts()       # Returns list of ContactRecord (Pydantic models)
companies = importer.load_companies()     # Returns list of VenueRecord
gig_leads = importer.load_gig_leads()    # Returns list of GigLeadRecord
```

`CRMImporter` uses `openpyxl` to read raw cell values and `pandas` for row iteration and field mapping. Each row is validated against the `ContactRecord` Pydantic model. Rows that fail validation are skipped and logged to the console with a `VALIDATION_ERROR` message — they do not cause the run to abort.

**What importer.py does NOT do:**
- It does not write to the Excel file (reads are safe to run any time)
- It does not filter contacts (filtering happens in Step 2)
- It does not validate email syntax beyond Pydantic field validation

---

### Step 2: Filter Eligible Contacts

**Module:** `importer.py` → `get_eligible_contacts()`

After loading all contacts, apply the eligibility filter. A contact is eligible for the current run if and only if ALL of the following are true:

| Condition | Field | Required value |
|---|---|---|
| Sequence enrolled | `Custom1` (sequence_id) | Not blank, must match a known sequence YAML filename |
| Sequence not complete | `Custom2` (step_number) | Integer value `< 4` |
| Not opted out | `Custom5` (email_opt_out_flag) | `No` |
| Not opted out (display field) | `Email Opt Out` | `No` |
| Email present | `Email` | Non-blank, contains `@` |

**Additionally**, a contact is only sent the *next* step if sufficient time has elapsed since the last send. The minimum delay between steps is defined in the sequence YAML under `step_delay_days`. The system compares `Custom3` (send_time) against the current date.

```python
eligible = importer.get_eligible_contacts(
    contacts=contacts,
    sequence_definitions=sequence_defs,
    today=date.today()
)
```

**Contacts excluded from this run:**
- `step_number` is blank or non-numeric → logged as `VALIDATION_SKIP`
- `step_number >= 4` → sequence complete, silently skipped
- `email_opt_out = Yes` → silently skipped (opt-out already honored)
- `Email` is blank → logged as `NO_EMAIL_SKIP`
- Step delay not yet elapsed → silently skipped, will be picked up on next run

---

### Step 3: Determine the Next Step for Each Contact

**Module:** `sequence_builder.py` → `SequenceBuilder.get_next_step()`

For each eligible contact, determine which step to send:

```
next_step_number = contact.step_number + 1
```

Load the step definition from the sequence YAML:

```yaml
# sequences/theater_outreach_v1.yaml
steps:
  - step_number: 1
    template: templates/step1_intro.j2
    subject: "Family theater inquiry: Princess Peigh's Sword Fighting Tea Party"
    step_delay_days: 0      # send immediately on first run
  - step_number: 2
    template: templates/step2_followup.j2
    subject: "Following up — Princess Peigh Adventures"
    step_delay_days: 5
  - step_number: 3
    template: templates/step3_resource.j2
    subject: "Resources + touring dates — Princess Peigh's Tea Party"
    step_delay_days: 12
  - step_number: 4
    template: templates/step4_closing.j2
    subject: "Last note from Tall People Performing Company"
    step_delay_days: 18
```

If the step definition for `next_step_number` does not exist in the YAML, the contact is skipped and a `SEQUENCE_DEFINITION_ERROR` is logged.

---

### Step 4: Run CAN-SPAM Compliance Check

**Module:** `deliverability.py` → `CANSPAMChecker.validate()`

Before rendering or sending anything, run the compliance check. This check validates that the outgoing email will include all required CAN-SPAM elements.

```python
checker = CANSPAMChecker(config)
result = checker.validate(contact=contact, step_def=step_def)
if not result.passed:
    audit.write(event_type="COMPLIANCE_BLOCK", ...)
    continue  # skip this contact, do not send
```

**What `CANSPAMChecker.validate()` checks:**

| Check | Source | Failure behavior |
|---|---|---|
| Sender name present | `config.compliance.sender_name` | Block send, log COMPLIANCE_BLOCK |
| Physical mailing address present | `config.compliance.physical_address` | Block send, log COMPLIANCE_BLOCK |
| Unsubscribe URL present | `config.compliance.unsubscribe_url` | Block send, log COMPLIANCE_BLOCK |
| Subject line not blank | `step_def.subject` | Block send, log COMPLIANCE_BLOCK |
| Recipient email present | `contact.email` | Block send (shouldn't reach here if Step 2 filter ran) |
| `email_opt_out` is `No` | `contact.custom5` | Block send, log COMPLIANCE_BLOCK |

A `COMPLIANCE_BLOCK` event is a non-fatal run error. The run continues to the next contact. The blocked contact will be retried on the next run — if the config issue is fixed, it will pass on the next attempt. If not, it will be blocked again.

**Operator action required:** Review `COMPLIANCE_BLOCK` events in the audit log after every run. These indicate a misconfiguration that is preventing sends.

---

### Step 5: Check Suppression List

**Module:** `deliverability.py` → `SuppressionList.is_suppressed()`

Look up the contact's email address in `config/suppression_list.csv`.

```python
suppression = SuppressionList(config)
if suppression.is_suppressed(contact.email):
    audit.write(event_type="SUPPRESSED_SKIP", ...)
    continue
```

The suppression check is case-insensitive (all emails are lowercased before comparison). If the email is on the suppression list for any reason (`OPT_OUT`, `HARD_BOUNCE`, `SOFT_BOUNCE`, `MANUAL`), the contact is skipped silently for this run.

Suppressed contacts are never automatically removed from the suppression list by the automation engine. Removal (if ever warranted) is a manual process with a documented reason — see `suppression_list_management.md`.

---

### Step 6: Check Daily Throttle

**Module:** `deliverability.py` → `ThrottleGuard.check()`

Before sending, verify that the daily send counter has not reached the configured maximum.

```python
throttle = ThrottleGuard(config, audit_db)
if throttle.daily_count_reached():
    audit.write(event_type="THROTTLE_HIT", ...)
    break  # stop the entire run — do not process further contacts today
```

The daily limit is read from `config/settings.yaml` → `sequence.max_sends_per_day`. This value must be set according to the current week in the domain warming schedule (see `domain_warming_schedule.md`).

| Warming week | `max_sends_per_day` |
|---|---|
| Week 1 | 10 |
| Week 2 | 25 |
| Week 3 | 50 |
| Week 4+ | 100 |

`ThrottleGuard` counts `EMAIL_SENT` events in the audit log for the current calendar day (UTC). It does not rely on an in-memory counter that could be reset by a process restart.

When `THROTTLE_HIT` is logged, the run stops immediately. Remaining eligible contacts are processed on the next scheduled run. The order in which contacts are processed is stable (sorted by `UniqueId` ascending) so that no contact is permanently disadvantaged by throttle cutoffs.

---

### Step 7: Render the Email Template

**Module:** `sequence_builder.py` → `SequenceBuilder.render()`

With all checks passed, render the email body using the Jinja2 template specified in the step definition.

```python
builder = SequenceBuilder(config)
email_payload = builder.render(contact=contact, step_def=step_def, company=company)
```

**Available Jinja2 merge fields:**

| Variable | Source |
|---|---|
| `{{ contact.first_name }}` | Contacts sheet, First Name |
| `{{ contact.last_name }}` | Contacts sheet, Last Name |
| `{{ contact.title }}` | Contacts sheet, Title |
| `{{ company.name }}` | Companies sheet, Name |
| `{{ company.city }}` | Companies sheet, City |
| `{{ company.state }}` | Companies sheet, State |
| `{{ config.compliance.sender_name }}` | settings.yaml |
| `{{ config.compliance.physical_address }}` | settings.yaml |
| `{{ config.compliance.unsubscribe_url }}` | settings.yaml |
| `{{ show.name }}` | settings.yaml → `show.name` |

**Template rendering rules:**
- All templates must include the unsubscribe footer (enforced by base template)
- Templates must not include any personalization token that could be `None` without a fallback — always use `{{ variable | default('') }}`
- Rendered output is a `EmailPayload` Pydantic object with fields: `to`, `subject`, `body_html`, `body_text`, `from_name`, `from_email`, `reply_to`

If rendering fails (e.g., template not found, Jinja2 syntax error), the contact is skipped and a `RENDER_ERROR` is logged. The run continues.

---

### Step 8: Send via Zoho SMTP

**Module:** `deliverability.py` → `DeliverabilityGuard.send_step()`

Submit the rendered email payload via Zoho Mail SMTP.

```python
guard = DeliverabilityGuard(config)
result = guard.send_step(payload=email_payload)
```

**SMTP configuration** (from `config/settings.yaml`):

```yaml
zoho_smtp:
  host: smtp.zoho.com
  port: 587
  use_tls: true
  username: "bookings@yourdomainhere.com"
  password: "${ZOHO_SMTP_PASSWORD}"    # loaded from environment variable
```

**SMTP password security:** The password must never be stored in plain text in `settings.yaml`. Use an environment variable (`ZOHO_SMTP_PASSWORD`) and reference it with `${VAR_NAME}` syntax. Load it at runtime using `os.environ`.

**Connection retry:** `send_step` will attempt SMTP connection up to 3 times with a 5-second delay between attempts. If all 3 attempts fail:
- Log `SMTP_FAILURE` event to audit log
- Skip this contact
- Continue to next contact

**SMTP response codes:**

| Code range | Meaning | System action |
|---|---|---|
| 2xx | Success | Proceed to Step 9 |
| 4xx | Temporary failure (soft bounce) | Log SOFT_BOUNCE, retry per bounce rules |
| 5xx | Permanent failure (hard bounce) | Log HARD_BOUNCE, add to suppression immediately |

---

### Step 9: Update step_number and send_time in CRM

**Module:** `importer.py` → `CRMImporter.update_contact()`

After a confirmed successful send (2xx SMTP response), immediately update the contact row in the CRM Excel file:

```python
importer.update_contact(
    contact_unique_id=contact.unique_id,
    step_number=next_step_number,
    send_time=datetime.utcnow().isoformat()
)
importer.save()
```

**Fields updated:**

| Field | New value |
|---|---|
| `Custom2` (step_number) | `next_step_number` (e.g., `1` after first send) |
| `Custom3` (send_time) | ISO 8601 UTC timestamp of send |

**Critical:** The CRM update and the audit event (Step 10) must both succeed. If the CRM write fails after the email was sent, the contact will appear eligible for re-send on the next run and may receive a duplicate email. `CRMImporter.update_contact()` raises an exception on write failure — the audit event is only written after a successful CRM update.

---

### Step 10: Write EMAIL_SENT Audit Event

**Module:** `audit.py` → `AuditLog.write()`

Write a complete audit event to `audit_log.db`:

```python
audit.write(
    event_type="EMAIL_SENT",
    contact_unique_id=contact.unique_id,
    company_unique_id=contact.company_unique_id,
    audit_trail_id=contact.audit_trail_id,
    step_number=next_step_number,
    sequence_id=contact.sequence_id,
    sent_at=send_timestamp,
    subject=email_payload.subject,
    smtp_response_code=result.code,
    operator="system"
)
```

**Audit event schema for EMAIL_SENT:**

| Field | Type | Description |
|---|---|---|
| `event_id` | UUID4 (auto) | Unique ID for this event row |
| `event_type` | string | `EMAIL_SENT` |
| `timestamp` | ISO 8601 UTC | When the event was recorded |
| `contact_unique_id` | string | CON-XXXXXX |
| `company_unique_id` | string | VEN-XXXXXX |
| `audit_trail_id` | UUID4 | Links to contact's audit trail |
| `step_number` | integer | Step that was sent |
| `sequence_id` | string | `theater_outreach_v1` |
| `sent_at` | ISO 8601 UTC | SMTP send timestamp |
| `subject` | string | Email subject line |
| `smtp_response_code` | integer | SMTP response code |
| `operator` | string | `system` for automated sends |

---

### Step 11: Sleep Before Next Send

After a successful send (Steps 8–10 complete), the run pauses before processing the next contact:

```python
import time
time.sleep(config.sequence.delay_between_sends_seconds)
```

The default delay is `90` seconds (`delay_between_sends_seconds: 90` in `settings.yaml`). This delay:
- Prevents burst sending patterns that trigger spam filters
- Spreads sends across a longer time window, which looks more like human behavior to receiving mail servers
- Gives time for any transient SMTP server issues to resolve

The delay applies between every send. If a contact is skipped (suppressed, throttled, compliance-blocked), no delay is applied — the run proceeds immediately to the next contact.

---

## Run Invocation

Run the sequence execution manually:

```bash
python3 scripts/run_sequence.py --config config/settings.yaml
```

Run with dry-run mode (no sends, no CRM writes, logs to console only):

```bash
python3 scripts/run_sequence.py --config config/settings.yaml --dry-run
```

Schedule via cron (example: run at 9:00 AM Eastern daily):

```
0 14 * * 1-5 /usr/bin/python3 /path/to/scripts/run_sequence.py --config /path/to/config/settings.yaml >> /path/to/logs/sequence_run.log 2>&1
```

(14:00 UTC = 9:00 AM EST / 10:00 AM EDT)

---

## Post-Run Checklist

After each automated run, review the following:

- [ ] Check console output or `logs/sequence_run.log` for any `VALIDATION_ERROR`, `COMPLIANCE_BLOCK`, or `RENDER_ERROR` entries
- [ ] Open `audit_log.db` and query: `SELECT * FROM events WHERE date(timestamp) = date('now') ORDER BY timestamp DESC LIMIT 50`
- [ ] Confirm `EMAIL_SENT` count matches expected number of sends for the day
- [ ] Confirm no `THROTTLE_HIT` events (if there are, no further sends happened today — check if this was expected)
- [ ] Check Zoho Mail sent folder to spot-check that emails arrived in sent
- [ ] Check for any new replies in the Zoho inbox — classify and route per `reply_categories.md`

---

## Common Errors and Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No contacts processed | All contacts at step_number >= 4 | Check step_number values; confirm leads were added correctly |
| Contact sent duplicate email | CRM write failed after SMTP success | Check audit log for SMTP_FAILURE or file write error; correct step_number manually |
| All sends blocked as COMPLIANCE_BLOCK | Config missing physical_address or unsubscribe_url | Update `config/settings.yaml` compliance section |
| THROTTLE_HIT on first contact | max_sends_per_day = 0 or already reached today | Check config; check if run was already executed today |
| SMTP_FAILURE on all contacts | Zoho SMTP credentials wrong or ZOHO_SMTP_PASSWORD env var not set | Verify credentials, check env var is exported |
| Template renders with blank name | Contact first_name is blank in CRM | Fix CRM data; ensure `\| default('')` is in template |
| Runs but no audit events written | SQLite DB path wrong or permissions issue | Check `config.audit.db_path`, verify write permissions |

---

## Drop-In Reusability Notes

This sequence execution workflow is the most reusable module in the system. Its 11-step structure applies to any outbound email sequence, regardless of show, industry, or target audience.

To adapt for a new project:

1. **Sequence ID and YAML file:** Change `theater_outreach_v1` to a new sequence name. Create a corresponding YAML file in `sequences/`. The workflow code does not need to change — it reads the sequence ID from the CRM contact record.
2. **Number of steps:** The YAML-driven approach supports any number of steps. Change `step_number < 4` in the filter (Step 2) to `step_number < N` where N is the last step number, or make this value configurable in the sequence YAML itself.
3. **Step timing:** Adjust `step_delay_days` values in the sequence YAML. No code changes needed.
4. **Templates:** Replace Jinja2 templates in `templates/` for new show content. The merge field variable names remain the same as long as the CRM schema is unchanged.
5. **Throttle limits:** `max_sends_per_day` in `settings.yaml` is the only tunable needed for scaling up or down.
6. **Compliance config:** Update `compliance.sender_name`, `compliance.physical_address`, and `compliance.unsubscribe_url` in `settings.yaml` for a new sender identity. No code changes needed.
7. **CRM path:** Update `crm.file_path` in `settings.yaml`. The entire data layer is abstracted behind `CRMImporter` — swapping to a different Excel file requires only a config change.
8. **SMTP credentials:** Update `zoho_smtp` section in `settings.yaml` and set the new `ZOHO_SMTP_PASSWORD` environment variable. The SMTP layer is abstracted — if a future project uses a different provider (SendGrid, Mailgun), only `DeliverabilityGuard.send_step()` needs to change.
