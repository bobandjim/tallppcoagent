# Inbox Placement Testing Protocol

## Purpose
Before any live sends to real venue contacts, verify that outbound emails land in the primary inbox (not spam/junk/promotions) across major email providers.

## Target
≥ 80% of seed addresses receive emails in primary inbox.

## When to Run
- Before first live send (required)
- Before increasing to a new warm-up week volume
- Any time inbox placement is suspected to be degrading
- After any DNS or authentication changes (SPF/DKIM/DMARC)

## 25-Seed Test Protocol

### Seed List Composition (minimum)
| Provider | Count |
|----------|-------|
| Gmail | 5 |
| Outlook / Hotmail | 5 |
| Yahoo | 3 |
| iCloud / Apple Mail | 2 |
| Zoho Mail | 2 |
| Corporate domain (example.com style) | 4 |
| Other / regional providers | 4 |
| **Total** | **25** |

Seed addresses must be real, monitored mailboxes — not disposable or temporary addresses.

### Test Procedure

1. Populate `data/seed_lists/seed_list.csv` with 25 addresses
2. Run sequence builder dry-run to confirm templates render:
   ```bash
   python3 run_sequence.py --dry-run
   ```
3. Create a test CRM file with 25 rows pointing to seed addresses (Step 1 unsent)
4. Run in test mode:
   ```bash
   python3 run_sequence.py --test-mode --seed-file data/seed_lists/seed_list.csv
   ```
5. Wait 5 minutes
6. Check each seed mailbox — record where Step 1 landed:

### Results Template

| Seed address | Provider | Location | Notes |
|-------------|---------|----------|-------|
| seed1@gmail.com | Gmail | Primary / Promotions / Spam | |
| seed2@outlook.com | Outlook | Primary / Junk | |
| ... | | | |

### Pass/Fail

- **Pass:** ≥ 20 of 25 seeds in primary inbox (80%)
- **Fail:** < 20 seeds in primary inbox

### If Failed
1. Do NOT proceed with live sends
2. Check SPF/DKIM/DMARC status (see `spf_dkim_dmarc_checklist.md`)
3. Check if sending domain is blacklisted (MXToolbox Blacklist Check)
4. Review subject line and body for spam-trigger language
5. Run email through [mail-tester.com](https://www.mail-tester.com) for a deliverability score
6. Fix identified issue, wait 24-48 hours, re-run test

---

## Drop-In Reusability Notes
This protocol applies to any outbound cold email system. The 25-seed test size, 80% threshold, and provider distribution are industry-standard defaults. The only project-specific element is the seed list itself (the CSV file and test mode runner). All other steps are universal.
