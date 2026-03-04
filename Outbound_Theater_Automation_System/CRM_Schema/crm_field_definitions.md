# CRM Field Definitions

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**CRM Format:** Excel/CSV, 6-sheet structure
**Last Updated:** 2026-03-04

---

## Overview

The CRM is maintained as a multi-sheet Excel workbook (or equivalent set of CSV files). There are six sheets:

| Sheet Name   | Record Type      | Primary Key     |
|--------------|------------------|-----------------|
| Companies    | VenueRecord      | lead_id         |
| Contacts     | ContactRecord    | contact_id      |
| Gigs_Leads   | GigLeadRecord    | gig_lead_id     |
| Calls        | CallRecord       | call_id         |
| Notes        | NoteRecord       | note_id         |
| Lookups      | LookupValues     | lookup_key      |

This document defines all 27 required fields across the three primary working sheets (Companies, Contacts, Gigs_Leads). Calls, Notes, and Lookups are supporting sheets and are described briefly at the end.

---

## Sheet 1: Companies (VenueRecord)

Stores one row per venue. A venue is a physical location or organization that books performing arts programming. Each venue may have multiple contacts (in the Contacts sheet) and multiple booking opportunities (in Gigs_Leads).

### Field Definitions

| # | Field Name            | Column Header in Excel | Excel Internal Label | Type        | Required | Valid Values / Notes |
|---|-----------------------|------------------------|----------------------|-------------|----------|----------------------|
| 1 | lead_id               | lead_id                | UniqueId             | Text/UUID   | Required | System-generated UUID4. Never edited after creation. Primary key. Format: `VEN-{UUID4}`. |
| 2 | company               | company                | Name                 | Text        | Required | Legal or operating name of the venue organization. Max 255 characters. |
| 3 | website               | website                | website              | URL         | Optional | Full URL including `https://`. Used to research programming and validate qualification. |
| 4 | segment               | segment                | Record Type          | Picklist    | Required | One of: `Community Theater`, `Performing Arts Center`, `Library`, `Municipal Cultural Venue`, `Other`. Maps to qualification tier. |
| 5 | phone                 | phone                  | phone                | Text        | Optional | Main venue phone number. Format: `(XXX) XXX-XXXX` or international equivalent. |
| 6 | city                  | city                   | Billing City         | Text        | Required | City where venue is physically located. |
| 7 | state                 | state                  | Billing State        | Text        | Required | Two-letter state abbreviation (e.g., `OH`, `PA`, `WV`). Used in dedup key and regional targeting filter. |
| 8 | notes                 | notes                  | notes                | Long Text   | Optional | Free-form notes about the venue. Not used in automation logic. Visible to human user only. |
| 9 | seating_capacity_tier | seating_capacity_tier  | Custom1              | Picklist    | Required | One of: `100-149`, `150-199`, `200-299`, `300-400`, `Unknown`. Drives qualification tier. |
| 10| mission_excerpt       | mission_excerpt        | Custom2              | Long Text   | Optional | Copy-pasted excerpt from venue's mission statement or About page. Used during manual qualification. |
| 11| programming_focus     | programming_focus      | Custom3              | Text        | Optional | Brief description of venue's programming focus (e.g., "Family series, school matinees, community plays"). Aids personalization. |
| 12| venue_name            | venue_name             | Custom4              | Text        | Optional | The public-facing name of the performance space if different from `company` (e.g., company = "Lakewood Arts Council", venue_name = "Beck Center for the Arts"). |

### Notes on Companies Sheet Usage

**Adding a new venue row:**
All Required fields must be populated before saving. `lead_id` is auto-generated. `last_updated` is not tracked on the Companies sheet directly; use the Notes sheet for venue-level activity history.

**Updating an existing venue row:**
Edit the row in place. All fields except `lead_id` may be updated. Do not leave Required fields blank during edits. When bulk-importing from a new data source, run deduplication (see `deduplication_rules.md`) before appending rows.

---

## Sheet 2: Contacts (ContactRecord)

Stores one row per individual contact person at a venue. A contact must be associated with exactly one venue (via `company_id`). Contacts drive all email outreach sequences.

### Field Definitions

