# CAN-SPAM Compliance Guidelines
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Important Notice

**This document is not legal advice.** It describes the team's internal operational guidelines for maintaining CAN-SPAM-safe email practices. These guidelines represent safe defaults based on the CAN-SPAM Act of 2003 and broadly accepted email compliance practice. For formal legal guidance, consult a licensed attorney familiar with email marketing and commercial communications law.

CAN-SPAM applies to commercial email messages. Outreach emails sent to venue programming directors on behalf of a touring theatrical show are commercial communications and are subject to the CAN-SPAM Act.

---

## Overview of CAN-SPAM Requirements

The CAN-SPAM Act establishes seven categories of requirements for commercial email. Each is summarized below with the safe default behavior and how this system enforces it.

---

## Requirement 1: Accurate "From" and Sender Identity

### What the law requires
The sender's name and email address must accurately identify who is sending the email. The "From" name and domain must not be falsified or misleading. Spoofing a sender identity — making an email appear to come from someone other than the actual sender — is prohibited.

### Safe default for this system
- **"From" name:** `Tall People Performing Company` (configured in `config/settings.yaml` → `compliance.sender_name`)
- **"From" email:** The registered Zoho Mail sending address (e.g., `bookings@yourdomainhere.com`)
- **Reply-To:** Must match the sending domain or a legitimate monitored inbox

### How the system enforces it
`CANSPAMChecker.validate()` checks that `config.compliance.sender_name` is non-blank before any email is sent. If the sender name field is empty or missing from config, the send is blocked and a `COMPLIANCE_BLOCK` event is logged.

The DKIM authentication setup (see `spf_dkim_dmarc_checklist.md`) cryptographically verifies that email originates from the declared sending domain, which technically enforces the anti-spoofing requirement.

### Operator responsibility
- Do not change the "From" name or "From" email in `settings.yaml` without a documented reason
- The sending address must be monitored — replies, bounces, and opt-out requests may arrive there and require action
- Do not use a "no-reply@" address. All outbound emails must come from an address capable of receiving replies.

---

## Requirement 2: Non-Deceptive Subject Lines

### What the law requires
Subject lines must accurately reflect the content of the email. A subject line that misleads the recipient about the content of the message (e.g., "Your order has shipped" when there is no order) violates CAN-SPAM.

### Safe default for this system
Subject lines are defined in the sequence YAML (`sequences/theater_outreach_v1.yaml`) and must accurately reflect the content of each email step:
- Step 1: Should indicate a booking inquiry about the show
- Step 2: Should indicate a follow-up to the initial email
- Step 3: Should reference the resource or information included
- Step 4: Should indicate a final outreach note

### How the system enforces it
`CANSPAMChecker.validate()` checks that the subject line field is non-blank. Content accuracy is a human review responsibility — the system cannot assess whether a subject line is "deceptive." All subject lines must be reviewed by Melissa Neufer or Zachary Gartrell before they are added to the sequence YAML.

### What operators must NOT do
- Do not use urgent or false-alarm subject lines ("Your listing has been flagged", "Invoice enclosed", "Re: our meeting yesterday" when no prior meeting occurred)
- Do not use subject lines that imply a pre-existing relationship that does not exist
- Do not use "RE:" or "FW:" prefixes to imply a conversation thread that did not take place

---

## Requirement 3: Physical Mailing Address

### What the law requires
Every commercial email must include a valid physical postal address of the sender. This can be a street address, a PO Box (compliant if valid USPS PO Box), or a private mailbox registered with a commercial mail receiving agency.

### Safe default for this system
The physical address is included in every email footer, rendered from `config/settings.yaml` → `compliance.physical_address`.

**Example config entry:**
```yaml
compliance:
  physical_address: "123 Main Street, Suite 100, City, State 12345"
```

This value is injected into every email template via the Jinja2 base template's footer block:
```
{{ config.compliance.physical_address }}
```

### How the system enforces it
`CANSPAMChecker.validate()` checks that `config.compliance.physical_address` is non-blank before any email is sent. If the field is empty, the send is blocked and a `COMPLIANCE_BLOCK` event is logged.

