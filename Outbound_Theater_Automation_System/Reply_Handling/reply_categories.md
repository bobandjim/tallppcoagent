# Reply Categories

Human reviews all replies. No auto-responses. This document defines how to classify and act on each reply type.

## Category Definitions

### Interested
**Trigger signals:** "yes," "interested," "tell me more," "sounds good," "let's talk," "I'd love to," "can you send," "scheduling a call"

**CRM Actions:**
- `Contacts.Custom5` (email_reply) = `Yes`
- `Contacts.Custom6` (reply_category) = `Interested`
- `Gigs_Leads.Custom1` (outcome) = `Interested`
- Write audit event: `REPLY_RECEIVED` with `category=Interested`

**Escalation:** Notify both Melissa Neufer and Zachary Gartrell same day. Human drafts response within 24 hours.

---

### Budget Question
**Trigger signals:** "fee," "cost," "budget," "how much," "pricing," "what do you charge," "do you do revenue share"

**CRM Actions:**
- `reply_category` = `Budget Question`
- Write audit event: `REPLY_RECEIVED` with `category=Budget Question`

**Escalation:** Zachary responds within 48h. Response should offer the 3 pricing models (flat fee, ticket split, guarantee + percentage) and ask about their typical structure.

---

### Programming Window Question
**Trigger signals:** "season," "calendar," "availability," "when are you available," "dates," "we're booking for"

**CRM Actions:**
- `reply_category` = `Programming Window Question`
- Write audit event: `REPLY_RECEIVED` with `category=Programming Window Question`

**Escalation:** Zachary responds within 48h with current touring calendar availability.

---

### Referral
**Trigger signals:** "you should contact," "try [name]," "I'm forwarding you to," "better person to talk to"

**CRM Actions:**
- `reply_category` = `Referral`
- Add note to Notes sheet: referred contact name and venue
- Create new lead row in CRM for referred contact (if sufficient info provided)
- Write audit event: `REPLY_RECEIVED` with `category=Referral`

**Escalation:** Zachary creates new CRM row within 24h. Warm introduction if possible.

---

### Not a Fit
**Trigger signals:** "not interested," "no thank you," "not right for us," "we don't book touring shows," "our programming doesn't include," "we're full for the season"

**CRM Actions:**
- `reply_category` = `Not a Fit`
- `Gigs_Leads.Custom1` (outcome) = `Not a Fit`
- `Gigs_Leads.Status` = `Lead` (stays as lead, not converted)
- Write audit event: `REPLY_RECEIVED` with `category=Not a Fit`

**Escalation:** None. No further follow-up. Do NOT suppress — they can be re-contacted in a future season.

---

### Opt-Out
**Trigger signals:** "unsubscribe," "remove me," "stop emailing," "don't contact me," "take me off your list"

**CRM Actions:**
- `Contacts.Email Opt Out` = `Yes`
- `reply_category` = `Opt-Out`
- Immediately add to suppression list: `SuppressionList.add(email, "OPT_OUT")`
- Write audit event: `OPT_OUT`
- `outcome` = `Suppressed`

**Escalation:** None. No response. No confirmation email. Honor immediately.

---

### Out of Office
**Trigger signals:** "I am currently out of office," "I will return on," "auto-reply," "I'm away from email," "please contact [alternative]"

**CRM Actions:**
- `reply_category` = `Out of Office`
- Add note to Notes sheet: "OOO — return date [date]" if available
- Do NOT suppress, do NOT mark as opt-out
- Re-queue for follow-up after return date

**Escalation:** None automated. Human manually checks return date and re-queues next step if appropriate.

---

### Bounce
**Trigger signals:** SMTP error codes, "mailer-daemon" sender, "delivery failure," "address not found," "mailbox does not exist"

**CRM Actions (Hard Bounce):**
- Immediately add to suppression: `SuppressionList.add(email, "HARD_BOUNCE")`
- `reply_category` = `Bounce`
- `outcome` = `Bounced`
- Write audit event: `BOUNCE`

**CRM Actions (Soft Bounce — 3x threshold):**
- Log soft bounce in Notes sheet
- After 3 soft bounces: add to suppression: `SuppressionList.add(email, "SOFT_BOUNCE")`
- Write audit event: `BOUNCE`

---

## Drop-In Reusability Notes
These 8 reply categories and their CRM actions apply to any outbound B2B sequence. Update trigger signals if needed for different industries (e.g., "we're fully booked" is theater-specific). The core categories (Interested, Budget, Not a Fit, Opt-Out, OOO, Bounce) are universal.