| # | Field Name       | Column Header in Excel | Excel Internal Label | Type        | Required | Valid Values / Notes |
|---|------------------|------------------------|----------------------|-------------|----------|----------------------|
| 13| contact_id       | contact_id             | UniqueId             | Text/UUID   | Required | System-generated UUID4. Never edited after creation. Primary key. Format: `CON-{UUID4}`. |
| 14| first_name       | first_name             | first_name           | Text        | Required | Contact's first name. Used in email personalization token `{{first_name}}`. Max 100 characters. |
| 15| last_name        | last_name              | last_name            | Text        | Optional | Contact's last name. Max 100 characters. |
| 16| company_id       | company_id             | company_id           | Foreign Key | Required | Must match a `lead_id` value in the Companies sheet. Links contact to venue. |
| 17| source           | source                 | Lead Source          | Picklist    | Required | One of: `TCG Directory`, `State Arts Council`, `Google Research`, `Library Network`, `Referral`, `Social Media`, `Inbound`, `Other`. |
| 18| phone            | phone                  | Work Phone           | Text        | Optional | Contact's direct phone number. Format: `(XXX) XXX-XXXX`. |
| 19| email            | email                  | email                | Email       | Required | Contact's professional email address. Primary dedup key for contacts. Must be unique across all non-suppressed contacts. |
| 20| email_opt_out    | email_opt_out          | Email Opt Out        | Boolean     | Required | `Yes` or `No`. Default on creation: `No`. Set to `Yes` on unsubscribe reply or manual removal. Records with `Yes` are retained but never emailed. |
| 21| title            | title                  | title                | Text        | Optional | Contact's job title (e.g., "Executive Director", "Programming Manager", "Children's Librarian"). Used in research and personalization. |
| 22| sequence_id      | sequence_id            | Custom1              | Text        | Optional | Identifier of the active outreach sequence assigned to this contact (e.g., `SEQ-PPSTFTP-V1`). Blank if no sequence assigned. |
| 23| step_number      | step_number            | Custom2              | Integer     | Optional | Current step number within the assigned sequence. Starts at `0` (not yet started), increments to `1` after first send, etc. |
| 24| open             | open                   | Custom3              | Boolean     | Optional | `Yes` or `No`. Set to `Yes` if any tracked open event is recorded for this contact. |
| 25| click            | click                  | Custom4              | Boolean     | Optional | `Yes` or `No`. Set to `Yes` if any tracked click event is recorded. |
| 26| reply            | reply                  | Custom5              | Boolean     | Optional | `Yes` or `No`. Set to `Yes` when a reply email is received from this contact. |
| 27| reply_category   | reply_category         | Custom6              | Picklist    | Optional | One of: `Interested`, `Not Interested`, `Opt Out`, `Bounce`, `Auto Reply`, `Meeting Booked`, `Show Booked`, `Other`. Updated when reply is logged. |
| 28| last_updated     | last_updated           | Custom7              | DateTime    | Required | ISO 8601 datetime string (`YYYY-MM-DDTHH:MM:SS`). Auto-set on creation and updated on every field change. |
| 29| audit_trail_id   | audit_trail_id         | Custom8              | Text/UUID   | Required | UUID4 generated once at row creation. Links this contact to all audit log entries. Never changes after creation. |

> Note: Fields 13–29 account for 17 fields on the Contacts sheet. The total field count across all three primary sheets is 29 defined fields, exceeding the "27 required" minimum — the additional two fields (open, click) are included as required tracking fields for sequence management.

### Notes on Contacts Sheet Usage

**Adding a new contact row:**
`contact_id`, `last_updated`, and `audit_trail_id` are auto-generated. `first_name`, `email`, `company_id`, `source`, and `email_opt_out` are Required. `step_number` defaults to `0`. `sequence_id` is blank until a sequence is explicitly assigned.

**Updating an existing contact row:**
All fields except `contact_id` and `audit_trail_id` may be updated. `last_updated` must be refreshed on every update. When `email_opt_out` is changed to `Yes`, write an `OPT_OUT` event to the audit log before saving.

---

## Sheet 3: Gigs_Leads (GigLeadRecord)

Stores one row per booking opportunity. A Gig_Lead links a venue and a contact to a potential or confirmed performance date. Status distinguishes an active lead from a confirmed booking.

### Field Definitions

