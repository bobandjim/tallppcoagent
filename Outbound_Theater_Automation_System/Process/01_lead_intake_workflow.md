# Lead Intake Workflow
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Overview

The lead intake workflow is the first step in the outbound booking pipeline. Its purpose is to transform a raw venue discovery — a website, a directory listing, a referral — into a fully qualified, correctly formatted CRM record that is ready for automated sequence execution. This workflow is performed manually by Melissa Neufer or Zachary Gartrell.

A lead is not considered "in the system" until all 10 steps below are complete and the Excel file is saved. Partial records are a source of sequencing errors and compliance failures; do not leave incomplete rows.

---

## Qualification Criteria

Before a venue enters the CRM, it must pass the following qualification checks. If a venue fails any criterion, do not create a record — note it in a separate "Reviewed / Not Qualified" log if useful for future reference.

| Criterion | Requirement |
|---|---|
| Venue type | Community theater, performing arts center, public library with performance space, or municipal cultural venue |
| Seat capacity | 100–400 seats |
| Geographic region | Within the current 1–3 state regional target (check `config/settings.yaml` → `targeting.states`) |
| Programming type | Books or has booked family programming, children's series, or general-audience touring shows |
| Contact reachability | A direct contact email is findable or inferable from the domain |
| Not already in CRM | UniqueId does not already exist in Companies sheet |

---

## Step-by-Step Workflow

### Step 1: Research the Venue

Use the venue's website, local arts council directories, state performing arts association listings, and the venue's social media presence to confirm:

- Legal venue name and any DBA/brand name
- Physical mailing address (required for CAN-SPAM compliance record)
- Website URL
- Seat capacity (check "About," "Rentals," or "Technical Specifications" pages)
- Proof of family or children's programming history (past season listings, current season, press releases)
- Geographic state confirmation

**Do not proceed** if seat capacity is unverifiable and you cannot find any evidence of family programming history.

---

### Step 2: Find the Primary Contact

Identify the single best contact for booking inquiry at this venue. Priority order:

1. **Programming Director** — decision-maker for season content selection
2. **Executive Director** — ultimate authority, appropriate if no Programming Director exists
3. **Family Series Coordinator** — appropriate if the venue has a dedicated family series

**Sources to check:**
- Venue website "Staff" or "About" page
- LinkedIn (search: `"[Venue Name]" Programming Director`)
- State performing arts association directories
- Previous show press releases naming the booking contact

**Email finding methods (in order of preference):**
1. Direct listing on venue website
2. LinkedIn profile with public email
3. Pattern inference: if other staff emails follow `firstname.lastname@domain.com`, apply the pattern
4. Press inquiry contact form (use only if no direct email is findable — note in record)

If no contact can be found with a verifiable or inferable email, do not create the contact record. Mark the venue as "Contact Not Found" in your research notes and revisit quarterly.

---

### Step 3: Populate VenueRecord in the Companies Sheet

Open the CRM Excel file. Navigate to the **Companies** sheet. Add a new row at the bottom with the following fields:

| Field | Value |
|---|---|
| `UniqueId` | Generate: `VEN-` + 6-digit zero-padded sequential number (e.g., `VEN-000047`) |
| `Name` | Full legal venue name |
| `Website` | Full URL including `https://` |
| `Record Type` | `Venue` |
| `Street` | Physical street address |
| `City` | City |
| `State` | Two-letter state abbreviation |
| `Zip` | ZIP code |
| `Phone` | Main venue phone (optional but recommended) |
| `Seat Capacity` | Integer (e.g., `250`) |
| `Venue Type` | One of: Community Theater / Performing Arts Center / Library / Municipal Cultural Venue |
| `Notes` | Any relevant context (e.g., "Books 2 family shows per season," "Renovation through June 2026") |
| `Created Date` | Today's date in YYYY-MM-DD format |
| `Created By` | Your first name |

**Validation rules:**
- `UniqueId` must be unique — check the column before assigning
- `State` must be in the configured target states list
- `Website` must begin with `https://` or `http://`
- Do not leave `Name`, `UniqueId`, `State`, or `Seat Capacity` blank

---

### Step 4: Populate ContactRecord in the Contacts Sheet

Navigate to the **Contacts** sheet. Add a new row with the following fields:

