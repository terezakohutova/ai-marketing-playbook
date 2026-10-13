**Today:** 2026-11-20. There is no README with an as-of date, so I took the newest date in `activity.csv`. The system clock says 2026-10-14, which I ignored because the log runs to November. **The data is stale (rule A1):** `nightly-sync` has no log line for 2026-11-18. Everything below was computed on data that missed one sync.

**Column mapping:**
- `stage` is status, `prio` is priority, `account_owner` is owner, and `country` is market.
- `next_action` is next step and `due` is next step date.
- `last_touch` is last contact and `active_offers` is live offers.
- In `contacts.csv`, `partner` is the partner id, `e-mail` is the address, and `state` is contact status.
- `partner-crm-steward.md` doesn't exist in the folder, so I worked from `agent.md` only.

**Status mapping:**
- `live-ish (soft launch)` (P02) is read as Live.
- `Paused till Feb` (P03) is read as Paused.
- `LOST` (P05) is read as Lost.
- `prospect` (P10) is read as Prospect.

## Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | Missing run on one day | First line 2026-11-14. Lines exist for 14, 15, 16, 17, 19 and 20 Nov, but none for 18 Nov. `morning-digest` has no gap (16 to 20 Nov). | high | Check why the run didn't happen, then re-run the sync (person) |
| 2 | B1 | P02+P07 | Likely duplicate partners | "Kettle & Crumb" and "Kettle and Crumb Ltd." are equal after normalisation. Contacts C02 and C03 share the domain kettleandcrumb.example. | high | Decide whether to merge. P07 has no owner and P02 is a soft launch (person) |
| 3 | C1 | P03 | Paused partner with live offers | Status "Paused till Feb", `active_offers`=1 | medium | Confirm whether the offer should end, or whether the status is wrong (person) |
| 4 | C2 | P08 | Live partner with no live offers | Status Live, `active_offers`=0 | medium | Check whether the status should change, or whether the offer count is wrong (person) |
| 5 | C3 | P01 | Last contact is out of date | `last_touch` 12.11.2026, but there is an email on 2026-11-19 ("Lena confirmed a call…") | low | Set last contact to 2026-11-19 (safe to apply) |
| 6 | C3 | P04 | Last contact is out of date | `last_touch` 2026-10-30, but there is an inbound email on 2026-11-17 (Ola asked for an extension) | low | Set last contact to 2026-11-17 (safe to apply) |
| 7 | D1 | P10 | Open partner with no next step or date | Next step and `due` are both empty. The note says "Met at the trade fair". | medium | Owner Jonas to set a next step, for example follow-up on the catalogue Nora is forwarding to her buyer (person) |
| 8 | D2 | P02 | Next step date has passed | `due` "Nov 10 2026" is before 2026-11-20 | medium | Owner Jonas to update the next step or date (person) |
| 9 | D3 | P05 | Lost partner still has a next step | Status LOST, next step "Send samples again" (due 2026-12-01). The note says "Went with another reseller". | low | Clear the next step (person) |
| 10 | D4 | P09 | Cold: no recent contact | Priority B (30-day window). `last_touch` is 2026-10-15, which is 36 days ago. The only email in the log is a bounce, which doesn't count as contact. | high | Owner Mia to reach out through a working contact (Kim) (person) |
| 11 | D5 | P02 | Cooling | Priority B (30-day window). `last_touch` is 2026-10-28, which is 23 days ago, above 22.5 (three quarters of the window). No emails in the log. | low | Owner Jonas to make contact (person) |
| 12 | E1 | C09 | Contact whose address bounced is still Active | On 2026-11-16 a "Returned mail… no such user" notice with `Final-Recipient: jo@wrenwillow.example` (not the postmaster). C09 Jo Wren is `Active`. | medium | Set C09 to `To verify` (safe to apply) |
| 13 | E2 | P10 | No usable contact | C11 is `to verify` and C12 is `former` | medium | Verify Nora Finch, or find a new contact (person) |
| 14 | F1 | P06 | Open partner with no priority | Prospect, `prio` empty | low | Owner Mia to set a priority (person) |
| 15 | F3 | P07 | Open partner with no owner | Prospect, `account_owner` empty | medium | Assign an owner, ideally together with the B1 duplicate decision (person) |

**Not flagged on purpose:**
- Bolt Bikes (P06) and Bold Bikes (P08) are different companies.
- P09 isn't E2, because Kim Willow (C10) is still Active.
- P04's next step date of 14.1.2027 fits Ola's request for an extension to mid-January.
- No B2 or B3 findings: every contact points to an existing partner, and no ids are repeated.
- No F2 or F4 findings: every open partner has a market and at least one contact.

## Today's three
1. **#1, A1 `nightly-sync` gap:** it makes every other result less reliable, so check it first.
2. **#10, D4 on P09 (Wren & Willow):** a Negotiation partner has been cold for 36 days with a contract pending. Its main contact (Jo) is bouncing, so the relationship is at risk. Reach Kim, and also apply the E1 fix (#12).
3. **#2, B1 on P02+P07 (Kettle & Crumb):** a possible duplicate with no owner on one record, and a soft launch on the other. Resolve it before anyone contacts them from either record.

## Clean partners
None of the 10 partners was clean: every one has at least one finding.

## What I did NOT do
No changes were made. This was a read-only pass. The "safe to apply" items (#5, #6, #12) are proposals only. I changed no human-owned fields, merged nothing and created no partners.

```findings
[
  {"rule": "A1", "entity": "nightly-sync", "bucket": "person"},
  {"rule": "B1", "entity": "P02+P07", "bucket": "person"},
  {"rule": "C1", "entity": "P03", "bucket": "person"},
  {"rule": "C2", "entity": "P08", "bucket": "person"},
  {"rule": "C3", "entity": "P01", "bucket": "safe"},
  {"rule": "C3", "entity": "P04", "bucket": "safe"},
  {"rule": "D1", "entity": "P10", "bucket": "person"},
  {"rule": "D2", "entity": "P02", "bucket": "person"},
  {"rule": "D3", "entity": "P05", "bucket": "person"},
  {"rule": "D4", "entity": "P09", "bucket": "person"},
  {"rule": "D5", "entity": "P02", "bucket": "person"},
  {"rule": "E1", "entity": "C09", "bucket": "safe"},
  {"rule": "E2", "entity": "P10", "bucket": "person"},
  {"rule": "F1", "entity": "P06", "bucket": "person"},
  {"rule": "F3", "entity": "P07", "bucket": "person"}
]
```
