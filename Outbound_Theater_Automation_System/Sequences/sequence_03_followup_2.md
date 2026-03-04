# Sequence Step 3 — Follow-Up 2 (Practical Angle)
**Day:** 9 (9 days after Step 1)
**Template file:** `templates/email/followup_2.j2`

## Purpose
Shift to the practical/operational angle. Most programmers who haven't responded to Steps 1-2 are not yet sold on logistics fit. This step removes friction: addresses technical footprint, pricing flexibility, booking format options, and explicitly offers a graceful exit ("even a 'not this season' is useful").

## Subject Line
```
No technical riders, no headaches — just great theater
```

## Key Content Elements
1. Short hook: "one more note before I leave you alone"
2. Core promise: lowest-friction family theatrical booking available
3. Format options: Saturday matinee, school-day morning, community anchor + workshop
4. Pricing flexibility: 3 models available (flat fee, ticket split, guarantee + percentage)
5. Explicit graceful exit offer: "even 'not this season, try us in the fall' is useful"
6. CAN-SPAM footer

## Tone Guide
- Confident and practical — no hedging
- "I know you're busy" energy without being servile
- Offer the exit explicitly — it respects the contact's time and signals professionalism

## CRM Actions on Send
- `Contacts.Custom2` (step_number) = `3`
- `Gigs_Leads.Custom4` (send_time) = ISO 8601 timestamp
- Audit event: `EMAIL_SENT` with `step=3`

---

## Drop-In Reusability Notes
This step's "practical angle" approach works for any touring product with flexible pricing and low logistics overhead. The key is:  (1) name the specific format options relevant to your venue types, (2) name the pricing models available, (3) offer the graceful exit explicitly. All three elements can be updated for a new show with minimal edits.
