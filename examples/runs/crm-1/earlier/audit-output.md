# Partner CRM audit, 2026-10-13

**Today = 2026-10-13**, from the as-of date in the folder's README. **The data is not fresh.** The nightly sync last logged a run on 2026-10-10 and has no entry for 10-11, 10-12 or 10-13. That means `live_offers` and `last_contact` could be up to three days old, and every finding below that relies on them should be read with that in mind. The morning digest ran every day from 10-05 to 10-13.

## Findings

| ID | Section | Partner | What's wrong | Evidence | Severity | Proposed fix / who decides |
|---|---|---|---|---|---|---|
| F1 | A | (all) | The nightly sync stopped logging runs after 2026-10-10, and the morning digest did not notice. | `activity.csv` has a `nightly-sync, Run OK; 10 partners synced` row every day from 10-05 to 10-10, then none for 10-11, 10-12 or 10-13. On those same days `morning-digest` logged "Run OK; nothing needed attention" (10-11, 10-12) and "2 items sent to owner" (10-13). | high | **Person:** check the sync job, re-run it, and then re-run this audit. Also add a "sync missing" check to the digest so a stopped sync gets reported. |
| F2 | B | P01 Nordlicht Coffee / P07 Nordlicht Coffee Roasters | Probably the same company entered twice, with two different owners working it at the same time. | Near-identical names. Contacts C01 `lena@nordlicht-coffee.example` (P01) and C02 `tobias@nordlicht-coffee.example` (P07) use the same domain. P01 is Live/A, Mia, "Send Q4 bundle proposal" 2026-10-20. P07 is Prospect, no priority, Jonas, "Pitch holiday collab" 2026-10-30. | high | **Person (Mia + Jonas):** confirm it is one company. If so, merge P07 into P01, move C02 over to P01, and agree on a single owner and a single pitch. Not safe to apply. |
| F3 | C | P04 Kestrel Outdoor | Status is "Paused", but an offer is still live and the partner wants to extend it. Their mail has not been answered. | `status=Paused`, `live_offers=1`, no next step. `activity.csv` 2026-10-05: "Anna: our discount code is still live on your site this week; can we extend it to November?" | high | **Person (Jonas):** decide whether the partnership is actually active again (status → Live, extend the code) or really paused (take the offer down). Then reply to Anna and set a next step and date. |
| F4 | D | P02 Ferrow Ceramics | Priority-A deal in Negotiation with no next step, no date, and gone cold. | `status=Negotiation, priority=A`, `next_step` and `next_step_date` empty, `last_contact=2026-08-29`. That is 45 days ago against a 14-day cadence. | high | **Person (Jonas):** set a next step and date and contact Elif Kaya (C03). If the deal is dead, change the status. |
| F5 | C/D | P04 Kestrel Outdoor | `last_contact` was not updated after the partner's mail, so on paper the relationship looks cold (31 days on a 30-day B cadence). | `last_contact=2026-09-12`, but `activity.csv` shows mail from Anna on 2026-10-05. | medium | **Safe to apply (machine-owned):** set `last_contact` to 2026-10-05. Together with F6, this suggests the morning mailbox update is not writing back. Check that too. |
| F6 | E | P09 Copperleaf Candles | Contact with a bounced address is still marked Active. | C11 Holly Avery `holly@copperleafcandles.example` `status=Active`. `activity.csv` 2026-10-07: "Delivery failure: holly@copperleafcandles.example (mailbox does not exist)". | medium | **Safe to apply (machine-owned):** set C11 to Bounced. P09 still has an active contact (C09 Tom Avery), so outreach is not blocked. |
| F7 | D | P03 Bramble & Oak | Next step is overdue on a Live partner. | `next_step="Renew affiliate terms"`, `next_step_date=2026-10-02`, which is 11 days ago. `last_contact=2026-09-30`. | medium | **Person (Mia):** finish the renewal or set a new date. Check that the affiliate terms have not lapsed while the offer is live (`live_offers=1`). |
| F8 | D/E | P06 Saltmarsh Soap | Partner is Lost but still has a next step, and its only contact is a former employee. | `status=Lost`, `next_step="Follow-up on sample feedback"`, `next_step_date=2026-10-28`. Only contact C07 Grace Lowe has `status=Former`. | low | **Person (Jonas):** clear the next step, or reopen the partner if the follow-up is real (it would also need a current contact). |
| F9 | E | P07 Nordlicht Coffee Roasters | The partner's only contact has not been verified. | Only contact is C02 Tobias Brandt, `status=To verify`. | low | **Person:** verify the contact when deciding on F2. It will probably move to P01. |
| F10 | F | P07 Nordlicht Coffee Roasters | Priority is missing on an open partner, so no cadence can be applied. | `priority` empty, `status=Prospect`. | low | **Person:** resolve as part of the F2 merge. Set a priority only if P07 stays a separate partner. |
| F11 | F | P08 Halden Linen | Market is missing on a Live partner. | `market` empty, `status=Live`, `live_offers=3`. | low | **Person (Mia):** fill in the market. Nothing in the export gives a single correct value. |

## Today's three

1. **F1, the nightly sync.** Until it runs again, live offers and last-contact dates may be stale, and today's digest was built on them.
2. **F3, Kestrel Outdoor.** A partner asked a direct question eight days ago and has had no reply. An offer is live on a partner marked Paused, which is a commercial and reputational risk. This also needs fixing before anyone acts on F5.
3. **F4, Ferrow Ceramics.** It is the only priority-A deal in negotiation, it is 45 days without contact, and no one has a plan for it. It is the most valuable relationship here that is quietly being lost.

F2 (the Nordlicht duplicate) comes next. Both owners have pitches planned for this month (10-20 and 10-30), so it needs settling before either one goes out.

## Clean partners

2 of 10 partners had no findings.

## What was not done

This was a read-only pass, and nothing in the CRM was changed. F5 and F6 are marked safe to apply but were not applied. Every other fix needs a person to decide. The activity log only goes back to 2026-10-05, so automation health before that date could not be checked.
