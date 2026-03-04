# Escalation Rules

## Escalation Matrix

| Category | Escalate To | Timeline | Channel |
|----------|-------------|----------|---------|
| Interested | Melissa Neufer + Zachary Gartrell | Same day | Direct notification (text/email) |
| Budget Question | Zachary Gartrell | Within 48h | Email review queue |
| Programming Window | Zachary Gartrell | Within 48h | Email review queue |
| Referral | Zachary Gartrell | Within 24h | Email review queue + CRM update |
| Not a Fit | None | — | CRM update only |
| Opt-Out | None | Immediate | Suppression list only |
| Out of Office | None | Return date | Notes log; manual re-queue |
| Bounce | None | Immediate | Suppression list + audit log |

## Human Approval Requirement

**ALL reply responses require human review and approval before sending.** No exceptions. No auto-responses.

Reason: The brand voice (whimsical, confident, peer-to-peer) must be maintained in every response. An automated response that mismatches the tone or context can damage a relationship that took 4 emails to build.

## Drafting Replies

For **Interested** replies:
1. Zachary drafts response
2. Melissa reviews if booking involves creative decisions (dates, format, workshop)
3. Response sent from Zachary's Zoho account
4. CRM updated with `MEETING_BOOKED` event if call is scheduled

For **Budget/Programming Window** replies:
1. Zachary drafts response
2. No mandatory second review unless numbers are non-standard
3. Response sent from Zachary's Zoho account

## Response Logging

After every human reply is sent:
1. Log call/meeting to Calls sheet if applicable
2. Update Gigs_Leads.Status if pipeline stage changes
3. Write `REPLY_RECEIVED` audit event with category
4. If meeting scheduled: write `MEETING_BOOKED` audit event + set `Gigs_Leads.Custom2 = Yes`

---

## Drop-In Reusability Notes
The escalation matrix (Same day for Interested, 48h for budget/window, 24h for referral) is a reasonable default for any high-touch B2B outreach. Adjust timelines based on team capacity. The "human approval for all replies" rule is non-negotiable for brand-critical outreach — always keep it.
