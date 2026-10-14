**Today:** I used 2026-11-20, the newest date in `activity.csv`, because there is no README with an as-of date. The data is **not fully fresh (rule A1)**. `morning-digest` has no log line on 2026-11-17, so everything below was computed with that gap.

I read `partners.csv`, `contacts.csv`, `activity.csv` and `agent.md`. `partner-crm-steward.md` does not exist in this folder. The columns matched the expected names, so no remapping was needed.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | morning-digest | The scheduled job skipped a day. | The job logs 11-14, 15, 16, 18, 19 and 20, with nothing on 11-17. `nightly-sync` has all 7 days. | High | Check why the 17th run didn't happen and re-run it. (person) |
| 2 | B1 | P04+P05 | Near-same names. | "Pebble Pet Co." and "Pebble Pets" both normalise to "pebble pet". P04 is Prospect and P05 is Paused. | High | Decide whether to merge or keep both. (person) |
| 3 | B2 | C13 (P14) | The contact points at a partner that doesn't exist. | C13 Iris Holt, `partner_id` P14, iris@northgatefoods.example. There is no P14. | High | Re-point the contact to the right partner or remove it. (person) |
| 4 | C2 | P02 Harbor Kitchen Supply | Status is Live but there are no live offers. | `status`=Live, `live_offers`=0. The 11-17 e-mail says Fatima asked when the spring promo goes live. | Medium | Confirm whether the partner is really Live or the offers count is stale. (person) |
| 5 | C3 | P02 | `last_contact` is behind the newest e-mail. | `last_contact` is 2026-11-15. The newest non-bounce e-mail is 2026-11-17. | Low | Set `last_contact` to 2026-11-17. (safe to apply) |
| 6 | C3 | P07 Alder Coffee | `last_contact` is behind the newest e-mail. | `last_contact` is 2026-10-20. The 2026-11-16 e-mail "Courier delivery failed twice; Sanne asked us to re-send the samples" is a real reply, not a bounce. | Low | Set `last_contact` to 2026-11-16. (safe to apply) |
| 7 | D5 | P01 Alder Bike Works | Relationship is cooling. | Priority A (14-day window). Effective last contact is 2026-11-09, which is 11 days ago and above 10.5. | Medium | Reach out before it goes cold. (person) |
| 8 | D5 | P06 Marlow Outdoor Ltd | Relationship is cooling. | Priority B (30-day window). Last contact is 2026-10-26, which is 25 days ago and above 22.5. There is no e-mail in the log. | Medium | Reach out soon. (person) |
| 9 | E1 | C10 (P10, Maya Grant) | A contact whose address bounced is still Active. | The 2026-11-19 notice "550 5.1.1 <maya@tidewaterprints.example>: Recipient address rejected: User unknown". C10 `status`=Active. | Medium | Set the contact status to Bounced. (safe to apply) |
| 10 | F3 | P03 Quill & Ink | Open partner with no owner. | Status Negotiation, `owner` empty. | Medium | Assign an owner. (person) |
| 11 | F4 | P04 Pebble Pet Co. | Open partner with no contact. | Status Prospect. No row in `contacts.csv` has `partner_id` P04. | Medium | Add a contact, or settle this together with the P04/P05 duplicate. (person) |

## Today's three
1. **A1 morning-digest.** The missed run means every other check rests on stale data, so fix this first.
2. **B2 C13 (orphan contact).** Iris Holt at Northgate Foods points at no partner, so either a partner record is missing or the contact is mislinked.
3. **B1 P04+P05.** A merge decision would also settle the P04 no-contact finding (F4) and avoid contacting a Paused duplicate.

## Clean partners
Four of the 12 partners had no findings: P08, P09, P11 and P12. P10 has only a contact-level finding (E1 on C10).

## What I did NOT do
This was a read-only pass, and no changes were made. The "safe to apply" items are only proposals.

```findings
[
  {"rule": "A1", "entity": "morning-digest", "bucket": "person"},
  {"rule": "B1", "entity": "P04+P05", "bucket": "person"},
  {"rule": "B2", "entity": "C13", "bucket": "person"},
  {"rule": "C2", "entity": "P02", "bucket": "person"},
  {"rule": "C3", "entity": "P02", "bucket": "safe"},
  {"rule": "C3", "entity": "P07", "bucket": "safe"},
  {"rule": "D5", "entity": "P01", "bucket": "person"},
  {"rule": "D5", "entity": "P06", "bucket": "person"},
  {"rule": "E1", "entity": "C10", "bucket": "safe"},
  {"rule": "F3", "entity": "P03", "bucket": "person"},
  {"rule": "F4", "entity": "P04", "bucket": "person"}
]
```
