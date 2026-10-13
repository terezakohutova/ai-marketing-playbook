The pattern file `cross-platform-inventory-sync.md` isn't in the project folder, so I worked from the rules in my instructions alone.

**Files and columns:** `export/storefront.csv` is the source of truth. `export/marketplace-a.csv` and `export/marketplace-b.csv` are the two channels. In all three files I used `item_id` as the item id and `status` as the status. None of the files has quantity or notes columns, so I did not check I5 or I6.

**Proposal queue**

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | ITM-014 | The storefront says `sold`. Marketplace A says `live` and Marketplace B says `live`. |
| I1 | confirmed | ITM-040 | The storefront says `sold`. Marketplace B says `live`. Marketplace A says `sold`. |
| I1 | confirmed | ITM-058 | The storefront says `Sold`. Marketplace A says `LIVE ` (live after trimming). Marketplace B says `sold`. |
| I2 | human | ITM-022 | The storefront says `live`. Marketplace B says `sold`. Marketplace A says `live`. Someone needs to check the actual stock or order records for this item to see whether B recorded a real sale the storefront missed or B is wrong. |
| I2 | human | ITM-043 | The storefront says `live`. Marketplace A says `reserved`. Marketplace B says `live`. Someone needs to check A for an open order or hold on this item and see whether it is still pending. |
| I2 | human | ITM-055 | The storefront says `live`. Marketplace A says `sold` and Marketplace B says `sold`. Both channels disagree with the storefront, so someone needs to check order records to see whether it really sold or the storefront count is stale. |
| I3 | human | ITM-052 | Marketplace A lists "Glass pendant light" as `live`. The storefront has no record of it. Someone needs to find out whether the item exists and is missing from the storefront export. |

Four of the ten storefront items (ITM-031, ITM-035, ITM-061, ITM-063) were clean: every channel that lists them agrees with the storefront.

**What I did not do:** I made no changes. This was a read-only pass over the exports, so I did not delist or mark anything sold on any channel. These findings reflect the snapshot when the exports were taken, not the current state.

```findings
[
  {"rule": "I1", "entity": "ITM-014", "bucket": "confirmed"},
  {"rule": "I1", "entity": "ITM-040", "bucket": "confirmed"},
  {"rule": "I1", "entity": "ITM-058", "bucket": "confirmed"},
  {"rule": "I2", "entity": "ITM-022", "bucket": "human"},
  {"rule": "I2", "entity": "ITM-043", "bucket": "human"},
  {"rule": "I2", "entity": "ITM-055", "bucket": "human"},
  {"rule": "I3", "entity": "ITM-052", "bucket": "human"}
]
```