| Field | Value |
|---|---|
| `UniqueId` | Generate: `CON-` + 6-digit zero-padded sequential number (e.g., `CON-000083`) |
| `First Name` | Contact's first name |
| `Last Name` | Contact's last name |
| `Company UniqueId` | The `VEN-XXXXXX` ID from Step 3 |
| `Email` | Verified or inferred email address |
| `Title` | Job title (e.g., "Programming Director") |
| `Phone` | Direct phone if available |
| `Email Opt Out` | `No` (default for new contacts) |
| `Notes` | Source of email (e.g., "Website staff page," "LinkedIn," "Pattern inferred from domain") |
| `Created Date` | Today's date in YYYY-MM-DD format |
| `Created By` | Your first name |

**Custom fields (critical for automation):**

| Custom Field | Value | Purpose |
|---|---|---|
| `Custom1` (sequence_id) | `theater_outreach_v1` | Identifies which sequence to run |
| `Custom2` (step_number) | `0` | Marks contact as not yet in sequence |
| `Custom3` (send_time) | *(leave blank)* | Populated by system after first send |
| `Custom4` (reply_category) | *(leave blank)* | Populated after reply received |
| `Custom5` (email_opt_out_flag) | `No` | Machine-readable opt-out flag |
| `Custom8` (audit_trail_id) | *(see Step 8)* | UUID4 assigned in Step 8 |

---

### Step 5: Create GigLeadRecord in the Gigs_Leads Sheet

Navigate to the **Gigs_Leads** sheet. Add a new row:

| Field | Value |
|---|---|
| `UniqueId` | Generate: `GIG-` + 6-digit zero-padded sequential number (e.g., `GIG-000031`) |
| `Status` | `Lead` |
| `Company UniqueId` | The `VEN-XXXXXX` ID from Step 3 |
| `Primary Contact UniqueId` | The `CON-XXXXXX` ID from Step 4 |
| `Show` | `Princess Peigh's Sword Fighting Tea Party` |
| `Source` | How the lead was found (e.g., "Directory Research," "Referral from [Name]," "State Arts Council Listing") |
| `Created Date` | Today's date in YYYY-MM-DD format |
| `Created By` | Your first name |
| `Notes` | Any relevant booking context |

**Status definitions for reference:**

| Status | Meaning |
|---|---|
| `Lead` | In outbound sequence, not yet replied |
| `Responded` | Has replied; human follow-up in progress |
| `Negotiating` | Active booking discussion |
| `Booked` | Contract signed |
| `Not a Fit` | Replied negatively or determined not suitable |
| `Closed` | Sequence complete, no response |

---

### Step 6: Set sequence_id in Contacts.Custom1

Return to the **Contacts** sheet. Confirm that `Custom1` for this contact row reads exactly:

```
theater_outreach_v1
```

This string must match the YAML filename in `sequences/theater_outreach_v1.yaml` exactly. The importer (`importer.py`) uses this value as a dictionary key to load the correct sequence definition. A typo here causes the contact to be silently skipped by the automation engine.

---

### Step 7: Set step_number = 0 in Contacts.Custom2

Confirm that `Custom2` for this contact row contains the integer `0` (not the string "0" — openpyxl will handle the cell type, but be aware of the distinction if editing via CSV).

`step_number = 0` means the contact is enrolled in the sequence but no step has been sent yet. On the next automation run, the engine will send Step 1.

---

### Step 8: Generate audit_trail_id and Store in Contacts.Custom8

Generate a UUID4 for this contact. This can be done:

**In Python:**
```python
import uuid
print(str(uuid.uuid4()))
# Example output: f47ac10b-58cc-4372-a567-0e02b2c3d479
```

**In a terminal:**
```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

**In Excel (manual fallback — use Python where possible):**
There is no native UUID4 generator in Excel. If entering manually, generate via Python or an online UUID generator and paste the result.

Copy the generated UUID4 string into `Custom8` for this contact row.

**Important:** The `audit_trail_id` links all audit log events for this contact — the `LEAD_CREATED` event written in Step 9, all subsequent `EMAIL_SENT` events, any `BOUNCE` or `OPT_OUT` events. It must never be changed after creation.

---

### Step 9: Write LEAD_CREATED Event to audit_log

After saving the Excel file, run the audit log writer to record the lead creation event:

```bash
python3 scripts/write_audit_event.py \
  --event_type LEAD_CREATED \
  --contact_unique_id CON-000083 \
  --audit_trail_id f47ac10b-58cc-4372-a567-0e02b2c3d479 \
  --operator "Melissa Neufer" \
  --notes "Lead created from State Arts Council directory"
