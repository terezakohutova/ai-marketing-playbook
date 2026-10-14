**Proposal queue** (read-only snapshot of the three exports)

Source of truth: `storefront.csv`. It is the storefront export, and the two marketplace files are the channels. All three files use `item_id` for the item id and `status` for the status. None has a quantity or notes column, so I5 and I6 could not be checked. `cross-platform-inventory-sync.md` is not in the folder, so I worked from the rules alone.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | PRT-101 | Storefront says `sold`. marketplace-a still shows `live`. |
| I1 | confirmed | PRT-110 | Storefront says `sold`. marketplace-b still shows `live`. marketplace-a does not list it. |
| I2 | human | PRT-101 | marketplace-b says `reserved`, while the storefront says `sold`. A status that is neither live nor sold is not the I1 case. To resolve it, check whether a pending order or hold exists for this item and whether it was actually sold. |
| I2 | human | PRT-105 | Storefront says `reserved`. marketplace-a says `live` and marketplace-b says `live`. To resolve it, find out who holds the reservation and whether the item should stay on sale. |
| I2 | human | PRT-107 | Storefront says `live`. marketplace-a says `sold`. To resolve it, check the order records for a real sale on marketplace-a, since the storefront may not have registered it. |
| I3 | human | PRT-108 | marketplace-a lists it as `sold`. The storefront has no record of it. To resolve it, confirm whether it is a legacy or mistaken listing, or an item missing from the storefront. |

No item appears on more than one row of a file, so I4 did not fire.

5 items were clean, with every channel that lists them matching the storefront: PRT-102, PRT-103, PRT-104, PRT-106 and PRT-109. Statuses were compared after trimming and ignoring case, so `Live` and `LIVE` match `live`.

**What I did not do:** I made no changes. This is a read-only pass. The I1 items are proposals for the queue, not actions taken. I did not delist, mark sold, or change anything on any channel.

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
