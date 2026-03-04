# CRM Audit Checklist — Post-Send

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**Email Platform:** Zoho Mail SMTP
**Last Updated:** 2026-03-04

---

## Overview

This checklist must be completed after every batch of outreach emails is sent, and again after reviewing incoming replies or bounce notifications. It ensures that the CRM accurately reflects what happened: who was emailed, what step they are on, how they responded, and what the current booking status is.

CRM accuracy is not optional. An inaccurate CRM causes:
- Contacts emailed twice at the same step (damaged credibility)
- Opt-outs ignored (CAN-SPAM violation)
- Bounced addresses re-attempted (wasted sends, reputation damage)
- Bookings not logged (revenue not attributed, celebration missed)

This checklist covers five time windows:
1. Immediately after send batch completes
2. After bounce notifications arrive (typically 1–24 hours post-send)
3. After reply inbox is reviewed (daily or per-campaign cadence)
4. After meetings are scheduled
5. After shows are confirmed/booked

---

## Section A: Immediately After Send Batch Completes

Complete this section within 1 hour of batch completion.

---

- [ ] **`EMAIL_SENT` event written to audit log for every sent message**

  For every contact in the batch, verify that an `EMAIL_SENT` event exists in the audit log with the contact's `audit_trail_id`. The event record must include:

  ```
  event_type:    EMAIL_SENT
  audit_trail_id: {contact's audit_trail_id}
  contact_id:    {contact_id}
  gig_lead_id:   {associated gig_lead_id, if applicable}
  sequence_id:   {sequence_id}
  step_number:   {step number sent}
  send_time:     {ISO 8601 datetime of send}
  from_address:  {sending email address}
  subject_line:  {subject line of email sent}
  ```

  Method: After the batch run, export the send log from Zoho Mail (or your send script's output log) and compare the count and contact list against the batch contact list. Every contact in the batch must have a matching `EMAIL_SENT` event. Contacts that failed to send (SMTP error) must have an `EMAIL_SEND_FAILED` event logged instead, and their `step_number` must NOT be incremented.

---

- [ ] **`step_number` incremented in Contacts.Custom2**

  For every contact that received a successful send, increment the `step_number` field (Custom2 in the Contacts sheet) by 1.

  - If the contact was at `step_number = 0`, change to `1`
  - If at `1`, change to `2`, and so on
  - Do NOT increment for contacts where the send failed

  Method: Use a bulk update on the Contacts sheet filtering by the batch contact list. Update `step_number` and `last_updated` in the same operation.

---

- [ ] **`send_time` updated in Gigs_Leads.Custom4**

  For every contact in the batch that has an associated Gigs_Leads row, update `send_time` (Custom4 on the Gigs_Leads sheet) to the datetime of the send batch.

  Format: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)

  If a contact does not yet have a Gigs_Leads row (e.g., a cold contact who was emailed before a lead was opened), create the Gigs_Leads row now with `status = Lead` and `outcome = Pending`, then set `send_time`.

---

- [ ] **`last_updated` updated in Contacts.Custom7**

  For every contact in the batch, refresh `last_updated` (Custom7 on the Contacts sheet) to the current datetime.

  This field must be updated every time any field on the Contacts row changes. Since `step_number` just changed, `last_updated` must be refreshed simultaneously.

  Format: ISO 8601 (`YYYY-MM-DDTHH:MM:SS`)

---

## Section B: After Bounce Notifications Arrive

Complete this section within 24 hours of send. Zoho Mail will surface bounce notifications in the sending account's inbox or via the mail log. Review the Zoho Mail Sent/Bounce report before running this section.

---

- [ ] **Hard bounces added to `suppression_list.csv` + `BOUNCE` audit event**

  A hard bounce indicates a permanent delivery failure (address does not exist, domain does not exist, account permanently disabled). For each hard bounce:

  1. Add the email address to `suppression_list.csv` with:
     ```
     email:       {bounced address}
     reason:      HARD_BOUNCE
     date_added:  {YYYY-MM-DD}
     source:      Zoho Mail bounce report
     ```
  2. Write a `BOUNCE` event to the audit log:
     ```
     event_type:    BOUNCE
     audit_trail_id: {contact's audit_trail_id}
     contact_id:    {contact_id}
     email:         {bounced address}
     bounce_type:   HARD
     timestamp:     {ISO 8601}
     ```
  3. Optionally set `email_opt_out = Yes` on the Contacts row (recommended — prevents accidental future sends if the suppression list is not checked).
  4. Set `reply_category = Bounce` on the Contacts row.
  5. Refresh `last_updated` on the Contacts row.

---