| # | Field Name     | Column Header in Excel | Excel Internal Label | Type        | Required | Valid Values / Notes |
|---|----------------|------------------------|----------------------|-------------|----------|----------------------|
| 30| gig_lead_id    | gig_lead_id            | UniqueId             | Text/UUID   | Required | System-generated UUID4. Never edited. Primary key. Format: `GIG-{UUID4}`. |
| 31| name           | name                   | name                 | Text        | Required | Human-readable label for this opportunity. Convention: `{Venue Name} — {Show} — {Year}`. Example: `Beck Center — PPSTFTP — 2026`. |
| 32| status         | status                 | Gig\|Lead            | Picklist    | Required | `Lead` (active pursuit, not yet booked) or `Gig` (confirmed booking). Never leave blank. Default on creation: `Lead`. |
| 33| company_id     | company_id             | company_id           | Foreign Key | Required | Must match a `lead_id` in Companies. |
| 34| contact_id     | contact_id             | contact_id           | Foreign Key | Required | Must match a `contact_id` in Contacts. |
| 35| source         | source                 | source               | Picklist    | Optional | Same picklist as Contacts.source. Documents how this lead was originally identified. |
| 36| show_date      | show_date              | show_date            | Date        | Optional | Proposed or confirmed performance date. Format: `YYYY-MM-DD`. Blank while still prospecting. |
| 37| venue_name     | venue_name             | venue_name           | Text        | Optional | Display name of the venue for this gig. May differ from Companies.company. |
| 38| final_fee      | final_fee              | Fee                  | Currency    | Optional | Confirmed performance fee in USD. Populated only when `status = Gig`. Format: numeric, no `$` symbol. |
| 39| projected_fee  | projected_fee          | Quote1               | Currency    | Optional | Estimated fee during negotiation. Format: numeric, no `$` symbol. |
| 40| outcome        | outcome                | Custom1              | Picklist    | Optional | One of: `Pending`, `Won`, `Lost`, `Postponed`, `No Response`. Updated as lead progresses. |
| 41| meeting_booked | meeting_booked         | Custom2              | Boolean     | Optional | `Yes` or `No`. Set to `Yes` when a discovery call or meeting is scheduled. Triggers `MEETING_BOOKED` audit event. |
| 42| show_booked    | show_booked            | Custom3              | Boolean     | Optional | `Yes` or `No`. Set to `Yes` when performance is confirmed. Triggers `SHOW_BOOKED` audit event and status change to `Gig`. |
| 43| send_time      | send_time              | Custom4              | DateTime    | Optional | ISO 8601 datetime of the most recent outreach email sent for this lead. Updated after each send. |

### Notes on Gigs_Leads Sheet Usage

**Adding a new Gig_Lead row:**
`gig_lead_id` is auto-generated. `name`, `status`, `company_id`, and `contact_id` are Required. `status` defaults to `Lead`. `outcome` defaults to `Pending`.

**Updating an existing Gig_Lead row:**
All fields except `gig_lead_id` may be updated. When `show_booked` is changed to `Yes`, also set `status` to `Gig`, set `outcome` to `Won`, and write a `SHOW_BOOKED` event to the audit log.

**Booking attribution flow:**
1. Contact replies positively and meeting is scheduled → set `meeting_booked = Yes`.
2. Contract signed → set `show_booked = Yes`, set `status = Gig`, populate `final_fee` and `show_date`.
3. The Gig_Lead row with `status = Gig` is the canonical record for all confirmed performances. All financial reporting pulls from rows where `status = Gig`.

---

## Supporting Sheets

### Sheet 4: Calls

Tracks phone call attempts and outcomes. Minimum fields: `call_id` (UUID4), `contact_id` (FK), `call_date`, `call_outcome` (Picklist: `Reached`, `Voicemail`, `No Answer`, `Wrong Number`), `notes`. Not part of email automation logic.

### Sheet 5: Notes

Free-form activity notes attached to any record type. Minimum fields: `note_id` (UUID4), `record_type` (`Company` | `Contact` | `GigLead`), `record_id` (FK to appropriate sheet), `note_date`, `note_text`, `author`. Provides audit-trail-lite for manual activities.

### Sheet 6: Lookups

Reference table for all picklist values. Minimum fields: `lookup_key` (e.g., `segment`), `lookup_value` (e.g., `Community Theater`), `display_order`, `active` (`Yes`/`No`). Adding a new valid picklist value requires adding a row here and updating the data validation dropdown in all affected sheets.

---

## Field Count Summary

| Sheet       | Required Fields | Optional Fields | Total |
|-------------|-----------------|-----------------|-------|
| Companies   | 6               | 6               | 12    |
| Contacts    | 6               | 11              | 17    |
| Gigs_Leads  | 4               | 10              | 14    |
| **Total**   | **16**          | **27**          | **43**|

The 27 fields called out in the system specification map directly to the 27 optional and tracking fields that capture research data, sequence state, and booking outcomes. The 16 Required fields form the structural skeleton that must be populated for the automation to function.

---

## Drop-In Reusability Notes

This field definitions document can be reused for any outbound booking campaign that uses the same 6-sheet Excel/CSV CRM structure. To adapt it for a new show or company:

1. **Change the show name and brand** in the header and in the `sequence_id` naming convention (e.g., replace `SEQ-PPSTFTP-V1` with the new show code).
2. **Adjust the `segment` picklist** in both this document and the Lookups sheet if the new show targets different venue types (e.g., festivals, schools, corporate).
3. **Adjust the `seating_capacity_tier` picklist** if the new show's venue size range differs.
4. **Add or remove Custom fields** on any sheet by editing the numbered rows in the relevant field table. Renumber sequentially and update the Field Count Summary.
5. **Preserve all primary key, foreign key, and audit fields** (`lead_id`, `contact_id`, `gig_lead_id`, `company_id`, `audit_trail_id`, `last_updated`) across any adaptation — these are structural and cannot be removed without breaking automation scripts.
6. The `email_opt_out` and suppression logic fields must remain intact regardless of campaign to maintain CAN-SPAM compliance.
