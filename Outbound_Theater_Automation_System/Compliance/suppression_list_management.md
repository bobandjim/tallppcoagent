# Suppression List Management
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Overview

The suppression list is the system's central registry of email addresses that must never receive outbound email from this campaign. Every send is checked against this list before delivery. No email is sent to a suppressed address under any circumstances.

The suppression list is an append-only record. Entries are never deleted — they are archived permanently. This creates a durable compliance record and prevents accidentally re-sending to addresses that should be excluded.

---

## File Location and Format

**File path:** `config/suppression_list.csv`

**Format:** CSV (comma-separated values), UTF-8 encoding, no BOM

**Column schema:**

| Column | Type | Description |
|---|---|---|
| `email` | string | The full email address to suppress (lowercase) |
| `reason` | string | Why the address was suppressed (see Valid Reasons below) |
| `suppressed_at` | string | ISO 8601 UTC timestamp of when suppression was added |

**Example file contents:**

```csv
email,reason,suppressed_at
john.doe@exampletheater.org,OPT_OUT,2026-03-05T14:22:00Z
booking@northstage.com,HARD_BOUNCE,2026-03-06T09:14:33Z
info@riverfrontarts.org,SOFT_BOUNCE,2026-03-08T16:45:00Z
director@oldtownplayhouse.com,MANUAL,2026-03-10T11:00:00Z
```

**Header row is required.** The first row must be the column names exactly as shown above. Do not add extra columns. Do not reorder columns.

---

## Valid Suppression Reasons

| Reason | When used |
|---|---|
| `OPT_OUT` | Contact replied asking to unsubscribe, clicked unsubscribe link, or otherwise clearly requested removal |
| `HARD_BOUNCE` | Email resulted in a permanent delivery failure (5xx SMTP code, invalid address, domain does not exist) |
| `SOFT_BOUNCE` | Email failed delivery 3 times over 7 days — treated as permanent for list hygiene purposes |
| `MANUAL` | Added manually by Melissa Neufer or Zachary Gartrell for any other reason (e.g., personal request not captured by system, known bad address from external source, legal hold) |

Do not use any other reason codes. Non-standard reason codes will cause the `SuppressionList` class to log a `SUPPRESSION_LOAD_WARNING` but will still enforce the suppression.

---

## Append-Only Rule

**Never delete rows from `suppression_list.csv`.**

This is a hard rule with no exceptions. If you believe an entry should be removed, you have two options:

1. **Add a note** by appending a new column `notes` to that specific row (the parser ignores extra columns) — but do not delete the row
2. **Contact Zachary Gartrell** to discuss whether removal is appropriate — removal requires documented justification and is extremely rare

If you need to "archive" old suppressions, copy the entire file with a dated filename (e.g., `suppression_list_archive_2026-03-01.csv`) — but the active `suppression_list.csv` file retains all entries.

**Why this matters:** Deleting an entry and then re-sending to that address could result in a CAN-SPAM violation if the address was suppressed due to an opt-out request. The append-only rule is a compliance safeguard, not a technical limitation.

---

## How to Add a Suppression Entry

### Method 1: Programmatic — SuppressionList.add() (Preferred)

Use the `SuppressionList` class in `compliance.py` to add entries programmatically. This method ensures correct formatting, lowercase normalization, and automatic timestamp generation.

```python
from compliance import SuppressionList

suppression = SuppressionList(config)

suppression.add(
    email="john.doe@exampletheater.org",
    reason="OPT_OUT"
)
```

`SuppressionList.add()` will:
- Normalize the email to lowercase
- Check if the email is already in the list (duplicate suppression is idempotent — adding again does nothing, no error raised)
- Append the new row to `config/suppression_list.csv` with the current UTC timestamp
- Write a `SUPPRESSION_ADDED` event to the audit log

### Method 2: Command Line Script

```bash
python3 scripts/add_suppression.py \
  --email "john.doe@exampletheater.org" \
  --reason OPT_OUT \
  --notes "Replied to Step 2 asking to be removed"
```

### Method 3: Manual CSV Edit (Use Only If System Is Unavailable)

If the system is unavailable and you must add a suppression immediately:

1. Open `config/suppression_list.csv` in a text editor (not Excel — Excel may corrupt the formatting)
2. Add a new row at the end of the file:
   ```
   email@domain.com,OPT_OUT,2026-03-04T15:30:00Z
   ```
3. Ensure the email is lowercase
4. Ensure the timestamp is in ISO 8601 UTC format (`YYYY-MM-DDTHH:MM:SSZ`)
5. Save the file as UTF-8 with no BOM
6. Manually write an audit log entry using the script as soon as the system is available:
   ```bash
   python3 scripts/write_audit_event.py --event_type SUPPRESSION_ADDED --email email@domain.com --reason OPT_OUT --notes "Added manually — system was unavailable"
   ```

---

## How Suppression Is Checked Before Every Send

`DeliverabilityGuard` calls `SuppressionList.is_suppressed()` before every send:

```python
suppression = SuppressionList(config)

if suppression.is_suppressed(contact.email):
    audit.write(event_type="SUPPRESSED_SKIP", contact_unique_id=contact.unique_id, ...)
    continue  # skip to next contact
```

`is_suppressed()` loads the CSV into memory at the start of each run and performs a case-insensitive lookup. The in-memory list is rebuilt from the file at the start of each automation run — changes to the CSV take effect on the next run without restarting any service.

**Suppression check is the second-to-last gate** before any email is sent (after compliance check, before throttle check). Even if a contact passed the CRM filter, if their email appears in the suppression list, they will not receive email.

---

## Audit Events Related to Suppression

All suppression-related actions are logged to `audit_log.db`:

