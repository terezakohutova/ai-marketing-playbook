**Proposal queue** (snapshot of the exports, read-only)

Columns used: `item_id` is the item id, `status` is the listing status, and `title` is the title. Inventory has no quantity columns, so I5 and I6 could not be checked. `inventory.csv` is the source of truth. The other three files are `auction-site.csv`, `shop-north.csv` and `shop-south.csv`.

| Rule | Bucket | Item | Evidence |
|---|---|---|---|
| I1 | confirmed | BK-201 | Inventory says "sold". auction-site, shop-north and shop-south all say "live". All three channels are stale. |
| I1 | confirmed | BK-208 | Inventory says "sold". shop-north says "live". (shop-south says "sold", which agrees.) |
| I2 | human | BK-203 | Inventory says "live". auction-site says "ended", which is neither live nor sold. To resolve it, someone needs to know whether the auction ended without a sale, so it should be relisted, or whether it ended for another reason. Please check the auction record and the physical stock. |
| I3 | human | BK-205 | shop-south lists "Annotated garden diary" as "live", but inventory has no record of it. To resolve it, someone needs to confirm whether the item exists and is missing from inventory, or whether the listing is an error. |
| I4 | human | BK-202 | shop-north has two rows for it, both "live". Inventory says "live". To resolve it, someone needs to check whether this is a duplicate row or two physical copies. |

4 items were clean: BK-204, BK-206, BK-207 and BK-209. BK-207 counts as clean because the case and spacing differences ("SOLD" and " sold") disappear after normalising. An item a channel doesn't list is not a discrepancy, so I raised nothing for those.

**What I did NOT do:** I made no changes and this was a read-only pass. Nothing was delisted, marked sold or edited on any channel. The I1 items are proposals for the queue only. I also did not read `cross-platform-inventory-sync.md`, because it isn't in the folder.

```findings
[
  {"rule": "I1", "entity": "BK-201", "bucket": "confirmed"},
  {"rule": "I1", "entity": "BK-208", "bucket": "confirmed"},
  {"rule": "I2", "entity": "BK-203", "bucket": "human"},
  {"rule": "I3", "entity": "BK-205", "bucket": "human"},
  {"rule": "I4", "entity": "BK-202", "bucket": "human"}
]
```
