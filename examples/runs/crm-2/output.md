**Today:** I used 2026-11-20, the newest date in `activity.csv`. There is no README in the folder, so no as-of date was stated. The data is **not fully fresh** (rule A1): `morning-digest` has no log line on 2026-11-17, so everything below rests on partly stale data. `nightly-sync` ran every day from 11-14 to 11-20.

I used these columns as they are. Status values were already one of the five standard statuses. The log's `email` source was treated as e-mail, and `nightly-sync` and `morning-digest` as automations.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | morning-digest | The job skipped a day. | The job has lines on 11-14, 15, 16, 18, 19 and 20, but none on 11-17. The `nightly-sync` line for 11-17 is present. | High | Check why the digest didn't run on 11-17 and whether items were missed (person). |
| 2 | B1 | P04+P05 | Probable duplicate partners. | "Pebble Pet Co." and "Pebble Pets" both normalise to "pebble pet". P04 is a Prospect (owner Ravi) and P05 is Paused (owner Ines). | High | Decide whether to merge. Nothing is merged without a yes (person). |
| 3 | B2 | C13 | The contact points at a partner that doesn't exist. | C13 (Iris Holt, iris@northgatefoods.example) has `partner_id` P14. There is no P14. | Medium | Re-attach the contact to the right partner or remove it (person). |
| 4 | C2 | P02 | Live partner with no live offers. | Harbor Kitchen Supply has status Live and `live_offers` 0. The 11-17 e-mail says "Fatima asked when the spring promo will go live". | Medium | Check whether an offer should be live, or whether the status is wrong (person). |
| 5 | C3 | P02 | `last_contact` is out of date. | `last_contact` is 2026-11-15. The newest non-bounce e-mail is 2026-11-17. | Low | Set `last_contact` to 2026-11-17 (safe to apply). |
| 6 | C3 | P07 | `last_contact` is out of date. | `last_contact` is 2026-10-20. The 2026-11-16 e-mail ("Courier delivery failed twice; Sanne asked us to re-send the samples") is a real conversation, not a bounce notice. | Low | Set `last_contact` to 2026-11-16 (safe to apply). |
| 7 | D5 | P01 | Relationship is cooling. | Priority A, so the window is 14 days. `last_contact` is 2026-11-09, which is 11 days ago, above 10.5 days (three quarters of the window). No newer e-mail. | Medium | Contact Alder Bike Works soon (person). |
| 8 | D5 | P06 | Relationship is cooling. | Priority B, so the window is 30 days. `last_contact` is 2026-10-26, which is 25 days ago, above 22.5 days. No newer e-mail. | Medium | Reach out to Marlow Outdoor (person). |
| 9 | E1 | C10 | A bounced contact is still Active. | The 11-19 log line for P10 says "Undeliverable… <maya@tidewaterprints.example>: Recipient address rejected: User unknown". C10 (Maya Grant) is still `Active`. | Medium | Set C10 to Bounced or To verify (safe to apply). |
| 10 | F3 | P03 | Open partner with no owner. | Quill & Ink is in Negotiation and the `owner` field is empty. | High | Assign an owner (person). |
| 11 | F4 | P04 | Open partner with no contact. | Pebble Pet Co. is a Prospect and `contacts.csv` has no row for P04. The only Pebble contact (C04, bea@pebblepets.example) sits on P05. | Medium | Resolve together with finding 2. If the partners are merged, C04 would cover this (person). |

## Today's three
1. **F3 on P03:** a deal in Negotiation with a contract draft due on 11-25 has no owner, so nobody is accountable.
2. **A1 on morning-digest:** the digest skipped 11-17. Until the cause is known, the digest's "nothing needed attention" lines can't be fully trusted.
3. **B1 on P04+P05:** a duplicate Pebble partner is splitting ownership and contacts, and it is the cause of the missing contact on P04. Fix it before more activity lands on the wrong record.

## Clean partners
Four of 12 partners (P08, P09, P11 and P12) have no findings against them.

## What I did NOT do
No changes were made; this was a read-only pass. The "safe to apply" items (findings 5, 6 and 9) are proposals only. I did not merge, close, reassign or change the status of any partner.

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
