**Proposal queue**

Source of truth: `stock-master.csv`. It's the inventory export, and the other two files are marketplaces. `cross-platform-inventory-sync.md` isn't in the folder, so I worked from the rules alone.

Column mapping:
- **stock-master.csv:** `SKU` is the item id, `Qty on hand` is stock, and `Status` is the status.
- **marketplace-a.csv:** `sku` is the item id, `qty_listed` is the quantity offered, and `state` is the status. `last_updated` is in mixed date formats and I ignored it.
- **marketplace-b.csv:** `Item ID` is the item id, `Available` is the quantity offered, `Listing status` is the status, and `notes` is notes.

I read "Active" and "live" as live, and "Sold out" and "Sold" as sold.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | SK-102 | Stock-master says "Sold out" (on hand 0). Marketplace A still shows `live`, qty 1. The marketplace A listing is stale. |
| I5 | confirmed | SK-103 | Stock-master has 2 on hand ("Active"). Marketplace A lists 3 as `live`, which is more than is on hand. Marketplace B lists 1 as "Active". Lower marketplace A to 2. |
| I6 | human | SK-101 | Stock-master has 4 on hand ("Active"). Marketplace A lists 4 as `live` and marketplace B lists 3 as "Active", so 7 in total. Neither channel exceeds 4 alone, but a sale on each could oversell. A person has to decide how to split the stock. |
| I6 | human | SK-105 | Stock-master has 10 on hand ("Active"). Marketplace A lists 6 as `live` and marketplace B lists 5 as "Active", so 11 in total. Neither channel exceeds 10 alone. A person has to decide how to split the stock. |
| I2 | human | SK-104 | Stock-master says "Active" (1 on hand). Marketplace B says "Sold", with the note "buyer asked for an extension on payment until Monday". Marketplace A says `live`, qty 1. To resolve it, check whether the sale to that buyer is actually pending or completed and whether the unit is still physically in stock. I can't tell which side is right. |
| I2 | human | SK-106 | Stock-master says "Reserved - pickup Fri", which is neither live nor sold. Marketplace A shows `live`, qty 1. To resolve it, confirm whether the pickup reservation is firm and whether the marketplace listing should be held. |
| I2 | human | SK-107 | Stock-master says "Active" (3 on hand). Marketplace A says `paused till Feb`, which is neither live nor sold. Marketplace B says "Active", qty 1. To resolve it, ask why marketplace A was paused (deliberate or not) and whether it should return to live. |
| I4 | human | SK-108 | Marketplace B has two rows for this item. One is "Cotton tote", "active", qty 2. The other is "Cotton tote (bundle)", "Active", qty 2, with the note "created by the bundle tool". Stock-master has 5 on hand ("Active"). To resolve it, decide whether the bundle row is a separate intended listing or a duplicate. The two rows total 4, which is within 5, so I raised no quantity finding. |
| I3 | human | SK-109 | Marketplace A lists it as `live`, qty 1. Stock-master has no record of it. To resolve it, find out whether it's a missing master record or a listing that shouldn't exist. |

None of the 9 items was clean. Every item has at least one finding. SK-108 has an I4 finding even though its statuses agree with stock-master.

**What I did not do:** I made no changes and proposed no delistings or quantity edits beyond the queue above. This was a read-only pass over a snapshot of the exports.

```findings
[
  {"rule": "I1", "entity": "SK-102", "bucket": "confirmed"},
  {"rule": "I5", "entity": "SK-103", "bucket": "confirmed"},
  {"rule": "I6", "entity": "SK-101", "bucket": "human"},
  {"rule": "I6", "entity": "SK-105", "bucket": "human"},
  {"rule": "I2", "entity": "SK-104", "bucket": "human"},
  {"rule": "I2", "entity": "SK-106", "bucket": "human"},
  {"rule": "I2", "entity": "SK-107", "bucket": "human"},
  {"rule": "I4", "entity": "SK-108", "bucket": "human"},
  {"rule": "I3", "entity": "SK-109", "bucket": "human"}
]
```
