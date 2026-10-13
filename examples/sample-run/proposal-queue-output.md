# Sample run: inventory-sync agent

**How this was produced (2026-10-13).** A fresh Claude Sonnet agent got the body of
[`.claude/agents/inventory-sync.md`](../../.claude/agents/inventory-sync.md) as its
instructions, read-only tools (Read, Grep, Glob), and a folder holding only
`cross-platform-inventory-sync.md` and the three CSVs below. No expected output, no
hint about which file is the source of truth or which items are the point. Everything
under the line is its output, unedited.

The planted cases are pinned in [`tests/test_reference_checks.py`](../../tests/test_reference_checks.py),
outside this folder so they don't leak into a run, and
[`tools/reference_check.py`](../../tools/reference_check.py) scores this file against
them: all 7 rule-derived findings are here, and the 4 clean items are not flagged.

Source files: [`storefront.csv`](storefront.csv), [`marketplace-a.csv`](marketplace-a.csv),
[`marketplace-b.csv`](marketplace-b.csv).

---

# Inventory sync proposal queue

**Source of truth:** `storefront.csv`. It is the storefront export, and the two marketplace files carry extra statuses (`reserved`) and an item it has never heard of, so it is the obvious ground truth. I compared `marketplace-a.csv` and `marketplace-b.csv` against it item by item, not against each other.

Status values were compared case- and whitespace-insensitively. Raw values are quoted below.

## Confirmed discrepancy (storefront says sold, a channel still shows live)

Each of these goes into the queue for human sign-off. None has been acted on.

| Item | Storefront | Marketplace A | Marketplace B | Proposal |
|---|---|---|---|---|
| ITM-014 Brass table lamp | `sold` | `live` | `live` | Delist on A and B |
| ITM-040 Walnut side table | `sold` | `sold` | `live` | Delist on B (A already agrees) |
| ITM-058 Pine step stool | `Sold` | `LIVE ` (capitalised, trailing space) | `sold` | Delist on A (B already agrees) |

## Needs a human call (not resolved by me)

| Item | Storefront | Marketplace A | Marketplace B | Why it is ambiguous and what would resolve it |
|---|---|---|---|---|
| ITM-022 Ceramic vase set | `live` | `live` | `sold` | B says sold, but the storefront does not corroborate it. Check B's order record: is there a real completed sale, or a stale or erroneous status? If the sale is real, the storefront is lagging and needs fixing first. |
| ITM-055 Rattan armchair | `live` | `sold` | `sold` | Both marketplaces say sold and the storefront says live. Two independent channels agreeing is suggestive, but the storefront is the source of truth and does not confirm it. Check for sale and payment records on A and B. Also check whether the storefront missed an update, or the item was sold twice. |
| ITM-043 Linen cushion pair | `live` | `reserved` | `live` | `reserved` is a status the storefront has no equivalent for. Find out whether it is a hold or an unpaid or unconfirmed order. If it turns into a sale, the storefront and B need to change. |
| ITM-052 Glass pendant light | not in storefront | `live` | not in B | Marketplace A lists an item the storefront has no record of. It could be a missing storefront row, a wrong ID, or an orphan listing. Someone needs to confirm whether the item exists in stock. |

## Clean

4 of the 11 distinct item IDs agree across all channels: ITM-031, ITM-035, ITM-061 and ITM-063.

## What I did NOT do

- I made no changes, and this was a read-only pass. Nothing was delisted, marked sold, or updated on any platform or in any file.
- I did not trust a marketplace's status over the storefront.
- I did not treat the `reserved` status or the unknown item ITM-052 as sold or delistable.
