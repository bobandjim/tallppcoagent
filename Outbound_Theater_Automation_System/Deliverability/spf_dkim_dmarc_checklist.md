# SPF, DKIM, and DMARC Setup Checklist
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Overview

SPF, DKIM, and DMARC are the three DNS-based email authentication standards that tell receiving mail servers whether an email from your domain is legitimate. Without them:

- Emails are far more likely to land in spam
- Receiving servers may reject your email outright
- Your domain is vulnerable to being spoofed by bad actors (which further damages your reputation)

All three records must be set up before the first campaign email is sent. This is not optional. Setup takes 30–60 minutes and requires access to your domain's DNS management panel (wherever your domain is registered or wherever DNS is hosted — e.g., Namecheap, GoDaddy, Cloudflare, AWS Route 53).

This checklist is designed to be followed in order. Complete each section fully before moving to the next.

---

## Prerequisites

Before starting, confirm you have:

- [ ] Access to your domain registrar or DNS host's control panel (admin credentials)
- [ ] Access to your Zoho Mail admin panel (`https://mailadmin.zoho.com`)
- [ ] The exact domain name you will send from (e.g., `yourdomainhere.com`)
- [ ] Time for DNS propagation: records can take 24–48 hours to propagate globally (many propagate within 1 hour, but plan for 24–48 hours before verifying)

---

## Part 1: SPF Record

### What SPF Does
SPF (Sender Policy Framework) tells receiving mail servers which mail servers are authorized to send email on behalf of your domain. When a server receives an email claiming to be from `yourdomainhere.com`, it checks the SPF record to verify the sending server is on the authorized list.

### SPF Record for Zoho Mail

Add the following TXT record to your domain's DNS:

| DNS Field | Value |
|---|---|
| **Record type** | `TXT` |
| **Host / Name** | `@` (represents the root domain, e.g., `yourdomainhere.com`) |
| **Value / Content** | `v=spf1 include:zoho.com ~all` |
| **TTL** | `3600` (1 hour) or your DNS host's default |

**Explanation of the record:**
- `v=spf1` — declares this is an SPF record
- `include:zoho.com` — authorizes Zoho's mail servers to send on your behalf
- `~all` — softfail: email from unlisted servers will be flagged but not rejected (recommended starting point; move to `-all` after confirming no legitimate senders are excluded)

**Important:** A domain can only have ONE SPF record. If you already have an SPF record (e.g., `v=spf1 include:google.com ~all`), do not add a second SPF record — merge them into one:
```
v=spf1 include:google.com include:zoho.com ~all
```

### SPF Setup Steps

- [ ] Log in to your DNS management panel
- [ ] Locate the DNS records section for your sending domain
- [ ] Check whether an SPF TXT record already exists (search for `v=spf1`)
- [ ] If no SPF record exists: add a new TXT record with the value above
- [ ] If an SPF record already exists: edit it to add `include:zoho.com` before the `~all` or `-all` at the end
- [ ] Save the record
- [ ] Note the time you saved it (for propagation tracking)

---

## Part 2: DKIM Record

### What DKIM Does
DKIM (DomainKeys Identified Mail) adds a cryptographic signature to every outgoing email. The signature is generated using a private key held by Zoho's mail servers and verified by receiving servers using a public key published in your DNS. This proves that the email was not altered in transit and that it genuinely originated from an authorized sender.

### Step 2.1: Generate the DKIM Key in Zoho Mail Admin

- [ ] Log in to Zoho Mail Admin at `https://mailadmin.zoho.com`
- [ ] Navigate to: **Email Configuration** → **Email Authentication** → **DKIM**
- [ ] Click **Add New Domain** (if your domain is not already listed)
- [ ] Enter your sending domain (e.g., `yourdomainhere.com`)
- [ ] Click **Generate** to create a DKIM key pair
- [ ] Zoho will display the DKIM TXT record values — copy them exactly

Zoho will provide values similar to:

| DNS Field | Value |
|---|---|
| **Record type** | `TXT` |
| **Host / Name** | `zoho._domainkey` (or a Zoho-specified selector) |
| **Value / Content** | `v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GN...` (long key string) |
| **TTL** | `3600` |

**Copy the exact values from your Zoho Mail admin panel** — do not use the example above, as DKIM keys are unique to your domain.

### Step 2.2: Add the DKIM Record to DNS

