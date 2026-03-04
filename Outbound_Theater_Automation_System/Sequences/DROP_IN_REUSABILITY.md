# Drop-In Reusability Notes — Sequences Module

## What This Module Contains
Four-step outbound email sequence for booking a touring family theatrical production at community theaters and performing arts centers. Templates use Jinja2, rendered by `src/email/sequence_builder.py`.

## How to Reuse for a New Show or Project

### Step 1: Update the Jinja2 templates
- Edit `templates/email/initial_outreach.j2`, `followup_1.j2`, `followup_2.j2`, `breakup.j2`
- Replace show-specific content (show name, runtime, differentiators, social proof)
- Keep the token structure (`{{ venue_name }}`, `{{ city }}`, etc.) — these are filled at runtime
- Keep the CAN-SPAM footer structure exactly

### Step 2: Update the sequence docs (this folder)
- Update `sequence_01_initial_outreach.md` through `sequence_04_breakup.md` with the new show's content notes

### Step 3: Update sequence config
In `config/settings.yaml`:
```yaml
sequences:
  default_sequence_id: "new_show_outreach_v1"  # update ID
  steps: 4                                      # adjust if adding/removing steps
  delays_days: [0, 5, 9, 14]                   # adjust timing if needed
```

### Step 4: Update CRM sequence_id
When enrolling new contacts, set `Contacts.Custom1` to the new `sequence_id` value.

## Personalization Token Reference

| Token | Source | Required |
|-------|--------|----------|
| `{{ contact_name }}` | Contacts.First Name | Yes |
| `{{ venue_name }}` | Gigs_Leads.Venue Name | Yes |
| `{{ city }}` | Companies.Billing City | Yes |
| `{{ state }}` | Companies.Billing State | Yes |
| `{{ seating_capacity_tier }}` | Companies.Custom1 | Yes (auto-labeled) |
| `{{ mission_excerpt }}` | Companies.Custom2 | No (block optional) |
| `{{ next_season }}` | Caller-supplied string | Yes (Step 4 only) |
| `{{ sender_name }}` | Config | Yes |
| `{{ physical_address }}` | Config | Yes (CAN-SPAM) |
| `{{ unsubscribe_url }}` | Config | Yes (CAN-SPAM) |

## Adding a 5th Step
1. Create `templates/email/step_05.j2`
2. Add entry to `STEP_TEMPLATES` dict in `src/email/sequence_builder.py`
3. Update `sequences.steps: 5` in `config/settings.yaml`
4. Update `sequences.delays_days` to add new delay
5. Create corresponding `sequence_05_*.md` doc in this folder
