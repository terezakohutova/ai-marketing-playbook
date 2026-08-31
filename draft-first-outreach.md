# Draft-first outreach

**Solves:** getting an agent to do real outbound work (cross-posting, connection requests, follow-ups) without ever letting it press send.

## The problem

Outreach is repetitive enough to automate and risky enough that you don't want an agent freelancing your voice in public, on your behalf, at scale. Most "AI marketing automation" demos skip straight to auto-posting, which is exactly the part that goes wrong first: wrong tone, wrong group, wrong day, and it's already live.

## The pattern

1. **Agent picks the targets.** Given a piece of content and a set of destinations (a list of groups, a list of prospects), the agent decides what goes where, based on rules that already exist (category match, exclusion lists, "we already reached this contact this month").
2. **Agent writes the draft per destination.** Not one message copy-pasted everywhere. Each destination gets its own draft in a voice appropriate to that channel, referencing the same underlying content or offer.
3. **Agent stages, never sends.** Every draft is left open and visible (a browser tab, a drafts folder, a review queue) in its native tool. The agent's job stops at "ready to review."
4. **Human does one pass.** A person skims the batch and hits send/publish themselves, channel by channel. This is the only step with a publish-capable credential in play, and it's a human's finger on it.

## Why this beats the alternatives

- **Versus full automation:** a bad auto-post to one channel is a bad post to one channel; a bad auto-post to twelve channels because the agent misjudged tone is a cleanup job. Draft-first caps the blast radius at "you'll notice before it goes out."
- **Versus doing it manually:** the agent still does the actual writing and channel-matching work, which is most of the effort. The human's remaining job is judgment, not typing.
- **Versus a single generic message:** per-destination drafting respects that a marketplace group, a cold connection request, and an existing customer are different conversations, even about the same thing.

## Where this breaks down

- Channels with hard rate limits or anti-bot detection need the human-paced review step anyway, so this pattern doesn't save time there, only quality.
- It assumes the human review pass actually happens. If drafts pile up unreviewed, you've built a to-do list generator, not an outreach system, budget calendar time for the review pass.

## Minimal implementation

An agent with browser access, a rules file describing what content maps to what destinations and any exclusions, and a lightweight way to track "already reached" so re-runs don't duplicate outreach. No posting credentials in the agent's hands, ever, just the ability to open tabs and type.
