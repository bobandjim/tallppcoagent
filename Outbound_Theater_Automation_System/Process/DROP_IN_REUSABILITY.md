# Drop-In Reusability Notes — Process Module

## What This Module Contains
System overview, lead intake workflow, and sequence execution workflow for the outbound booking automation system.

## Fully Reusable Components
- The overall system flow (Research → CRM → Validate → Render → Send → Audit → Reply) applies to any outbound sequence
- Lead intake workflow steps 1-10 apply to any venue/contact research + CRM population task
- Sequence execution workflow steps 1-11 apply to any Jinja2 + Python + SMTP outbound system

## Project-Specific Updates
1. **System overview** — update show name, company, targets, and tech stack notes
2. **Lead intake workflow** — update the `sequence_id` name (step 6) for the new project
3. **Contact title targets** — update from "Programming Director/Executive Director" to whatever is appropriate

## Key Process Invariants (Never Change)
- Suppression check before every send (step 5 in execution workflow)
- Audit event written for every send (step 10)
- CRM saved after every batch run
- Human reviews all replies before responding
