# Drop-In Reusability Notes — Testing Module

## What This Module Contains
Pre-send manual QA checklist, post-send CRM audit checklist, 25-seed inbox placement protocol, and seed list template.

## Fully Reusable (No Changes Needed)
- `seed_list_25_protocol.md` — provider distribution and setup protocol are universal
- `inbox_placement_protocol.md` — 80% threshold and test procedure are universal
- `crm_audit_checklist.md` — audit event structure and timing are universal
- `manual_qa_checklist.md` — all 12 pre-send checks apply to any outbound sequence

## Project-Specific Updates
1. **Seed list CSV** — replace addresses with ones you actually control
2. **CRM field names** in audit checklist — update if using a different CRM structure
3. **QA checklist** — update "sender_name" and "sequence_id" values to match new project

## Key Invariants
- Run inbox placement test before EVERY first live send on a new domain or after a significant pause
- Never skip the manual QA checklist for a new batch
- Always check the CRM audit checklist after the first send of a new wave
