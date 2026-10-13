## Inventory sync proposal queue

Source of truth: `storefront.csv` (the storefront export). Compared against `marketplace-a.csv` and `marketplace-b.csv`. Statuses were trimmed and compared case-insensitively.

### Findings

- **I1, confirmed, PRT-101** (Harbour at dusk). The storefront says `sold`. marketplace-a still shows `live`. The listing is stale, so proposal: delist it on marketplace-a.
- **I1, confirmed, PRT-110** (Salt flats panorama). The storefront says `sold`. marketplace-b still shows `live`. The listing is stale, so proposal: delist it on marketplace-b.
- **I2, human, PRT-101.** marketplace-b shows `reserved` while the storefront says `sold`. This is a separate finding from the I1 one above. To resolve it, check whether a buyer actually has a reservation on marketplace-b or the reservation is a leftover. Check the sale record (order and date) against the reservation.
- **I2, human, PRT-105** (Night market poster). The storefront says `reserved`. marketplace-a and marketplace-b both show `live`. I can't tell whether the reservation is real. To resolve it, check who holds the reservation and whether it is still valid. If it is valid, both channels should be paused. If it has lapsed, the storefront is the stale side.
- **I2, human, PRT-107** (Kestrel in flight). The storefront says `live`, but marketplace-a says `sold`. A channel claims a sale the source of truth doesn't know about. To resolve it, check marketplace-a's order records for a real sale. If there is one, the storefront needs updating. If not, the marketplace status is wrong.
- **I3, human, PRT-108** (Moth wing study). marketplace-a lists it as `sold`, but the storefront has no record of the item. To resolve it, find out whether the item was ever stocked and whether it is a missing storefront record or a stray marketplace listing.
- **I4:** none. No item appears on more than one row of any file.

Clean: 5 items (PRT-102, PRT-103, PRT-104, PRT-106, PRT-109) match the source of truth on every channel that lists them.

### What I did not do

I made no changes. This is a read-only pass, and nothing was delisted, marked sold or edited. The delist proposals for PRT-101 and PRT-110 are queue entries that need someone's approval before action.

```findings
[
  {"rule": "I1", "entity": "PRT-101", "bucket": "confirmed"},
  {"rule": "I1", "entity": "PRT-110", "bucket": "confirmed"},
  {"rule": "I2", "entity": "PRT-101", "bucket": "human"},
  {"rule": "I2", "entity": "PRT-105", "bucket": "human"},
  {"rule": "I2", "entity": "PRT-107", "bucket": "human"},
  {"rule": "I3", "entity": "PRT-108", "bucket": "human"}
]
```
