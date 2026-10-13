## Inventory sync proposal queue

Source of truth: `storefront.csv`. Compared against `marketplace-a.csv` and `marketplace-b.csv`. Statuses were trimmed and compared case-insensitively.

- **I1, confirmed, ITM-014 (Brass table lamp):** storefront says `sold`, marketplace-a says `live` and marketplace-b says `live`. Proposal: delist on both marketplaces.
- **I1, confirmed, ITM-040 (Walnut side table):** storefront says `sold`, marketplace-a says `sold`, marketplace-b says `live`. Proposal: delist on marketplace-b.
- **I1, confirmed, ITM-058 (Pine step stool):** storefront says `Sold`, marketplace-a says `LIVE ` (live after trimming and ignoring case), marketplace-b says `sold`. Proposal: delist on marketplace-a.
- **I2, human, ITM-022 (Ceramic vase set):** storefront says `live`, marketplace-a says `live`, marketplace-b says `sold`. Needs the sales record or order, or a physical check, to show whether it sold on marketplace-b. If it did, the storefront and marketplace-a are stale.
- **I2, human, ITM-043 (Linen cushion pair):** storefront says `live`, marketplace-a says `reserved`, marketplace-b says `live`. Needs the marketplace-a reservation details (buyer, expiry) to show whether a hold is genuine or stale.
- **I2, human, ITM-055 (Rattan armchair):** storefront says `live`, marketplace-a says `sold`, marketplace-b says `sold`. Both marketplaces say sold and the storefront does not. Needs the order or payment records, or a physical stock check. Neither side is trusted here.
- **I3, human, ITM-052 (Glass pendant light):** marketplace-a lists it as `live`. The storefront has no record of it, and marketplace-b does not list it. Needs confirmation of whether the item exists in stock and was left out of the storefront, or whether the listing is orphaned.

I4 (the same item on more than one row of a file) did not fire in any file.

Clean: 4 items (ITM-031, ITM-035, ITM-061, ITM-063) agree with the source of truth on every channel that lists them.

### What I did NOT do
I made no changes. This was a read-only pass, and nothing was delisted, marked sold or edited. All of the above are proposals for a human to approve.

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
