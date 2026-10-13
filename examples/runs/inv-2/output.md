**Proposal queue** (read-only pass over `export/storefront.csv`, `marketplace-a.csv` and `marketplace-b.csv`)

I treated `storefront.csv` as the source of truth because it is the storefront export. All three files use `item_id`, `title` and `status`, so no columns needed remapping. None of them has quantity columns, so I did not apply the quantity rules I5 and I6. I also couldn't find `cross-platform-inventory-sync.md` in the project. I worked from the rules in my instructions alone.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | PRT-101 | The storefront says `sold`. Marketplace A still shows `live`. |
| I2 | human | PRT-101 | The storefront says `sold`. Marketplace B shows `reserved`. This could be a pending order or a stale hold. To resolve it, check B's reservation or order record and whether a sale was actually completed. |
| I1 | confirmed | PRT-110 | The storefront says `sold`. Marketplace B still shows `live`. |
| I2 | human | PRT-105 | The storefront says `reserved`. Marketplace A and Marketplace B both show `live`. To resolve it, check who holds the reservation and whether it is still active. The storefront's own record of the reservation would show this. |
| I2 | human | PRT-107 | The storefront says `live`. Marketplace A says `sold`. To resolve it, check Marketplace A's order record for a sale. If a sale exists, the storefront stock count is wrong. If not, A's status is wrong. |
| I3 | human | PRT-108 | Marketplace A lists it as `sold`. The storefront has no record of the item. To resolve it, check whether the item was ever in inventory or was removed from the storefront export. |

I1 is a rule match on the storefront's own status, not an instruction to act. Any delist for PRT-101 or PRT-110 still goes through the queue.

Five items had every listing agreeing with the storefront: PRT-102, 103, 104, 106 and 109. Case and spacing differences such as `Live` and `LIVE` count as matching. PRT-104 and PRT-110 are not listed on Marketplace A, and PRT-102, PRT-107 and PRT-108 are not listed on Marketplace B. I did not count those gaps as discrepancies. I found no duplicate rows in any file, so I4 did not fire.

**What I did not do:** I made no changes to any channel or to the source of truth. I did not delist, mark anything sold, or resolve any human-bucket item by trusting one side. This is a snapshot of the exports as they were taken.

```findings
[
  {"rule": "I1", "entity": "PRT-101", "bucket": "confirmed"},
  {"rule": "I2", "entity": "PRT-101", "bucket": "human"},
  {"rule": "I1", "entity": "PRT-110", "bucket": "confirmed"},
  {"rule": "I2", "entity": "PRT-105", "bucket": "human"},
  {"rule": "I2", "entity": "PRT-107", "bucket": "human"},
  {"rule": "I3", "entity": "PRT-108", "bucket": "human"}
]
```
