**Today:** I used 2026-11-20, the newest date in `activity.csv`. There is no README and so no as-of date. **The data is not fresh (rule A1):** `nightly-sync` has no log line on 2026-11-18, so everything below is computed on possibly stale data.

**Column mapping:** `stage` is status, `prio` is priority, `account_owner` is owner, `country` is market, `next_action` is next step, `due` is next step date, `last_touch` is last contact, `active_offers` is live offers, and `partner` in contacts is the partner id. Contact `state` is compared case-insensitively. Dates were read as `dd.mm.yyyy`, `Mon dd yyyy` and ISO.

**Status mapping:**
- P02 "live-ish (soft launch)" is Live.
- P03 "Paused till Feb" is Paused.
- P05 "LOST" is Lost.
- P10 "prospect" is Prospect.

| # | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | The job has no run on one day between its first line and today. | Lines exist for 11-14, 15, 16, 17, 19 and 20, but none for 11-18. `morning-digest` started 11-16 and has a line every day since. | high | Check why the 11-18 run is missing and re-run it (person). |
| 2 | B1 | P02+P07 | Near-same names, and a shared contact domain. | "Kettle & Crumb" and "Kettle and Crumb Ltd." both normalise to "kettle crumb". C02 and C03 are both @kettleandcrumb.example. | high | Decide whether to merge. P07 is a Prospect and P02 is Live (person). |
| 3 | D4 | P09 Wren & Willow | Cold. | Priority B (30-day window). `last_touch` is 2026-10-15 and the only log e-mail is a bounce, which doesn't count as contact. That is 36 days. | high | Reach out through a working address, then update the status or next step (person). |
| 4 | E1 | C09 (P09) | A bounced address is still Active. | The 11-16 notice says Final-Recipient: jo@wrenwillow.example, 5.1.1 no such user. C09 Jo Wren is `Active`. The postmaster address is only the sending server. | medium | Set C09 to To verify or Former (safe to apply). |
| 5 | C1 | P03 Lumo Lighting | Paused with live offers. | Status "Paused till Feb", `active_offers` 1. | medium | Check whether the offer should be ended or the status changed (person). |
| 6 | C2 | P08 Bold Bikes | Live with no live offers. | Status Live, `active_offers` 0. | medium | Check the offer count or the status (person). |
| 7 | C3 | P01 | Last contact is older than the newest e-mail. | `last_touch` 12.11.2026; e-mail on 2026-11-19 ("Lena confirmed a call"). | low | Set last contact to 2026-11-19 (safe to apply). |
| 8 | C3 | P04 | Last contact is older than the newest e-mail. | `last_touch` 2026-10-30; e-mail on 2026-11-17 (Ola asked for an extension). | low | Set last contact to 2026-11-17 (safe to apply). |
| 9 | D1 | P10 Copperline | Open partner with no next step and no date. | Prospect; `next_action` and `due` are both empty. | medium | Set a next step and date (person). |
| 10 | D2 | P02 | Next step date has passed. | "Check soft-launch numbers", due Nov 10 2026, which is before 2026-11-20. | medium | Complete the step or set a new date (person). |
| 11 | D3 | P05 Saltwick Soap | Lost partner still has a next step. | Status LOST; next step "Send samples again", due 2026-12-01. The note says "Went with another reseller". | low | Clear the next step (person). |
| 12 | D5 | P02 | Cooling. | Priority B (30-day window, 22.5 days is three quarters). Last contact 2026-10-28, which is 23 days ago. | low | Contact them soon (person). |
| 13 | E2 | P10 | Every contact is unverified or former. | C11 "to verify", C12 "former". | medium | Verify Nora Finch's address or add a new contact (person). |
| 14 | E2 | P05 | Every contact is unverified or former. | C06 Grace Lowe is `Former`. | low | Likely moot because the partner is Lost; a person decides (person). |
| 15 | F1 | P06 Bolt Bikes | Open partner with no priority. | Prospect, `prio` empty. | low | Assign a priority (person). |
| 16 | F3 | P07 | Open partner with no owner. | Prospect, `account_owner` empty. | medium | Assign an owner (person). |

I considered P06 Bolt Bikes and P08 Bold Bikes as duplicates and ruled it out. "bolt" and "bold" are under 5 letters, where no typo is allowed, and their domains differ.

**Today's three:**
1. **A1, the missing `nightly-sync` run.** The other findings sit on data that may be stale, so this comes first.
2. **B1, P02+P07.** A merge decision affects the Live partner, its overdue step (D2) and its cooling status (D5).
3. **D4, P09.** It is a Negotiation partner that has gone cold. Its only known contact address is dead, and "Send contract" is due 2026-11-25.

**Clean partners:** none of the 10 partners was clean.

**What I did NOT do:** I made no changes. This was a read-only pass. The "safe to apply" items (E1, C3) are proposals only and nothing was applied.

```findings
[
  {"rule": "A1", "entity": "nightly-sync", "bucket": "person"},
  {"rule": "B1", "entity": "P02+P07", "bucket": "person"},
  {"rule": "D4", "entity": "P09", "bucket": "person"},
  {"rule": "E1", "entity": "C09", "bucket": "safe"},
  {"rule": "C1", "entity": "P03", "bucket": "person"},
  {"rule": "C2", "entity": "P08", "bucket": "person"},
  {"rule": "C3", "entity": "P01", "bucket": "safe"},
  {"rule": "C3", "entity": "P04", "bucket": "safe"},
  {"rule": "D1", "entity": "P10", "bucket": "person"},
  {"rule": "D2", "entity": "P02", "bucket": "person"},
  {"rule": "D3", "entity": "P05", "bucket": "person"},
  {"rule": "D5", "entity": "P02", "bucket": "person"},
  {"rule": "E2", "entity": "P10", "bucket": "person"},
  {"rule": "E2", "entity": "P05", "bucket": "person"},
  {"rule": "F1", "entity": "P06", "bucket": "person"},
  {"rule": "F3", "entity": "P07", "bucket": "person"}
]
```
