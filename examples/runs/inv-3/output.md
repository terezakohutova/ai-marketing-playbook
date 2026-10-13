Source of truth: `inventory.csv` (the inventory system export). Channels compared: `auction-site.csv`, `shop-north.csv`, `shop-south.csv`. Statuses were compared after trimming spaces and ignoring case.

## Proposal queue

- **I1 / confirmed / BK-201** (First edition field guide): inventory says `sold`, but auction-site says `live`, shop-north says `live` and shop-south says `live`. All three channels are stale. Proposed for delisting on all three, pending approval.
- **I1 / confirmed / BK-208** (Map of the old town): inventory says `sold`. shop-north still says `live`. auction-site doesn't list it, and shop-south says `sold`, which agrees. shop-north is stale. Proposed for delisting there, pending approval.
- **I2 / human / BK-203** (Signed poetry chapbook): inventory says `live`, auction-site says `ended`. shop-north and shop-south don't list it. I can't tell whether the auction ended without a sale (so it could be relisted) or the inventory record is out of date. To resolve it, check the auction's end reason (unsold or sold) and confirm the physical copy is still in stock.
- **I3 / human / BK-205** (Annotated garden diary): shop-south lists it as `live`, but inventory has no record of it. To resolve it, check whether it is a missing inventory entry (a stock item never logged) or a stray or mistaken listing.
- **I4 / human / BK-202** (Atlas of rivers): shop-north has two rows for it, both `live`. Inventory says `live`, so the status is consistent. The duplicate may be a double listing or an export artifact. To resolve it, check shop-north's admin for one listing or two, and whether there is one copy or two in stock.

Clean: 4 items (BK-204, BK-206, BK-207, BK-209) had every listing matching inventory. BK-207 matched after normalising `SOLD` and ` sold`. BK-202 matches on status but is flagged under I4 above.

## What I did not do
I made no changes. This was a read-only pass, and nothing was delisted, relisted or edited. All items above are proposals for a human to approve.

```findings
[
  {"rule": "I1", "entity": "BK-201", "bucket": "confirmed"},
  {"rule": "I1", "entity": "BK-208", "bucket": "confirmed"},
  {"rule": "I2", "entity": "BK-203", "bucket": "human"},
  {"rule": "I3", "entity": "BK-205", "bucket": "human"},
  {"rule": "I4", "entity": "BK-202", "bucket": "human"}
]
```
