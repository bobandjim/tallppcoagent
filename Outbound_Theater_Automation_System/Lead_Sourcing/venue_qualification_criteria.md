# Venue Qualification Criteria

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**Last Updated:** 2026-03-04

---

## Overview

Not every venue that appears in a directory or search result is worth pursuing. This document defines the criteria used to decide whether a venue should be added to the CRM as an active lead, how to score it into a tier, and what data points to gather during the research phase.

The goal is to focus outreach on venues that are:
1. The right type of organization (programs live arts for the public)
2. The right physical size (can host the show in a way that works financially and logistically)
3. Geographically in target territory
4. Philosophically aligned with Princess Peigh Adventures' family/education/arts mission

Applying these criteria before adding a venue to the CRM saves outreach time and keeps the pipeline accurate.

---

## Part 1: Qualifying Criteria

A venue passes qualification if it meets **all** of the following:

### 1.1 Venue Type

The organization must be one of the following:

| Type                        | Description |
|-----------------------------|-------------|
| Community Theater           | A nonprofit or volunteer-driven theater organization that produces its own shows and/or presents guest productions for the local community. |
| Performing Arts Center (PAC)| A dedicated performance facility operated by a nonprofit, municipality, or university that presents a season of programming for the public. |
| Library                     | A public library that hosts live performances, typically in a multipurpose room or small auditorium, often as part of a family/children's programming series. |
| Municipal Cultural Venue    | A city- or county-owned facility (community center, civic auditorium, cultural arts center) that hosts public programming and books outside performers. |

Venues that do not fall clearly into one of these categories may still qualify on a case-by-case basis (use `segment = Other`) but require additional manual review.

### 1.2 Seating Capacity

The venue's main performance space must seat between **100 and 400 people.**

- Below 100: Revenue potential does not support the fee structure for a touring production.
- Above 400: Venue likely expects higher production values, larger marketing budgets, and more staff than this show can provide; also, scaling intimately-staged children's theater to 500+ seats reduces effectiveness.
- Unknown capacity: Add to CRM with `seating_capacity_tier = Unknown` and schedule research to confirm before outreach begins.

### 1.3 Active Programming

The venue must show evidence that it is currently programming live performances for the public. Look for:

- A current-season events page or calendar on the website with dated upcoming shows
- Recent past events listed (within the last 12 months)
- A "book a performer" or "rental/presenter inquiry" form or contact

A venue with a website that shows only its history, a dark season, or events more than 18 months old is not considered actively programming and should be marked as `outcome = Postponed` or held without outreach until activity is confirmed.

### 1.4 Geographic Targeting

The venue must be located in the campaign's target states. The current campaign covers a 1-to-3 state regional footprint. The specific target states are defined in the campaign configuration document (see `campaign_config.md` or ask the campaign manager).

Record the venue's state in the `state` field (two-letter abbreviation). Venues outside target states should not be added to the active CRM. They may be added to a holding list for future campaign cycles.

### 1.5 Mission Alignment

The venue's stated mission, programming description, or event history should indicate compatibility with:

- Family audiences (children and parents attending together)
- Educational programming (school matinees, curriculum-connected arts, residencies)
- Arts access and community enrichment
- Youth engagement or children's series

Venues that exclusively program adult drama, experimental art, or abstract/avant-garde work are lower priority. Venues with an explicit children's series, family series, or educational outreach component are the best fit.

Check the mission statement on the About page, look for a "Family Series" or "For Schools" section, and scan the event history for shows that skew family or children's.

---

## Part 2: Disqualifying Criteria

A venue is disqualified and should not be added to the active CRM if it meets **any** of the following:

| Disqualifier                              | How to Identify |
|-------------------------------------------|-----------------|
| Private event venue only                  | Website describes exclusively weddings, corporate events, private parties. No public programming calendar. |
| Purely rental, no house programming       | Venue rents space but does not produce, present, or book any of its own programming. All events are renter-initiated and renter-promoted. |
| Seating capacity below 100                | Confirmed seat count under 100, or venue described as a "black box" or "studio" with clearly limited capacity. |
| Seating capacity above 400                | Confirmed seat count over 400. |
| Explicitly does not book touring shows    | Website or booking FAQ states they only produce in-house or only book local groups. |
| Outside target states                     | Location confirmed to be outside the 1-to-3 state regional footprint for this campaign cycle. |
| Permanently closed                        | Website is down, social media inactive for 2+ years, confirmed closure in news or community sources. |
| Amusement park, hotel, or casino venue    | Not a civic or arts-mission organization; booking dynamics and audience expectations are incompatible. |

When a venue is disqualified:
- Do not add it to the Companies sheet as an active lead
- If it was already added, set `outcome = Lost` on any Gigs_Leads row and annotate the Companies row in the `notes` field with the disqualification reason and date

---

## Part 3: Venue Scoring and Tiering

Once a venue passes basic qualification, assign it to one of three tiers. The tier drives outreach priority and, where relevant, fee negotiation expectations.

### Tier A — High Priority

**Criteria (must meet all three):**
- Venue type: Performing Arts Center or Municipal Cultural Venue with a formal presenter operation
- Seating capacity: 200–400 seats
- Has an explicit family or children's series listed on the programming page (named series, e.g., "Family Fun Series," "Magic Circle Children's Programming," "Saturday Family Matinees")

