# Sequence Step 4 — Breakup / Final Touch
**Day:** 14 (14 days after Step 1)
**Template file:** `templates/email/breakup.j2`

## Purpose
Final email in the sequence. Clear, gracious, respects the contact's time. Leaves the door open for a future season without being pushy. Provides a genuine opt-out offer. No new sales content.

## Subject Line
```
Leaving the door open for {{ next_season }}
```

## Key Content Elements
1. Acknowledge this is the last message
2. Three explicit options for the contact to respond:
   - "Not a fit right now but sounds interesting → reconnect for {{ next_season }}"
   - "Genuinely not a fit at all → say the word and we won't reach out again"
3. Brief appreciation: "thank you for the work you do bringing live performance to {{ city }}"
4. CAN-SPAM footer with explicit removal offer

## Tone Guide
- Gracious, not desperate
- Three clear options to respond (interested, future interest, no interest)
- Thank the contact for their work — genuine, not performative
- No new selling points. The sequence has done its job.

## CRM Actions on Send
- `Contacts.Custom2` (step_number) = `4`
- `Gigs_Leads.Custom4` (send_time) = ISO 8601 timestamp
- Audit event: `EMAIL_SENT` with `step=4`
- Contact is now at end of sequence — do not send further steps unless explicitly re-enrolled

## Post-Step 4 Rules
- Contact is NOT suppressed after Step 4 (they can still reply)
- If contact replies with "try next season" → add Note to Notes sheet, set `Gigs_Leads.Custom4` with target reconnect date
- If contact replies with "not a fit / remove me" → treat as Opt-Out immediately

---

## Drop-In Reusability Notes
The breakup email structure (three explicit options, genuine thanks, no sales content) applies universally to outbound B2B sequences. Update `{{ next_season }}` and `{{ city }}` tokens, and reference the show/product name once. Keep it short — breakup emails that run long undermine their own message.
