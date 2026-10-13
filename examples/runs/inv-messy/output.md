# Proposal queue

**Files and columns used.** `stock-master.csv` is the source of truth. It is the only stock-keeping export, and the other two are marketplaces.
- `stock-master.csv`: `SKU` is the item id, `Qty on hand` is stock, `Status` is the status.
- `marketplace-a.csv`: `sku` is the item id, `qty_listed` is the quantity offered, `state` is the status.
- `marketplace-b.csv`: `Item ID` is the item id, `Available` is the quantity offered, `Listing status` is the status, and `notes` is read for context.

Statuses were trimmed and compared ignoring case. `Active` is treated as live and `Sold out` / `Sold` as sold.

| Item | Rule | Bucket | Evidence |
|---|---|---|---|
| SK-102 | I1 | confirmed | Stock master: `Sold out`, on hand 0. Marketplace A: `live`, qty 1. The listing is stale. |
| SK-103 | I5 | confirmed | Stock master: `Active`, on hand 2. Marketplace A lists 3 as `live`, which is more than on hand. Lower A's quantity to 2. Marketplace B lists 1 as `Active`. |
| SK-104 | I2 | human | Stock master: `Active`, on hand 1. Marketplace B: `Sold`, qty 0, note "buyer asked for an extension on payment until Monday". Marketplace A: `live`, qty 1. B may have a pending sale that hasn't reached the stock master. Resolving it needs B's order record and whether the buyer has paid. |
| SK-106 | I2 | human | Stock master: `Reserved - pickup Fri`, on hand 1. Marketplace A: `live`, qty 1. Resolving it needs confirmation that the pickup reservation is still valid, which decides whether A's listing should be live. |
| SK-107 | I2 | human | Stock master: `Active`, on hand 3. Marketplace A: `paused till Feb` (something else), last updated 2026-11-02. Marketplace B: `Active`, qty 1. Resolving it needs confirmation from whoever paused it on A, and whether it should stay paused. |
| SK-108 | I4 | human | Marketplace B has two rows for this item: "Cotton tote", `active`, qty 2, and "Cotton tote (bundle)", `Active`, qty 2, note "created by the bundle tool". Stock master: `Active`, on hand 5. Resolving it needs confirmation of whether the bundle row is a deliberate separate listing or an accidental duplicate. |
| SK-109 | I3 | human | Marketplace A lists it as `live`, qty 1. The stock master has no record of it. Resolving it needs confirmation of whether it is a missing stock record or an erroneous listing. |
| SK-101 | I6 | human | Stock master: `Active`, on hand 4. Marketplace A lists 4 and Marketplace B lists 3. Neither exceeds 4 alone, but together they list 7. A sale on each would oversell. Whether and how to split the stock is a person's call. |
| SK-105 | I6 | human | Stock master: `Active`, on hand 10. Marketplace A lists 6 and Marketplace B lists 5. Neither exceeds 10 alone, but together they list 11. Whether and how to split the stock is a person's call. |

**Clean items:** 0 of 9 distinct items were clean. Every item has at least one finding.

**Notes**
- SK-103 gets only I5. Its combined listing of 4 against 2 on hand is already covered by A's single-channel overlist, and I6 applies only when no single channel is over.
- Marketplace A's `last_updated` values are in three date formats, and several fall after today's date (2026-10-14). I did not rely on them.

**What I did NOT do:** I made no changes. This was a read-only pass over the exports. I did not delist, mark sold, or edit any quantity on any channel. Every finding is a proposal for a person to act on.

```findings
[
  {"rule": "I1", "entity": "SK-102", "bucket": "confirmed"},
  {"rule": "I5", "entity": "SK-103", "bucket": "confirmed"},
  {"rule": "I2", "entity": "SK-104", "bucket": "human"},
  {"rule": "I2", "entity": "SK-106", "bucket": "human"},
  {"rule": "I2", "entity": "SK-107", "bucket": "human"},
  {"rule": "I4", "entity": "SK-108", "bucket": "human"},
  {"rule": "I3", "entity": "SK-109", "bucket": "human"},
  {"rule": "I6", "entity": "SK-101", "bucket": "human"},
  {"rule": "I6", "entity": "SK-105", "bucket": "human"}
]
```
