# Data Sources for Venue Research

**Project:** Princess Peigh's Sword Fighting Tea Party — Outbound Booking System
**Company:** Tall People Performing Company (brand: Princess Peigh Adventures)
**Last Updated:** 2026-03-04

---

## Overview

This document catalogs the recommended sources for identifying and researching potential venues for the Princess Peigh's Sword Fighting Tea Party touring campaign. For each source, it explains how to use it, what data to extract, and how to import that data into the Excel CRM.

Target venues are: community theaters, performing arts centers, libraries, and municipal cultural venues in a 1-to-3 state regional footprint, with 100–400 seats, actively programming live arts.

---

## Source 1: TCG (Theatre Communications Group) Theatre Directory

**URL:** https://www.tcg.org
**What it is:** The national membership organization for professional nonprofit theaters. Their online directory lists member theaters by state, with organization type, contact information, and links to websites.

**How to use it:**
1. Navigate to the TCG member directory or theater finder tool.
2. Filter by your target states.
3. Review each listed organization for fit: look at venue type, website, and any budget/seat information included.
4. Note that TCG members trend toward professional and semi-professional theaters — many will exceed the 400-seat threshold or present more adult/literary programming. Screen carefully using `venue_qualification_criteria.md`.

**What to extract:**
- Organization name
- City and state
- Website URL
- Primary contact name and title (when listed)

**How to import to Excel CRM:**
1. Build a staging CSV with columns: `company`, `city`, `state`, `website`, `segment`, `first_name`, `last_name`, `title`
2. Leave `lead_id`, `contact_id`, `email_opt_out`, `last_updated`, `audit_trail_id` blank — these are auto-generated on import
3. Run deduplication against existing Companies rows before appending
4. Manually assign `segment` (typically `Community Theater` or `Performing Arts Center`) based on website review
5. Paste validated rows into the Companies sheet; create corresponding Contacts rows for any named contacts

---

## Source 2: Playbill Venue Directory

**URL:** https://www.playbill.com
**What it is:** Playbill maintains a database of performing arts venues with contact information, primarily theater-focused. Search and filter tools vary by access level.

**How to use it:**
1. Use the venue search or browse by state/region to identify community theaters and PACs.
2. Look for venues that list a programming director or education director — these are your contacts.
3. Playbill skews toward Broadway and large professional venues; filter aggressively for community and regional venues.

**What to extract:**
- Venue name, city, state
- Phone number (often listed; email may require website visit)
- Contact name and title when available
- Capacity when listed

**How to import to Excel CRM:**
Same staging CSV process as TCG (see Source 1 steps). Supplement missing emails by visiting each venue's website directly.

---

## Source 3: State Arts Council Databases and Grant Recipient Lists

**What it is:** Every U.S. state has a state arts agency (SAA) that distributes public arts funding. Grant recipient lists are public records and represent a curated list of actively-funded, actively-programming arts organizations — exactly the type of venue this campaign targets.

**How to find them:**
- Search: `[State] arts council grant recipients [Year]` or `[State] arts agency grantee list`
- Examples:
  - Ohio Arts Council: https://www.oac.ohio.gov (look for "Grants" → "Grant Recipients")
  - Pennsylvania Council on the Arts: https://www.arts.pa.gov
  - West Virginia Division of Culture and History Arts Section: https://www.wvculture.org
- The National Assembly of State Arts Agencies (NASAA) maintains a directory of all SAAs: https://www.nasaa-arts.org/research/links/

**How to use it:**
1. Download or copy the grantee list for each target state.
2. Filter for discipline categories that include: Theater, Performing Arts, Arts Education, Community Arts, Cultural Organizations.
3. Remove higher education institutions (unless they have public-facing presenter programs) and individual artist grantees.
4. For each remaining organization, visit the website and apply qualification criteria from `venue_qualification_criteria.md`.

**What to extract:**
- Organization name
- City and state
- Grant category (useful for `programming_focus`)
- Website URL (often included in grantee lists)

**How to import to Excel CRM:**
Same staging CSV process. The grant category can be pasted into `programming_focus` (Custom3) or `notes` as context.

---

