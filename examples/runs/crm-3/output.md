**Today:** I used 2027-01-15, the newest date in `activity.csv`, because there is no README with an as-of date. The data is fresh under rule A1. `nightly-sync` and `morning-digest` each have a log line on every day from 2027-01-09 to 2027-01-15, with no gaps.

I used the columns as named, with no renames. Contact C09 is absent from the file, but nothing points to it, so it is not a finding.

| ID | Rule | Partner | What's wrong | Evidence | Severity | Proposed fix (who decides) |
|---|---|---|---|---|---|---|
| 1 | C1 | P04 Linden Botanicals | Lost partner still has live offers | status=Lost, live_offers=1 | High | Check whether the offer is really live. Then end the offer or reconsider the status (person). |
| 2 | B1 | P01+P02 | Near-same names, and the contacts share a company domain | "Brightwater GmbH" and "Brightwater" both normalise to "brightwater". C01 jana@brightwater.example and C02 felix@brightwater.example share brightwater.example. | High | Decide whether to merge. P01 is Live/A/DE and P02 is Prospect/B/AT (person). |
| 3 | B3 | P06 | Same `partner_id` on two rows | Two identical rows for P06 Meadowlark Games in `partners.csv` | Medium | Remove the duplicate row after a person confirms (person). |
| 4 | E1 | C03 (P03) | Contact address bounced but is still Active | 2027-01-13 notice: "Delivery Status Notification (Failure): Theo.Marsh@cobaltcycling.example - address not found". C03 is theo.marsh@cobaltcycling.example with status Active. | Medium | Set C03 to To verify or Former (safe to apply). |
| 5 | D4 | P03 Cobalt Cycling | Cold. The bounce does not count as contact. | Priority B (30-day window). Last contact is 2026-12-10, which is 36 days ago. The only log line since then is the bounce. | Medium | Reach Ida Kern (C04) and refresh the relationship (person). |
| 6 | D4 | P05 Sundial Watches | Cold | Priority C (60-day window). Last contact is 2026-11-01, which is 75 days ago. | Medium | Contact them, or re-rank the partner (person). |
| 7 | D1 | P03 Cobalt Cycling | Open partner has a next step but no date | next_step="Review Q4 numbers", next_step_date empty | Medium | Set a date (person). |
| 8 | D2 | P06 Meadowlark Games | Next step is overdue | next_step_date=2027-01-08, before 2027-01-15, for "Holiday recap" | Medium | Do the step or reschedule it (person). |
| 9 | E2 | P05 Sundial Watches | No usable contact | C06 Omar Haddad is To verify and C07 Rhea Stone is Former | Medium | Verify Omar or find a new contact (person). |
| 10 | E2 | P02 Brightwater | No usable contact | The only contact, C02 Felix Roth, is To verify | Low | Verify Felix. Fold this into the B1 decision (person). |
| 11 | F2 | P05 Sundial Watches | Open partner has no market | market empty, status Negotiation | Low | Assign a market (person). |

**Today's three:**
1. **P04 (C1):** a Lost partner with a live offer may still be running something. This is the biggest contradiction in the data.
2. **P01+P02 (B1):** a possible duplicate involving a Live A-priority partner. Any other work on either record may be wasted until this is decided.
3. **P05 (D4):** the partner is in Negotiation and has had no contact for 75 days. It also has no verified contact (E2) and no market (F2), so one conversation could fix all three.

Of the 9 partners, 2 were clean: P08 and P09. The other 7 have at least one finding. P07 is Paused with no problems, so it is clean too, which makes 3 clean partners.

**What I did not do:** I made no changes. This was a read-only pass. Every fix above, including the safe-to-apply one (E1 on C03), is a proposal and is not applied.

```findings
[
  {"rule": "C1", "entity": "P04", "bucket": "person"},
  {"rule": "B1", "entity": "P01+P02", "bucket": "person"},
  {"rule": "B3", "entity": "P06", "bucket": "person"},
  {"rule": "E1", "entity": "C03", "bucket": "safe"},
  {"rule": "D4", "entity": "P03", "bucket": "person"},
  {"rule": "D4", "entity": "P05", "bucket": "person"},
  {"rule": "D1", "entity": "P03", "bucket": "person"},
  {"rule": "D2", "entity": "P06", "bucket": "person"},
  {"rule": "E2", "entity": "P05", "bucket": "person"},
  {"rule": "E2", "entity": "P02", "bucket": "person"},
  {"rule": "F2", "entity": "P05", "bucket": "person"}
]
```
