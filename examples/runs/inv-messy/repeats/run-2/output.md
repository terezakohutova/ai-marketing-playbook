**Proposal queue.** I treated `stock-master.csv` as the source of truth. It is the only stock-count file, and the other two are marketplace exports. I read these columns:
- **stock-master.csv:** `SKU` is the item id, `Qty on hand` is on-hand stock, and `Status` is the status.
- **marketplace-a.csv:** `sku` is the item id, `qty_listed` is the quantity offered, and `state` is the status.
- **marketplace-b.csv:** `Item ID` is the item id, `Available` is the quantity offered, `Listing status` is the status, and `notes` is notes.

I mapped "Active" and "live" to live, and "Sold out" and "Sold" to sold. I did not read the other file, `cross-platform-inventory-sync.md`, because it does not exist in this folder. I worked from the rules in my instructions only.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | SK-102 | Master says "Sold out" (on hand 0). Marketplace A still shows "live" with qty 1. Marketplace B doesn't list it. |
| I2 | human | SK-104 | Master says "Active" (on hand 1). Marketplace B says "Sold" (Available 0), with the note "buyer asked for an extension on payment until Monday". Marketplace A says "live". To resolve it, check whether the buyer's payment on B actually completed. If it didn't, the sale may fall through and master stays right. If it did, master's count is stale. |
| I2 | human | SK-106 | Master says "Reserved - pickup Fri", which is neither live nor sold. Marketplace A shows "live" (qty 1). To resolve it, confirm whether the pickup reservation is still active. If it is, A should come down. |
| I2 | human | SK-107 | Master says "Active" (on hand 3). Marketplace A says "paused till Feb" (last updated 2026-11-02), which is neither live nor sold. Marketplace B says "Active" (qty 1). To resolve it, ask whether the pause on A was deliberate and should stay. |
| I3 | human | SK-109 | Marketplace A lists it as "live" (qty 1), but master has no record of it. To resolve it, find out whether it is a missing master entry or an erroneous listing. |
| I4 | human | SK-108 | Marketplace B has two rows: "Cotton tote" (Available 2, "active") and "Cotton tote (bundle)" (Available 2, "Active", note "created by the bundle tool"). Master says "Active" (on hand 5). To resolve it, decide whether the bundle row is an intended separate listing or a duplicate. |
| I5 | confirmed | SK-103 | Master says "Active" with on hand 2. Marketplace A lists qty 3 as "live", which is more than on hand. Lowering A to 2 is the fix. Marketplace B lists 1. |
| I6 | human | SK-101 | Master on hand is 4. Marketplace A lists 4 ("live") and B lists 3 ("Active"), which is 7 in total. No single channel exceeds 4. A person needs to decide how to split the stock. |
| I6 | human | SK-105 | Master on hand is 10. Marketplace A lists 6 ("live") and B lists 5 ("Active"), which is 11 in total. No single channel exceeds 10. A person needs to decide how to split the stock. |

None of the 9 distinct items was fully clean. Every item that appears in the exports has at least one finding.

**What I did NOT do:** I made no changes. This was a read-only pass, and I did not delist or mark anything sold. The exports are a snapshot. They show the state when they were taken, not the current state.

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
