# Bounce Classification and Handling
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Overview

A bounce occurs when a sent email cannot be delivered to the recipient's mailbox. Not all bounces are equal — some are permanent, some are temporary, and some are not bounces at all (out-of-office auto-replies are often confused with bounces but require entirely different handling).

Mishandling bounces is one of the fastest ways to damage domain reputation. Continuing to send to addresses that hard-bounce signals to mail providers that you are not maintaining your list, which is a spam behavior pattern. Correct bounce classification and immediate suppression of hard-bounced addresses is mandatory.

---

## Bounce Type 1: Hard Bounce

### Definition
A hard bounce is a permanent delivery failure. The email cannot be delivered and will never be deliverable to this address. Retrying a hard-bounced address is always wrong and harms deliverability.

### Causes
- The email address does not exist (invalid username, misspelled address)
- The recipient domain does not exist or has no mail exchanger (MX) record
- The receiving mail server has permanently rejected the sender's domain or IP
- The account has been permanently closed or deleted

### SMTP Response Codes (Hard Bounce Indicators)

| Code | Meaning |
|---|---|
| `550` | Mailbox unavailable / does not exist |
| `551` | User not local / address rejected |
| `552` | Mailbox storage limit exceeded — permanent (rarely hard; see soft bounce for temporary variant) |
| `553` | Mailbox name not allowed |
| `554` | Transaction failed — permanent rejection |
| `5.1.1` | Bad destination mailbox address |
| `5.1.2` | Bad destination mailbox address syntax |
| `5.7.1` | Delivery not authorized / refused |

### System Handling: Hard Bounce

When a hard bounce SMTP response is detected, the system must take the following actions **immediately, before processing any other contacts**:

1. **Add to suppression list** via `SuppressionList.add()`:
   ```python
   suppression.add(
       email=contact.email,
       reason="HARD_BOUNCE",
       suppressed_at=datetime.utcnow().isoformat()
   )
   ```
2. **Write `HARD_BOUNCE` audit event:**
   ```python
   audit.write(
       event_type="HARD_BOUNCE",
       contact_unique_id=contact.unique_id,
       audit_trail_id=contact.audit_trail_id,
       email=contact.email,
       smtp_code=response_code,
       smtp_message=response_message,
       suppressed_at=datetime.utcnow().isoformat()
   )
   ```
3. **Update Gigs_Leads status** to `Closed` in the CRM (no further outreach to this contact from any sequence)
4. **Do not retry** — the address is now on the suppression list and will be skipped on all future runs

### Manual Hard Bounce Handling (If Detected Outside the System)

If you receive a mailer-daemon / delivery failure email in the Zoho inbox that the system did not catch automatically:

1. Open `config/suppression_list.csv`
2. Add a new row: `email@domain.com,HARD_BOUNCE,2026-03-04T14:30:00Z`
3. Run the manual audit event script:
   ```bash
   python3 scripts/write_audit_event.py --event_type HARD_BOUNCE --email email@domain.com --notes "Detected manually from Zoho inbox mailer-daemon"
   ```
4. Update the contact's Gigs_Leads record status to `Closed` in the CRM Excel

---

## Bounce Type 2: Soft Bounce

### Definition
A soft bounce is a temporary delivery failure. The address may be valid, but delivery failed due to a transient condition. Soft bounces can be retried, but only up to a defined limit — if the temporary issue persists across multiple retry attempts, the address should be treated as a hard bounce for list hygiene purposes.

### Causes
- Recipient's mailbox is full (over quota)
- Receiving mail server is temporarily unavailable or overloaded
- Message is too large for the recipient's server
- Receiving server is temporarily blocking the sender (greylisting)
- Auto-responder loop / temporary configuration issue on receiving end

### SMTP Response Codes (Soft Bounce Indicators)

| Code | Meaning |
|---|---|
| `421` | Service temporarily unavailable — try again later |
| `450` | Mailbox unavailable — try again later |
| `451` | Local error in processing — try again later |
| `452` | Insufficient storage — mailbox temporarily full |
| `4.2.1` | Mailbox full |
| `4.3.1` | Mail system storage full |
| `4.7.0` | Delivery temporarily suspended — greylisting |

### Retry Policy

