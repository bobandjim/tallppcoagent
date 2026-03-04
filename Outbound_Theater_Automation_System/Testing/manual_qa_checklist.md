# Manual QA Checklist — Pre-Send

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**Email Platform:** Zoho Mail SMTP
**Last Updated:** 2026-03-04

---

## Overview

This checklist must be completed before any batch of outreach emails is sent. It covers both content quality (does the email look correct?) and compliance/data integrity (is this contact eligible to receive email?). All items must pass. Any failed item blocks the send and requires a fix and re-check.

The checklist applies to:
- Initial sequence sends (Step 1 emails to new leads)
- Follow-up sequence sends (Steps 2, 3, etc. to ongoing leads)
- Manual one-off emails sent outside of the sequence (these also require all applicable checks)

Complete this checklist once per batch. If a batch covers multiple sequence steps or contact segments, complete a separate checklist instance for each distinct template/step combination being sent.

---

## Section A: Content and Rendering Checks

These checks verify that the email itself is correct and will display properly to recipients.

---

- [ ] **All personalization tokens render correctly (no `{{ }}` artifacts)**

  Open the draft email or the test send (see Section D). Scan every line for any unrendered merge tags. Common tokens to check:
  - `{{first_name}}` → should show the contact's actual first name
  - `{{venue_name}}` → should show the venue's name as entered in the CRM
  - `{{city}}` → should show the venue's city
  - `{{programming_focus}}` → should show the venue's programming description if used

  If any `{{ }}` placeholder remains visible, the template variable is either misspelled, mapped to a blank field, or the contact record is missing the required data. Fix the template or populate the missing CRM field before sending. Never send an email with a visible unrendered token.

---

- [ ] **Unsubscribe URL is valid and functional**

  Click the unsubscribe link in the test email. Verify:
  - The link opens a working page (no 404, no redirect loop)
  - The page confirms the unsubscribe action or provides a way to confirm it
  - The link is specific to the sending domain and complies with CAN-SPAM one-click unsubscribe requirements

  If using a manually managed unsubscribe page, confirm the page is live and the form submission writes to the suppression list.

---

- [ ] **Physical address is present in all email footers**

  CAN-SPAM requires a valid physical mailing address in every commercial email. Verify the footer of the email includes:
  - Tall People Performing Company's current mailing address (street or P.O. Box, city, state, ZIP)
  - The address must be a real, deliverable address — not a placeholder

  If the address is missing or shows a placeholder, update the email template footer before sending.

---

- [ ] **Sender name matches Zoho Mail account sender identity**

  Check the "From" display name in the draft or test send. It should read exactly as configured in the Zoho Mail sender identity settings (e.g., "Princess Peigh Adventures" or "Tall People Performing Company"). Mismatches between the From name and the account's configured identity can trigger spam filters or damage sender reputation.

  Verify in Zoho Mail: Settings → Email → From Name / Sender Identity.

---

- [ ] **Subject line contains no spam-trigger phrases**

  Review the subject line manually before sending. Avoid or remove:
  - ALL CAPS words or phrases
  - Excessive exclamation marks (`!!`, `!!!`)
  - Currency symbols (`$`, `€`) used in a promotional context
  - Words commonly flagged: "FREE", "Guaranteed", "Act Now", "Limited Time", "Winner", "Urgent", "No cost", "Click here"
  - Misleading subject lines that misrepresent the email's content

  A subject line for this campaign should be professional, specific to the booking conversation, and clearly identify the purpose (e.g., "Booking inquiry: Princess Peigh's Sword Fighting Tea Party — [Venue Name]").

---

## Section B: Contact Eligibility Checks

These checks verify that the contacts in the batch are eligible to receive email under CRM rules and CAN-SPAM requirements.

---

- [ ] **Contact email is not on suppression list**

  Before running the batch, cross-reference all contact emails in the batch against `suppression_list.csv`. Any email address that appears in the suppression list must be removed from the batch, regardless of what the Contacts sheet says.

  Method: Export the batch contact list to a temporary CSV. Use a VLOOKUP or filter in Excel to flag any emails matching entries in `suppression_list.csv`. Remove flagged rows from the batch.

---

- [ ] **Contact `email_opt_out` flag is `No`**

  For every contact in the batch, verify the `email_opt_out` field in the Contacts sheet is `No`. Any contact with `email_opt_out = Yes` must be removed from the batch.

  Method: Add a filter to the Contacts sheet on `email_opt_out = Yes` before generating the batch. Confirm zero matching rows are included in the send list.

---

