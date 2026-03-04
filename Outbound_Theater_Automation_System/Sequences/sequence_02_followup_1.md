# Sequence Step 2 — Follow-Up 1
**Day:** 5 (5 days after Step 1)
**Template file:** `templates/email/followup_1.j2`

## Purpose
Reinforce with social proof and logistics specifics. Shorter than Step 1. Assumes the contact received Step 1 but hasn't responded. Adds new value (proven results, logistics ease) rather than repeating the original message.

## Subject Line
```
Quick follow-up: Princess Peigh at {{ venue_name }}
```

## Key Content Elements
1. Brief reference to previous email (no re-introduction)
2. Social proof: Irvington Theater, sold-out Jewish community runs, testimonial reference
3. Logistics ease: self-contained, efficient load-in, no complicated rider
4. Geographic/seasonal hook: "booking for the upcoming season in the {{ state }} region"
5. Soft CTA: "Worth a quick call?"
6. CAN-SPAM footer

## Tone Guide
- Shorter than Step 1 (aim for under 150 words body text)
- Confident, not apologetic about following up
- New information only — no repetition of Step 1 bullets

## CRM Actions on Send
- `Contacts.Custom2` (step_number) = `2`
- `Gigs_Leads.Custom4` (send_time) = ISO 8601 timestamp
- `Contacts.Custom7` (last_updated) = ISO 8601 timestamp
- Audit event: `EMAIL_SENT` with `step=2`

---

## Drop-In Reusability Notes
Adapt the social proof section for the new show's actual proven performances. Keep the structure (brief reference → new social proof → logistics ease → soft CTA) — it works across venue outreach contexts. Do not repeat Step 1 content.
