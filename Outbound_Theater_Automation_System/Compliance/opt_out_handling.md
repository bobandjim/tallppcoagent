# Opt-Out Handling Procedures

## How Opt-Outs Arrive
1. **Reply-based:** Contact replies with opt-out language ("unsubscribe," "remove me," "stop," "don't contact me again")
2. **Link-based:** Contact clicks unsubscribe URL in email footer
3. **Manual:** Team member identifies an opt-out and manually processes it

## Required Response Time
- **CAN-SPAM:** Within 10 business days
- **This system's safe default:** Same-day processing

## Processing Procedure
1. Identify opt-out (from reply inbox or unsubscribe form)
2. Add to suppression list: `SuppressionList.add(email, "OPT_OUT")`
3. Set `Contacts.Email Opt Out = Yes` in Excel CRM
4. Write audit event: `audit.log("OPT_OUT", lead_id=..., payload={"email": ...})`
5. Update `Gigs_Leads.Custom1` (outcome) = `"Suppressed"`
6. Export updated CRM to Excel

## What NOT to Do
- Do NOT delete the contact record — keep for reference and to prevent re-import
- Do NOT re-add an opted-out address to any future campaigns
- Do NOT send a "confirmation" email to the opt-out (adds to spam risk)
- Do NOT ask why they opted out (unsolicited follow-up after opt-out is problematic)

## Suppression List Maintenance
File: `config/suppression_list.csv`
Format: `email,reason,suppressed_at`

The suppression list is checked before every send in `DeliverabilityGuard`. It is never purged — only appended.

---

## Drop-In Reusability Notes
This opt-out procedure is standard for any CAN-SPAM-compliant outbound system. The only customization needed is the suppression list file path and the CRM field names for `email_opt_out` and `outcome`. The processing procedure itself is universal.
