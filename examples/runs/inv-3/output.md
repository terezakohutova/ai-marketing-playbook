**Proposal queue** (read-only pass)

Source of truth: `export/inventory.csv`. It is the only file with no channel role, and the others are two shops and an auction site. Columns used: `item_id` is the item id and `status` is the listing status. None of the files has quantity columns, so rules I5 and I6 could not be checked. I did not find `cross-platform-inventory-sync.md` in the folder, so I worked from my instructions alone.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | BK-201 | Inventory says `sold`. auction-site says `live`, shop-north says `live` and shop-south says `live`. All three channels are stale. |
| I1 | confirmed | BK-208 | Inventory says `sold`. shop-north says `live`. shop-south says `sold`, which agrees. |
| I2 | human | BK-203 | Inventory says `live`. auction-site says `ended`. I can't tell which side is right. A person would need to check the auction site's end reason, for example whether the auction closed unsold or was cancelled, and whether the physical copy is still in stock. |
| I3 | human | BK-205 | shop-south lists "Annotated garden diary" as `live`. Inventory has no record of it. A person would need to confirm whether the item exists, for example by checking stock or a missing inventory entry. |
| I4 | human | BK-202 | shop-north has two identical rows, both `live`. Inventory also says `live`. A person would need to confirm whether these are one listing duplicated in the export or two separate listings. |

Four items were clean, with every channel that lists them matching inventory: BK-204, BK-206, BK-207 and BK-209. BK-207 matches once the inventory's `SOLD` and shop-south's ` sold` are trimmed and lowercased. BK-209 appears on three channels and all show `live`.

**What I did NOT do:** I made no changes and this was a read-only pass. I did not delist or mark anything sold on any channel. The I1 items are proposals for the queue only. The statuses are a snapshot from when the exports were taken.

```findings
[
  {"rule": "I1", "entity": "BK-201", "bucket": "confirmed"},
  {"rule": "I1", "entity": "BK-208", "bucket": "confirmed"},
  {"rule": "I2", "entity": "BK-203", "bucket": "human"},
  {"rule": "I3", "entity": "BK-205", "bucket": "human"},
  {"rule": "I4", "entity": "BK-202", "bucket": "human"}
]
```
