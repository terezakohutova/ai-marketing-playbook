# Staged-draft outreach queue

[`queue.json`](queue.json) is an invented outreach queue in the shape the [draft-first outreach](../../draft-first-outreach.md) pattern uses: the agent adds drafts, a person approves a draft by recording their name, the time and the SHA-256 of the exact body they read, and the person sends it. [`tools/outreach_check.py`](../../tools/outreach_check.py) checks the queue after the fact.

Planted problems, one per rule: a draft sent with no approval, by the agent itself (O1, O3); a draft edited after it was approved (O2); a second message to the same contact inside the cooldown (O4); a draft staged for an excluded group (O5). The unsent, unapproved draft D05 is fine: staging is the agent's job.

```bash
python tools/outreach_check.py examples/outreach/queue.json
python tools/outreach_check.py examples/outreach/queue.json --hash D05   # what a reviewer records on approval
```

This is a deterministic check, not an agent, and it does not send anything. Where the real channel has a drafts folder or a draft-only API scope, the queue can be that folder; the check only needs an export of it.
