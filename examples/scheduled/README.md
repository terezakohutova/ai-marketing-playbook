# Run-log examples for safe scheduled agents

Two small, invented run logs for three scheduled jobs (a nightly sync, a morning digest, a weekly heartbeat), each with the same `schedule.json` saying how often each job runs and which fields it may write.

- [`healthy/`](healthy/): every run present, writes only to allowed fields with the old value recorded, digests only when there is something in them. Expected result: all clear.
- [`broken/`](broken/): the sync stops, the heartbeat goes missing, the sync writes a human-owned field, creates a partner from an e-mail and overwrites a value without recording it, and the digest fires with nothing in it. Expected result: one finding per rule (S1 to S5), pinned in the tests.

```bash
python tools/run_log_check.py examples/scheduled/healthy
python tools/run_log_check.py examples/scheduled/broken
```

This is a deterministic check, not an agent. It is what the weekly heartbeat in [safe scheduled agents](../../safe-scheduled-agents.md) does with the run log.
