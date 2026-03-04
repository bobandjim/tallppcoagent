# Deliverability Module — Drop-In Reusability Notes

## Overview

This module governs everything that must be true before an email is sent and everything that controls the sending cadence. It is the primary defense against inbox placement failure, deliverability reputation damage, and compliance violations.

**Files in this module:**
- `domain_warming_schedule.md` — progressive ramp-up schedule for new sending domains
- `spf_dkim_dmarc_checklist.md` — step-by-step DNS verification for Zoho Mail
- `throttling_rules.md` — rate limits, delays, and when to slow down
- `bounce_classification.md` — hard vs soft bounce handling

**Code files this module documents:**
- `src/email/deliverability.py` — `DeliverabilityGuard` class (throttle + suppression + compliance + template gate)
- `src/email/zoho_sender.py` — SMTP sender with STARTTLS
- `config/settings.yaml` (deliverability section) — max_sends_per_day, delay_between_sends_seconds, warm_up_schedule

---

## Drop-In Reusability: Adapting for a New Project

### Step 1 — Update the Warm-Up Schedule in `config/settings.yaml`

The warm-up schedule is project-specific and tied to the sending domain's age and reputation:

```yaml
deliverability:
  max_sends_per_day: 50         # Set to current week's cap
  delay_between_sends_seconds: 90
  warm_up_schedule:
    week_1: 10
    week_2: 25
    week_3: 50
    week_4: 100
  current_week: 1               # Update weekly
```

For a **brand new domain** (never sent before): start at week_1 = 10 and advance each week.
For a **domain with sending history**: you may start at a higher tier, but verify inbox placement first.

### Step 2 — Configure the New Sending Domain

For each new project you will have a new domain or subdomain. Complete the DNS checklist in `spf_dkim_dmarc_checklist.md` for the new domain before any sends.

Key records to set:
- **SPF**: `v=spf1 include:zoho.com ~all` (or your mail provider's SPF record)
- **DKIM**: Add the DKIM public key provided by your mail platform (Zoho → Settings → Email Authentication)
- **DMARC**: `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`

Verify all three are active at `mxtoolbox.com` or `mail-tester.com` before first live send.

### Step 3 — Update the Seed List for a New Inbox Placement Test

The seed list at `data/seed_lists/seed_list.csv` contains 25 test inboxes across providers (Gmail, Outlook, Yahoo, Apple Mail) to verify inbox placement before live sends.

For a new project:
1. Replace or supplement seed list entries with inboxes you can check manually
2. Run: `python3 run_sequence.py --test-mode --seed-file data/seed_lists/seed_list.csv`
3. Check each inbox for: inbox placement (not spam), rendering quality, unsubscribe link functionality
4. Target: >80% inbox placement before proceeding to live sends

### Step 4 — Adjust Throttle for a Different Email Platform

This system defaults to **Zoho Mail SMTP**. If adapting to a different platform:

| Platform | SMTP Host | Port | Auth |
|----------|-----------|------|------|
| Zoho Mail | smtp.zoho.com | 587 | STARTTLS |
| Gmail (Workspace) | smtp.gmail.com | 587 | STARTTLS + App Password |
| SendGrid | smtp.sendgrid.net | 587 | STARTTLS + API Key as password |
| Mailgun | smtp.mailgun.org | 587 | STARTTLS + API credentials |

Update `src/email/zoho_sender.py` → `SMTP_HOST`, `SMTP_PORT`, and auth logic for the new platform.
The throttle settings in `config/settings.yaml` remain the same regardless of platform.

### Step 5 — Verify DNS Records for Any New Domain

Before first live send on any new project, run this checklist:
- [ ] SPF record published and resolving
- [ ] DKIM key published and signing verified
- [ ] DMARC policy published (p=none for monitoring, p=quarantine for enforcement)
- [ ] Reverse DNS (PTR) configured for sending IP (if using dedicated IP)
- [ ] Domain not on any blocklists (check mxtoolbox.com/blacklists)
- [ ] Seed inbox test run: >80% inbox placement confirmed

---

## Key Invariants — Never Change These

These rules apply to every project that reuses this module. They are not configurable.

1. **Always warm up a new domain gradually.** Never jump to full volume on day 1. A new domain sending 100+ emails immediately will be flagged as spam.

2. **Always verify SPF/DKIM/DMARC before the first live send.** Missing these records means emails may be rejected or quarantined by major mail providers.

3. **Never exceed the daily cap for the current warm-up week.** The cap in `settings.yaml → deliverability.max_sends_per_day` must match the current week's limit from `warm_up_schedule`. Update `current_week` each week.

4. **Hard bounces are suppressed immediately, no exceptions.** A hard bounce means the address is invalid or the domain is rejecting mail. Any retry to a hard bounce damages sender reputation. This is enforced automatically in `deliverability.py`.

5. **Seed inbox test before every new list or sequence.** When starting with a new venue list or new email sequence, always run `--test-mode` first to confirm inbox placement.

6. **The `template_approved` gate must never be bypassed.** No live sends until a human has reviewed rendered templates and set `template_approved: true` in settings. This is enforced at the CLI level in `run_sequence.py` and at the guard level in `deliverability.py`.

---

## Troubleshooting Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Emails landing in spam | SPF/DKIM not configured | Complete DNS checklist |
| High bounce rate | List quality issues | Verify email addresses before import |
| Daily limit hit immediately | `current_week` not updated | Advance `current_week` in settings.yaml |
| Soft bounce loop | Sending to invalid domain | Suppress after 3 soft bounces (automatic) |
| SMTP auth failure | Wrong env vars | Verify ZOHO_EMAIL and ZOHO_PASSWORD in .env |
| Template approval blocked | Gate active | Run `--review-mode`, then set `template_approved: true` |
