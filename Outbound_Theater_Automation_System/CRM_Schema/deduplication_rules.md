# Deduplication Rules

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**CRM Format:** Excel/CSV, 6-sheet structure
**Last Updated:** 2026-03-04

---

## Overview

Deduplication (dedup) is the process of identifying and resolving records that represent the same real-world entity appearing more than once in the CRM. Failing to dedup results in:

- Duplicate outreach emails sent to the same contact
- Inflated lead counts and inaccurate pipeline reporting
- Inconsistent data across records that should be one

This document defines the dedup rules for the two primary record types that are prone to duplication: **Venues** (Companies sheet) and **Contacts** (Contacts sheet). Gigs_Leads records are not deduped because each one is intentionally created by a human user; however, orphaned or duplicate Gigs_Leads should be manually reviewed when a venue or contact merge occurs.

Dedup should be run:
- Before any bulk import from a new data source
- After any manual data entry session
- Weekly as a maintenance task if the database is actively growing

---

## Part 1: Venue Deduplication (Companies Sheet)

### 1.1 Dedup Key

The venue dedup key is a composite of two normalized fields:

```
dedup_key = normalize(company) + "|" + normalize(state)
```

**Normalization rules for `company`:**
- Convert to lowercase
- Strip leading/trailing whitespace
- Remove all punctuation except hyphens within words (apostrophes, periods, commas, ampersands replaced with empty string or space)
- Replace `&` with `and`
- Collapse multiple spaces into one
- Remove common legal suffixes that do not differentiate venues: `inc`, `llc`, `ltd`, `corp`, `co`
- Do not remove words like `theater`, `theatre`, `center`, `centre`, `arts` — these are meaningful

**Normalization rules for `state`:**
- Convert to uppercase two-letter abbreviation
- Strip whitespace

**Example:**

| Raw company          | Raw state | Normalized key                          |
|----------------------|-----------|-----------------------------------------|
| Beck Center for Arts | OH        | `beck center for arts\|OH`              |
| Beck Center for the Arts | OH    | `beck center for the arts\|OH`          |
| Beck Center For Arts | OH        | `beck center for arts\|OH`              |
| Beck Center for Arts | PA        | `beck center for arts\|PA`              |

In the example above, rows 1 and 3 share a dedup key and are duplicates. Rows 1 and 4 have different states and are distinct venues.

Note: "for" vs "for the" produces different keys in this schema. Human review is recommended when the normalized name differs by only stopwords (`the`, `a`, `an`, `of`, `for`). A secondary fuzzy similarity check (Levenshtein distance < 5 on the name component) can be used as a flagging heuristic, but humans make the final merge decision.

### 1.2 Merge Strategy for Venues

When two venue rows share the same dedup key:

1. **The row with the higher numeric ID suffix wins** (the more recently created record is the survivor). Because `lead_id` uses the format `VEN-{UUID4}`, compare the `last_updated` timestamp instead of the UUID itself. The record with the more recent `last_updated` is the survivor.
2. **Field-level merge:** For each field, if the survivor has a null/blank value and the losing record has a non-null value, copy the non-null value from the losing record into the survivor. Non-null fields on the survivor are never overwritten by values from the losing record.
3. **Relationship re-pointing:** All Contacts rows with `company_id` matching the losing record's `lead_id` must be updated to reference the survivor's `lead_id`. All Gigs_Leads rows must likewise be re-pointed.
4. **Losing record disposition:** Mark the losing record with a special `notes` annotation: `[MERGED into {survivor_lead_id} on {YYYY-MM-DD}]`. Do not delete the row. This preserves auditability. The row should be visually hidden or filtered in normal working views by adding a `merged` flag column (Boolean, `Yes`/`No`, default `No`).

### 1.3 Audit Logging for Venue Merges

Write the following event to the audit log when a venue merge is executed:

```
event_type:   VENUE_MERGE
timestamp:    {ISO 8601}
survivor_id:  {lead_id of surviving record}
loser_id:     {lead_id of merged-away record}
fields_copied: {comma-separated list of fields copied from loser to survivor}
performed_by: {user or "system"}
```

---

## Part 2: Contact Deduplication (Contacts Sheet)

### 2.1 Dedup Key

The contact dedup key is a single normalized field:

```
dedup_key = normalize(email)
```

**Normalization rules for `email`:**
- Convert to lowercase
- Strip leading/trailing whitespace
- Do not strip subaddress tags (e.g., `name+tag@domain.com` is treated as distinct from `name@domain.com` unless manually reviewed)
- Do not resolve email aliases — treat each address as-is

**Example:**

| Raw email                    | Normalized key               |
|------------------------------|------------------------------|
| Director@BeckCenter.org      | director@beckcenter.org      |
| director@beckcenter.org      | director@beckcenter.org      |
| DIRECTOR@BECKCENTER.ORG      | director@beckcenter.org      |
| director@beckcenter.org (space trailing) | director@beckcenter.org |

Rows 1, 2, 3, and 4 all normalize to the same key and are duplicates.

### 2.2 Merge Strategy for Contacts

When two contact rows share the same normalized email:

