**Today and data freshness:** There is no README and no `partner-crm-steward.md` in the folder. I used the newest date in `activity.csv`, **2026-10-13**, as today. **The data is stale (rule A1):** `nightly-sync` has no log line on 10-11, 10-12 or 10-13, so everything below was computed on data that may be out of date.

I read the columns as named: `partner_id`, `name`, `status`, `priority`, `owner`, `market`, `next_step`, `next_step_date`, `last_contact` and `live_offers` in `partners.csv`. `contacts.csv` has `contact_id`, `partner_id`, `email` and `status`. `activity.csv` has `date`, `partner_id`, `source` and `summary`. Every status was already one of the five standard ones.

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | The sync skipped 3 days. | First line is 10-05, and it ran daily through 10-10. There is no line for 10-11, 10-12 or 10-13. `morning-digest` ran every day from 10-05 to 10-13. | High | Check why the sync stopped and re-run it (person). |
| 2 | B1 | P01+P07 | Probable duplicate partners. | "Nordlicht Coffee" and "Nordlicht Coffee Roasters" (the first name is the second without its last word). C01 and C02 share the domain nordlicht-coffee.example. | High | Decide whether to merge (person). |
| 3 | C1 | P04 Kestrel Outdoor | Paused partner still has live offers. | status=Paused, live_offers=1. The 10-05 e-mail says the discount code is still live and asks to extend it to November. | High | Confirm whether the partner should be reopened, or end the offer (person). |
| 4 | D4 | P02 Ferrow Ceramics | Cold: no contact for 45 days. | Priority A (14-day window). last_contact=2026-08-29 and there are no e-mails in the log. | High | Owner Jonas to reach out (person). |
| 5 | D1 | P02 Ferrow Ceramics | Open partner has no next step and no date. | status=Negotiation, next_step and next_step_date are empty. | High | Jonas to set a next step and date (person). |
| 6 | D2 | P03 Bramble & Oak | Next step is overdue. | next_step_date=2026-10-02 ("Renew affiliate terms"). Today is 10-13. | Medium | Mia to do it or reschedule (person). |
| 7 | C3 | P04 Kestrel Outdoor | last_contact is out of date. | last_contact=2026-09-12, but the newest non-bounce e-mail is 2026-10-05. | Low | Set last_contact to 2026-10-05 (safe to apply). |
| 8 | E1 | C11 Holly Avery (P09) | A bounced address is still Active. | 10-07: "Delivery failure: holly@copperleafcandles.example (mailbox does not exist)". C11 status=Active. | Medium | Set C11 to To verify or Former (safe to apply). |
| 9 | E2 | P07 Nordlicht Coffee Roasters | No usable contact. | The only contact, C02, is To verify. | Medium | Verify the contact (person). |
| 10 | E2 | P06 Saltmarsh Soap | No usable contact. | The only contact, C07, is Former. | Low | Likely moot while the partner is Lost (person). |
| 11 | D3 | P06 Saltmarsh Soap | Lost partner still has a next step. | status=Lost, next_step="Follow-up on sample feedback", dated 2026-10-28. | Medium | Clear the next step, or reconsider the status (person). |
| 12 | F1 | P07 Nordlicht Coffee Roasters | Open partner has no priority. | status=Prospect, priority is empty. | Medium | Jonas to set a priority (person). |
| 13 | F2 | P08 Halden Linen | Open partner has no market. | status=Live, market is empty. | Low | Mia to set a market (person). |

**Today's three:**
1. **Finding 1 (A1):** The sync is down, so every other finding rests on stale data. Fix this first.
2. **Finding 3 (C1, P04):** Kestrel is Paused, but its discount code is still live and the partner is asking to extend it. This is a live commercial exposure.
3. **Finding 4 (D4, P02):** Ferrow is a priority-A negotiation, silent for 45 days with no next step (finding 5).

Two of the ten partners (P05 and P10) have no findings.

**What I did not do:** I made no changes. This was a read-only pass, and the two "safe to apply" fixes (findings 7 and 8) are only proposed.

```findings
[
  {"rule": "A1", "entity": "nightly-sync", "bucket": "person"},
  {"rule": "B1", "entity": "P01+P07", "bucket": "person"},
  {"rule": "C1", "entity": "P04", "bucket": "person"},
  {"rule": "D4", "entity": "P02", "bucket": "person"},
  {"rule": "D1", "entity": "P02", "bucket": "person"},
  {"rule": "D2", "entity": "P03", "bucket": "person"},
  {"rule": "C3", "entity": "P04", "bucket": "safe"},
  {"rule": "E1", "entity": "C11", "bucket": "safe"},
  {"rule": "E2", "entity": "P07", "bucket": "person"},
  {"rule": "E2", "entity": "P06", "bucket": "person"},
  {"rule": "D3", "entity": "P06", "bucket": "person"},
  {"rule": "F1", "entity": "P07", "bucket": "person"},
  {"rule": "F2", "entity": "P08", "bucket": "person"}
]
```
