# Partner CRM steward

**Solves:** a partner CRM that quietly rots. Duplicates, statuses that contradict reality, partners nobody has a next step for, contacts whose e-mail bounced months ago, and automations that stopped running without anyone noticing.

## The problem

A small team keeps its partners (brands, affiliates, suppliers, resellers) in one database. Everyone edits it, a few automations write into it, and nobody owns its health. The data looks fine row by row and is wrong as a whole: the same partner exists twice because an automation created a row from an e-mail, a "Paused" partner still has a live offer, the most important relationship has had no contact for six weeks. Nobody notices until a partner asks why they got the wrong deck, or a renewal date passes.

## The pattern

1. **Split the fields by owner.** Facts that can be pulled from somewhere else (live offers, revenue, last e-mail, sends) are machine-owned and get synced. Judgment fields (status, priority, next step and its date) are human-owned: the steward only ever flags them, never writes them.
2. **Three rhythms, each with one job.**
   - *Night:* read-only pulls from the systems of record into machine-owned fields and an append-only history section on each partner. No deletes, no rewrites of what a person typed.
   - *Morning:* read the mailbox for partner mail, update last contact and contacts (new people land as "to verify", bounces as "bounced"), and send one short digest **only if something needs a person today**.
   - *Weekly:* a full audit that always reports, even "all clear", so silence never means "the automation died".
3. **Audit in a fixed order**, from the most dangerous to the most cosmetic: automation health, integrity (duplicates, broken relations), consistency (status vs. what is actually live), action (missing or overdue next steps, relationships going cold against a cadence set by priority), contacts, data gaps, trend vs. last week.
4. **Propose, then fix only the safe class.** Typos in machine-owned fields, a missing link that has exactly one candidate: marked safe to apply, then applied by a routine that may write only those fields, and logged. Merging duplicates, changing a status, closing a partner: proposed with evidence, done after a yes.
5. **Pilot every change to the automation on a few partners first**, with the partner list as a setting, before it touches all of them.

## Why this beats the alternatives

- **Versus "everyone keeps it tidy":** nobody does, because nobody sees the whole table. The steward's value is the cross-row view (duplicates, cadence, contradictions) a person editing one row never has.
- **Versus a CRM's built-in automation that creates and updates records freely:** auto-creating partners from e-mails is the classic source of duplicates. Here nothing creates a partner and nothing overwrites a human-owned field.
- **Versus alerts on every change:** a digest that only fires when action is needed gets read. The weekly heartbeat covers the opposite failure, an automation that silently stopped.

## Where this breaks down

- It can only see what has an API or an export. Opens, clicks and in-app conversions often live in tools a scheduled agent cannot reach; say so in the report instead of pretending the numbers are complete.
- Cadence thresholds (how long until a partner is "cold") are a business decision. Wrong thresholds produce a digest full of noise and the team stops reading it.
- If the team never answers the proposals, the queue just grows. Keep it short and ranked.

## Minimal implementation

A database with the owner split above, scheduled agent runs (a cloud routine or cron) with read access to the systems of record and write access only to machine-owned fields, a run log, and an on-demand agent for audits: [`.claude/agents/crm-steward.md`](.claude/agents/crm-steward.md). That agent is the audit half only and is read-only by its tool list: it marks the safe class of fixes as "safe to apply" but never applies them. Applying them (step 4) belongs to the scheduled routine, under the rules in [safe scheduled agents](safe-scheduled-agents.md).

Applying a confirmed proposal is a separate, person-started step: [`tools/apply_changes.py`](tools/apply_changes.py) takes a signed changes file, refuses anything stale or two changes to one field, replaces each file atomically and logs old and new values, with a journal that makes a half-finished apply visible ([example](examples/apply/)).

The agent has three clean sample exports and one messy one (renamed columns, mixed date formats, free-text statuses) in [`examples/crm/`](examples/crm/), a hand-written answer key for each in [`tests/answer_keys/`](tests/answer_keys/), and unedited blind runs (one per clean dataset, three for the messy one) in [`examples/runs/`](examples/runs/). [`tools/score_run.py`](tools/score_run.py) scores each run's findings block against its key; the current numbers are in the [README](README.md#results).
