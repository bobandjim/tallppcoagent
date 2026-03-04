# Row Logic

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**CRM Format:** Excel/CSV, 6-sheet structure
**Last Updated:** 2026-03-04

---

## Overview

This document defines the rules that govern how rows are created, updated, suppressed, and attributed across the three primary CRM sheets (Companies, Contacts, Gigs_Leads). These rules ensure data consistency, protect contacts from unwanted outreach, and maintain an accurate record of booking outcomes.

---

## Part 1: Row Creation

### 1.1 When to Create a New Row

| Sheet       | Create a new row when...                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------|
| Companies   | A venue is identified that does not already exist in the CRM (verified via dedup check on `company + state`).      |
| Contacts    | An individual at a venue is identified who does not already exist in the CRM (verified via dedup check on `email`). |
| Gigs_Leads  | A new booking opportunity is opened for a venue/contact pair. One contact may have multiple Gigs_Leads over time.   |

Never create a new row when an existing row for the same entity can be updated. Run the dedup check before every import or manual entry.

### 1.2 Required Fields at Row Creation

**Companies (VenueRecord):**

| Field                | Value at Creation                                          |
|----------------------|------------------------------------------------------------|
| lead_id              | Auto-generate: `VEN-` + UUID4 (e.g., `VEN-a3f1c2d4-...`) |
| company              | Manually entered — must not be blank                       |
| segment              | Manually selected from Lookups picklist                    |
| city                 | Manually entered — must not be blank                       |
| state                | Manually entered — two-letter abbreviation                 |
| seating_capacity_tier| Manually selected from Lookups picklist                    |

All other Companies fields are Optional and may be populated later.

**Contacts (ContactRecord):**

| Field          | Value at Creation                                                         |
|----------------|---------------------------------------------------------------------------|
| contact_id     | Auto-generate: `CON-` + UUID4 (e.g., `CON-7b2e9f1a-...`)                |
| first_name     | Manually entered — must not be blank                                      |
| email          | Manually entered — must not be blank; run dedup check before saving       |
| company_id     | Must reference an existing `lead_id` in Companies                         |
| source         | Manually selected from Lookups picklist                                   |
| email_opt_out  | Default: `No`                                                             |
| step_number    | Default: `0`                                                              |
| last_updated   | Auto-generate: current datetime in ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)      |
| audit_trail_id | Auto-generate: UUID4 (e.g., `f8c3a2b1-...`) — no prefix, raw UUID       |

All other Contacts fields are Optional at creation. `sequence_id` remains blank until a sequence is deliberately assigned.

**Gigs_Leads (GigLeadRecord):**

| Field       | Value at Creation                                                          |
|-------------|----------------------------------------------------------------------------|
| gig_lead_id | Auto-generate: `GIG-` + UUID4 (e.g., `GIG-2d5f8e3c-...`)                |
| name        | Manually entered. Convention: `{Venue Name} — PPSTFTP — {Year}`          |
| status      | Default: `Lead`                                                            |
| company_id  | Must reference an existing `lead_id` in Companies                          |
| contact_id  | Must reference an existing `contact_id` in Contacts                        |
| outcome     | Default: `Pending`                                                         |

All other Gigs_Leads fields are Optional at creation.

### 1.3 Auto-Generated Fields: Rules

**UUID4 generation:**
- Use any standard UUID4 generator (Python `uuid.uuid4()`, Excel formula workarounds, or an online generator for manual entry).
- UUIDs must be generated fresh for each new row. Never copy-paste an existing ID into a new row.
- The `VEN-`, `CON-`, and `GIG-` prefixes are for human readability only. Strip the prefix when doing programmatic lookups.

**`last_updated` timestamp:**
- Format: `YYYY-MM-DDTHH:MM:SS` (ISO 8601, local time, no timezone suffix unless the system uses UTC consistently — choose one and document it).
- For Excel manual entry, use the formula `=TEXT(NOW(),"YYYY-MM-DDTHH:MM:SS")` pasted as a value.
- For scripted entry, use `datetime.now().isoformat(timespec='seconds')` in Python.

**`audit_trail_id`:**
- Generated once at row creation and never changed.
- This ID is written into every audit log entry that touches this contact, creating a permanent link between the contact record and its full activity history.
- If a contact is merged (duplicate resolution), the survivor's `audit_trail_id` is retained. The loser's `audit_trail_id` is written into the merge audit event so the old history remains traceable.

