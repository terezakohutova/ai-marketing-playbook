**Today:** There is no README in the folder, so I used the newest date in `activity.csv`, 2026-10-13. **The data is stale (rule A1):** `nightly-sync` has no log line for 2026-10-11, 2026-10-12 or 2026-10-13, so `live_offers` and `last_contact` may be out of date. Everything below rests on that data.

Column mapping: the columns matched the expected names, so no remapping was needed. The only e-mail lines in `activity.csv` have source `email`. Bounce handling: the line for P09 contains "Delivery failure" and names holly@copperleafcandles.example, which is therefore the bounced address.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | The job has no log line for 3 days. | First line 2026-10-05, then runs through 10-10. Nothing on 10-11, 10-12 or 10-13. `morning-digest` has a line every day from 10-05 to 10-13. | High | Check why the sync stopped and re-run it (person). |
| 2 | B1 | P01+P07 | Probable duplicate partner. | "Nordlicht Coffee" and "Nordlicht Coffee Roasters" differ only by words added at the end. Contacts C01 (lena@nordlicht-coffee.example) and C02 (tobias@nordlicht-coffee.example) share the domain nordlicht-coffee.example. | High | Decide whether to merge (person). |
| 3 | C1 | P04 Kestrel Outdoor | Paused partner with a live offer. | Status Paused, `live_offers`=1. The 10-05 e-mail says the discount code is still live and asks for an extension to November. | High | Decide whether to reactivate the partner or end the offer (person). |
| 4 | D4 | P02 Ferrow Ceramics | Cold: no contact for 45 days on a priority A partner, window 14. | `last_contact` 2026-08-29. No e-mails in the log. | High | Re-engage; the owner Jonas decides (person). |
| 5 | D1 | P02 Ferrow Ceramics | Open partner with no next step and no date. | Negotiation; `next_step` and `next_step_date` are empty. | High | Jonas sets a next step and date (person). |
| 6 | D2 | P03 Bramble & Oak | Next step is overdue. | "Renew affiliate terms", date 2026-10-02, today 10-13. | Medium | Mia does it or reschedules (person). |
| 7 | C3 | P04 Kestrel Outdoor | `last_contact` is behind the newest e-mail. | `last_contact` 2026-09-12; newest non-bounce e-mail 2026-10-05. | Low | Set `last_contact` to 2026-10-05 (safe to apply). |
| 8 | E1 | C11 Holly Avery (P09) | Bounced address still Active. | 2026-10-07 "Delivery failure: holly@copperleafcandles.example (mailbox does not exist)". C11 status is Active. | Medium | Set C11 to To verify (safe to apply). |
| 9 | E2 | P07 Nordlicht Coffee Roasters | Its only contact is unverified. | C02 Tobias Brandt is To verify. | Medium | Verify the contact (person). |
| 10 | E2 | P06 Saltmarsh Soap | Its only contact is Former. | C07 Grace Lowe is Former. | Low | Find a new contact, or leave it as the partner is Lost (person). |
| 11 | D3 | P06 Saltmarsh Soap | Lost partner still has a next step. | Next step "Follow-up on sample feedback", date 2026-10-28. | Medium | Clear the next step, or reconsider the Lost status (person). |
| 12 | F1 | P07 Nordlicht Coffee Roasters | Open partner with no priority. | `priority` is empty (Prospect). | Medium | Set a priority (person). |
| 13 | F2 | P08 Halden Linen | Open partner with no market. | `market` is empty (Live). | Low | Set a market (person). |

## Today's three
1. **Finding 1, the `nightly-sync` gap.** Every other check depends on fresh data, so fix it first.
2. **Finding 3, P04.** A paused partner has a live discount code, and the partner is asking to extend it, so it needs a decision now.
3. **Finding 2, P01 and P07.** If these are duplicates, any other work on either record may be wasted. This also settles findings 9 and 12, which concern P07.

P02 (findings 4 and 5) is the next priority. It is a priority A negotiation that has gone cold with no next step.

## Clean partners
Two of the 10 partners (P05 and P10) had no findings.

## What I did NOT do
No changes were made; this was a read-only pass. The "safe to apply" items (findings 7 and 8) are proposals only. I did not merge, close or change the status of any partner.

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
