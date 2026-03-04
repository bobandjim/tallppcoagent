# Drop-In Reusability Notes — Compliance Module

## What This Module Contains
CAN-SPAM safe defaults, GDPR/UK PECR/CASL awareness, opt-out handling, and suppression list management for US-based outbound B2B email campaigns.

## Fully Reusable Components (No Modification Needed)
- `src/utils/compliance.py` — `SuppressionList` and `CANSPAMChecker` classes
- `config/suppression_list.csv` — format is universal
- Opt-out processing procedure (`opt_out_handling.md`)
- Suppression list management rules (`suppression_list_management.md`)

## Project-Specific Updates Required
1. **Physical address** in `config/settings.yaml` → `brand.physical_address`
2. **Unsubscribe URL** → set up URL for new project, update in config
3. **Sender name** → `brand.sender_name` in config
4. **International contacts** → review `gdpr_awareness.md` if expanding to non-US venues

## Key Compliance Invariants (Never Change These)
- Suppression list is always append-only (no deletes)
- Opt-outs are honored same day
- Physical address and unsubscribe URL are present in every email
- `CANSPAMChecker.validate()` is called before every send
