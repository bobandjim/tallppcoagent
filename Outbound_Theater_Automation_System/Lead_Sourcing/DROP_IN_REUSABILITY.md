# Drop-In Reusability Notes — Lead Sourcing Module

## What This Module Contains
Venue qualification criteria (Tier A/B/C scoring), data source guide (8 sources), and enrichment checklist (seating tier, mission, programming focus).

## Fully Reusable Components
- `enrichment_checklist.md` — 3-field enrichment approach (seating tier / mission / focus) applies to any venue outreach
- `data_sources.md` — research sources (TCG, state arts councils, Google Maps, library networks) apply to any arts/entertainment venue research

## Project-Specific Updates Required
1. **Seat range** — adjust Small/Mid/Large cutoffs if targeting a different show size
2. **Tier A criteria** — update "family series listed" qualifier for new show's target program type
3. **Disqualifying criteria** — adapt for new show's requirements

## Key Enrichment Rule (Always Apply)
Never send Step 1 without at least `seating_capacity_tier` populated. The `mission_excerpt` block is optional but significantly improves response rates when populated with a real, venue-specific phrase. Do not fabricate mission excerpts.
