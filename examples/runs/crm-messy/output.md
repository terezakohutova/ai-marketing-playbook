**Today:** I used 2026-11-20, the newest date in `activity.csv`, because the folder has no README with an as-of date. **The data is not fresh (A1):** `nightly-sync` has no line on 2026-11-18, so everything below is computed on stale data.

**Column mapping:**
- `stage` = status
- `prio` = priority
- `account_owner` = owner
- `country` = market
- `next_action` = next step
- `due` = next step date
- `last_touch` = last_contact
- `active_offers` = live_offers
- In `contacts.csv`, `partner` = partner id and `state` = contact status.

I read dates in several formats. I mapped `live-ish (soft launch)` to Live, `Paused till Feb` to Paused, and `LOST` to Lost.

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | A1 | nightly-sync | The job has no log line on one day. | It runs daily from 2026-11-14 to 2026-11-20 but nothing is logged for 2026-11-18. `morning-digest` (first line 11-16) has no gap. | high | Check why the 18 Nov sync didn't run. (person) |
| 2 | B1 | P02+P07 | Near-same names and a shared company domain. | "Kettle & Crumb" and "Kettle and Crumb Ltd." both normalise to "kettle crumb". C02 and C03 both use `@kettleandcrumb.example`. | high | Decide whether to merge them. (person) |
| 3 | C1 | P03 Lumo Lighting | Paused but still has live offers. | Status "Paused till Feb", `active_offers`=1. | medium | Check the offer, or confirm the pause. (person) |
| 4 | C2 | P08 Bold Bikes | Live with no live offers. | Status Live, `active_offers`=0. | medium | Check the status or the offers. (person) |
| 5 | C3 | P01 | Last contact is older than the newest e-mail. | `last_touch` 12.11.2026, newest non-bounce e-mail 2026-11-19. | low | Set last_contact to 2026-11-19. (safe to apply) |
| 6 | C3 | P04 | Last contact is older than the newest e-mail. | `last_touch` 2026-10-30, inbound e-mail 2026-11-17. | low | Set last_contact to 2026-11-17. (safe to apply) |
| 7 | D1 | P10 Copperline | Open partner with no next step and no date. | Prospect, `next_action` and `due` are both empty. | medium | Set a next step and date. (person) |
| 8 | D2 | P02 | Next step date has passed. | `due` = Nov 10 2026, "Check soft-launch numbers". | medium | Update or redo the next step. (person) |
| 9 | D3 | P05 Saltwick Soap | Lost partner still has a next step. | LOST, `next_action` "Send samples again", due 2026-12-01. | low | Clear the next step. (person) |
| 10 | D4 | P09 Wren & Willow | Cold. | Priority B (window 30 days), last_touch 2026-10-15, so 36 days old. The only e-mail since then is a bounce, which isn't contact. | high | Reach out via a working contact. (person) |
| 11 | D5 | P02 | Cooling. | Priority B, last contact 2026-10-28, so 23 days old, above 22.5 and within 30. | medium | Contact them soon. (person) |
| 12 | E1 | C09 (P09) | A contact whose address bounced is still Active. | 2026-11-16 notice: Final-Recipient `jo@wrenwillow.example`. The sender `postmaster@mx…` is only the server. C09 is `Active`. | medium | Set C09 to To verify or Former. (safe to apply) |
| 13 | E2 | P05 | Every contact is Former or To verify. | C06 is Former. | low | Find a new contact, or leave it as the partner is Lost. (person) |
| 14 | E2 | P10 | Every contact is Former or To verify. | C11 is "to verify" and C12 is "former". | medium | Verify Nora Finch. (person) |
| 15 | F1 | P06 Bolt Bikes | Open partner with no priority. | Prospect, `prio` empty. | medium | Set a priority. (person) |
| 16 | F3 | P07 | Open partner with no owner. | Prospect, `account_owner` empty. | medium | Assign an owner. (person) |

**Today's three:**
1. **P09 (finding 10, with the bounce in 12):** a Negotiation partner has gone 36 days without contact, and its main contact, Jo, is unreachable. The contract is due 25 Nov, so this is the most urgent revenue risk.
2. **P02+P07 (finding 2):** a possible duplicate with no owner on one record. It is also behind on its next step and cooling. Settle which record is real before anyone contacts them, so two owners don't pitch the same company.
3. **Nightly-sync gap (finding 1):** the stale data affects everything above. Fix this first so the other findings can be trusted.

**Clean partners:** none. All 10 partners have at least one finding.

**What I did NOT do:** no changes were made. This was a read-only pass, and every "safe to apply" fix is only proposed.

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
  {"rule": "E2", "entity": "P05", "bucket": "person"},
  {"rule": "E2", "entity": "P10", "bucket": "person"},
  {"rule": "F1", "entity": "P06", "bucket": "person"},
  {"rule": "F3", "entity": "P07", "bucket": "person"}
]
```