- [ ] **Soft bounces tracked; suppressed after 3 consecutive soft bounces**

  A soft bounce indicates a temporary delivery failure (mailbox full, server temporarily unavailable, message too large). Soft bounces are normal and expected occasionally.

  For each soft bounce:
  1. Write a `SOFT_BOUNCE` event to the audit log with the same structure as `BOUNCE` (use `bounce_type: SOFT`).
  2. Track a soft bounce counter for this contact (can be a dedicated column in the Contacts sheet: `soft_bounce_count`). Increment by 1.
  3. If `soft_bounce_count` reaches **3** for the same contact:
     - Add to `suppression_list.csv` with `reason: SOFT_BOUNCE_3X`
     - Write a `BOUNCE` audit event with `bounce_type: SOFT_3X_SUPPRESSED`
     - Set `email_opt_out = Yes` on the Contacts row
     - Refresh `last_updated`

  Soft bounces should NOT trigger immediate suppression on the first or second occurrence. Retry the contact on the next natural sequence step.

---

## Section C: After Reply Inbox Is Reviewed

Complete this section each time the Zoho Mail inbox is reviewed for replies. Frequency: at minimum once per business day during active campaign periods.

---

- [ ] **All replies logged: `reply` flag and `reply_category` updated**

  For every reply received from a contact:
  1. Set `reply = Yes` on the Contacts row (Custom5).
  2. Set `reply_category` (Custom6) to the appropriate value from the picklist:

  | Reply type                                | `reply_category` value |
  |-------------------------------------------|------------------------|
  | Expressed interest, asked for more info   | `Interested`           |
  | Declined, not a fit, not interested       | `Not Interested`       |
  | Requested to be removed from list        | `Opt Out`              |
  | Automated out-of-office or vacation reply | `Auto Reply`           |
  | Agreed to a meeting or call               | `Meeting Booked`       |
  | Confirmed a booking                       | `Show Booked`          |
  | Any other reply not fitting above         | `Other`                |

  3. Refresh `last_updated` on the Contacts row.
  4. Write a `REPLY_RECEIVED` event to the audit log:
     ```
     event_type:      REPLY_RECEIVED
     audit_trail_id:  {contact's audit_trail_id}
     contact_id:      {contact_id}
     reply_category:  {reply_category value}
     timestamp:       {ISO 8601}
     notes:           {brief description of reply content}
     ```

---

- [ ] **Opt-out replies: `email_opt_out` set to `Yes` + `OPT_OUT` audit event**

  When a contact replies with any variation of "remove me," "unsubscribe," "stop emailing me," or similar:

  1. Set `email_opt_out = Yes` on the Contacts row.
  2. Set `reply = Yes` and `reply_category = Opt Out`.
  3. Add the email address to `suppression_list.csv` with `reason: OPT_OUT`.
  4. Refresh `last_updated`.
  5. Write an `OPT_OUT` event to the audit log:
     ```
     event_type:      OPT_OUT
     audit_trail_id:  {contact's audit_trail_id}
     contact_id:      {contact_id}
     email:           {contact email}
     method:          REPLY (or LINK_CLICK if via unsubscribe link)
     timestamp:       {ISO 8601}
     ```
  6. Do not reply to the contact to confirm the removal unless they specifically ask for confirmation. Replying to opt-out emails is considered poor practice.

  This step must be completed within **10 business days** of receiving the opt-out request to comply with CAN-SPAM requirements. Same-day processing is strongly preferred.

---

## Section D: When a Meeting Is Scheduled

Complete this section as soon as a discovery call, Zoom meeting, or in-person meeting is confirmed with a contact.

---

- [ ] **Meeting booking: `meeting_booked = Yes` + `MEETING_BOOKED` audit event**

  When a contact agrees to a meeting (via reply, phone, or any channel):

  1. Set `meeting_booked = Yes` on the Gigs_Leads row (Custom2).
  2. If a Gigs_Leads row does not yet exist for this contact, create one now with `status = Lead` and `outcome = Pending`.
  3. Update `reply_category = Meeting Booked` on the Contacts row.
  4. Refresh `last_updated` on the Contacts row.
  5. Write a `MEETING_BOOKED` event to the audit log:
     ```
     event_type:    MEETING_BOOKED
     audit_trail_id: {contact's audit_trail_id}
     contact_id:    {contact_id}
     gig_lead_id:   {gig_lead_id}
     company_id:    {company_id}
     meeting_date:  {YYYY-MM-DD if known, else "TBD"}
     timestamp:     {ISO 8601}
     performed_by:  {user name}
     ```
  6. Add a Note row documenting the meeting context: who initiated, what format (call/Zoom/in-person), proposed agenda.
  7. The contact should be paused from the automated sequence while the meeting is pending. Set `sequence_id` to blank or add a `paused` flag if your workflow supports it, to prevent automated Step N+1 from going out during the meeting window.

---

## Section E: When a Show Is Confirmed/Booked

Complete this section immediately upon receiving confirmation of a booking (signed contract, written confirmation, or verbal confirmation followed by written follow-up).

---

