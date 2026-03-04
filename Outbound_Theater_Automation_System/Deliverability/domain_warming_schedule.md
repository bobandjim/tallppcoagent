# Domain Warming Schedule
**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**Brand:** Princess Peigh Adventures
**Document version:** 1.0
**Last updated:** 2026-03-04

---

## Overview

Email deliverability is earned, not assumed. When a sending domain or IP address is new — or when it has been dormant — receiving mail servers have no data to determine whether the sender is trustworthy. Sudden high-volume sending from an unknown domain is one of the most reliable signals of spam behavior.

Domain warming is the process of gradually increasing send volume over several weeks, giving receiving mail servers time to observe consistent, positive sending behavior (good open rates, low bounces, no spam complaints) before the domain sends at full campaign volume.

Skipping or rushing the warming process can result in:
- Emails landing in spam or promotions folders
- Temporary blocks from major ISPs (Gmail, Outlook, Yahoo)
- Permanent domain reputation damage that is difficult to recover
- Loss of deliverability for the entire campaign

This document defines the warming schedule for Tall People Performing Company's Zoho Mail sending domain.

---

## Warming Schedule

### Week 1 — Establish Baseline Trust
**Maximum sends per day:** 10
**Send method:** Manual (do not use automated sequence runner this week)
**Recipient selection:** Highest-quality recipients only — venues where you have a warm relationship, professional contacts who are likely to engage, or seed accounts you control

**Guidance:**
- Send 5–10 emails per day, personally composed or using the system with dry-run review before actual send
- Prioritize contacts who are likely to open — known contacts, people you have spoken with, well-known venues with active programming
- Do not send to all new cold contacts this week
- Monitor the Zoho Mail sent folder to confirm delivery to inbox (not spam) using seed accounts

**Config:** Set `sequence.max_sends_per_day: 10` and `warming.current_week: 1` in `config/settings.yaml`

---

### Week 2 — Build Volume Gradually
**Maximum sends per day:** 25
**Send method:** Automated sequence runner may be used

**Guidance:**
- Automated runs can begin, but continue to spot-check daily for deliverability
- Check open rates in Zoho Mail analytics if available; open rate should stay above 20%
- Check bounce rate; if bounce rate exceeds 2%, pause and investigate before continuing
- Do not skip directly to Week 3 volume even if Week 1 went well

**Config:** Set `sequence.max_sends_per_day: 25` and `warming.current_week: 2` in `config/settings.yaml`

---

### Week 3 — Accelerate with Monitoring
**Maximum sends per day:** 50
**Send method:** Automated sequence runner

**Guidance:**
- Continue daily log review
- By Week 3, you should have observable open rate data — if open rates have dropped below 20%, do not proceed to Week 4. Investigate first.
- Check for any spam complaints received (Zoho Mail admin → Spam Reports if available)
- Verify that Step 1 emails are still landing in inbox using seed accounts

**Config:** Set `sequence.max_sends_per_day: 50` and `warming.current_week: 3` in `config/settings.yaml`

---

### Week 4 and Beyond — Full Campaign Volume
**Maximum sends per day:** 100
**Send method:** Automated sequence runner

**Guidance:**
- At 100 sends/day, the full outbound campaign can run at normal pace
- Continue weekly health checks (see Monitoring section below)
- Do not increase beyond 100 sends/day without reassessing deliverability metrics and adjusting the warming schedule

**Config:** Set `sequence.max_sends_per_day: 100` and `warming.current_week: 4` in `config/settings.yaml`

---

## Warming Rules — Non-Negotiable

These rules apply throughout the entire warming process:

1. **Never skip a week.** Moving from Week 1 directly to Week 3 volume will trigger spam filters. The gradual ramp is the point — each step gives mail servers time to record positive sending behavior before the next volume increase.

2. **Never send a burst.** Sending 0 emails on Monday and 50 on Tuesday reads as suspicious behavior. Consistent daily sends are better than irregular bursts. If you miss a day, do not double-up the next day.

3. **Never ignore declining metrics.** If open rates, reply rates, or bounce rates move in the wrong direction, pause the run and investigate. Do not assume the metrics will self-correct.

4. **Warm-up applies to new domains only.** If the sending domain has sent high-quality email for over a year with good metrics, a full warm-up may not be needed. However, if the domain has been dormant for 3+ months, treat it as a new domain and warm from the beginning.

5. **Do not warm multiple sequences simultaneously.** During the warming period, only run the `theater_outreach_v1` sequence. Adding additional campaigns during warm-up splits the signal and makes it harder to diagnose issues.

---

## Health Metrics to Monitor

Monitor these metrics throughout the warming schedule and on an ongoing basis:

| Metric | Target | Danger threshold | Action if threshold breached |
|---|---|---|---|
| Open rate | > 20% | < 15% | Pause sends, review subject lines and recipient quality |
| Reply rate | > 1% | < 0.5% | Review email content relevance and personalization |
| Bounce rate | < 2% | > 3% | Pause sends, clean CRM data, check suppression list |
| Spam complaint rate | < 0.1% | > 0.3% | Immediately pause, investigate, do not resume until cause identified |
| Unsubscribe rate | < 0.5% | > 1% | Review email content and frequency |

---

## Monitoring Approach

### 1. Audit Log Review (Daily)

After each automated run, query the audit log for key metrics:

