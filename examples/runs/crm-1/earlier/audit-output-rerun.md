# Earlier run: crm-steward, second attempt (previous spec)

**How this was produced (2026-10-13, before the rule ids and the findings block existed).**
A fresh Claude Sonnet agent got the then-current body of the crm-steward agent as its
instructions, read-only tools (Read, Grep, Glob), and a folder holding only
`partner-crm-steward.md` plus the CSVs and README of [`crm-1`](../../../crm/crm-1/). Everything
under the line is its output, unedited. By hand, it missed one finding the rules imply:
P06's only contact is `Former` (now rule E2). It has no machine-readable findings block, so
the current scorer can't score it; it is kept to show run-to-run variance.

---

## Partner CRM audit

**Today:** 2026-10-13, taken from the as-of date in `exports/README.md`. The data is **not fully fresh**. The nightly sync has no log line for 2026-10-11, 2026-10-12 or 2026-10-13, so sections B to F below are computed on data at least 3 days stale (last sync 2026-10-10).

### Findings

| ID | Section | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| F01 | A | All | Nightly sync stopped. The morning digest kept running and reported "nothing needed attention" on stale data. | `nightly-sync` last logged 2026-10-10 ("10 partners synced"). It has no line for 10-11, 10-12 or 10-13. `morning-digest` has a line for every day 10-05 to 10-13, including 10-11 and 10-12 "nothing needed attention". | High | Restart the sync and re-check the digests for 10-11 and 10-12 (person). |
| F02 | A / C | P04 Kestrel Outdoor | The sync and digest also missed this partner's 10-05 mail, so `last_contact` is stale. It would show as cold when it is not. | `last_contact` = 2026-09-12. `activity.csv` has an e-mail from P04 on 2026-10-05, so the real gap is 8 days, not 31 (B-priority cadence is 30 days). | Medium | Set `last_contact` to 2026-10-05, which has exactly one correct value (safe to apply, still list it). |
| F03 | B | P01 Nordlicht Coffee / P07 Nordlicht Coffee Roasters | Probable duplicate partner. P01 is Live with 2 offers and priority A. P07 is a Prospect with no priority and a different owner (Jonas). | Names differ only by "Roasters". Contacts C01 (`lena@nordlicht-coffee.example`) and C02 (`tobias@nordlicht-coffee.example`) share one domain. Both are market DE. | High | Merge P07 into P01, or confirm they are separate entities, before anyone pitches "holiday collab" to a partner already in a Q4 bundle talk (person, needs a yes). |
| F04 | C | P04 Kestrel Outdoor | Status Paused, but an offer is live and the partner has sent deal-changing mail. | `status` = Paused, `live_offers` = 1. 2026-10-05 e-mail from Anna: "our discount code is still live on your site this week; can we extend it to November?". There is no next step or date. | High | Decide whether to switch the offer off or move status to Live/Negotiation, and reply to the extension request (person). |
| F05 | D | P02 Ferrow Ceramics | Priority A in Negotiation with no next step and no date. It is cold. | `next_step` and `next_step_date` empty. `last_contact` = 2026-08-29, which is 45 days ago against the 14-day A cadence. | High | Owner Jonas sets a next step and date and re-contacts Elif Kaya, or proposes Lost if the deal is dead (person). |
| F06 | D | P03 Bramble & Oak | Next step overdue. | "Renew affiliate terms", `next_step_date` = 2026-10-02, which is 11 days past. Status Live. | Medium | Owner Mia does the renewal or sets a new date (person). |
| F07 | D | P06 Saltmarsh Soap | Closed partner still carries a next step. | `status` = Lost, `next_step` = "Follow-up on sample feedback" dated 2026-10-28. | Low | Clear the next step, or reopen the partner if the follow-up is real (person). |
| F08 | E | P09 Copperleaf Candles | Bounced address still marked Active. | 2026-10-07 e-mail log: "Delivery failure: holly@copperleafcandles.example (mailbox does not exist)". Contact C11 Holly Avery has `status` = Active. | Medium | Set C11 to Bounced (safe to apply). Tom Avery (C09) remains an active contact. |
| F09 | E | P07 Nordlicht Coffee Roasters | The only contact is unverified. | C02 Tobias Brandt `status` = To verify, and it is the only contact on P07. | Low | Resolve through the F03 merge decision (person). |
| F10 | F | P07 Nordlicht Coffee Roasters | Missing priority on an open partner. | `priority` empty. Status Prospect. | Low | Set after the F03 decision (person). |
| F11 | F | P08 Halden Linen | Missing market on a Live partner. | `market` empty. Status Live, 3 live offers. | Low | Owner Mia fills in the market (person). |

### Today's three

1. **F01, the sync outage.** Every other result here rests on this data, and the digest reported all clear while the sync was dead. Fix it first or the CRM keeps rotting unseen.
2. **F04, the Kestrel offer.** A paused partner has a live offer and a pending discount-extension request that nobody has answered since 2026-10-05. This is the one finding that touches live money and a partner waiting on a reply.
3. **F05, Ferrow Ceramics.** It is the highest-priority open deal with no plan, 45 days of silence and no next step. It will slip away without anyone deciding.

The F03 duplicate comes right after these. It is the next to decide because it can cause a wrong pitch.

### Clean partners

Only 2 of 10 partners had no finding.

### What I did NOT do

No changes were made. This was a read-only pass over the exports. The "safe to apply" fixes (F02, F08) are listed but not applied, and nothing was merged, closed or re-statused.