- [ ] Return to your DNS management panel
- [ ] Add a new TXT record using the exact host name and value Zoho provided
- [ ] Double-check that the host name is exactly as Zoho specified (common error: adding an extra dot or your domain name twice)
- [ ] Save the record

### Step 2.3: Verify and Activate DKIM in Zoho

- [ ] Return to Zoho Mail Admin → **Email Authentication** → **DKIM**
- [ ] Wait at least 1 hour after adding the DNS record (or up to 24 hours)
- [ ] Click **Verify** next to your domain in the Zoho DKIM panel
- [ ] Zoho will confirm verification with a green checkmark or "Verified" status
- [ ] Once verified, click **Enable** to activate DKIM signing for outgoing email

---

## Part 3: DMARC Record

### What DMARC Does
DMARC (Domain-based Message Authentication, Reporting, and Conformance) builds on SPF and DKIM. It tells receiving servers what to do when an email fails SPF or DKIM checks, and it provides a reporting mechanism so you can receive data about authentication failures and potential spoofing attempts.

### DMARC Record — Start with p=none

Begin with a policy of `p=none` (monitor only). This means receiving servers will not reject or quarantine emails that fail DMARC — they will only report the failures to you. This gives you time to confirm that all legitimate sending sources are covered by SPF and DKIM before enforcing a stricter policy.

| DNS Field | Value |
|---|---|
| **Record type** | `TXT` |
| **Host / Name** | `_dmarc` |
| **Value / Content** | `v=DMARC1; p=none; rua=mailto:dmarc-reports@yourdomainhere.com` |
| **TTL** | `3600` |

**Explanation:**
- `v=DMARC1` — declares this is a DMARC record
- `p=none` — monitor only; do not reject or quarantine failing email
- `rua=mailto:dmarc-reports@yourdomainhere.com` — send aggregate DMARC reports to this address (must be a real, monitored mailbox; replace with an actual address)

### DMARC Setup Steps

- [ ] Log in to your DNS management panel
- [ ] Add a new TXT record with Host = `_dmarc` and the value above
- [ ] Replace `dmarc-reports@yourdomainhere.com` with a real email address you can access
- [ ] Save the record

### DMARC Policy Progression

Start with `p=none` and progress to stricter policies only after confirming authentication is working correctly for all legitimate email sources:

| Phase | Policy | When to use |
|---|---|---|
| Phase 1 (start here) | `p=none` | Always start here. Monitor reports for 2–4 weeks. |
| Phase 2 | `p=quarantine` | After confirming all legitimate email passes DMARC. Failing email goes to spam. |
| Phase 3 | `p=reject` | After sustained clean DMARC reports. Failing email is rejected entirely. |

**Do not move to `p=reject` until you have received and reviewed DMARC reports and are confident no legitimate sending sources are being caught.**

---

## Part 4: Verification

After setting all three records, wait for DNS propagation (at minimum 1 hour; ideally 24 hours) and then verify each record.

### Verification Tools

