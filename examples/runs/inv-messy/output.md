**Proposal queue** (read-only pass; the exports are a snapshot)

Source of truth: `stock-master.csv`. It is the only inventory-system export; the other two are marketplaces.

Columns used:
- **stock-master.csv:** `SKU` is the item id, `Qty on hand` is on-hand stock, `Status` is the status.
- **marketplace-a.csv:** `sku` is the item id, `qty_listed` is the quantity offered, `state` is the status.
- **marketplace-b.csv:** `Item ID` is the item id, `Available` is the quantity offered, `Listing status` is the status, and `notes` is read for context.

Status mapping: "Active", "active" and "live" mean live. "Sold out" and "Sold" mean sold. "Reserved - pickup Fri" and "paused till Feb" are something else.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | SK-102 | The master says "Sold out" (on hand 0). Marketplace A still shows it "live" with qty 1. Marketplace A is stale. |
| I2 | human | SK-104 | The master says "Active" (on hand 1). Marketplace B says "Sold" (Available 0). Marketplace B's note reads "buyer asked for an extension on payment until Monday", so a sale may be pending payment. Marketplace A says "live" (qty 1). To resolve it, someone needs to know whether that sale is completed or still unpaid, and whether the unit is still in the warehouse. |
| I2 | human | SK-106 | The master says "Reserved - pickup Fri" (on hand 1), which is neither live nor sold. Marketplace A shows it "live" (qty 1). To resolve it, someone needs to know whether the reservation is firm and whether the item should stay listed. |
| I2 | human | SK-107 | The master says "Active" (on hand 3). Marketplace A says "paused till Feb". Marketplace B says "Active" (Available 1). To resolve it, someone needs to know whether the pause on A is deliberate. |
| I3 | human | SK-109 | Marketplace A lists it as "live" (qty 1), but the master has no record of it. To resolve it, someone needs to confirm whether it is a real product missing from the master or a stray listing. |
| I4 | human | SK-108 | Marketplace B has two rows. One is "Cotton tote", "active", Available 2. The other is "Cotton tote (bundle)", "Active", Available 2, with the note "created by the bundle tool". To resolve it, someone needs to know whether the bundle is a separate product or a duplicate. |
| I5 | confirmed | SK-103 | The master has 2 on hand. Marketplace A lists 3 as live, which is more than on hand. Marketplace B lists 1. The fix is to lower A to 2. |
| I6 | human | SK-101 | The master has 4 on hand. Marketplace A lists 4 and Marketplace B lists 3, so 7 in total. Neither channel alone exceeds 4, but together they do. A person needs to decide how to split the stock. |
| I6 | human | SK-105 | The master has 10 on hand. Marketplace A lists 6 and Marketplace B lists 5, so 11 in total. Neither channel alone exceeds 10, but together they do. A person needs to decide how to split the stock. |

Clean items: 0 of the 9 items were fully clean. Every item has at least one finding.

**What I did NOT do:** I made no changes. This was a read-only pass, and nothing was delisted, marked sold, or re-quantified. Everything above is a proposal for a person to review. `cross-platform-inventory-sync.md` does not exist in this folder, so I worked from the rules in my instructions.

```findings
[
  {"rule": "I1", "entity": "SK-102", "bucket": "confirmed"},
  {"rule": "I2", "entity": "SK-104", "bucket": "human"},
  {"rule": "I2", "entity": "SK-106", "bucket": "human"},
  {"rule": "I2", "entity": "SK-107", "bucket": "human"},
  {"rule": "I3", "entity": "SK-109", "bucket": "human"},
  {"rule": "I4", "entity": "SK-108", "bucket": "human"},
  {"rule": "I5", "entity": "SK-103", "bucket": "confirmed"},
  {"rule": "I6", "entity": "SK-101", "bucket": "human"},
  {"rule": "I6", "entity": "SK-105", "bucket": "human"}
]
```