Soft bounces are retried up to 3 times total over a 7-day window:

| Attempt | When | Action if failure |
|---|---|---|
| Attempt 1 | Original send | Log SOFT_BOUNCE; schedule retry |
| Attempt 2 | 2–3 days after Attempt 1 | Log SOFT_BOUNCE; schedule retry |
| Attempt 3 | 5–7 days after Attempt 1 | If fails again: add to suppression, log SOFT_BOUNCE_MAX |

### System Handling: Soft Bounce

On detection of a soft bounce SMTP response:

1. **Write `SOFT_BOUNCE` audit event:**
   ```python
   audit.write(
       event_type="SOFT_BOUNCE",
       contact_unique_id=contact.unique_id,
       audit_trail_id=contact.audit_trail_id,
       email=contact.email,
       smtp_code=response_code,
       smtp_message=response_message,
       attempt_number=current_attempt_number
   )
   ```
2. **Update `retry_after` timestamp** in the contact's CRM record (Custom6) to 2 days from now
3. **Do not increment `step_number`** — the step has not been successfully sent
4. **On next run:** Check if retry is due (current date >= retry_after date) and retry send if attempt count < 3

On the **3rd soft bounce failure**:

1. **Add to suppression list:**
   ```python
   suppression.add(
       email=contact.email,
       reason="SOFT_BOUNCE",
       suppressed_at=datetime.utcnow().isoformat()
   )
   ```
2. **Write `SOFT_BOUNCE_MAX` audit event**
3. **Update Gigs_Leads status** to `Closed` in the CRM

---

## Bounce Type 3: Out-of-Office Auto-Reply

### Definition
An out-of-office (OOO) auto-reply is not a bounce. It is an automated response from the recipient's mail system indicating that the person is temporarily unavailable. The email address is valid, the contact is real, and they may be interested in booking the show — they are simply out of office.

**Critical distinction:** Marking an OOO as an opt-out or adding it to the suppression list is incorrect and could cause you to lose a genuine booking lead.

### OOO Detection Signals

Common patterns in auto-reply subject lines and body text that indicate an out-of-office:

| Signal type | Examples |
|---|---|
| Subject line patterns | "Out of Office:", "Automatic Reply:", "Auto-Reply:", "OOO:", "Away from office" |
| Body text patterns | "I am out of the office", "I will return on", "I am currently away", "will respond upon my return", "will be back on [date]" |
| Sender indicators | Reply comes from same address as sent-to address; no unique human-written content |

### System Handling: Out-of-Office

When an OOO auto-reply is received and classified:

1. **Do NOT add to suppression list**
2. **Do NOT mark email_opt_out = Yes**
3. **Do NOT increment step_number** (the sequence step is still pending for this contact)
4. **Extract the return date** from the OOO message if available (e.g., "I will return on March 15, 2026")
5. **Write a note** to the Contacts sheet Notes field: `OOO auto-reply received YYYY-MM-DD. Return date: YYYY-MM-DD if found.`
6. **Write `OOO_RECEIVED` audit event:**
   ```python
   audit.write(
       event_type="OOO_RECEIVED",
       contact_unique_id=contact.unique_id,
       audit_trail_id=contact.audit_trail_id,
       ooo_received_at=datetime.utcnow().isoformat(),
       return_date=extracted_return_date_or_none
   )
   ```
7. **Set `retry_after` date** (Custom6) in CRM to the return date + 2 business days (to give the contact time to catch up after returning). If no return date is found, use 14 days from OOO received.
8. **Re-queue:** On the next run after the retry_after date, the contact will be picked up and the pending step will be sent

---

## How Bounces Are Detected via Zoho Mail SMTP

### Method 1: SMTP Response Code (Primary)

The primary bounce detection mechanism is the SMTP response code returned by the receiving mail server during the SMTP handshake. This is captured synchronously — the sender knows within seconds whether the message was accepted or rejected.

In Python using `smtplib`:

```python
import smtplib

try:
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        result = smtp.sendmail(from_addr, to_addr, message.as_string())
        # result is empty dict on full success
        # SMTP exceptions are raised for rejections
except smtplib.SMTPRecipientsRefused as e:
    # e.recipients is a dict of {email: (code, message)}
    code, message = list(e.recipients.values())[0]
    classify_bounce(code, message, contact)
except smtplib.SMTPConnectError:
    # Connection failure — not a bounce, log SMTP_FAILURE
    pass
```

