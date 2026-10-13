**Today:** I used 2027-01-15, the newest date in `activity.csv`. There is no README with an as-of date. The data is fresh under rule A1: `nightly-sync` and `morning-digest` both have a log line every day from 2027-01-09 to 2027-01-15, with no gaps.

I mapped columns by name, and none were renamed. The one bounce in the log is the P03 line, which names `Theo.Marsh@cobaltcycling.example` as the failed address.

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | B1 | P01+P02 | Likely duplicate partners | "Brightwater GmbH" and "Brightwater" are the same name once "gmbh" is dropped. Their contacts C01 and C02 share the domain `brightwater.example`. The two records have different status, market and owner (Live/DE/Ana vs Prospect/AT/Lukas). | High | A person decides whether to merge. Nothing is merged automatically (person). |
| 2 | B3 | P06 | Partner id appears on two rows | The P06 "Meadowlark Games" row appears twice with identical values. | Medium | A person removes the duplicate row (person). |
| 3 | C1 | P04 | Lost partner still has live offers | Status Lost, `live_offers` = 1. | High | A person checks whether the offer is really still live and ends it, or corrects the status (person). |
| 4 | D4 | P03 | Cold partner | Priority B, window 30 days. `last_contact` is 2026-12-10, and the only e-mail in the log is a bounce. That makes 36 days. | Medium | The owner (Ana) re-engages. The bounced contact needs replacing first (person). |
| 5 | D4 | P05 | Cold partner | Priority C, window 60 days. `last_contact` is 2026-11-01, which is 75 days ago. | Medium | The owner (Ana) re-engages or reviews the priority (person). |
| 6 | D1 | P03 | Open partner has a next step but no date | Live, next step "Review Q4 numbers", `next_step_date` empty. | Medium | The owner sets a date (person). |
| 7 | D2 | P06 | Next step is overdue | `next_step_date` 2027-01-08 is before 2027-01-15, for "Holiday recap". | Medium | The owner (Lukas) completes the step or reschedules it (person). |
| 8 | E1 | C03 (P03) | Contact bounced but is still Active | The 2027-01-13 notice says "address not found" for `Theo.Marsh@cobaltcycling.example`. C03 has `theo.marsh@cobaltcycling.example` and status Active. | Medium | Set C03 to To verify or Former. Only one answer is correct (safe to apply). |
| 9 | E2 | P05 | No usable contact | C06 is To verify and C07 is Former. | Medium | A person finds a valid contact (person). |
| 10 | E2 | P02 | No usable contact | The only contact, C02, is To verify. | Low | A person verifies C02 (person). |
| 11 | F2 | P05 | Open partner has no market | Negotiation, `market` empty. | Low | A person sets the market (person). |

**Today's three**
1. **B1 P01+P02:** a duplicate Brightwater record splits the history and ownership of a Live A-priority partner. Fix it before anyone acts on either record.
2. **C1 P04:** a Lost partner with a live offer is a contradiction that may have a real commercial effect.
3. **D4 P05:** a Negotiation partner with 75 days of silence and no valid contact (E2) is the deal most at risk of being lost. P03, which went cold and has a bounced contact, is next.

Three of the nine partners (P07, P08 and P09) had no findings.

**What I did NOT do:** I made no changes. This was a read-only pass, and the safe fix for C03 is only proposed.

```findings
[
  {"rule": "B1", "entity": "P01+P02", "bucket": "person"},
  {"rule": "B3", "entity": "P06", "bucket": "person"},
  {"rule": "C1", "entity": "P04", "bucket": "person"},
  {"rule": "D4", "entity": "P03", "bucket": "person"},
  {"rule": "D4", "entity": "P05", "bucket": "person"},
  {"rule": "D1", "entity": "P03", "bucket": "person"},
  {"rule": "D2", "entity": "P06", "bucket": "person"},
  {"rule": "E1", "entity": "C03", "bucket": "safe"},
  {"rule": "E2", "entity": "P05", "bucket": "person"},
  {"rule": "E2", "entity": "P02", "bucket": "person"},
  {"rule": "F2", "entity": "P05", "bucket": "person"}
]
```
