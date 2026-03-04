# Knowledge Base — Princess Peigh Adventures Outbound System
## Master Evolving Document

**Show:** Princess Peigh's Sword Fighting Tea Party
**Company:** Tall People Performing Company
**System version:** 1.0 (Wave 1)
**Last updated:** 2026-03-04
**Branch:** `claude/complete-system-build-crm-jrfpP`

> This document never closes. Every wave of outreach adds to it. Every booking attempt generates learnings that belong here.

---

## Brand Reference (Do Not Change Without Team Approval)

### Core Identity
- Original IP — not a character act, not a princess party
- 60-minute scripted theatrical show + optional post-show sword-fighting workshop
- Ages 4-8 primary; works for all ages including adults
- Sensory-considerate; neurodivergent-aware design
- Core message: **"I Am Enough"** — embedded in theater, not announced
- Fully insured; stage combat certified; portable technical footprint

### Creators
- **Melissa Neufer** — Creator, emotional architect, performs Princess Peigh (spunky, whimsical, imperfect, self-aware)
- **Zachary Gartrell** — Performer (Squire), structural producer, theatrical systems builder (grounded, reserved)

### Brand Tone Rules
- Whimsical and confident — not precious or apologetic
- Emotionally sincere — not preachy or agenda-driven
- Intelligent and peer-to-peer — not salesy or corporate
- Inclusive because human — never labeled or over-explained
- **Never use:** "educational," "empowerment" (overused), "magical" (generic), "unforgettable" (unverifiable)

### Proven Social Proof
- 2 sold-out Jewish community runs
- Successful performance at Irvington Theater (100+ audience)
- Testimonials from programmers and parents (file separately; never publish without permission)

### Social Media
- `@PrincessPeighadventures` — primary content source for brand voice reference
- Request access if needed for current content

---

## System Architecture Summary

```
Lead Research → Excel CRM (6 sheets) → Python Validator → Jinja2 Renderer →
Zoho SMTP → Audit Trail (SQLite) → Reply Inbox → Human Review → CRM Update
```

**CRM file:** `data/crm/leads.xlsx` (local, not committed to git unless sample data)
**Audit log:** `data/audit.db` (SQLite, append-only)
**Suppression list:** `config/suppression_list.csv`
**Email platform:** Zoho Mail SMTP (smtp.zoho.com:587)
**Config:** `config/settings.yaml` (credentials via env vars in `.env`)

---

## Targeting Reference

| Parameter | Value |
|-----------|-------|
| Geography | Regional (1-3 states; update `settings.yaml` as scope expands) |
| Venue seat range | 100-400 seats |
| Venue types | Community theater, PAC, library, municipal cultural venue, arts nonprofit |
| Contact titles | Programming Director, Executive Director, Family Series Coordinator, Arts Director |
| Sequence | 4 steps over 14 days |
| Daily send limit | 10 (Week 1 warm-up) → 100 (Week 4+) |

---

## Wave Log

### Wave 1 — 2026-03-04 — Initial System Build

**Status:** Build complete; not yet deployed

**What was built:**
- Full Python codebase (schema, import, export, dedup, compliance, email, audit)
- 4-step email sequence (Jinja2 templates)
- CRM mapped to actual Excel template (6-sheet structure confirmed)
- Full 10-phase implementation roadmap (PLAN.md)
- Complete documentation sub-modules (all 8 modules)
- Test suite (pytest)

**Key decisions made:**
- CRM: Excel/CSV only (no SaaS) — keeps costs zero, keeps data local
- Email: Zoho Mail SMTP — already available, no new subscriptions
- Geography: Regional (1-3 states) — matches current touring capacity
- Venue size: 100-400 seats — matches show's proven performance size

**Excel template structure (confirmed from actual file):**
- Sheet: Companies (venue records, 22 sample rows)
- Sheet: Contacts (contact records, 10 sample rows)
- Sheet: Gigs_Leads (booking pipeline, 10 sample rows)
- Sheet: Calls (call log)
- Sheet: Notes (notes log)
- Sheet: Lookups (dropdown values: Yes/No, Held/Planned/Not Held, Gig/Lead)
- Custom1-Custom15 columns used for outbound tracking fields (not pre-defined in template)

**Open items for Wave 2:**
- Zoho account + sending domain setup (requires Melissa/Zachary action)
- SPF/DKIM/DMARC DNS configuration
- Seed list population (25 addresses needed)
- Initial venue list research (50+ venues across target states)
- Touring calendar input (which dates are unavailable)
- Physical mailing address for CAN-SPAM footer (update in settings.yaml)
- Unsubscribe URL (set up page/form, update in settings.yaml)
- Email copy review and approval by Melissa and Zachary

---

## Performance Benchmarks (Update After Each Wave)

| Metric | Target | Wave 1 Actual | Wave 2 Actual |
|--------|--------|--------------|--------------|
| Inbox placement | ≥ 80% | TBD | |
| Open rate | ≥ 25% | TBD | |
| Reply rate | ≥ 3% | TBD | |
| Bookings / 50 leads | ≥ 1 | TBD | |
| Bounce rate | < 2% | TBD | |

---

## Venue Research Learnings (Add After Each Research Round)

*No research completed in Wave 1 — build only.*

---

## Reply Patterns (Add After First Sends)

*No sends in Wave 1 — build only.*

---

## Sequence Performance (Add After Each Send Wave)

*No sends in Wave 1 — build only.*

---

## Known Issues and Resolutions

| Issue | Status | Resolution |
|-------|--------|------------|
| No known issues | — | — |

---

## System Decisions Log

| Date | Decision | Rationale | Decided By |
|------|----------|-----------|-----------|
| 2026-03-04 | Excel/CSV CRM (no SaaS) | Zero cost; data stays local; openpyxl handles all operations | User |
| 2026-03-04 | Zoho Mail SMTP | Already available; no new subscriptions needed | User |
| 2026-03-04 | Regional 1-3 states, 100-400 seats | Matches current touring capacity and proven performance size | User |
| 2026-03-04 | 4-step sequence over 14 days | Industry standard for cold outreach to arts programmers | System design |
| 2026-03-04 | SQLite for audit trail | Local, zero-config, append-only, easy to query | System design |
| 2026-03-04 | Human approval for all replies | Non-negotiable — brand voice must be maintained | System design |

---

## Continuation Backlog

- [ ] Social media research ingestion (@PrincessPeighadventures content → brand voice updates)
- [ ] Calendar integration (Zoho Calendar or Calendly → auto-log meetings)
- [ ] Proposal tracking (PDF template + send logging)
- [ ] School matinee segment (separate sequence + targeting)
- [ ] Festival circuit sequence (Fringe Festival)
- [ ] Library consortium targeting (different pitch for library networks)
- [ ] Reply classifier (keyword-based Python pre-categorization; human still approves)
- [ ] Multi-sequence management (prevent re-enrolling venues already in pipeline)
- [ ] Open/click tracking (requires Zoho Campaigns API or tracking pixel)
- [ ] Reporting dashboard (Python script → flat CSV report from audit.db)
