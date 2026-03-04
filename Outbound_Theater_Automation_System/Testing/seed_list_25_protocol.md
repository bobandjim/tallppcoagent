# Seed List — 25-Seed Protocol

## What Is a Seed List
A set of monitored email addresses spread across different mail providers, used to check inbox placement before live sends. No real venue contacts are in the seed list.

## Setting Up the Seed List

File: `data/seed_lists/seed_list.csv`

```csv
email,provider,label
your.test1@gmail.com,Gmail,seed_gmail_1
your.test2@gmail.com,Gmail,seed_gmail_2
your.test3@gmail.com,Gmail,seed_gmail_3
your.test4@gmail.com,Gmail,seed_gmail_4
your.test5@gmail.com,Gmail,seed_gmail_5
test1@outlook.com,Outlook,seed_outlook_1
test2@outlook.com,Outlook,seed_outlook_2
test3@hotmail.com,Outlook,seed_hotmail_1
test4@hotmail.com,Outlook,seed_hotmail_2
test5@live.com,Outlook,seed_live_1
test1@yahoo.com,Yahoo,seed_yahoo_1
test2@yahoo.com,Yahoo,seed_yahoo_2
test3@yahoo.com,Yahoo,seed_yahoo_3
test1@icloud.com,iCloud,seed_icloud_1
test2@me.com,iCloud,seed_icloud_2
test1@zoho.com,Zoho,seed_zoho_1
test2@zohomail.com,Zoho,seed_zoho_2
test1@yourdomain.com,Corporate,seed_corp_1
test2@yourdomain.com,Corporate,seed_corp_2
test3@anotherdomain.com,Corporate,seed_corp_3
test4@anotherdomain.com,Corporate,seed_corp_4
test1@aol.com,Other,seed_aol_1
test1@protonmail.com,Other,seed_proton_1
test2@fastmail.com,Other,seed_fastmail_1
test1@msn.com,Other,seed_msn_1
```

## Seed List Rules
- Use real, monitored mailboxes — not disposable addresses
- Use addresses you actually control and can check
- At least one address per major provider (Gmail, Outlook, Yahoo, iCloud, Zoho)
- Do NOT include any real venue contacts in the seed list

## Checking Results
After test send, check each mailbox and note:
- **Primary inbox** — ideal
- **Promotions tab** (Gmail) — acceptable; watch for trend toward spam
- **Spam/Junk folder** — immediate action needed
- **Not delivered** — flag for bounce investigation

---

## Drop-In Reusability Notes
This seed list protocol is reusable for any outbound system. Replace the example addresses with real addresses you control. The CSV format and `--test-mode` runner are already implemented and reusable.
