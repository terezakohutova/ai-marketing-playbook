# Sample run: inventory-sync agent

A fresh agent was given only `.claude/agents/inventory-sync.md`, the
`cross-platform-inventory-sync.md` pattern doc, and the three CSVs in this
folder, no expected output, no hint about which item was the point of
the exercise. This is the actual, unedited result.

Source files:
- [`storefront.csv`](storefront.csv), the source of truth
- [`marketplace-a.csv`](marketplace-a.csv)
- [`marketplace-b.csv`](marketplace-b.csv)

## What it found

**Source of truth:** `storefront.csv`, identified correctly from context
alone, the agent was never told which file was which.

**1 item clean** (all channels agree with storefront): ITM-031, Oak
bookshelf.

**ITM-014, Brass table lamp, confirmed discrepancy**
Evidence: storefront = sold; marketplace-a = live; marketplace-b = live.
Both marketplace channels are stale against the source of truth.
Delist candidate on both, pending human confirmation, not actioned.

**ITM-022, Ceramic vase set, needs a human call**
Evidence: storefront = live; marketplace-a = live; marketplace-b = sold.
Marketplace-b shows sold but storefront doesn't corroborate it, could be
a real sale not yet reflected in storefront, or a stale/incorrect status
on marketplace-b. The agent didn't resolve this by trusting either side,
it named what would resolve it: check marketplace-b's own order record,
or storefront's order log, for an actual transaction around this item.

**What it did not do:** no changes to any listing, status, or file. Both
items above are flagged for human confirmation before any delist or
status update happens, exactly as the pattern specifies.

## Why this is the useful case

ITM-014 is the easy one, an agent could get that right by just trusting
whichever platform says "sold." ITM-022 is the one the pattern doc exists
for: a signal that could be a real sale or could be a stale platform, and
the agent's job is to say which is which as far as it can, then hand off
the ambiguous part rather than guessing.