| Event type | When logged |
|---|---|
| `SUPPRESSION_ADDED` | Any time a new address is added to the suppression list |
| `SUPPRESSED_SKIP` | Any time a send is skipped because the address is suppressed |
| `OPT_OUT` | Specifically when reason is `OPT_OUT` (in addition to `SUPPRESSION_ADDED`) |
| `HARD_BOUNCE` | When a hard bounce adds an address to suppression |
| `SOFT_BOUNCE_MAX` | When a 3rd soft bounce adds an address to suppression |

Query the audit log to see all suppressions:
```sql
SELECT * FROM events WHERE event_type = 'SUPPRESSION_ADDED' ORDER BY timestamp DESC;
```

Query to see how many sends were blocked by suppression this month:
```sql
SELECT COUNT(*) FROM events
WHERE event_type = 'SUPPRESSED_SKIP'
AND timestamp >= date('now', 'start of month');
```

---

## Monthly Review Process

Perform a monthly review of the suppression list. The review does not result in deletions — it is an audit of list health and an opportunity to identify patterns.

**Monthly review checklist:**

- [ ] Open `config/suppression_list.csv` and count total entries
- [ ] Count entries by reason: `OPT_OUT`, `HARD_BOUNCE`, `SOFT_BOUNCE`, `MANUAL`
- [ ] Check for any entries added in the past 30 days — confirm each was correctly categorized
- [ ] For `HARD_BOUNCE` entries: check whether the domain still appears valid (if the venue has changed staff or domain, the old address is still invalid — keep the suppression)
- [ ] For `SOFT_BOUNCE` entries: check if enough time has passed (90+ days) and if the domain now appears healthy. **Never automatically remove — document reasoning if removal is considered and escalate to Zachary Gartrell**
- [ ] For `OPT_OUT` entries: do not remove — opted-out contacts must remain suppressed indefinitely unless they provide documented re-consent
- [ ] For `MANUAL` entries: review each one to confirm it is still appropriate
- [ ] Write a summary note in the audit log:
  ```bash
  python3 scripts/write_audit_event.py --event_type SUPPRESSION_REVIEW \
    --operator "Melissa Neufer" \
    --notes "Monthly review complete. 47 total suppressions: 22 OPT_OUT, 15 HARD_BOUNCE, 7 SOFT_BOUNCE, 3 MANUAL. No changes made."
  ```

---

## Exporting for External Use

The suppression list may need to be shared with a third-party email service or reviewed by an external compliance auditor.

**Safe export procedure:**

1. Copy `config/suppression_list.csv` to a new file with a date-stamped name: `suppression_export_2026-03-01.csv`
2. Share the copied file — never share the live `config/suppression_list.csv` directly
3. Do not share `audit_log.db` externally — the SQLite database contains more sensitive operational data than the suppression CSV

**Do not share the suppression list outside the team without explicit authorization from Zachary Gartrell.** The list contains email addresses that may constitute personally identifiable information depending on applicable privacy laws.

---

## Edge Cases

### Contact opts out via reply but email_opt_out flag wasn't updated in CRM

If you discover that a contact opted out and is in the suppression list but their CRM record still shows `email_opt_out = No`:

1. Open the CRM Excel file
2. Find the contact's row in the Contacts sheet
3. Set `Email Opt Out` to `Yes` and `Custom5` to `Yes`
4. Save the file
5. The contact will now be filtered at the CRM eligibility filter stage as well (belt and suspenders — the suppression list is the primary safeguard, but the CRM flag should match)

### Venue has multiple contacts and one opts out

If Contact A at a venue opts out but Contact B at the same venue is also in the CRM:

- Only Contact A's email address is suppressed
- Contact B continues in the sequence unless they also opt out or the Gigs_Leads record is closed
- Do not suppress the entire venue based on one contact's opt-out — the opt-out applies to the individual, not the organization (unless the opt-out message explicitly says "please do not contact anyone at our organization")

### Email address changed and old address was suppressed

If a venue contact's email has changed (e.g., they moved to a new organization) and you want to add the new address:

- The new email address is not suppressed — it can be added as a new ContactRecord with the new email
- The old email address remains in the suppression list (it may still be active at the old organization)
- Create a new ContactRecord for the new organization rather than editing the old one

---

## Drop-In Reusability Notes

This suppression list management document and the associated `SuppressionList` class are fully reusable for any outbound email campaign without modification.

To adapt for a new project:

1. **File path:** The suppression list is at `config/suppression_list.csv`. If the new project uses a different directory structure, update the path reference in this document and in `config/settings.yaml` → `suppression.file_path`.
2. **Reason codes:** `OPT_OUT`, `HARD_BOUNCE`, `SOFT_BOUNCE`, `MANUAL` are the four standard reason codes. They cover all cases for any outbound campaign. Add new reason codes only if a genuinely new category arises (e.g., `LEGAL_HOLD` for contacts under litigation-related communication restrictions) — and update the `SuppressionList` class's validation set.
3. **Append-only rule:** This rule applies to every project without exception. It is a compliance safeguard, not a project-specific convention.
4. **Monthly review checklist:** The checklist is generic and reusable for any project. Update the operator names (Melissa Neufer, Zachary Gartrell) to the new project's team.
5. **Audit event types:** `SUPPRESSION_ADDED`, `SUPPRESSED_SKIP`, and `SUPPRESSION_REVIEW` are generic event types that work for any project using the same audit schema.
6. **Export procedure:** The procedure is generic and applicable to any project. Update the filename convention (date-stamp format) if the new project uses a different naming standard.
7. **Edge cases:** The three edge cases documented here (CRM flag mismatch, multi-contact venue opt-out, changed email address) are universal patterns in outbound B2B email. They apply to any project targeting organizations with multiple contacts.