---

## Part 2: Row Updates

### 2.1 Which Fields Can Be Updated

**Companies — updatable fields:**
All fields except `lead_id`. The `lead_id` is the primary key and is permanent.

**Contacts — updatable fields:**
All fields except `contact_id` and `audit_trail_id`. The `contact_id` is the permanent primary key. The `audit_trail_id` is a permanent link to the audit log and must never change.

**Gigs_Leads — updatable fields:**
All fields except `gig_lead_id`. The `gig_lead_id` is the permanent primary key.

### 2.2 How `last_updated` Is Maintained

Every time any field on a Contacts row is changed (manually or by automation), `last_updated` must be refreshed to the current datetime before saving.

`last_updated` on Companies is not tracked at the sheet level — use the Notes sheet to log activity on venue records.

Gigs_Leads does not have a `last_updated` field; the `send_time` field (Custom4) serves as the timestamp of the most recent outreach activity.

### 2.3 Update Workflow

**Manual update (single row):**
1. Locate the row by filtering or searching on the relevant ID.
2. Edit the target field(s).
3. Update `last_updated` on the Contacts sheet.
4. Save the workbook.
5. If the change triggers an audit event (e.g., setting `email_opt_out = Yes`, setting `meeting_booked = Yes`), write the event to the audit log before closing.

