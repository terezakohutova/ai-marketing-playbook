## CRM audit

**Today and freshness (A1).** There is no README, so I took "today" from the newest date in `activity.csv`: **2027-01-15**. The log runs 2027-01-09 to 2027-01-15. `nightly-sync` and `morning-digest` each have a line on every one of those days, so rule A1 does not fire and the data is fresh. I did not have `partner-crm-steward.md`, so I worked from the agent rules alone.

### Findings

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | D4 | P03 Cobalt Cycling | Cold. Live, priority B, last real contact is 36 days ago (window 30). | `last_contact` 2026-12-10. The only 2027 e-mail line for P03 is a bounce, which does not count as contact. | high | Reach out to Cobalt through a working address and update `last_contact` once someone replies. (person) |
| 2 | E1 | C03 (P03) | Contact whose address bounced is still Active. | C03 `theo.marsh@cobaltcycling.example`, status Active. On 2027-01-13 the activity log has "Delivery Status Notification (Failure): Theo.Marsh@cobaltcycling.example - address not found". | high | Set C03 to To verify or Former. One correct answer. (safe to apply) |
| 3 | D1 | P03 Cobalt Cycling | Open partner with a next step but no next step date. | next_step "Review Q4 numbers", `next_step_date` empty. | medium | Owner Ana sets a date. (person) |
| 4 | D4 | P05 Sundial Watches | Cold. Negotiation, priority C, last contact 75 days ago (window 60). | `last_contact` 2026-11-01, no e-mail lines in the log. | high | Ana decides whether to chase, re-prioritise or pause. The "Send counter-offer" step is due 2027-01-19. (person) |
| 5 | E2 | P05 Sundial Watches | None of its contacts is usable. | C06 Omar Haddad is To verify and C07 Rhea Stone is Former. | medium | Find and add a verified contact. (person) |
| 6 | F2 | P05 Sundial Watches | Open partner with no market. | `market` empty. | medium | Ana fills in the market. (person) |
| 7 | B1 | P01+P02 | Likely duplicate. | "Brightwater GmbH" and "Brightwater" are near-same once "gmbh" is dropped. Contacts C01 `jana@brightwater.example` and C02 `felix@brightwater.example` share the domain brightwater.example. The two rows differ in market (DE vs AT), status, owner and priority, so they may be two entities. | high | A person decides whether to merge or keep both. Nothing is merged without a yes. (person) |
| 8 | E2 | P02 Brightwater | Its only contact is unusable. | C02 Felix Roth is To verify. | medium | Verify Felix's address or find another contact. (person) |
| 9 | B3 | P06 | Same `partner_id` on two rows. | Two identical rows for P06 Meadowlark Games (Live, C, Lukas, AT, 2027-01-08, 2026-12-20, 1 offer). | medium | Remove one row after a person confirms. (person) |
| 10 | D2 | P06 Meadowlark Games | Next step overdue. | "Holiday recap" is dated 2027-01-08, 7 days before today. | medium | Lukas does the step or sets a new date. (person) |
| 11 | C1 | P04 Linden Botanicals | Lost, but still has a live offer. | status Lost, `live_offers` 1. | high | A person checks the offer and switches it off, or corrects the status if the partner is not actually lost. (person) |

### Today's three

1. **P03 Cobalt Cycling (findings 1-3).** This is a Live priority-B partner with 2 live offers. It is the only one whose contact failed on 2027-01-13: its only unreachable address is still marked Active, and the relationship has gone cold. The bounce hides the fact that nobody has been in touch for 36 days.
2. **P01+P02 Brightwater (finding 7).** P01 is a Live priority-A partner and a possible duplicate with a Prospect. This needs a person's decision before anyone contacts the wrong Brightwater or splits its history.
3. **P05 Sundial Watches (findings 4-6).** A live negotiation that has been silent for 75 days, with no verified contact and no market. The counter-offer is due on 2027-01-19, and nobody currently has a way to send it.

Finding 11 (P04 with a live offer) is close behind them.

### Clean partners

3 of the 9 distinct partners had no findings.

### What I did NOT do

No changes were made. This was a read-only pass. The "safe to apply" item (E1 on C03) is only proposed. I also changed no status, priority, owner, market or next step, and I merged nothing.

```findings
[
  {"rule": "D4", "entity": "P03", "bucket": "person"},
  {"rule": "E1", "entity": "C03", "bucket": "safe"},
  {"rule": "D1", "entity": "P03", "bucket": "person"},
  {"rule": "D4", "entity": "P05", "bucket": "person"},
  {"rule": "E2", "entity": "P05", "bucket": "person"},
  {"rule": "F2", "entity": "P05", "bucket": "person"},
  {"rule": "B1", "entity": "P01+P02", "bucket": "person"},
  {"rule": "E2", "entity": "P02", "bucket": "person"},
  {"rule": "B3", "entity": "P06", "bucket": "person"},
  {"rule": "D2", "entity": "P06", "bucket": "person"},
  {"rule": "C1", "entity": "P04", "bucket": "person"}
]
```