**Rationale:** These venues have the infrastructure, budget, and audience development habit to book a touring children's show with minimal hand-holding. They are likely to have a programming director or executive director with decision-making authority and a budget for presenter fees.

**CRM entry:** Set `seating_capacity_tier` to the matching range (200-299 or 300-400). Add `programming_focus` field with the series name if found.

### Tier B — Standard Priority

**Criteria:**
- Venue type: Community Theater (any seat count in range), or Performing Arts Center without a named family series, or Municipal Cultural Venue with limited presenter infrastructure
- Seating capacity: 100–299 seats
- Shows evidence of public programming but no dedicated family series

**Rationale:** Community theaters are strong candidates because they serve local family audiences and are often looking for guest productions to fill gaps in their season. They may have smaller budgets, so be prepared to discuss pricing flexibility. Programming decisions may involve an artistic director, board committee, or volunteer leadership rather than a full-time presenter.

**CRM entry:** Set `seating_capacity_tier` to the matching range.

### Tier C — Lower Priority / Longer Lead Time

**Criteria:**
- Venue type: Library, small community center, or municipal venue with a modest performance program
- Seating capacity: 100–149 seats (or unknown but described as a smaller space)
- Programs live events but infrequently or informally

**Rationale:** Libraries and small venues can be excellent partners for educational or matinee-style bookings, but they often have very limited budgets (sometimes under $1,500), require grant cycles to fund performances, and may need more lead time (6–18 months). Best approached with a lighter-touch email sequence and realistic fee expectations.

**CRM entry:** Set `seating_capacity_tier` to `100-149` or `Unknown`. Note the library system or municipal department in `programming_focus`.

### Tier Summary Table

| Tier | Venue Type               | Seat Range | Family Series? | Outreach Priority |
|------|--------------------------|------------|----------------|-------------------|
| A    | PAC / Municipal PAC      | 200–400    | Yes            | First             |
| B    | Community Theater / PAC  | 100–299    | Optional       | Second            |
| C    | Library / Small Venue    | 100–149    | No requirement | Third             |

---

## Part 4: Data Points to Research for Each Venue

Before adding a venue to the CRM and before composing the first outreach email, gather the following information. Record findings in the corresponding CRM fields.

| Data Point             | Where to Find It                                        | CRM Field             |
|------------------------|---------------------------------------------------------|-----------------------|
| Organization name      | Website header, Google Maps listing, directory entry    | `company`             |
| Performance space name | Website (often different from org name)                 | `venue_name` (Custom4)|
| Website URL            | Google search, directory                                | `website`             |
| City                   | Website contact page, Google Maps                       | `city`                |
| State                  | Website contact page, Google Maps                       | `state`               |
| Venue type/segment     | About page, programming page                            | `segment`             |
| Seating capacity       | Website, Google Maps "about" section, venue FAQ, direct call | `seating_capacity_tier` |
| Mission statement      | About page — copy a 1-3 sentence excerpt                | `mission_excerpt` (Custom2) |
| Programming focus      | Programming/events page — summarize in 1 sentence       | `programming_focus` (Custom3) |
| Main phone             | Contact page, Google Maps                               | `phone`               |
| Contact person name    | Staff page, About page, Facebook "About," LinkedIn      | `first_name`, `last_name` |
| Contact title          | Staff page, LinkedIn                                    | `title`               |
| Contact email          | Staff page, contact form (may require a first-contact call or form submission to obtain) | `email` |
| Current season evidence| Events calendar, news page, Facebook events             | Used to confirm `active programming` qualifier |

**Research depth required before outreach:**
At minimum, confirm: venue type, seating capacity tier, one contact name and email, and evidence of active programming. Outreach should not begin without these four data points confirmed.

A venue where the contact email cannot be found should be noted in the `notes` field and a call should be logged to request the correct contact.

---

## Drop-In Reusability Notes

This venue qualification criteria document can be adapted for any outbound theatrical touring booking campaign. To reuse it for a new show:

1. **Review the Venue Type table** in Part 1. If the new show targets different venue types (e.g., outdoor festivals, schools, corporate events), update the table accordingly and revise the Lookups sheet `segment` picklist to match.
2. **Revise the Seating Capacity range** in sections 1.2 and the Tier table if the new show has different technical or financial requirements. A larger-scale production may target 300–1,000 seats; a more intimate show may work best at 50–200.
3. **Update the Mission Alignment criteria** in section 1.5 to match the new show's target audience (e.g., adult drama instead of family/children; LGBTQ+ arts instead of general family; classical music instead of theater).
4. **The Disqualifying Criteria** (Part 2) are broadly applicable to any outbound booking campaign and require minimal changes. Add any show-specific dealbreakers (e.g., "no fly rigging available," "no orchestra pit") as additional rows in the disqualification table.
5. **The Tier scoring system** (Part 3) maps to the `seating_capacity_tier` and `programming_focus` CRM fields. To use a different tier structure (e.g., four tiers, or tiers based on budget rather than seat count), update the Tier table and add the tier as a new CRM field (Custom) on the Companies sheet.
6. **The Research Data Points table** (Part 4) is universally applicable with only the CRM field mappings needing verification against the field definitions in `crm_field_definitions.md` for the new campaign.
