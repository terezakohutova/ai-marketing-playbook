# AI Marketing Playbook

[![CI](https://github.com/terezakohutova/ai-marketing-playbook/actions/workflows/check.yml/badge.svg)](https://github.com/terezakohutova/ai-marketing-playbook/actions/workflows/check.yml)

AI agent patterns for marketing and e-commerce operations (data hygiene, CRM, inventory, outreach): five ways to let an agent do the work without letting it publish, delete or spend on its own.

**Scope:** operations for a small online seller or brand: keeping sales channels, a partner CRM and recurring automations correct. Not ad buying, content strategy or analytics.

**What this is and isn't.** Each pattern is the shape of an operations workflow, with the business taken out. The repo does not measure their effect on a business (no time saved, no revenue, no error rates in production), so it makes no such claim. What it does measure is narrower: whether the two shipped agents apply their written rules correctly to planted data they have never seen, including messy exports that a script can't read, scored against hand-written answer keys.

## Patterns

| Pattern | What it solves | What ships |
|---|---|---|
| [Cross-platform inventory sync](cross-platform-inventory-sync.md) | Compare snapshot exports of every sales channel against one source of truth and queue what is stale or oversold (single items and multi-unit stock), for a person to confirm | **Runnable:** [agent](.claude/agents/inventory-sync.md), 3 clean + 1 messy dataset, blind runs, scorer |
| [Partner CRM steward](partner-crm-steward.md) | Keep a partner database honest: duplicates, contradicting statuses, missing next steps, cooling relationships, bounced contacts and silently dead automations | **Runnable:** [agent](.claude/agents/crm-steward.md), 3 clean + 1 messy dataset, blind runs, scorer, [apply step](examples/apply/) |
| [Safe scheduled agents](safe-scheduled-agents.md) | Let an agent run every night or every week without quietly breaking things, and notice when it quietly stops running | **Runnable check, no agent:** [run-log checker](tools/run_log_check.py) with a [healthy and a broken log](examples/scheduled/) |
| [Draft-first outreach](draft-first-outreach.md) | Let an agent write and stage outbound content across many channels, without giving it the job of publishing | **Runnable check, no agent:** [queue checker](tools/outreach_check.py) (approval before send, approved text = sent text, cooldown, exclusions) with an [example queue](examples/outreach/) |
| [Photo-to-multichannel listing](photo-to-multichannel-listing.md) | Turn one photoshoot into ready-to-review copy for every sales channel at once | Design note only: nothing runnable ships for it |

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

Copy only the CSVs if you want your run to be blind: the dataset READMEs describe what kinds of cases are planted. The same works for `inventory-sync.md` with `examples/inventory/inv-*/`. To repeat a committed run exactly the way it was made (fresh session, only the agent definition and the CSVs, read-only tools), use the harness: `python tools/blind_run.py crm-2 --work-dir <run-dir>`.

## How the runs are checked

A model's own report is not proof, so every run gets a second, boring opinion.

1. **Rules with ids.** Each agent definition has a rule table (CRM: A1 to F4, inventory: I1 to I6) saying exactly when a finding fires, what entity it is about and who decides the fix. One finding is one (rule, entity) pair, so a duplicate pair is one finding and a partner with three problems is three.
2. **A machine-readable block.** The agent must end its output with a fenced `findings` block: a JSON list of `{"rule", "entity", "bucket"}`. Only that block is scored.
3. **Answer keys written by hand**, per dataset, in [`tests/answer_keys/`](tests/answer_keys/), with the expected findings and a list of near-misses that must not be flagged. They live outside the input folders. The tests require every rule to have at least one positive and one negative case across the keys.
4. **A mechanical checker**, [`tools/reference_check.py`](tools/reference_check.py), applies the written rules to clean CSVs. It is a second opinion, not the source of the keys: [`tools/key_vs_checker.py`](tools/key_vs_checker.py) lists every finding only one of them has, and the tests pin that outcome per dataset, so a disagreement can't be hidden by editing either side.
5. **A scorer**, [`tools/score_run.py`](tools/score_run.py), compares a run's block with the key and reports precision and recall, overall and per rule. Wrong flags, wrong buckets, unknown rules and catch-all entities ("all", "P01-P10", a list) count against precision. The tests show that a junk table row, a block of catch-all entities, and a block that flags every rule for every entity all score badly.

```bash
python tools/score_run.py --all --per-rule
python tools/key_vs_checker.py
python -m unittest discover -s tests -v
```

**Why the clean datasets alone prove little.** On the six clean datasets the checker and the keys agree on every finding. An agent scoring 1.00 there has matched what a few hundred lines of script also get, so those runs show rule-following, not value. The two messy datasets ([crm-messy](examples/crm/crm-messy/), [inv-messy](examples/inventory/inv-messy/)) are built to be what a script can't handle: renamed and extra columns, dates in three formats (`2026-11-20`, `19.11.2026`, `Nov 18 2026`), free-text statuses (`live-ish (soft launch)`, `Paused till Feb`, `Sold out`), an e-mail logged under `E-mail (inbound)`, a bounce whose first address is the postmaster, notes that carry the real signal ("asked for an extension"), and multi-unit stock. Their keys were written by hand before any model saw the data.

What the checker does with them is pinned in the tests: on the raw files it stops at the missing columns. With the headers renamed by hand it stops at the first non-ISO date (CRM), or runs and gets 4 of 9 inventory findings wrong ("Sold out" is not "sold", "Active" is not "live"). With dates converted too, it still misses 3 CRM findings and adds 2 wrong ones (it takes the `E-mail (inbound)` channel for a broken scheduled job and calls a partner cold who wrote last week).

### Results

Eight blind runs, one per dataset, made on 2026-10-14 with [`tools/blind_run.py`](tools/blind_run.py): a fresh, non-interactive Claude Code session (model: sonnet) in an empty folder holding only a copy of the agent definition and the dataset's CSVs. The agent definition was the whole system prompt and the session had only the Read, Grep and Glob tools, so it could not write, edit or run anything; the harness saved its final answer. Outputs are unedited apart from LF line endings; each folder's `run.json` has the exact command, prompt and file hashes, and a test checks those hashes against the files.

| Pattern | Dataset | Findings in key | Caught | Wrong flags | Precision | Recall |
|---|---|---|---|---|---|---|
| Inventory sync | [inv-1](examples/runs/inv-1/output.md) | 7 | 7 | 0 | 1.00 | 1.00 |
| Inventory sync | [inv-2](examples/runs/inv-2/output.md) | 6 | 6 | 0 | 1.00 | 1.00 |
| Inventory sync | [inv-3](examples/runs/inv-3/output.md) | 5 | 5 | 0 | 1.00 | 1.00 |
| Inventory sync | [**inv-messy**](examples/runs/inv-messy/output.md) | 9 | 9 | 0 | 1.00 | 1.00 |
| CRM steward | [crm-1](examples/runs/crm-1/output.md) | 13 | 13 | 0 | 1.00 | 1.00 |
| CRM steward | [crm-2](examples/runs/crm-2/output.md) | 11 | 11 | 0 | 1.00 | 1.00 |
| CRM steward | [crm-3](examples/runs/crm-3/output.md) | 11 | 11 | 0 | 1.00 | 1.00 |
| CRM steward | [**crm-messy**](examples/runs/crm-messy/output.md) | 16 | 15 | 0 | 1.00 | 0.94 |

The messy rows are where the model adds something over the script: it mapped the renamed columns and said how, read all three date formats, mapped the free-text statuses and quoted them, treated the `E-mail (inbound)` line as contact and took the failed address from the `Final-Recipient` line. The checker, on the same files, refuses them or gets them wrong as described above.

The one miss is worth spelling out. The crm-messy key as first written didn't have E2 for P05 (a Lost partner whose only contact is Former), and the blind run didn't flag it either. Comparing the key with the checker on the repaired files showed it: the rule has no open-partner condition, and the clean crm-1 key already flags the same case. The key was corrected after the run (recorded in its `revisions` field) and the run is scored as missing it. So this is one place where the script caught something both the model and its author missed.

How to read all of it: the datasets are small (9 to 12 entities each), each run happened once, and the messy cases were planted by the same person who wrote the rules, so they are messy in ways the agent definition anticipates. It doesn't show how often the agents would get it right on a second run (an [earlier run](examples/runs/crm-1/earlier/audit-output-rerun.md) under a looser spec missed one finding), or on a real export that is messy in ways nobody planned. That is the reason the patterns put a person and a deterministic check after the agent rather than trusting one pass.

Standard library Python 3.9+ only, nothing to install. CI runs the tests, the scorer and the link check on Python 3.9 and 3.13, on Ubuntu and Windows, plus [ruff](https://docs.astral.sh/ruff/).

## Principles behind all of them

- **The agent drafts, a human publishes.** Every pattern produces output a person reviews before anything goes live, and none of them give the agent posting, payment or delete rights. The two shipped agents declare that in their tool list (`Read, Grep, Glob`). Claude Code enforces a subagent's `tools:` line, and the committed runs were made with exactly those tools and nothing else (see Results), so they could not change a file even if told to. If you copy the prompt text somewhere without the tool list, the guarantee doesn't come with it. Where a tool can't separate drafting from publishing (a logged-in browser), the pattern says so.
- **Audit and apply are separate steps.** The shipped agents only audit and propose. Applying is a second step a person starts: they copy the proposals they agree with into a changes file with their name on it, and [`tools/apply_changes.py`](tools/apply_changes.py) applies it, refusing anything stale, unsigned or two changes to one field, replacing each file atomically, and keeping a journal so a half-finished apply is noticed ([example](examples/apply/)).
- **One pass, not one click.** The unit of work is a batch (a photoshoot, a day's sales, a list of prospects), not a single item, because that's the shape the human's actual week takes.
- **One answer to "what's the current state".** Each pattern names one system of record that is treated as the truth (the storefront for stock, the CRM for partners, the run log for automations) and compares everything else against it, instead of scattering status across channels.

## Stack

Built with [Claude Code](https://claude.com/claude-code) as the agent runtime, driving a mix of browser automation and existing business tools (inventory database, storefronts, marketplaces, CRM). The write-ups focus on the workflow shape rather than any specific integration, so the patterns without an agent are tool-agnostic on purpose.

## License

[MIT](LICENSE). Take the patterns and adapt them to your own stack.