1. **Survivor selection:** The contact with the more recent `last_updated` timestamp is the survivor.
2. **Field-level merge:** For each field, if the survivor has a null/blank value and the losing record has a non-null value, copy the non-null value from the losing record into the survivor. The survivor's non-null values are never overwritten.
3. **Critical fields — manual review required before merge:**
   - `email_opt_out`: If either record has `email_opt_out = Yes`, the merged survivor must have `email_opt_out = Yes`. Opt-out status is never lost in a merge.
   - `sequence_id` and `step_number`: If both records have different active sequences, a human must decide which sequence the merged contact should continue.
4. **Relationship re-pointing:** All Gigs_Leads rows referencing the losing `contact_id` must be updated to reference the survivor's `contact_id`.
5. **Losing record disposition:** Annotate the losing record's first_name field or a dedicated notes column: `[MERGED into {survivor_contact_id} on {YYYY-MM-DD}]`. Do not delete. Apply the `merged = Yes` flag.

### 2.3 Audit Logging for Contact Merges

Write the following event to the audit log when a contact merge is executed:

```
event_type:    CONTACT_MERGE
timestamp:     {ISO 8601}
survivor_id:   {contact_id of surviving record}
loser_id:      {contact_id of merged-away record}
fields_copied: {comma-separated list of fields copied from loser to survivor}
opt_out_note:  {Yes if opt_out was inherited from loser, No otherwise}
performed_by:  {user or "system"}
```

---

## Part 3: Edge Cases

### 3.1 Contacts with No Email Address

Some contacts may have only a phone number or mailing address — no email. These contacts:

- Cannot be deduped against other contacts using the email key
- Are **kept without deduplication** — each no-email contact row is treated as unique
- Are **excluded from all email outreach sequences** (they cannot be targeted without an email)
- May still appear on Calls records and Notes records for phone outreach tracking
- Should be manually reviewed periodically to see if an email address has been discovered

When a no-email contact is later updated with a valid email address, run the dedup check immediately after the email is added to catch newly created duplicates.

### 3.2 Venues with No State

Some venue records may be imported without a state value (e.g., scraped data from a source that didn't include state, or an international venue added by mistake). These venues:

- Cannot be deduped using the standard composite key (since state is part of the key)
- Are **flagged for manual review** — a placeholder state of `XX` is added to signal missing data
- Dedup key becomes: `normalize(company) + "|XX"` — this will match other no-state venues with the same name, triggering a merge, but will never accidentally match a real state-specific record
- Venue should not be actively worked until state is confirmed and corrected

Recommended process: Create a filtered view of the Companies sheet showing all rows where `state = XX` or `state` is blank. Review and correct weekly.

### 3.3 Same Venue, Multiple Locations

Some venue organizations operate multiple distinct performance spaces in different cities (e.g., a regional arts council with two buildings). These are **not duplicates** — they are distinct venues that happen to share an organization name.

Resolution:
- Enter each physical location as a separate Companies row
- Differentiate by using the specific location name in the `venue_name` field (Custom4)
- Both rows may share the same organization in `company`, but the combination of `company + city` will differ
- The dedup key (company + state) may match both — in this case, a human reviewer should override the system merge recommendation and mark both records as intentionally separate using a `dedupe_override = Yes` flag column

### 3.4 Spelling Variants and Abbreviations

The normalization rules will not catch all spelling variants. Known edge cases:

| Variant A                          | Variant B                          | Same venue? |
|------------------------------------|------------------------------------|-------------|
| Community Theater of Medina        | Community Theatre of Medina        | Yes (theater/theatre variant) |
| St. Joseph Cultural Arts Center    | Saint Joseph Cultural Arts Center  | Likely yes (saint/st variant) |
| Tri-County Arts Council            | Tri County Arts Council            | Yes (hyphen variant) |
| WVPAC                              | West Virginia Performing Arts Center | Maybe — requires human review |

Recommendation: After automated dedup, run a secondary pass that groups venues by state and sorts by normalized name, allowing a human to visually scan for near-matches. This is a manual step and should be logged as a `MANUAL_REVIEW` event.

### 3.5 Contacts Who Change Organizations

A contact may move from one venue to another. This is not a duplicate — it is a data update. The contact's `company_id` should be updated to the new venue, and a Note should be written documenting the change. Do not create a new contact record. This preserves the contact's full outreach history.

---

## Drop-In Reusability Notes

This deduplication rules document can be reused for any campaign using the same 6-sheet Excel/CSV CRM structure. To adapt it for a new show or campaign:

1. **The dedup keys are universal** — normalized `company + state` for venues and normalized `email` for contacts are appropriate for virtually any outbound theatrical booking campaign. No changes needed unless the CRM structure changes fundamentally.
2. **The opt-out merge rule is non-negotiable** — always ensure that `email_opt_out = Yes` is never lost during a contact merge. This rule must be preserved in any adaptation to maintain CAN-SPAM compliance.
3. **The no-email edge case section** may expand if the new campaign includes a significant portion of phone-only or mail-only outreach. In that case, consider adding a secondary dedup key based on phone number.
4. **The multi-location edge case** is common in performing arts — any campaign targeting regional arts organizations will encounter it. The override flag approach described here is reusable as-is.
5. **Audit log event types** (`VENUE_MERGE`, `CONTACT_MERGE`, `MANUAL_REVIEW`) should be added to the Lookups sheet's `event_type` picklist when adapting this system for a new campaign.
