**Today:** 2026-11-20. The folder has no README, so I used the newest date in `activity.csv`. Data freshness (A1): `morning-digest` has no log line on 2026-11-17, so there is a gap in the log. `nightly-sync` ran every day from 2026-11-14 to 2026-11-20, so the CRM data itself is current. Only the digest is affected, and it may have skipped a day of alerts.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | morning-digest | No run logged on one day | Log runs 2026-11-14 to 2026-11-20; digest has lines for 14, 15, 16, 18, 19, 20 but none for 17 | high | Check why the digest skipped 11-17 and whether alerts were lost (person) |
| 2 | E1 | C10 (P10 Tidewater Prints) | Contact's address bounced but contact is still Active | 2026-11-19 P10 email: "Undeliverable ... <maya@tidewaterprints.example>: Recipient address rejected: User unknown"; C10 Maya Grant status Active | high | Set C10 to Bounced (safe to apply). Leo Grant (C09) is the remaining live contact for P10. |
| 3 | B2 | C13 | Contact points at a partner that doesn't exist | C13 Iris Holt (northgatefoods.example) has partner_id P14; partners run P01 to P12 | high | Find the right partner or create the partner record (person; nothing creates partners automatically) |
| 4 | B1 | P04+P05 | Probable duplicate partner | "Pebble Pet Co." and "Pebble Pets" normalise to "pebble pet" and "pebble pets", one character apart. P04 Prospect/Ravi, P05 Paused/Ines, both UK, priority C. | high | Decide whether to merge. If yes, keep one record and move contact C04 (Bea Collins). Merging needs a person's yes. |
| 5 | C2 | P02 Harbor Kitchen Supply | Live with no live offers | status Live, live_offers 0 | high | Either an offer is missing or the status is wrong (person) |
| 6 | F4 | P04 Pebble Pet Co. | Open partner with no contact | No contacts row has partner_id P04; the only Pebble contact (C04) sits on P05 | medium | Add a contact, or resolve with the P04/P05 duplicate decision (person) |
| 7 | F3 | P03 Quill & Ink | Open partner with no owner | owner empty; status Negotiation; contract draft due 2026-11-25 | medium | Assign an owner (person) |
| 8 | D5 | P01 Alder Bike Works | Cooling, priority A | last_contact 2026-11-09 = 11 days; the A window is 14 days, three quarters of it is 10.5; no non-bounce email in the log | medium | Reach out before it goes cold on 11-23 (person) |
| 9 | D5 | P06 Marlow Outdoor Ltd | Cooling, priority B | last_contact 2026-10-26 = 25 days; the B window is 30 days, three quarters of it is 22.5; no email in the log | medium | Contact them soon, and note the affiliate payout review is due 12-05 (person) |
| 10 | C3 | P02 Harbor Kitchen Supply | last_contact is out of date | last_contact 2026-11-15, but 2026-11-17 email "Fatima asked when the spring promo will go live" | low | Set last_contact to 2026-11-17 (safe to apply) |
| 11 | C3 | P07 Alder Coffee | last_contact is out of date | last_contact 2026-10-20, but 2026-11-16 email "Courier delivery failed twice; Sanne asked us to re-send the samples". It has no email address, so it is not a bounce but real contact. | low | Set last_contact to 2026-11-16 (safe to apply). Sanne also asked for a sample re-send, which is worth acting on. |

```findings
[
  {"rule": "A1", "entity": "morning-digest", "bucket": "person"},
  {"rule": "E1", "entity": "C10", "bucket": "safe"},
  {"rule": "B2", "entity": "C13", "bucket": "person"},
  {"rule": "B1", "entity": "P04+P05", "bucket": "person"},
  {"rule": "C2", "entity": "P02", "bucket": "person"},
  {"rule": "F4", "entity": "P04", "bucket": "person"},
  {"rule": "F3", "entity": "P03", "bucket": "person"},
  {"rule": "D5", "entity": "P01", "bucket": "person"},
  {"rule": "D5", "entity": "P06", "bucket": "person"},
  {"rule": "C3", "entity": "P02", "bucket": "safe"},
  {"rule": "C3", "entity": "P07", "bucket": "safe"}
]
```

## Today's three
1. **The Pebble Pet Co. / Pebble Pets duplicate (P04+P05, with F4).** Two records for one company mean split history, a paused record next to an open one, and the open one has no contact. It is also the only one that needs a merge decision.
2. **P02 Harbor Kitchen Supply: Live with 0 offers (C2).** A Live partner with nothing live is a status or sync error, and Fatima is already asking about the spring promo.
3. **C10 bounced address and the C13 orphan contact.** Maya's address is confirmed dead but still marked Active, so outreach will keep failing. The fix is a one-field safe change. C13 points at a partner that doesn't exist, so that contact is unreachable from any partner.

## Clean partners
Of 12 partners, 4 were clean; the other 8 are touched by at least one finding.

## What I did NOT do
No changes were made. This was a read-only pass; the "safe" items are proposals that wait for a person to apply them. I did not have the pattern doc `partner-crm-steward.md`, so I worked from the rules in my instructions only.