## Source 4: Google Maps Venue Research

**What it is:** Direct Google Maps searches for venue types in specific cities and counties within target states. This is a manual but highly effective method for finding venues that are not members of national directories.

**Search queries to use:**
```
performing arts center near [city, state]
community theater [city, state]
civic auditorium [city, state]
children's theater [state]
[county name] cultural arts center
library auditorium [city, state]
arts council [city, state]
```

**How to use it:**
1. Run each search query in Google Maps.
2. Review the map results and the sidebar listing of matching venues.
3. Click on each venue to view the Google Business Profile: check hours, website link, photos (gives a sense of scale and type), and reviews (often mention the type of events held).
4. Visit the linked website and apply the qualification criteria.
5. Note the approximate seating capacity if visible in photos or reviews.

**What to extract:**
- Name, address (city and state), phone, website from the Google Business Profile
- Any capacity information visible in photos, reviews, or the venue's website

**How to import to Excel CRM:**
Manual entry or staging CSV. Google Maps data should always be verified against the venue's own website before adding to CRM, as the Business Profile may be outdated.

---

## Source 5: Library Consortium and Regional Library Network Websites

**What it is:** Public libraries are organized into regional networks and state library systems that often maintain program directories or event calendars listing libraries that host live performances.

**How to find them:**
- Search: `[State] library system performing arts` or `[State] public library live programs`
- State library agencies:
  - Ohio: State Library of Ohio — https://library.ohio.gov
  - Pennsylvania: Pennsylvania State Library — https://www.statelibrary.pa.gov
  - West Virginia: West Virginia Library Commission — https://wvlc.lib.wv.us
- Search for regional library consortia (e.g., "CLEVNET" in northeast Ohio, "POWER Library" in Pennsylvania)
- Many library systems publish annual "system-wide" programming calendars that show which branches or libraries host live events

**How to use it:**
1. Navigate to the state library agency or a regional consortium site.
2. Look for member library directories — these list all public libraries in the network with addresses and contacts.
3. Filter for libraries large enough to have a dedicated programming room or auditorium (usually branches serving populations of 10,000+, or main branches of library systems).
4. Visit each qualifying library's website and look for a "Programs" or "Events" page — a library that books live performers will usually have a past events history showing theater groups, storytellers, or musical performers.

**What to extract:**
- Library name (branch name + system name: e.g., "Medina County District Library — Medina Branch")
- City, state
- Programming contact: often "Children's Librarian," "Program Coordinator," or "Branch Manager"
- Website URL

**How to import to Excel CRM:**
Set `segment = Library` for all library venues. Enter the library system name as `company` and the branch name as `venue_name` (Custom4) if applicable.

---

## Source 6: State Humanities Council Grantee Lists

**What it is:** State humanities councils are independent nonprofits affiliated with the National Endowment for the Humanities (NEH). They fund public humanities programming — including storytelling, theater, and educational performances — through grants to libraries, museums, historical societies, and community organizations. Their grantee lists reveal venues that actively fund and host educational and artistic programming for the public.

**How to find them:**
- National list of state humanities councils: https://www.neh.gov/about/state-humanities-councils
- Examples:
  - Humanities Ohio: https://humanitiesohio.org
  - Pennsylvania Humanities Council: https://pahumanities.org
  - West Virginia Humanities Council: https://wvhumanities.org

**How to use it:**
1. Navigate to the Grants or Awards section of the state council website.
2. Look for "Speaker's Bureau," "Chautauqua," "Reading and Discussion," or "Public Programs" grantee lists.
3. Organizations that receive humanities grants for public programs are strong candidates — they have a track record of presenting outside performers to community audiences.
4. Note that humanities councils often fund libraries, historical societies, and community centers that would not appear in theater directories.

**What to extract:**
- Organization name, city, state
- Program description (useful for `programming_focus`)
- Website if listed

**How to import to Excel CRM:**
Same staging CSV process. The program description from the grant can inform `mission_excerpt` (Custom2) or `programming_focus` (Custom3).

---

## Source 7: Social Media — Facebook and Instagram