#### SPF Verification
- **Tool:** [MXToolbox SPF Checker](https://mxtoolbox.com/spf.aspx)
- **Steps:**
  - [ ] Go to `https://mxtoolbox.com/spf.aspx`
  - [ ] Enter your sending domain (e.g., `yourdomainhere.com`)
  - [ ] Click "SPF Record Lookup"
  - [ ] Confirm the record shows `include:zoho.com` and ends with `~all` or `-all`
  - [ ] Confirm no errors or warnings are shown

#### DKIM Verification
- **Tool:** [MXToolbox DKIM Checker](https://mxtoolbox.com/dkim.aspx)
- **Steps:**
  - [ ] Go to `https://mxtoolbox.com/dkim.aspx`
  - [ ] Enter your domain and the DKIM selector Zoho specified (e.g., `zoho`)
  - [ ] Click "DKIM Lookup"
  - [ ] Confirm the public key record is found and valid
  - [ ] Also verify via Zoho Mail Admin → DKIM → Verify

#### DMARC Verification
- **Tool:** [MXToolbox DMARC Checker](https://mxtoolbox.com/dmarc.aspx)
- **Steps:**
  - [ ] Go to `https://mxtoolbox.com/dmarc.aspx`
  - [ ] Enter your domain
  - [ ] Click "DMARC Lookup"
  - [ ] Confirm the record shows `p=none` and the `rua` address is correct

#### Full Email Authentication Test
- **Tool:** [mail-tester.com](https://www.mail-tester.com)
- **Steps:**
  - [ ] Go to `https://www.mail-tester.com`
  - [ ] Copy the unique test email address provided
  - [ ] Send a real email from your Zoho Mail account to that address
  - [ ] Wait 30 seconds, then click "Check your score"
  - [ ] Target score: 8/10 or higher before beginning your campaign
  - [ ] Review any issues identified and resolve them before sending campaign emails

---

## Recommended Setup Timeline

| Day | Action |
|---|---|
| Day 0 | Add SPF, DKIM (DNS record only), and DMARC records to DNS |
| Day 0 | Begin DNS propagation |
| Day 1 | Verify SPF and DMARC via MXToolbox |
| Day 1 | Verify DKIM in Zoho Mail Admin, enable DKIM signing |
| Day 1 | Run mail-tester.com test |
| Day 1–2 | Resolve any issues found during verification |
| Day 2 | Run mail-tester.com test again, confirm score ≥ 8/10 |
| Day 3+ | Begin domain warming (see `domain_warming_schedule.md`) |

Do not begin sending campaign emails until all three records are verified and mail-tester.com score is 8/10 or higher.

---

## Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| "SPF record not found" | TXT record not saved or not propagated | Wait 1–2 hours and check again; verify record is saved in DNS panel |
| "Multiple SPF records found" | Two separate SPF TXT records exist | Delete one; merge all `include:` statements into a single SPF TXT record |
| "SPF too many lookups" | More than 10 DNS lookups in SPF chain | Simplify SPF record; remove unused `include:` statements |
| "DKIM record not found" | Wrong selector used in MXToolbox query or DNS not propagated | Verify selector in Zoho Mail Admin; wait for propagation |
| "DKIM key mismatch" | Record was saved with line breaks or missing characters | Delete and re-add DKIM DNS record, copy key as a single unbroken string |
| "DMARC record not found" | Host entered as `_dmarc.yourdomainhere.com` instead of `_dmarc` | Edit record host to just `_dmarc` (some DNS hosts append the domain automatically) |
| "DMARC rua address invalid" | Reporting email address is a different domain not authorized | Add a DMARC record to the reporting domain, or use an address on the same domain |
| Emails going to spam after setup | SPF/DKIM correct but domain reputation not yet established | Begin proper warming schedule; do not send high volume immediately |
| mail-tester.com score below 8 | One or more authentication records failing or content issues | Review mail-tester.com recommendations and fix each item listed |

---

## Post-Setup Monitoring

After authentication is confirmed and the campaign is running:

- **Weekly during warming:** Re-run MXToolbox SPF and DKIM checks to confirm records remain intact
- **Monthly ongoing:** Review DMARC aggregate reports (emailed to `rua` address) for any authentication failures
- **If deliverability drops suddenly:** Run full MXToolbox suite immediately — DNS records can sometimes be accidentally deleted or overwritten during other DNS changes

---

## Drop-In Reusability Notes

This checklist is fully reusable for any new sending domain using Zoho Mail as the SMTP provider. To adapt for a new project:

1. **Sending domain:** Replace all instances of `yourdomainhere.com` with the new project's sending domain. Search and replace throughout the document.
2. **DMARC reporting address:** Replace `dmarc-reports@yourdomainhere.com` with the new project's designated DMARC report recipient address.
3. **Other SMTP providers:** If the new project uses a provider other than Zoho Mail (e.g., Gmail Workspace, SendGrid, Mailgun), replace the SPF `include:` value with the provider's specified include:
   - Gmail: `include:_spf.google.com`
   - SendGrid: `include:sendgrid.net`
   - Mailgun: `include:mailgun.org`
   - The DKIM setup steps will differ — follow the new provider's admin panel instructions
4. **SPF policy (`~all` vs `-all`):** `~all` (softfail) is the safe starting point for any new project. Move to `-all` (hardfail) only after confirming all legitimate senders are included.
5. **DMARC progression:** The `p=none` → `p=quarantine` → `p=reject` progression is universally applicable. Do not skip it for any new project, regardless of how confident you are in the SPF/DKIM setup.
6. **Verification tools:** MXToolbox and mail-tester.com are free, publicly available tools that work for any domain. No substitution needed.