### Method 2: Mailer-Daemon Inbox Monitoring (Secondary)

Some bounces, particularly those from receiving servers that accept the message initially and then fail delivery (delayed bounces), arrive as bounce-back emails to the sending inbox from `mailer-daemon@...` or `postmaster@...`.

Monitor the Zoho Mail inbox regularly for these messages. They should be processed manually using the manual hard bounce handling procedure documented above.

**Recommended frequency:** Check inbox for mailer-daemon messages every day during active sending. These messages typically arrive within 1–72 hours of the failed send.

---

## Bounce Audit Event Reference

All bounce events are written to `audit_log.db`. Full event schema:

| Field | `HARD_BOUNCE` | `SOFT_BOUNCE` | `SOFT_BOUNCE_MAX` | `OOO_RECEIVED` |
|---|---|---|---|---|
| `event_type` | `HARD_BOUNCE` | `SOFT_BOUNCE` | `SOFT_BOUNCE_MAX` | `OOO_RECEIVED` |
| `timestamp` | UTC ISO 8601 | UTC ISO 8601 | UTC ISO 8601 | UTC ISO 8601 |
| `contact_unique_id` | CON-XXXXXX | CON-XXXXXX | CON-XXXXXX | CON-XXXXXX |
| `audit_trail_id` | UUID4 | UUID4 | UUID4 | UUID4 |
| `email` | address | address | address | address |
| `smtp_code` | 5xx code | 4xx code | 4xx code | N/A |
| `smtp_message` | response text | response text | response text | N/A |
| `attempt_number` | N/A | 1, 2, or 3 | 3 | N/A |
| `suppressed` | `true` | `false` | `true` | `false` |
| `ooo_return_date` | N/A | N/A | N/A | date or null |

---

## Bounce Handling Quick Reference

| Bounce type | Retry? | Add to suppression? | Reason code | CRM status update |
|---|---|---|---|---|
| Hard bounce (5xx) | Never | Immediately | `HARD_BOUNCE` | Gigs_Leads → Closed |
| Soft bounce (1st) | Yes — after 2 days | No | `SOFT_BOUNCE` | No change |
| Soft bounce (2nd) | Yes — after 2 more days | No | `SOFT_BOUNCE` | No change |
| Soft bounce (3rd) | Never | Yes | `SOFT_BOUNCE` | Gigs_Leads → Closed |
| Out-of-office | Yes — after return date | Never | N/A (OOO event) | Note added, retry_after set |

---

## Drop-In Reusability Notes

This bounce classification document applies without modification to any outbound email campaign using Python's `smtplib` and SMTP. SMTP response codes are a global standard — the 4xx/5xx classification and the specific codes documented here are not Zoho-specific.

To reuse for a new project:

1. **Show and company name:** Update header only. All bounce logic, SMTP codes, and audit event schemas are generic.
2. **CRM field mapping:** This document references `Custom6` for `retry_after` date. Verify that the new project's CRM schema uses the same custom field index, or update the reference.
3. **Retry policy (3 attempts over 7 days):** This is a reasonable default for B2B outreach. More aggressive retry policies (e.g., 5 attempts) may be appropriate for B2C campaigns where mailbox-full bounces are more common. Adjust `max_soft_bounce_retries` and `soft_bounce_retry_delay_days` in `settings.yaml`.
4. **OOO detection patterns:** The keyword lists in the OOO Detection Signals section are based on common English-language auto-reply patterns. For international campaigns, add localized patterns (e.g., "je suis absent" for French, "Ich bin abwesend" for German).
5. **Manual monitoring:** The mailer-daemon inbox monitoring requirement applies to any SMTP-based sending setup. The frequency (daily) and the manual process are the same regardless of the project.
6. **Audit event schema:** The event schema table at the end of this document assumes the `audit_log.db` SQLite schema from this project. If the new project uses a different audit log structure, update the field names but preserve the distinction between the four event types (`HARD_BOUNCE`, `SOFT_BOUNCE`, `SOFT_BOUNCE_MAX`, `OOO_RECEIVED`).
