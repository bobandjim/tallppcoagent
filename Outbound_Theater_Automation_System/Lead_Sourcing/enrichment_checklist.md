# Venue Enrichment Checklist

Run this checklist for each venue after initial research. Goal: populate Custom1-Custom3 in the Companies sheet before any sequence step is sent.

## Per-Venue Enrichment Checklist

**Venue:** _______________
**Website:** _______________
**Date enriched:** _______________

### Seating Capacity (Companies.Custom1)
- [ ] Found seating capacity on website (check: About, Rentals, FAQ pages)
- [ ] Classified tier:
  - [ ] Small (100-199 seats) → enter `Small`
  - [ ] Mid (200-299 seats) → enter `Mid`
  - [ ] Large (300-400 seats) → enter `Large`
  - [ ] Outside range (< 100 or > 400) → **remove from list**

### Mission Excerpt (Companies.Custom2)
- [ ] Found mission statement or "About" page text
- [ ] Extracted 1 short phrase (<100 characters) that:
  - Reflects their community focus
  - Can be naturally referenced in Step 1 email
  - Example: "bringing world-class arts to underserved communities"
  - Example: "fostering the next generation of arts audiences"
- [ ] Entered in Custom2 column

If no mission statement found:
- [ ] Leave Custom2 empty (Step 1 mission block will not render)
- [ ] Note in Companies.Notes: "No mission found — [date]"

### Programming Focus (Companies.Custom3)
- [ ] Checked current season page / programming page
- [ ] Classified focus:
  - [ ] `Family` — family series, children's programs
  - [ ] `Education` — school programs, student matinees
  - [ ] `Community` — community events, local acts
  - [ ] `Arts` — broad arts programming without family focus
  - [ ] `Mixed` — multiple focus areas
- [ ] Entered in Custom3 column

### Contact Verification
- [ ] Programming Director or equivalent found
- [ ] Email address is current (check: Staff page, Contact page, LinkedIn)
- [ ] Title entered in Contacts.Title
- [ ] Email entered in Contacts.Email

### Final Check
- [ ] Companies.Custom1 populated (seating tier)
- [ ] Companies.Custom2 populated OR confirmed blank
- [ ] Companies.Custom3 populated
- [ ] Contacts.Email verified
- [ ] Contacts.Title verified
- [ ] Companies.Notes updated with research date

---

## Drop-In Reusability Notes
This enrichment checklist applies to any touring show outbound system targeting venue programmers. The three enrichment fields (seating_capacity_tier, mission_excerpt, programming_focus) are high-value for personalization and directly map to Jinja2 tokens in the email templates. For a new project, update the tier labels (Small/Mid/Large) if the seat ranges differ.
