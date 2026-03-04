# Drop-In Reusability Notes — CRM Schema Module

## What This Module Contains
Full CRM field definitions mapped to the 6-sheet Excel import format, row creation/update/suppression logic, deduplication rules, and the machine-readable schema (crm_schema.json).

## Fully Reusable Components
- `crm_schema.json` — schema is reusable for any project using the same Excel import format
- `deduplication_rules.md` — dedup key approach (company+state for venues, email for contacts) is universal
- `row_logic.md` — row creation/update/suppression logic applies to any 6-sheet CRM structure

## Project-Specific Updates
1. **Custom field assignments** — Custom1-Custom8 mappings in Contacts and Custom1-Custom4 in Gigs_Leads are defined here. Update if a future project needs different tracking fields.
2. **Segment values** — venue types listed under Companies.Record Type may differ for non-theater projects
3. **Reply category values** — Contacts.Custom6 valid values list matches the 8 reply categories in Reply_Handling/

## The Custom Column Strategy
This project repurposes the Excel template's Custom1-Custom15 columns (pre-existing but undefined) to store outbound tracking data without modifying the base import format. This approach works for any system using this Excel template — just assign different meanings to the Custom columns and document them in `crm_field_definitions.md`.