### Operator responsibility
- The physical address must be a real, valid address associated with Tall People Performing Company
- The address must be kept current in `settings.yaml` — if the company moves or changes address, update the config before the next send run
- Do not use a fake address or a foreign address. The address must be a valid US address for USPS delivery.

---

## Requirement 4: Unsubscribe Mechanism

### What the law requires
Every commercial email must include a clear and conspicuous mechanism for the recipient to opt out of future emails. The unsubscribe mechanism must:
- Be clearly visible (not hidden in tiny print or behind multiple clicks)
- Be functional at the time of sending
- Remain functional for at least 30 days after the email is sent
- Not require the recipient to provide any information beyond their email address to unsubscribe
- Not require the recipient to pay any fee to unsubscribe

### Safe default for this system
Every email includes an unsubscribe link in the email footer, rendered from `config/settings.yaml` → `compliance.unsubscribe_url`.

**Example config entry:**
```yaml
compliance:
  unsubscribe_url: "https://yourdomainhere.com/unsubscribe?id={{ contact.audit_trail_id }}"
```

Alternatively, the footer includes a clear instruction to reply with "unsubscribe" in the subject line, which is handled by the reply classification system (see `reply_categories.md`).

### How the system enforces it
`CANSPAMChecker.validate()` checks that `config.compliance.unsubscribe_url` is non-blank before any email is sent. If the URL is empty or missing, the send is blocked.

The base Jinja2 template includes the unsubscribe link in a mandatory footer block that cannot be overridden by individual step templates.

### Operator responsibility
- Ensure the unsubscribe URL is functional before each sending period — test it manually
- If the URL changes (e.g., new domain or new unsubscribe system), update `settings.yaml` immediately — any email sent with a dead unsubscribe URL is a CAN-SPAM violation
- Unsubscribe links must remain functional for 30 days after the last email sent to any recipient. Do not take down the unsubscribe handler prematurely.

---

## Requirement 5: Honoring Opt-Out Requests

### What the law requires
Opt-out requests must be honored within 10 business days of receipt. You may not charge a fee, require additional information, or require the recipient to take any additional steps beyond the unsubscribe mechanism.

### Safe default for this system
**Opt-outs are honored within 24 hours**, not 10 business days. This is a stricter internal standard that is far below the legal maximum and reduces the risk of sending to someone who has asked to be removed.

### How the system enforces it

When an opt-out is received (via unsubscribe link click or reply with opt-out language):

1. `email_opt_out` field in Contacts sheet is set to `Yes` immediately
2. `Custom5` (email_opt_out_flag) is set to `Yes` immediately
3. Email is added to `config/suppression_list.csv` with `reason=OPT_OUT`
4. An `OPT_OUT` audit event is written to `audit_log.db`
5. On the next automation run, `get_eligible_contacts()` filters out any contact where `email_opt_out = Yes`

The sequence engine checks the opt-out flag before every send. A contact who opts out between Step 1 and Step 2 will never receive Step 2.

### What operators must NOT do
- Do not continue sending to a contact who has asked to unsubscribe, even if the sequence is almost complete
- Do not send a "confirmation" email to an opt-out request (one additional email to confirm removal is technically permissible under CAN-SPAM, but the safe default is to send nothing further)
- Do not re-enroll an opted-out contact in a new sequence without documented consent

---

## Requirement 6: No Harvested or Purchased Lists

### What the law requires
CAN-SPAM does not explicitly prohibit purchased or harvested lists, but using them significantly increases compliance risk, deliverability risk, and the likelihood of spam complaints. More importantly, building lists from publicly available sources without any indication of interest or relationship is ethically questionable and operationally counterproductive.

### Safe default for this system
All contacts entered into the CRM must be:
- Researched by a team member using publicly available venue directories, state arts council listings, or similar professional sources
- Verified to be associated with a qualifying venue (see `01_lead_intake_workflow.md`, Qualification Criteria)
- Found via sources appropriate to the industry (arts council directories, venue websites, professional LinkedIn profiles)