- [ ] **Step number matches correct template file**

  Each contact in the batch should be receiving the template that corresponds to their current `step_number`. Verify:
  - All contacts with `step_number = 0` are receiving Template Step 1
  - All contacts with `step_number = 1` are receiving Template Step 2
  - And so on

  Do not mix steps in a single batch unless the send system explicitly handles step routing. When in doubt, run a single-step batch (all contacts at the same step).

---

- [ ] **`sequence_id` is set on ContactRecord**

  All contacts in the batch must have a non-blank `sequence_id` field (Custom1 on the Contacts sheet). A blank `sequence_id` means the contact has not been formally enrolled in a sequence and should not receive a sequence email.

  Method: Filter the batch list to confirm `sequence_id` is populated for all rows. Remove any rows with blank `sequence_id` and manually assign a sequence before re-adding them to a future batch.

---

## Section C: Audit and Tracking Checks

These checks verify that the infrastructure for tracking and logging is in place before the send.

---

- [ ] **Audit trail ID is set before send**

  Every contact in the batch must have a non-blank `audit_trail_id` (Custom8 on the Contacts sheet). The audit trail ID must have been generated at row creation and must not be blank.

  If a contact row has a blank `audit_trail_id`, generate a new UUID4 and populate it before proceeding. Then write an `AUDIT_ID_ASSIGNED` event to the audit log noting the correction.

---

- [ ] **Daily send count is below configured maximum**

  Check the current day's send log. Verify that the number of emails already sent today plus the size of the current batch does not exceed the configured daily send limit.

  The daily send limit is configured to stay within Zoho Mail's outbound SMTP rate limits and to maintain a sending pattern that does not trigger spam classification. The limit is documented in `campaign_config.md` (or the equivalent configuration file for this campaign). If the combined count would exceed the limit, split the batch and schedule the remainder for the next day.

  Log the send count in the audit log under the `DAILY_SEND_COUNT` event type.

---

## Section D: Test Send Verification

This check is the final gate before the live batch send.

---

- [ ] **Test send to seed address completed before live run**

  Before sending the batch to real contacts, send a test version of each template in the batch to a designated internal seed email address. The seed address must be a real, working inbox that team members can review.

  Verify in the seed inbox:
  1. The email arrives (not in spam)
  2. All personalization tokens are rendered correctly with the test contact's data
  3. The subject line displays correctly in the inbox preview
  4. The From name and From address are correct
  5. The footer is present with the physical address and unsubscribe link
  6. The unsubscribe link is clickable and functional
  7. No images are broken (if images are used)
  8. The email renders acceptably on mobile (check in a mobile client or use a preview tool)

  If the test send goes to spam in the seed inbox, do not proceed with the live batch. Investigate deliverability (SPF, DKIM, DMARC records on the sending domain) before sending to real contacts.

---

## Sign-Off

Complete this section after all checklist items are verified:

| Item                      | Value |
|---------------------------|-------|
| Batch date                | `YYYY-MM-DD` |
| Sequence step being sent  | `Step X` |
| Number of contacts in batch | `#` |
| Seed address used         | `seed@example.com` |
| Checked by                | `[Name]` |
| Time of check             | `HH:MM` |
| All checks passed?        | `Yes / No` |
| Notes on any failed checks| _(describe any issues and how they were resolved)_ |

Do not send the batch until "All checks passed?" is `Yes`.

---

## Drop-In Reusability Notes

This pre-send QA checklist can be reused for any outbound email campaign using a Zoho Mail SMTP sending setup and an Excel/CSV CRM. To adapt it for a new campaign:

1. **Update the personalization token list** in the first check item to reflect the tokens used in the new campaign's templates. Add any new tokens the new show's email templates introduce (e.g., `{{show_name}}`, `{{fee_range}}`, `{{available_dates}}`).
2. **Update the sender name** in the "Sender name" check to reflect the new campaign's configured Zoho sender identity.
3. **The unsubscribe, physical address, and spam-trigger checks** are CAN-SPAM compliance items and should remain unchanged in any adaptation. The physical address will need to be updated if the company's mailing address changes.
4. **The daily send limit check** requires updating the reference to `campaign_config.md` or whatever configuration document stores the daily send cap for the new campaign. The cap itself may differ based on the Zoho plan and the sending volume of the new campaign.
5. **The seed address** referenced in Section D should be updated to the new campaign's designated internal test inbox. Document the seed address in the campaign config so it is consistent across all checklist uses.
6. **The Sign-Off table** is universal and requires no changes. Consider storing completed sign-off records in a dedicated `send_log` tab in the CRM workbook for traceability.
