# Auto-Logging Specification — Reply Handling to CRM

## Overview
This document defines which CRM fields are updated and which audit events are written for each reply category. These updates happen when the human operator processes a reply.

## Field Update Map

### On Any Reply (all categories)
| Field | Value | Sheet |
|-------|-------|-------|
| `Contacts.Custom5` (email_reply) | `Yes` | Contacts |
| `Contacts.Custom6` (reply_category) | [category string] | Contacts |
| `Contacts.Custom7` (last_updated) | ISO 8601 timestamp | Contacts |
| Audit event | `REPLY_RECEIVED` | audit.db |

### Category-Specific Additional Updates

**Interested:**
- `Gigs_Leads.Custom1` (outcome) = `Interested`
- Add note to Notes sheet: "Reply: Interested — [date]"

**Budget Question / Programming Window:**
- Add note to Notes sheet: "[category] — [summary of question] — [date]"

**Referral:**
- Add note to Notes sheet: "Referral: [referred contact name, venue, email if available] — [date]"
- Create new Companies + Contacts rows for referred venue if sufficient info

**Not a Fit:**
- `Gigs_Leads.Custom1` (outcome) = `Not a Fit`

**Opt-Out:**
- `Contacts.Email Opt Out` = `Yes`
- `Gigs_Leads.Custom1` (outcome) = `Suppressed`
- Audit event: `OPT_OUT`
- Write to `config/suppression_list.csv`: `email,OPT_OUT,[timestamp]`

**Meeting Booked (after Interested reply results in scheduled call):**
- `Gigs_Leads.Custom2` (meeting_booked) = `Yes`
- Create Calls row: Subject="Discovery Call with [venue_name]", Status="Planned", CallDateTime=[date/time]
- Audit event: `MEETING_BOOKED`

**Show Booked (after call results in confirmed performance):**
- `Gigs_Leads.Custom3` (show_booked) = `Yes`
- `Gigs_Leads.Status` = `Gig`
- `Gigs_Leads.Fee` = agreed fee
- `Gigs_Leads.Show Date` = confirmed date
- `Gigs_Leads.Venue Name` = confirmed venue
- `Gigs_Leads.Custom1` (outcome) = `Booked`
- Audit event: `SHOW_BOOKED`

**Hard Bounce:**
- `Gigs_Leads.Custom1` (outcome) = `Bounced`
- Write to `config/suppression_list.csv`: `email,HARD_BOUNCE,[timestamp]`
- Audit event: `BOUNCE`

## Audit Event Payloads

All events written via `src/utils/audit.py`:

```python
audit.log(
    "REPLY_RECEIVED",
    lead_id=gig.gig_lead_id,
    audit_trail_id=contact.audit_trail_id,
    payload={
        "email": contact.email,
        "category": "Interested",
        "step": contact.step_number,
        "summary": "Brief human-written summary of reply content",
    }
)
```

---

## Drop-In Reusability Notes
This field update map is specific to the 6-sheet Excel CRM structure. For a different CRM, update the field names but keep the update logic:
1. Mark reply on contact record
2. Update gig/deal status
3. Write audit event
4. Create call/note record for significant events
5. Trigger suppression for opt-outs and bounces immediately
