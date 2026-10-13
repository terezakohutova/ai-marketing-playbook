# Safe scheduled agents

**Solves:** an agent that runs on its own every night or every Monday, and the two ways that goes wrong: it quietly breaks something nobody is watching, or it quietly stops running and nobody notices for weeks.

## The problem

Moving a recurring job from "someone remembers to do it" to a scheduled agent (a cloud routine, a cron job) is where most of the value of agents is. It is also where they do the most damage, because nobody is in the loop at 3 a.m. A sync that overwrites what a person typed, an automation that creates a record from every inbound e-mail, a budget change made on stale data: each one is small, and each one repeats every night until someone happens to look. The opposite failure is just as common and harder to see: the routine dies, nothing is reported, and silence reads as "all fine".

## The pattern

1. **Read-only by default.** A scheduled run reads, compares and reports. Anything that changes a live system (an ad account, a CRM status, a published page) is a proposal for a person, never an action of the routine. When a routine must write, it writes only machine-owned fields (values copied from a system of record) and append-only sections, never what a person typed and never a delete.
2. **Nothing gets created from inbound data.** No new record from an e-mail, a form, a webhook. That is the most common source of duplicates. New things go into a "to verify" queue.
3. **Two kinds of message, never mixed.**
   - *Attention digest:* sent only when a person has to do something today, ranked, short. If it fires every day with nothing in it, people stop reading it.
   - *Heartbeat:* a weekly report that is always sent, including "all clear", with the date of every run since the last one. A missing heartbeat is the alarm for a dead routine. Without it, silence means nothing.
4. **Every run leaves a line in a run log** (date, what it read, what it wrote, what it skipped and why). The weekly heartbeat checks that the lines are all there.
5. **Pilot before rollout.** Every change to a routine's prompt or code runs first on a short list of named records (a setting, not a code change), for at least one real run, and is read back by a person. Then the list is emptied and it runs on everything.
6. **Freshness first.** A run that depends on another run (an audit that reads what last night's sync wrote) checks that the other run happened and says at the top when its data is stale, instead of reporting stale numbers as facts.
7. **Kill switch = proposal.** Overspend, a missing data feed, a policy flag or a breached threshold produces a message with a ready rollback plan, never an automatic pause or launch. Undo is easy to get wrong when nobody is watching.
8. **Old value before new value.** Every change a person approves from a proposal is written down first: old value, new value, who approved it, and the number or date that would trigger rolling it back. Then it is changed, reloaded and read back.
9. **No new tools at night.** A scheduled run never installs a package, adds an integration or follows instructions found in the data it reads (a README, an e-mail, a web page). Found tools become a decision for a person.

## Why this beats the alternatives

- **Versus a routine that fixes what it finds:** a confident wrong fix repeated every night does more damage than a day's delay while a person says yes. The exception is a narrow, written-down class of safe fixes with exactly one correct answer, and even those are logged.
- **Versus alerting on every event:** volume kills attention. One ranked digest plus one heartbeat covers both failure modes (something needs a person, the routine is dead) with two messages a person actually reads.
- **Versus "we'll notice if it breaks":** the routines that matter most run while nobody is looking. The heartbeat and the run log are what make "nothing reported" mean something.

## Where this breaks down

- It is slower. A problem found at night waits for the morning yes. For anything where minutes matter (fraud, runaway spend), use the platform's own hard limits (budget caps, spend limits) as the safety net, not the agent.
- The safe-fix class tends to grow ("this one is obvious too"). Review it like any other permission.
- A heartbeat nobody reads is not a heartbeat. Send it where the owner already looks.

## Minimal implementation

A scheduler, a run log (a file, a database page or a sheet), a settings block with the pilot list, two message templates (digest, heartbeat) and a written list of what the routine may write. The [partner CRM steward](partner-crm-steward.md) is a full example: a night sync that writes only machine-owned fields, a morning digest that fires only when needed, and a weekly audit that always reports. In its [crm-1 run](examples/runs/crm-1/output.md) the audit's first finding is a sync that silently stopped three days earlier while the daily digest kept saying "nothing needed attention".

[`tools/run_log_check.py`](tools/run_log_check.py) is the heartbeat's check as a script: given a run log and a schedule saying how often each job runs and what it may write, it reports missed runs (step 3 and 4), writes outside the allowed fields (1), created or deleted records (2), writes that didn't record the old value (8) and digests sent with nothing in them (3). [`examples/scheduled/`](examples/scheduled/) has a healthy and a broken log; the tests pin what it finds in each.