### What is NOT permitted
- Purchasing email lists from third-party data vendors without compliance review
- Scraping email addresses from websites en masse using automated tools
- Using email addresses provided for a different purpose (e.g., a press contact database sold by another company)
- Adding contacts from personal social media networks who have not indicated professional programming interest

### Operator responsibility
Each lead intake must include a note in the Contacts sheet indicating the source of the email address (e.g., "Venue website staff page," "State Arts Council directory," "LinkedIn public profile"). This source documentation is part of the record and may be relevant in the event of a complaint or audit.

---

## Requirement 7: Prohibition on Address Harvesting

### What the law requires
Certain forms of email address harvesting are specifically prohibited by CAN-SPAM (15 U.S.C. § 7704(b)):
- Using automated scripts to harvest email addresses from websites
- Using "dictionary attacks" (generating email addresses by combining common names with domains)
- Using relay systems to obscure the origin of commercial email

### Safe default for this system
Pattern inference (e.g., inferring `firstname.lastname@domain.com` based on known staff email patterns) is permissible as a manual research technique, but must be used judiciously and documented in the contact's Notes field. If pattern inference results in a hard bounce, update the Notes field to reflect this.

Automated scraping or dictionary attacks are not part of this system and are prohibited.

---

## CAN-SPAM Enforcement Summary

| Requirement | Config location | Enforced by | Failure behavior |
|---|---|---|---|
| Honest sender identity | `compliance.sender_name` | `CANSPAMChecker.validate()` | COMPLIANCE_BLOCK, no send |
| Non-deceptive subject | Sequence YAML | Human review (no auto-check for content) | Operator responsibility |
| Physical mailing address | `compliance.physical_address` | `CANSPAMChecker.validate()` + base template | COMPLIANCE_BLOCK, no send |
| Unsubscribe mechanism | `compliance.unsubscribe_url` + base template | `CANSPAMChecker.validate()` | COMPLIANCE_BLOCK, no send |
| Opt-out honored within 24h | Suppression list + opt-out flag | `get_eligible_contacts()` filter | Contact skipped on next run |
| No harvested/purchased lists | Lead intake process | Human review at intake | Operator responsibility |
| No address harvesting tools | System design | Not implemented in any scripts | Operator responsibility |

---

## What to Do If You Receive a Formal Opt-Out or Complaint

If you receive a formal opt-out request (by email reply, letter, or through any channel):

1. **Immediately** update the contact's `email_opt_out` to `Yes` in the CRM
2. **Immediately** add the email to `config/suppression_list.csv` with `reason=OPT_OUT`
3. Write an `OPT_OUT` audit event with `operator` = the team member who processed it and `notes` = how the request was received
4. Do not send any further emails to this address from any sequence
5. If the request was a formal complaint (e.g., filed with FTC or ISP), notify Zachary Gartrell immediately and document the complaint

---

## Drop-In Reusability Notes

This CAN-SPAM guidelines document is reusable for any outbound email campaign in the United States. CAN-SPAM is a federal law that applies uniformly to all commercial email senders, regardless of industry.

To adapt for a new project:

1. **Company and show name:** Update the header block. The compliance requirements themselves do not change.
2. **Config field names:** Verify that `compliance.sender_name`, `compliance.physical_address`, and `compliance.unsubscribe_url` match the new project's `settings.yaml` schema. If the schema differs, update the references in the Enforcement Summary table.
3. **Physical address:** Replace with the new company's valid US mailing address in `settings.yaml`.
4. **Unsubscribe URL:** Replace with the new project's functional unsubscribe endpoint.
5. **Opt-out timing:** The 24-hour safe default is stricter than required and can be kept as-is for any project. Do not loosen it toward the 10-business-day legal maximum — 24 hours is the right standard.
6. **International considerations:** CAN-SPAM applies to US senders and recipients. If the new project targets venues in Canada, CASL (Canada's Anti-Spam Legislation) applies and has stricter requirements, including explicit or implied consent before sending. If targeting EU venues, GDPR and the ePrivacy Directive apply. Update this document accordingly if the geographic scope changes.
7. **Legal review:** Any new project sending to a significantly larger audience, a new geographic market, or using a new type of recipient list should have its compliance approach reviewed by a licensed attorney before the first send.
