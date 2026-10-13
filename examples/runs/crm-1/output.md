**Today and freshness.** No README with an as-of date, so "today" = 2026-10-13, the newest date in `activity.csv`. The data is NOT fully fresh (rule A1): `nightly-sync` has no log line for 2026-10-11, 2026-10-12 or 2026-10-13, so everything below is computed on data that may be up to 3 days stale. `morning-digest` ran every day.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | Job missing on 3 days | Log covers 2026-10-05 to 2026-10-13; nightly-sync lines exist for 10-05..10-10 only; none for 10-11, 10-12, 10-13 | high | Check why the sync stopped after 10-10 and rerun it (person) |
| 2 | B1 | P01+P07 | Probable duplicate | "Nordlicht Coffee" vs "Nordlicht Coffee Roasters" (words added at the end); contacts C01 and C02 both on nordlicht-coffee.example | high | Decide whether to merge; P01 is Live (A, 2 offers), P07 is Prospect (no priority) (person) |
| 3 | C1 | P04 | Paused but has live offers | status Paused, live_offers 1 | high | Decide: end the offer or reactivate the partner (person) |
| 4 | C3 | P04 | last_contact is stale | last_contact 2026-09-12, but non-bounce e-mail on 2026-10-05 (Anna asks to extend the discount code to November) | medium | Set last_contact to 2026-10-05 (safe to apply) |
| 5 | D1 | P02 | Open partner without next step or date | Negotiation, next_step and next_step_date empty | high | Owner Jonas to set a next step and date (person) |
| 6 | D4 | P02 | Cold | Priority A (14-day window), effective last contact 2026-08-29 = 45 days | high | Owner to re-engage or downgrade; see D1 (person) |
| 7 | D2 | P03 | Next step overdue | "Renew affiliate terms" dated 2026-10-02, today 10-13 | medium | Owner Mia to do it or reschedule (person) |
| 8 | D3 | P06 | Lost partner still has a next step | status Lost, next step "Follow-up on sample feedback" 2026-10-28 | low | Clear the next step or reconsider the status (person) |
| 9 | E1 | C11 | Bounced contact still Active | 2026-10-07: delivery failure for holly@copperleafcandles.example (mailbox does not exist); C11 status Active | medium | Set C11 to To verify or Former (safe to apply) |
| 10 | E2 | P07 | No usable contact | only contact C02 is To verify | medium | Verify Tobias Brandt or add a contact (person) |
| 11 | E2 | P06 | No usable contact | only contact C07 is Former (partner is Lost, so low impact) | low | Nothing needed if it stays Lost (person) |
| 12 | F1 | P07 | Open partner without priority | priority empty, status Prospect | medium | Owner to set priority (person) |
| 13 | F2 | P08 | Open partner without market | market empty, status Live | medium | Owner to set market (person) |

## Today's three
1. **A1, the stopped nightly sync.** It affects trust in every other number, and it is the cheapest to check.
2. **B1 / P01+P07, the likely duplicate.** Live partner A with 2 offers, and a second Prospect record at the same company with its own owner (Jonas vs Mia) and a pitch under way. Risk of two people pitching the same company.
3. **P02 (D1 + D4).** Priority A deal in Negotiation, 45 days without contact and no next step: the most likely to be lost. (P04, Paused with a live offer and an unanswered partner request, is next.)

## Clean partners
2 of 10 partners (P05 and P10) had no findings.

## What I did NOT do
No changes were made; this was a read-only pass. Items marked "safe to apply" (4 and 9) are proposals only. No duplicates were merged and no statuses changed.

```findings
[
  {"rule": "A1", "entity": "nightly-sync", "bucket": "person"},
  {"rule": "B1", "entity": "P01+P07", "bucket": "person"},
  {"rule": "C1", "entity": "P04", "bucket": "person"},
  {"rule": "C3", "entity": "P04", "bucket": "safe"},
  {"rule": "D1", "entity": "P02", "bucket": "person"},
  {"rule": "D4", "entity": "P02", "bucket": "person"},
  {"rule": "D2", "entity": "P03", "bucket": "person"},
  {"rule": "D3", "entity": "P06", "bucket": "person"},
  {"rule": "E1", "entity": "C11", "bucket": "safe"},
  {"rule": "E2", "entity": "P07", "bucket": "person"},
  {"rule": "E2", "entity": "P06", "bucket": "person"},
  {"rule": "F1", "entity": "P07", "bucket": "person"},
  {"rule": "F2", "entity": "P08", "bucket": "person"}
]
```
