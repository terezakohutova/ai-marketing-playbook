**Today:** I used 2026-11-20, the newest date in `activity.csv`. There is no README with an as-of date, so I did not use the system clock. **The data is not fully fresh (rule A1):** `nightly-sync` has no log line on 2026-11-18, so everything below rests on a sync history with a gap.

**Column mapping.** I mapped the columns by meaning.
- `stage` is status, `prio` is priority, `account_owner` is owner and `country` is market.
- `next_action` is next step, `due` is next step date, `last_touch` is last contact and `active_offers` is live offers.
- In `contacts.csv`, `partner` is the partner id and `state` is the contact status.
- Dates came in `dd.mm.yyyy`, `Mon dd yyyy` and ISO formats, and I read them all.

**Status mapping.**
- "live-ish (soft launch)" (P02) is Live.
- "Paused till Feb" (P03) is Paused.
- "LOST" (P05) is Lost.
- "prospect" (P10) is Prospect.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | No run logged on 2026-11-18 | The job has lines on 11-14, 15, 16, 17, 19 and 20, but none on 11-18. The digest ran that day. | High | Check why the sync skipped that day and re-run it (person) |
| 2 | B1 | P02+P07 | Likely duplicate partner | "Kettle & Crumb" and "Kettle and Crumb Ltd." are the same name after normalisation. Both contacts use `@kettleandcrumb.example` (C02, C03). | High | Confirm and merge, or keep both (person) |
| 3 | E1 | C09 (P09) | Contact whose address bounced is still Active | On 2026-11-16, a `Returned mail` line gave `Final-Recipient: jo@wrenwillow.example`, status 5.1.1 (no such user). The first address, `postmaster@mx...`, is only the sending server. C09 is `Active`. | Medium | Set C09 to To verify or Former (safe to apply) |
| 4 | D4 | P09 Wren & Willow | Cold Negotiation partner | Priority B (30-day window). `last_contact` is 2026-10-15, so the age is 36 days. The only newer log line is the bounce, which does not count as contact. | High | Owner Mia to reach out via Kim Willow (C10) (person) |
| 5 | C1 | P03 Lumo Lighting | Paused partner with live offers | Status "Paused till Feb", `active_offers` = 1. The note says it is paused until the February relaunch. | Medium | Confirm whether the offer should be closed or the status changed (person) |
| 6 | C2 | P08 Bold Bikes | Live partner with 0 live offers | Status Live, `active_offers` = 0 | Medium | Check whether it is really Live (person) |
| 7 | C3 | P01 | Last contact is stale | `last_touch` is 2026-11-12. An e-mail on 2026-11-19 confirmed a call. | Low | Set last contact to 2026-11-19 (safe to apply) |
| 8 | C3 | P04 | Last contact is stale | `last_touch` is 2026-10-30. An inbound e-mail on 2026-11-17 asked for a terms extension. | Low | Set last contact to 2026-11-17 (safe to apply) |
| 9 | D2 | P02 Kettle & Crumb | Next step overdue | "Check soft-launch numbers", due Nov 10 2026, which is before 2026-11-20 | Medium | Owner Jonas to reschedule or complete the step (person) |
| 10 | D5 | P02 | Cooling | Priority B (30-day window), last contact 2026-10-28, so the age is 23 days. That is within the window and above 22.5 days (three quarters of it). | Low | Owner to make contact soon (person) |
| 11 | D3 | P05 Saltwick Soap | Lost partner still has a next step | "Send samples again", due 2026-12-01. The note says "Went with another reseller". | Medium | Clear the next step (person) |
| 12 | E2 | P05 | All contacts unusable | C06 is `Former`, and it is the only contact. | Low | Nothing needed if P05 stays Lost (person) |
| 13 | D1 | P10 Copperline | Open partner with no next step or date | Both `next_action` and `due` are empty. The status is "prospect" and the priority is A. | High | Owner Jonas to set a next step and date (person) |
| 14 | E2 | P10 | All contacts unusable | C11 is `to verify` and C12 is `former` | Medium | Verify Nora Finch (C11) or find a new contact (person) |
| 15 | F1 | P06 Bolt Bikes | Open partner with no priority | `prio` is empty | Low | Set a priority (person) |
| 16 | F3 | P07 Kettle and Crumb Ltd. | Open partner with no owner | `account_owner` is empty | Medium | Assign an owner, ideally together with the merge decision (person) |

I did not flag "Bold Bikes" and "Bolt Bikes" as duplicates. They differ by a typo in a word under 5 letters, which the name rule does not allow, and their domains differ.

## Today's three
1. **A1, nightly-sync gap.** It makes every other finding less reliable, so check it first.
2. **P09 (D4 with E1).** It is a Negotiation partner that has gone cold, and its main contact address is dead. Kim Willow (C10) is the only reachable contact.
3. **P02+P07 (B1).** A duplicate partner affects ownership, next steps and the P02 overdue and cooling findings, so decide it before working on either record.

P10 (D1, with an empty next step on a priority-A prospect) is a close fourth.

## Clean partners
No partner was fully clean: all 10 have at least one finding.

## What I did NOT do
No changes were made. This was a read-only pass. The "safe to apply" items (findings 3, 7 and 8) are proposals only.

```findings
[
  {"rule": "A1", "entity": "nightly-sync", "bucket": "person"},
  {"rule": "B1", "entity": "P02+P07", "bucket": "person"},
  {"rule": "E1", "entity": "C09", "bucket": "safe"},
  {"rule": "D4", "entity": "P09", "bucket": "person"},
  {"rule": "C1", "entity": "P03", "bucket": "person"},
  {"rule": "C2", "entity": "P08", "bucket": "person"},
  {"rule": "C3", "entity": "P01", "bucket": "safe"},
  {"rule": "C3", "entity": "P04", "bucket": "safe"},
  {"rule": "D2", "entity": "P02", "bucket": "person"},
  {"rule": "D5", "entity": "P02", "bucket": "person"},
  {"rule": "D3", "entity": "P05", "bucket": "person"},
  {"rule": "E2", "entity": "P05", "bucket": "person"},
  {"rule": "D1", "entity": "P10", "bucket": "person"},
  {"rule": "E2", "entity": "P10", "bucket": "person"},
  {"rule": "F1", "entity": "P06", "bucket": "person"},
  {"rule": "F3", "entity": "P07", "bucket": "person"}
]
```
