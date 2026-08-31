# Cross-platform inventory sync

**Solves:** noticing that something sold on one sales channel before it oversells (or gets refunded and apologized for) on another.

## The problem

Selling the same one-of-a-kind or limited-stock items across multiple marketplaces and a storefront means the same item can look available in three places right after it sells in one. Checking this by hand means opening every platform, cross-referencing by eye, every day, forever. Nobody keeps that up, so the failure mode is a customer buying something that's already gone.

## The pattern

1. **Scan, don't touch.** On a schedule (or triggered by the first check-in of the day), the agent reads current listing status across every platform, read-only, no changes made yet.
2. **Cross-reference against a single source of truth.** Not platform A against platform B directly, everything gets compared against the one system that's supposed to reflect real inventory. Discrepancies (sold here, still listed there) get written to a proposal queue, not acted on immediately.
3. **Human reviews the queue.** A short list of "these look sold elsewhere, confirm and I'll delist," reviewed in one sitting.
4. **Apply, on confirmation.** Only after human sign-off does the agent actually delist, mark sold, or update stock counts, and it does so everywhere at once so the platforms don't drift out of sync with each other again immediately.

## Why this beats the alternatives

- **Versus manual daily checking:** the tedious, error-prone part (comparing several platforms by eye) is exactly what an agent is reliable at; the part that stays human is judgment on ambiguous cases (a bid but no sale yet, a platform that's slow to update).
- **Versus a webhook-based real-time sync:** most small sellers don't have API access to every platform they sell on. A scan-based approach works with whatever access exists, including plain browser access to a seller dashboard.
- **Versus fully automatic delisting:** an agent acting on a false positive (misreading a listing's status) at wire speed across every platform is a worse failure than a one-day delay while a human confirms.

## Where this breaks down

- Only as fresh as the last scan, real-time flash sales or high-velocity categories need tighter loops than a daily check.
- Depends on one platform being trustworthy as the source of truth. If that system itself lags reality, the whole comparison is built on sand, fix that first.

## Minimal implementation

An agent with read access to each platform (browser automation is enough), one system treated as ground truth for current stock, and a proposal-queue file or ticket the human clears in a single daily pass rather than being interrupted per discrepancy.