- [ ] **Show booking: `show_booked = Yes` + `SHOW_BOOKED` audit event + Gigs_Leads `status = Gig`**

  When a booking is confirmed:

  1. On the Gigs_Leads row:
     - Set `show_booked = Yes` (Custom3)
     - Set `status = Gig`
     - Set `outcome = Won`
     - Populate `final_fee` with the confirmed fee (numeric USD)
     - Populate `show_date` with the confirmed performance date (YYYY-MM-DD)
     - Populate `venue_name` if not already set
  2. On the Contacts row:
     - Set `reply_category = Show Booked` (unless a more specific value is already set)
     - Refresh `last_updated`
  3. Write a `SHOW_BOOKED` event to the audit log:
     ```
     event_type:    SHOW_BOOKED
     audit_trail_id: {contact's audit_trail_id}
     contact_id:    {contact_id}
     gig_lead_id:   {gig_lead_id}
     company_id:    {company_id}
     final_fee:     {numeric USD value}
     show_date:     {YYYY-MM-DD}
     timestamp:     {ISO 8601}
     performed_by:  {user name}
     ```
  4. Add a Note row documenting the booking details: contract status, any special requirements, who the day-of contact is.
  5. Remove the contact from the outreach sequence (set `sequence_id` to blank or mark sequence as `Completed`). No further sequence emails should be sent to a booked contact for this show cycle.
  6. The Gigs_Leads row with `status = Gig` is now the canonical record for financial reporting. Confirm it is linked to the correct Companies and Contacts rows via `company_id` and `contact_id`.

---

## Audit Log Reference

All events described in this checklist write to the same audit log. The audit log is a flat table (separate sheet or CSV file) with the following minimum columns:

| Column          | Description |
|-----------------|-------------|
| `log_id`        | UUID4, auto-generated per event |
| `event_type`    | One of the event type values listed in this document |
| `audit_trail_id`| Links to the Contacts row's `audit_trail_id` |
| `contact_id`    | FK to Contacts sheet |
| `gig_lead_id`   | FK to Gigs_Leads sheet (when applicable) |
| `company_id`    | FK to Companies sheet (when applicable) |
| `timestamp`     | ISO 8601 datetime of the event |
| `performed_by`  | Username or "system" |
| `notes`         | Free-text notes about the event |
| Additional fields as noted per event type above |

Valid `event_type` values (maintain in Lookups sheet):
```
EMAIL_SENT
EMAIL_SEND_FAILED
BOUNCE (HARD)
SOFT_BOUNCE
BOUNCE (SOFT_3X_SUPPRESSED)
REPLY_RECEIVED
OPT_OUT
MEETING_BOOKED
SHOW_BOOKED
VENUE_MERGE
CONTACT_MERGE
BULK_IMPORT
BULK_UPDATE
SUPPRESSION_SKIP
AUDIT_ID_ASSIGNED
DAILY_SEND_COUNT
MANUAL_REVIEW
```

---

## Post-Send Audit Sign-Off

Complete after running all applicable checklist sections:

| Item                                  | Value |
|---------------------------------------|-------|
| Audit date                            | `YYYY-MM-DD` |
| Batch reviewed                        | `[batch name or date]` |
| Total emails sent in batch            | `#` |
| Hard bounces found and processed      | `#` |
| Soft bounces found and tracked        | `#` |
| Opt-outs processed                    | `#` |
| Meetings booked and logged            | `#` |
| Shows booked and logged               | `#` |
| Audit log events written              | `#` |
| Reviewed by                           | `[Name]` |
| All applicable sections completed?    | `Yes / No` |
| Notes on any exceptions               | _(describe)_ |

---

## Drop-In Reusability Notes

This post-send CRM audit checklist can be reused for any outbound email campaign using an Excel/CSV CRM and any SMTP-based sending platform. To adapt it for a new campaign:

1. **The audit log event types** are the most campaign-specific element. Review the full event type list and add any new event types required by the new campaign's workflow (e.g., `CONTRACT_SENT`, `DEPOSIT_RECEIVED`, `SHOW_COMPLETED`). Add new types to the Lookups sheet.
2. **The soft bounce threshold of 3** is a reasonable default for cold outreach campaigns. For campaigns sending to a warmer list or with longer gaps between sequence steps, this threshold may be adjusted.
3. **The opt-out processing timeline** (10 business days per CAN-SPAM) is a legal requirement and must not be changed in any adaptation. Process opt-outs same-day whenever possible.
4. **Section D (Meeting Booked) and Section E (Show Booked)** reflect the two-step conversion model for theatrical booking. For a different campaign with a different conversion model (e.g., single-step direct booking, or a multi-step contract process), revise these sections and their corresponding audit event types accordingly.
5. **The Sign-Off table** is universal. Consider maintaining a running log of completed sign-offs in a dedicated `audit_sign_off_log` tab in the CRM workbook, with one row per batch, to create a permanent record of post-send review compliance.
6. **The audit log structure** (flat table with `log_id`, `event_type`, `audit_trail_id`, etc.) is universal and should remain unchanged across campaigns. The `audit_trail_id` FK to the Contacts sheet is the critical link that enables per-contact activity history reconstruction.