```

Or, if running the full intake script:

```bash
python3 scripts/lead_intake.py --crm_path data/CRM.xlsx
```

The audit log event schema for `LEAD_CREATED`:

| Field | Value |
|---|---|
| `event_type` | `LEAD_CREATED` |
| `timestamp` | ISO 8601 UTC datetime |
| `contact_unique_id` | CON-XXXXXX |
| `company_unique_id` | VEN-XXXXXX |
| `gig_lead_unique_id` | GIG-XXXXXX |
| `audit_trail_id` | UUID4 |
| `operator` | Full name of person creating the record |
| `sequence_id` | `theater_outreach_v1` |
| `step_number_at_creation` | `0` |
| `notes` | Free text |

---

### Step 10: Save the Excel File

Save the CRM Excel file with Ctrl+S (or Cmd+S on Mac). Confirm that Excel shows no unsaved indicator.

**File naming convention:** The CRM file should be kept at the path configured in `config/settings.yaml` under `crm.file_path`. Do not rename or move the file without updating the config.

**Backup reminder:** The CRM Excel file is the source of truth for all contact and venue data. After any session where new leads are added, copy the file to the backup location defined in `config/settings.yaml` → `crm.backup_path`. A date-stamped backup (e.g., `CRM_2026-03-04.xlsx`) is the minimum acceptable backup practice.

---

## Lead Intake Checklist (Quick Reference)

Use this checklist for each new lead. Check each box before considering the lead complete.

- [ ] Venue passes all qualification criteria
- [ ] Primary contact identified with verifiable or strongly inferred email
- [ ] VenueRecord created in Companies sheet (UniqueId, Name, Website, Address, Seat Capacity, Venue Type)
- [ ] ContactRecord created in Contacts sheet (UniqueId, First/Last Name, Company UniqueId, Email, Title)
- [ ] `Email Opt Out` = `No`
- [ ] `Custom1` (sequence_id) = `theater_outreach_v1`
- [ ] `Custom2` (step_number) = `0`
- [ ] `Custom3` (send_time) = blank
- [ ] `Custom8` (audit_trail_id) = valid UUID4
- [ ] GigLeadRecord created in Gigs_Leads sheet (UniqueId, Status=Lead, Company UniqueId, Primary Contact UniqueId, Show)
- [ ] `LEAD_CREATED` event written to audit_log
- [ ] Excel file saved
- [ ] Backup copy made if session is complete

---

## Common Errors and How to Fix Them

| Error | Likely cause | Fix |
|---|---|---|
| Contact skipped by automation | sequence_id typo in Custom1 | Correct to exact string `theater_outreach_v1`, save, rerun |
| Contact skipped by automation | step_number missing or non-numeric in Custom2 | Set Custom2 to integer `0`, save, rerun |
| Duplicate record created | UniqueId not checked before creation | Delete duplicate row, verify no emails were sent to it |
| Audit event missing | Script not run after Excel save | Run `write_audit_event.py` with LEAD_CREATED manually |
| Email bounces on first send | Email address was pattern-inferred incorrectly | Update email in Contacts sheet, log MANUAL_CORRECTION to audit |
| Contact receives wrong sequence | sequence_id points to non-existent YAML | Verify file exists at `sequences/theater_outreach_v1.yaml` |

---

## Drop-In Reusability Notes

This lead intake workflow is designed for reuse across any touring show or outbound booking campaign that uses the same CRM architecture (Excel with Companies, Contacts, Gigs_Leads sheets and Custom1–Custom8 automation fields).

To adapt for a new project:

1. **Show name:** Replace "Princess Peigh's Sword Fighting Tea Party" in Step 5 and the Gigs_Leads row with the new show title. Consider making this a config value (`config/settings.yaml` → `show.name`) rather than a hardcoded string.
2. **Sequence ID:** Replace `theater_outreach_v1` in Steps 6 and 7 with the new sequence YAML filename. Update all references consistently — the YAML file, Custom1 default, and this documentation.
3. **Qualification criteria:** The criteria table in the Qualification section can be edited for different venue types (e.g., festival venues, school touring, corporate events) without changing the rest of the workflow.
4. **Contact priority order:** The priority order in Step 2 (Programming Director → Executive Director → Family Series Coordinator) reflects family theater booking norms. Adjust for other show types (e.g., school shows might prioritize "Director of Student Activities").
5. **UniqueId prefixes:** `VEN-`, `CON-`, `GIG-` are conventions. They can be changed to any prefix as long as they are consistent within the project.
6. **Audit event types:** `LEAD_CREATED` is a fixed event type string. It must match the audit log schema definition. If the schema changes, update the string here and in `audit.py`.
7. **Operators:** Replace Melissa Neufer and Zachary Gartrell with the new project's team members in the overview and in any operator-specific instructions.