```sql
-- Count today's sends
SELECT COUNT(*) FROM events WHERE event_type = 'EMAIL_SENT' AND date(timestamp) = date('now');

-- Check for bounces today
SELECT * FROM events WHERE event_type IN ('HARD_BOUNCE', 'SOFT_BOUNCE') AND date(timestamp) = date('now');

-- Check for throttle hits
SELECT * FROM events WHERE event_type = 'THROTTLE_HIT' AND date(timestamp) = date('now');
```

### 2. Zoho Mail Dashboard

Log in to Zoho Mail at `https://mail.zoho.com` and check:
- Sent Items count for the day (should match audit log EMAIL_SENT count)
- Zoho Mail admin panel → Mail Analytics (if available on your plan)
- Check for any bounce-back emails received in the inbox (mailer-daemon replies, delivery failure notices)

### 3. Seed List Tests

Maintain a seed list of 3–5 email addresses across different mail providers (e.g., one Gmail account, one Outlook account, one Yahoo account). Send a test email to the seed list before increasing to a new week's volume. Confirm:
- Email arrives in inbox (not spam/junk/promotions)
- Subject line and sender name display correctly
- Unsubscribe link is functional
- Email renders correctly in each client

Seed accounts must use real email providers — do not use temporary/disposable addresses for seed testing.

### 4. MXToolbox Checks

Run deliverability checks at [MXToolbox](https://mxtoolbox.com) after DNS setup and whenever deliverability concerns arise:
- SPF lookup: `mxtoolbox.com/SuperTool.aspx` → select "SPF Record Lookup"
- Blacklist check: `mxtoolbox.com/blacklists.aspx` → enter your sending domain

---

## How to Update Warming Config

When advancing to the next warming week, update `config/settings.yaml`:

```yaml
sequence:
  max_sends_per_day: 25        # change this to the new week's maximum

warming:
  current_week: 2              # increment this by 1 each week
  warming_started: "2026-03-10"  # date you began warming (do not change after first entry)
```

**Steps to advance to the next week:**

1. Review all health metrics for the current week (open rate, bounce rate, complaint rate)
2. Confirm all metrics are within target thresholds
3. Open `config/settings.yaml` in a text editor
4. Update `sequence.max_sends_per_day` to the new week's value
5. Update `warming.current_week` to the new week number
6. Save the file
7. Run `python3 scripts/run_sequence.py --config config/settings.yaml --dry-run` to confirm config loads correctly
8. Begin sending at the new volume on the next scheduled run

**Do not advance weeks mid-day.** Only change the config at the start of a new day.

---

## Warming Schedule Quick Reference

| Week | Max sends/day | Config value | Method |
|---|---|---|---|
| Week 1 | 10 | `max_sends_per_day: 10` | Manual or very light automation |
| Week 2 | 25 | `max_sends_per_day: 25` | Automated, monitor daily |
| Week 3 | 50 | `max_sends_per_day: 50` | Automated, monitor daily |
| Week 4+ | 100 | `max_sends_per_day: 100` | Automated, monitor weekly |

---

## What to Do If Deliverability Degrades

If open rates drop, bounce rates spike, or you see evidence of emails going to spam (seed accounts show spam delivery), take the following steps in order:

1. **Stop the automated run immediately.** Set `max_sends_per_day: 0` in the config to block all sends. This is not a panic measure — it is the correct first response.
2. **Do not increase volume.** Sending more email while deliverability is degraded accelerates reputation damage.
3. **Run a seed account test** to determine whether the issue is deliverability (spam folder) or engagement (inbox but unopened).
4. **Check the bounce rate** in the audit log. A spike in hard bounces suggests bad CRM data — clean the contact list.
5. **Check SPF, DKIM, and DMARC records** using MXToolbox. An authentication lapse can cause sudden deliverability drops.
6. **Check if the domain is blacklisted** using MXToolbox Blacklist Check.
7. **Review subject lines and content** for spam trigger words. Run a test email through [mail-tester.com](https://www.mail-tester.com) to get a deliverability score.
8. **Wait 48–72 hours** after fixing the identified issue before resuming sends. Mail server reputation updates are not instantaneous.
9. **Resume at a lower volume** than where you paused. If you were at Week 3 (50/day) when the issue occurred, resume at Week 2 (25/day) and re-warm.
10. **Document the incident** in the audit log using a `DELIVERABILITY_INCIDENT` manual event with a description of what happened and what was changed.

---

## Drop-In Reusability Notes

This warming schedule document applies to any new Zoho Mail sending domain used for outbound cold email campaigns. To reuse it for a different project:

1. **Company and show name:** Update the header block. The warming schedule itself (volumes, weeks, thresholds) is not show-specific.
2. **Volume targets:** The Week 1–4 volume targets (10 / 25 / 50 / 100) are conservative defaults appropriate for cold outreach to professional contacts. For warmer audiences (e.g., venue contacts you already know), you may be able to ramp more aggressively — but err on the side of caution.
3. **Config field names:** `sequence.max_sends_per_day` and `warming.current_week` are project-specific YAML paths. Verify these match the new project's `settings.yaml` schema.
4. **Health metric thresholds:** The open rate (>20%), bounce rate (<2%), and complaint rate (<0.1%) targets are industry-standard benchmarks for B2B outbound email. They apply across industries.
5. **Monitoring approach:** The audit log queries, Zoho dashboard, and seed list approach are fully reusable. Update the audit log query syntax if the new project uses a different database (e.g., PostgreSQL instead of SQLite).
6. **Degradation response protocol:** The 10-step degradation protocol is fully reusable and does not require any modification for a new project.
