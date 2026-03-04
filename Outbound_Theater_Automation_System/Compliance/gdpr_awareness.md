# GDPR / UK PECR / CASL Awareness
**Not legal advice. Document current awareness only. Consult a lawyer before contacting non-US venues.**

## Scope of This System
This system is designed for US-based outreach to US venues. International contacts require additional review.

## If You Plan to Contact Non-US Venues

### European Union (GDPR)
- GDPR applies to contacts in EU member states regardless of where the sender is located
- B2B cold outreach may be permissible under "legitimate interest" grounds, but requirements are stricter than US CAN-SPAM
- Recommended default: do not include EU contacts in automated sequences without legal review
- Flag any EU venue in CRM: Companies.Notes = "EU venue — GDPR review needed before outreach"

### United Kingdom (UK PECR)
- Similar to GDPR post-Brexit; separate regulation
- B2B email marketing requires either consent or soft opt-in from prior business relationship
- Recommended default: do not include UK contacts in automated sequences without review

### Canada (CASL — Canada's Anti-Spam Legislation)
- CASL is stricter than CAN-SPAM; requires express or implied consent before commercial email
- Implied consent may exist for venues that have publicly listed contact info for commercial purposes
- CASL violations can result in significant fines
- Recommended default: flag Canadian venues; only contact with documented implied consent

## How to Flag International Contacts in CRM
In the Gigs_Leads sheet: set `Gigs_Leads.Custom1` (outcome) = `"International — Hold"`
In Companies.Notes: add "International: [country] — compliance review needed before outreach"
Do NOT assign a sequence_id to these contacts until reviewed.

## Safe Defaults for This System
1. Only include contacts where venue is in the US (Companies.Billing Country = "USA")
2. Any non-US venue goes into a "hold" state in the CRM
3. Document any exceptions and the legal basis in the CRM notes

---

## Drop-In Reusability Notes
This document is reusable for any outbound system that may expand internationally. Update the country list and legal references as scope expands. The CRM flagging approach (set outcome = "International — Hold") applies regardless of the target country.