**Bulk update (from new import data):**
1. Run deduplication to identify matched rows.
2. For each matched row, apply field-level merge rules (non-null from import overwrites blank on existing; survivor's non-null fields are not overwritten).
3. Refresh `last_updated` on all updated Contacts rows.
4. Write a `BULK_UPDATE` event to the audit log documenting the import file name, row count, and date.

---

## Part 3: Suppression Logic

### 3.1 The `email_opt_out` Flag

The `email_opt_out` field on the Contacts sheet is the primary suppression mechanism. It is a Boolean field with two valid values:

| Value | Meaning |
|-------|---------|
| `No`  | Contact is eligible for email outreach (subject to other checks) |
| `Yes` | Contact is suppressed — no future email sends under any circumstances |

### 3.2 What Triggers a Suppression

| Trigger                                | Action |
|----------------------------------------|--------|
| Contact replies with unsubscribe request | Set `email_opt_out = Yes`, set `reply = Yes`, set `reply_category = Opt Out` |
| Contact clicks unsubscribe link in email | Set `email_opt_out = Yes` (system-automated via Zoho Mail webhook or manual processing) |
| Hard email bounce                        | Add to `suppression_list.csv`; optionally set `email_opt_out = Yes` on the Contacts row |
| Manual removal requested by contact     | Set `email_opt_out = Yes` |
| Contact identified as wrong person      | Set `email_opt_out = Yes` and update `notes` |

### 3.3 What Suppression Does NOT Do

- **Records are never deleted.** A contact with `email_opt_out = Yes` remains in the CRM permanently. Deletion would remove the suppression record itself, potentially allowing the address to be re-imported and emailed again in the future.
- **Suppression does not affect Calls or Notes.** Phone outreach is not governed by `email_opt_out`. A suppressed contact may still be called (subject to separate do-not-call tracking if applicable).
- **Suppression applies to all sequences.** If `email_opt_out = Yes`, the contact is excluded from every past, current, and future email sequence — not just the active one. There is no per-sequence suppression toggle.

### 3.4 Suppression Check in the Send Workflow

Before any email is dispatched (automated or manual), the send logic must verify:

1. `email_opt_out` on the Contacts row = `No`
2. The contact's email address does not appear in `suppression_list.csv`
3. The contact's `email` field is not blank

If any of these checks fail, skip the contact and log a `SUPPRESSION_SKIP` event to the audit log.

### 3.5 The `suppression_list.csv` File

A flat CSV file maintained alongside the Excel workbook. It serves as a secondary hard-block list used to catch addresses that may have been re-imported or whose CRM row cannot be located quickly.

Minimum columns:
```
email, reason, date_added, source
```

Valid `reason` values: `OPT_OUT`, `HARD_BOUNCE`, `SOFT_BOUNCE_3X`, `MANUAL`, `LEGAL_REQUEST`

The `suppression_list.csv` is checked at send time in addition to — not instead of — the `email_opt_out` field on the Contacts sheet. Both mechanisms must independently pass for a send to proceed.

---

## Part 4: Booking Attribution

### 4.1 The Attribution Chain

When a lead converts to a confirmed booking, the attribution must flow correctly across all three primary sheets. The chain is:

```
Contact (Contacts sheet)
    → linked via contact_id to Gig_Lead (Gigs_Leads sheet)
        → status changes from Lead to Gig
            → linked via company_id to Venue (Companies sheet)
```

### 4.2 Step-by-Step Booking Attribution Process

**Step 1 — Meeting booked:**
- On the Gigs_Leads row: Set `meeting_booked = Yes`
- On the Contacts row: Set `reply = Yes`, set `reply_category = Meeting Booked`
- Write a `MEETING_BOOKED` event to the audit log:
  ```
  event_type:    MEETING_BOOKED
  gig_lead_id:   {gig_lead_id}
  contact_id:    {contact_id}
  company_id:    {company_id}
  timestamp:     {ISO 8601}
  performed_by:  {user or "system"}
  ```

**Step 2 — Show confirmed:**
- On the Gigs_Leads row:
  - Set `show_booked = Yes`
  - Set `status = Gig` (this is the critical status change — all financial reporting filters on this field)
  - Set `outcome = Won`
  - Populate `final_fee` with the agreed performance fee (numeric, USD)
  - Populate `show_date` with the confirmed performance date (YYYY-MM-DD)
- On the Contacts row:
  - Set `reply_category = Show Booked` (if not already set to a more specific value)
  - Refresh `last_updated`
- Write a `SHOW_BOOKED` event to the audit log:
  ```
  event_type:    SHOW_BOOKED
  gig_lead_id:   {gig_lead_id}
  contact_id:    {contact_id}
  company_id:    {company_id}
  final_fee:     {numeric USD value}
  show_date:     {YYYY-MM-DD}
  timestamp:     {ISO 8601}
  performed_by:  {user or "system"}
  ```

**Step 3 — Financial reporting:**
- All confirmed bookings are summarized by filtering the Gigs_Leads sheet where `status = Gig`
- Total revenue = `SUM(final_fee)` where `status = Gig`
- Bookings by state = pivot of `company_id → Companies.state` where `status = Gig`

### 4.3 Attribution for Lost Leads

When a lead is determined to be unwinnable:
- On the Gigs_Leads row: Set `outcome = Lost` (status remains `Lead` — do not change to `Gig`)
- Add a Note row documenting the reason (e.g., "Venue booked another show for that date", "Budget too low", "No response after full sequence")
- The contact remains in the CRM and may be re-engaged in a future campaign if `email_opt_out = No`

### 4.4 Multiple Gigs_Leads for One Contact

A single contact may generate multiple Gigs_Leads records over time (e.g., booked one year, re-engaged the next). This is expected and correct. Each Gigs_Leads row is a separate opportunity. Do not reuse or overwrite a closed Gigs_Leads row — create a new one.

---

## Drop-In Reusability Notes

This row logic document can be reused for any outbound touring show booking campaign using the same 6-sheet Excel/CSV CRM. To adapt it for a new campaign:

1. **The `lead_id` / `contact_id` / `gig_lead_id` prefix conventions** (`VEN-`, `CON-`, `GIG-`) can be changed to any project-specific prefix without affecting logic. Update the examples in section 1.2 to match.
2. **The auto-generated fields section** (1.3) is universally applicable and requires no changes across campaigns — UUID4 and ISO 8601 datetime are implementation-agnostic.
3. **The suppression logic** (Part 3) is designed to meet CAN-SPAM minimum requirements and should be preserved without modification in any adaptation. The only permitted change is adding additional trigger types to the `reason` picklist in `suppression_list.csv`.
4. **The booking attribution chain** (Part 4) assumes a two-step conversion (meeting → confirmed show). For campaigns with a different conversion model (e.g., direct booking without a discovery call, or multi-step contract process), update the Step-by-Step section accordingly and add the appropriate audit event types to the Lookups sheet.
5. **The `name` field convention** in Gigs_Leads currently uses `{Venue Name} — PPSTFTP — {Year}`. Replace `PPSTFTP` with the new show's code for the new campaign.
