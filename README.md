# AI Marketing Playbook

[![CI](https://github.com/terezakohutova/ai-marketing-playbook/actions/workflows/check.yml/badge.svg)](https://github.com/terezakohutova/ai-marketing-playbook/actions/workflows/check.yml)

Five patterns for letting an AI agent do marketing and e-commerce operations work (outreach, listings, inventory, partner CRM, scheduled runs) without letting it publish, delete or spend on its own.

**Scope:** operations for a small online seller or brand: keeping sales channels, a partner CRM and recurring automations correct. Not ad buying, content strategy or analytics.

**What this is and isn't.** Each pattern is the shape of an operations workflow, with the business taken out. The repo does not measure their effect on a business (no time saved, no revenue, no error rates in production), so it makes no such claim. What it does measure is narrower: whether the two shipped agents apply their written rules correctly to planted data they have never seen, scored by a deterministic check.

## Patterns

| Pattern | What it solves | What ships |
|---|---|---|
| [Cross-platform inventory sync](cross-platform-inventory-sync.md) | Catch the moment something sells on one channel before it oversells on another | **Runnable:** [agent](.claude/agents/inventory-sync.md), 3 datasets, blind runs, scorer |
| [Partner CRM steward](partner-crm-steward.md) | Keep a partner database honest: duplicates, contradicting statuses, missing next steps, cooling relationships, bounced contacts and silently dead automations | **Runnable:** [agent](.claude/agents/crm-steward.md), 3 datasets, blind runs, scorer, [apply step](examples/apply/) |
| [Safe scheduled agents](safe-scheduled-agents.md) | Let an agent run every night or every week without quietly breaking things, and notice when it quietly stops running | **Runnable check, no agent:** [run-log checker](tools/run_log_check.py) with a [healthy and a broken log](examples/scheduled/) |
| [Draft-first outreach](draft-first-outreach.md) | Let an agent write and stage outbound content across many channels, without giving it the job of publishing | Written pattern only |
| [Photo-to-multichannel listing](photo-to-multichannel-listing.md) | Turn one photoshoot into ready-to-review copy for every sales channel at once | Written pattern only |

## See one running

![Excerpt of an earlier blind crm-steward run against the crm-1 sample](examples/runs/crm-1/earlier/preview.png)

An excerpt of an [earlier blind run](examples/runs/crm-1/earlier/audit-output.md) on the [crm-1 sample](examples/crm/crm-1/): the agent's first finding is that the nightly sync had silently stopped three days earlier while the daily digest kept reporting "nothing needed attention". The current, scored run on the same data is [`examples/runs/crm-1/output.md`](examples/runs/crm-1/output.md).

## Try it

The two agents are [Claude Code](https://claude.com/claude-code) subagents. Copy one into your own project and point it at a dataset:

```bash
cp .claude/agents/crm-steward.md <your-project>/.claude/agents/
mkdir -p <your-project>/crm-export && cp examples/crm/crm-2/*.csv <your-project>/crm-export/
# then, in Claude Code: "audit the partner CRM export in crm-export/"
python tools/score_run.py tests/answer_keys/crm-2.json <your saved output>.md
```

Copy only the CSVs if you want your run to be blind: the dataset READMEs describe what kinds of cases are planted. The same works for `inventory-sync.md` with `examples/inventory/inv-*/`.

## How the runs are checked

A model's own report is not proof, so every run gets a second, boring opinion.

1. **Rules with ids.** Each agent definition has a rule table (CRM: A1 to F4, inventory: I1 to I4) saying exactly when a finding fires, what entity it is about and who decides the fix. One finding is one (rule, entity) pair, so a duplicate pair is one finding and a partner with three problems is three.
2. **A machine-readable block.** The agent must end its output with a fenced `findings` block: a JSON list of `{"rule", "entity", "bucket"}`. Only that block is scored.
3. **Answer keys written by hand**, per dataset, in [`tests/answer_keys/`](tests/answer_keys/), with the expected findings and a list of near-misses that must not be flagged. They live outside the input folders.
4. **A mechanical checker**, [`tools/reference_check.py`](tools/reference_check.py), applies the written rules to the CSVs. The tests require it to agree exactly with every answer key, and require every rule to have at least one positive and one negative case across the datasets.
5. **A scorer**, [`tools/score_run.py`](tools/score_run.py), compares a run's block with the key and reports precision and recall, overall and per rule. Wrong flags, wrong buckets, unknown rules and catch-all entities ("all", "P01-P10", a list) count against precision. The tests show that a junk table row, a block of catch-all entities, and a block that flags every rule for every entity all score badly.

```bash
python tools/score_run.py --all --per-rule
python -m unittest discover -s tests -v
```

### Results

Six blind runs, one per dataset, all on 2026-10-13: a fresh Claude Code subagent (model: sonnet) given only a copy of the agent definition and the dataset's CSVs, nothing else. Outputs are unedited; each folder's `run.json` has the exact prompt and file hashes.

| Pattern | Dataset | Findings in key | Caught | Wrong flags | Precision | Recall |
|---|---|---|---|---|---|---|
| Inventory sync | [inv-1](examples/runs/inv-1/output.md) | 7 | 7 | 0 | 1.00 | 1.00 |
| Inventory sync | [inv-2](examples/runs/inv-2/output.md) | 6 | 6 | 0 | 1.00 | 1.00 |
| Inventory sync | [inv-3](examples/runs/inv-3/output.md) | 5 | 5 | 0 | 1.00 | 1.00 |
| CRM steward | [crm-1](examples/runs/crm-1/output.md) | 13 | 13 | 0 | 1.00 | 1.00 |
| CRM steward | [crm-2](examples/runs/crm-2/output.md) | 11 | 11 | 0 | 1.00 | 1.00 |
| CRM steward | [crm-3](examples/runs/crm-3/output.md) | 11 | 11 | 0 | 1.00 | 1.00 |

How to read that: the datasets are small (9 to 12 entities each) and the rules are written out precisely, so this shows that the agents follow a precise spec on data they haven't seen, once each. It doesn't show how often they would on a second run (an [earlier run](examples/runs/crm-1/earlier/audit-output-rerun.md) under a looser spec missed one finding), or how they do on messy real exports. That is the reason the patterns put a person and a deterministic check after the agent rather than trusting one pass.

Standard library Python 3.9+ only, nothing to install. CI runs the tests, the scorer and the link check on Python 3.9 and 3.13, on Ubuntu and Windows, plus [ruff](https://docs.astral.sh/ruff/).

## Principles behind all of them

- **The agent drafts, a human publishes.** Every pattern produces output a person reviews before anything goes live, and none of them give the agent posting, payment or delete rights. The two shipped agents enforce that with their tool list (`Read, Grep, Glob`), not just their prompt: they cannot change a file even if told to. Where a tool can't separate drafting from publishing (a logged-in browser), the pattern says so.
- **Audit and apply are separate steps.** The shipped agents only audit and propose. Applying is a second step a person starts: they copy the proposals they agree with into a changes file with their name on it, and [`tools/apply_changes.py`](tools/apply_changes.py) applies it, refusing anything stale or unsigned and writing the old value to a change log before it writes the new one ([example](examples/apply/)).
- **One pass, not one click.** The unit of work is a batch (a photoshoot, a day's sales, a list of prospects), not a single item, because that's the shape the human's actual week takes.
- **One answer to "what's the current state".** Each pattern names one system of record that is treated as the truth (the storefront for stock, the CRM for partners, the run log for automations) and compares everything else against it, instead of scattering status across channels.

## Stack

Built with [Claude Code](https://claude.com/claude-code) as the agent runtime, driving a mix of browser automation and existing business tools (inventory database, storefronts, marketplaces, CRM). The write-ups focus on the workflow shape rather than any specific integration, so the two written-only patterns are tool-agnostic on purpose.

## License

[MIT](LICENSE). Take the patterns and adapt them to your own stack.
