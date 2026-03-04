# Sequence Step 1 — Initial Outreach
**Day:** 0 (first contact)
**Template file:** `templates/email/initial_outreach.j2`

## Purpose
Warm, direct first contact. Introduce the show, establish relevance to the venue's programming, and make a clear ask for a 15-minute call. Not a sales letter — a professional peer reaching out.

## Subject Line
```
A show your {{ city }} families will still be talking about
```

## Personalization Tokens Required
| Token | Source field | Notes |
|-------|-------------|-------|
| `{{ contact_name }}` | Contacts.First Name | Use first name only |
| `{{ venue_name }}` | Gigs_Leads.Venue Name or Companies.Custom4 | Display name |
| `{{ city }}` | Companies.Billing City | |
| `{{ state }}` | Companies.Billing State | |
| `{{ seating_capacity_tier }}` | Companies.Custom1 | Auto-labels as "Small (100-199 seats)" etc. |
| `{{ mission_excerpt }}` | Companies.Custom2 | Optional; block skipped if null |
| `{{ sender_name }}` | Config | "Zachary Gartrell" |
| `{{ physical_address }}` | Config | Required for CAN-SPAM |
| `{{ unsubscribe_url }}` | Config | Required for CAN-SPAM |

## Key Content Elements
1. Opening: why this venue specifically
2. What the show is (not what it isn't)
3. Bullet list: key differentiators (60-min, self-contained, ages 4-8, neurodivergent-aware, "I Am Enough")
4. Capacity tier reference (natural, not template-y)
5. Optional: mission alignment block (only renders if mission_excerpt is populated)
6. Clear CTA: 15-minute call, OR offer to send one-sheet + video clip
7. CAN-SPAM footer: sender name, physical address, unsubscribe URL

## Tone Guide
- Peer-to-peer, not sales pitch
- Whimsical but not precious
- Specific, not generic
- Do not over-explain. Let the bullet list do the work.

## CAN-SPAM Compliance Check
- [ ] Sender name present (not just email address)
- [ ] Subject line accurately reflects email content
- [ ] Physical mailing address in footer
- [ ] Unsubscribe mechanism present and functional
- [ ] No deceptive subject line language

## CRM Actions on Send
- `Contacts.Custom1` (sequence_id) = `theater_outreach_v1`
- `Contacts.Custom2` (step_number) = `1`
- `Gigs_Leads.Custom4` (send_time) = ISO 8601 timestamp
- `Contacts.Custom7` (last_updated) = ISO 8601 timestamp
- Audit event: `EMAIL_SENT` with `step=1`

---

## Drop-In Reusability Notes

This initial outreach template is structured for any touring performing arts act reaching out to venue programmers. To adapt for a different show:
1. Update the show name, runtime, and differentiator bullets in `initial_outreach.j2`
2. Keep the 5-element structure: intro → what it is → differentiators → capacity ref → CTA
3. The mission_excerpt conditional block is reusable for any enriched venue list
4. Keep the CAN-SPAM footer structure exactly as-is
