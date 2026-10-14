**Proposal queue**

The source of truth is `storefront.csv`. It is the storefront export, and the other two files are marketplaces. I used `item_id` as the item id and `status` as the status in all three files. The exports have no quantity columns, so I5 and I6 could not be checked. `cross-platform-inventory-sync.md` is not in the project folder, so I worked from the rules in my instructions only.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | ITM-014 | Storefront says "sold". Marketplace A says "live" and Marketplace B says "live". Both channels are stale. |
| I1 | confirmed | ITM-040 | Storefront says "sold". Marketplace A says "sold". Marketplace B says "live", so B is stale. |
| I1 | confirmed | ITM-058 | Storefront says "Sold". Marketplace A says "LIVE " (after trimming and ignoring case, this is live), so A is stale. Marketplace B says "sold". |
| I2 | human | ITM-022 | Storefront says "live". Marketplace A says "live". Marketplace B says "sold". To resolve it, check the physical stock count or B's sales record for this item. |
| I2 | human | ITM-043 | Storefront says "live". Marketplace A says "reserved", which is neither live nor sold. Marketplace B says "live". To resolve it, check whether A holds a real open reservation or order for this item. |
| I2 | human | ITM-055 | Storefront says "live". Marketplace A says "sold" and Marketplace B says "sold". Two channels agree on sold, but I can't confirm that over the source of truth. To resolve it, check for order records on A and B and the physical stock. |
| I3 | human | ITM-052 | Marketplace A lists "Glass pendant light" as "live". The storefront has no record of it. To resolve it, find out whether the item exists in inventory and was left out of the storefront export, or whether it is an orphan listing. |

I4: no item appears on more than one row of a file.

Four items were clean, with every channel matching the storefront: ITM-031, ITM-035, ITM-061 and ITM-063.

**What I did not do:** I made no changes. This was a read-only pass over a snapshot. I'm not proposing any delist or status change from channel data alone. The I1 items are queued for review, not actioned.

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
