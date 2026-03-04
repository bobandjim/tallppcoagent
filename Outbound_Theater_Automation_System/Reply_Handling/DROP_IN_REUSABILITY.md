# Drop-In Reusability Notes — Reply Handling Module

## What This Module Contains
8-category reply classification system, escalation rules, and CRM auto-logging spec for outbound B2B email sequences.

## Fully Reusable (No Changes Needed)
- The 8 reply categories (Interested, Budget, Window, Referral, Not a Fit, Opt-Out, OOO, Bounce) are universal for B2B outreach
- The escalation timeline matrix (same-day / 48h / 24h)
- The "human approval for all replies" rule — keep this for any brand-critical outreach
- The audit event structure in `auto_logging_spec.md`

## Project-Specific Updates Required
1. **Escalation names** — update "Melissa Neufer / Zachary Gartrell" to new project team
2. **Trigger signals** — update industry-specific terms (e.g., "we're fully booked" is theater-specific)
3. **CRM field names** — update field references if using a different CRM structure
4. **Response templates** — create reply templates for the new show/product

## Key Non-Negotiables
- Opt-Outs: always suppressed immediately, never auto-responded to
- Bounces: always suppressed immediately (hard) or after 3x (soft)
- All human replies: always require approval before sending