**What it is:** Many community theaters, small PACs, and arts organizations have active Facebook pages or Instagram accounts even when their websites are outdated or sparse. Social media search can surface venues that are actively programming but difficult to find via directories.

**How to use Facebook:**
1. Facebook search: `[city] community theater`, `[city] performing arts`, `[state] children's theater`
2. Review the Pages results (not Groups) for organizations with:
   - A venue or organization (not an individual artist)
   - Recent posts showing event photos, ticket announcements, or show recaps
   - An "About" section listing a website or address
3. Check the Events tab on any Facebook page to see if the organization is currently booking shows.

**How to use Instagram:**
1. Search hashtags: `#[cityname]theater`, `#[statename]communitytheater`, `#[cityname]performingarts`
2. Look for organizational accounts (not personal accounts) with a consistent posting history
3. Visit the linked website in the bio to qualify the venue

**What to extract:**
- Organization name, website link, city/state from the About section
- Any contact name visible in About or posts
- Evidence of current programming (recency and type of events)

**How to import to Excel CRM:**
Manual entry only — social media data is informal and must be verified against the venue website before CRM entry. Do not import an email address obtained from social media without confirming it is a professional contact email.

---

## Source 8: Referrals from Existing Contacts

**What it is:** Every booked venue, every venue contact, and every industry peer is a potential source of referrals to other venues. Warm referrals are significantly more effective than cold outreach and should be actively solicited.

**How to use it:**
1. After any booking call or show performance, ask the contact: "Are there any other venues in the region you think would love this show? Do you know their programming director?"
2. When a contact says they can't book this cycle but knows another venue, ask for the specific name and email of the right contact there.
3. When receiving a referral, note the referring contact's name and contact_id in the `notes` field of the new venue/contact record.

**What to extract:**
- Referred venue name and city
- Referred contact name, title, and email
- Name of the referring contact (for use in the first outreach email: "Your colleague [Name] at [Venue] suggested I reach out...")

**How to import to Excel CRM:**
- Set `source = Referral` on both the Companies and Contacts rows for any referral-sourced lead
- Referral leads skip the standard cold outreach sequence — they should receive a customized first email mentioning the referral name, then continue into the standard sequence from step 2

---

## General Import Protocol for All Sources

Regardless of source, follow this sequence before adding any new venue or contact to the live CRM:

1. **Qualify first.** Apply `venue_qualification_criteria.md` to each venue before adding it. Do not add disqualified venues.
2. **Stage in a separate tab or CSV.** Build a `staging` sheet with all new records before touching the live Companies and Contacts sheets.
3. **Run dedup.** Compare the staging sheet against live Companies (on `company + state`) and live Contacts (on `email`) to identify existing records.
4. **Merge or skip duplicates.** Update existing records with new data rather than creating duplicate rows (per `deduplication_rules.md`).
5. **Assign required fields.** Auto-generate `lead_id`, `contact_id`, `audit_trail_id`, and `last_updated` for all new rows.
6. **Move validated rows.** Append clean, deduplicated rows from staging to the live Companies and Contacts sheets.
7. **Log the import.** Write a `BULK_IMPORT` event to the audit log noting the source name, date, and row count added.

---

## Drop-In Reusability Notes

This data sources document can be reused for any regional outbound booking campaign targeting civic and nonprofit performing arts venues. To adapt it for a new campaign:

1. **Update the target state examples** in Sources 3, 5, and 6 to match the new campaign's geographic footprint. The structure of each source type (state arts council, state library agency, state humanities council) is consistent across all 50 states — only the URLs and organization names change.
2. **Adjust the Google Maps search queries** (Source 4) to reflect the venue types targeted by the new show. Add or remove search phrases based on the new show's segment targets.
3. **The referral source** (Source 8) is universally applicable and requires no changes. The referral tracking note in the `notes` field and the `source = Referral` field value are standard across campaigns.
4. **The general import protocol** at the end of this document is campaign-agnostic and should remain unchanged in any adaptation.
5. **Add new sources** as they are discovered — for example, a regional presenter consortium, a venue-matching service, or a state theater association not listed here. Follow the same documentation structure: what it is, how to use it, what to extract, how to import.
