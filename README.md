# AI Marketing Playbook

Reusable patterns for running marketing and e-commerce operations with an AI agent, written up from workflows built and run in production for a small e-commerce business.

Not prompts. Not theory. Each pattern below is a workflow that has processed real listings, real outreach, and real inventory, generalized here so the structure (not the business) is the point.

## Patterns

| Pattern | What it solves |
|---|---|
| [Draft-first outreach](draft-first-outreach.md) | Let an agent write and stage outbound content across many channels, without ever giving it the power to publish |
| [Photo-to-multichannel listing](photo-to-multichannel-listing.md) | Turn one photoshoot into ready-to-review copy for every sales channel at once |
| [Cross-platform inventory sync](cross-platform-inventory-sync.md) | Catch the moment something sells on one channel before it oversells on another |

## See one running

[`.claude/agents/inventory-sync.md`](.claude/agents/inventory-sync.md) is
a working reference implementation of the cross-platform-inventory-sync
pattern, not just its description. Copy it into your own project's
`.claude/agents/`, point it at [`examples/sample-run/`](examples/sample-run/)
(three small CSV exports), and compare what it finds against
[`examples/sample-run/proposal-queue-output.md`](examples/sample-run/proposal-queue-output.md),
the actual, unedited output of a fresh agent run against that data. The
other two patterns are documented as workflow shape only, tool-agnostic
on purpose, see "Stack" below.

## Principles behind all three

- **The agent drafts, a human publishes.** Every pattern here produces output a person reviews before anything goes live. None of them hold posting or payment credentials.
- **One pass, not one click.** The unit of work is a batch (a photoshoot, a day's sales, a list of prospects), not a single item, because that's the shape the human's actual week takes.
- **State lives in one place.** Each pattern writes to a single system of record instead of scattering status across channels, so "what's the current state of X" always has one answer.

## Stack

Built with [Claude Code](https://claude.com/claude-code) as the agent runtime, driving a mix of browser automation and existing business tools (inventory database, storefronts, marketplaces). The patterns are tool-agnostic; the write-ups focus on the workflow shape rather than any specific integration.

## License

[MIT](LICENSE), take the patterns and adapt them to your own stack.
