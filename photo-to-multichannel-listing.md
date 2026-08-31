# Photo-to-multichannel listing

**Solves:** turning a batch of raw product photos into ready-to-review listing copy for every sales channel at once, instead of writing each one by hand, per channel, per item.

## The problem

A single photoshoot day produces items that need to exist in several places: a marketplace listing, a storefront product page, a social caption, sometimes an image-generation prompt for a styled shot. Written by hand, that's the same information re-typed four different ways, in four different tones, for every single item. It's the kind of work that gets postponed precisely because it's tedious, not because it's hard.

## The pattern

1. **One drop, one batch.** The human's part of the job ends at "photos are in a folder." No per-item setup.
2. **Agent identifies each item from the photos**, pulling out the attributes that matter for that category (material, condition, era, dimensions, whatever the business actually sells on).
3. **Agent writes channel-specific copy from the same attributes.** A marketplace listing optimizes for search terms and category fields. A caption optimizes for voice and a hook. A product page optimizes for scannable structure. Same underlying facts, different shape per destination, generated together so they can't drift out of sync with each other.
4. **Everything lands in one place for review.** Not four separate outputs to hunt down, one row per item in whatever system already tracks inventory, with each channel's draft attached and a status field for "reviewed" versus "not yet."
5. **Human does one review pass per batch**, not per item. Approve, edit, or reject each field, then publish channel by channel using existing tools.

## Why this beats the alternatives

- **Versus writing each channel by hand:** the expensive part (looking at the item, deciding what's true and interesting about it) happens once, not four times.
- **Versus a single generic description copy-pasted everywhere:** every channel keeps its native strengths, a marketplace listing still reads like a marketplace listing.
- **Versus doing this per item as items are photographed:** batching matches how the photography actually happens (a shoot day, not a trickle), so the human's review time is also batched into one sitting instead of a dozen interruptions.

## Where this breaks down

- Needs a category taxonomy the agent can actually apply consistently, undefined or overlapping categories produce inconsistent attribute extraction.
- Image-only identification has a real error rate on ambiguous items (unmarked materials, unclear maker's marks). The review pass exists specifically to catch this, don't skip it to save time.

## Minimal implementation

An agent with image reading, a category schema, access to whatever system already holds inventory (a spreadsheet or database works fine), and per-channel copy templates written once and reused every batch.
