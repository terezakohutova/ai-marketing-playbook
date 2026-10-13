# Applying confirmed proposals

[`crm-1-confirmed.json`](crm-1-confirmed.json) holds the two "safe to apply" proposals from the [crm-1 run](../runs/crm-1/output.md), as they would look after a person read them and said yes. [`tools/apply_changes.py`](../../tools/apply_changes.py) applies such a file: it checks every change first (named approver, row exists exactly once, current value still equals the proposal's old value), writes the old and new value to a change log, and only then changes the CSV. All or nothing.

```bash
python tools/apply_changes.py examples/crm/crm-1 examples/apply/crm-1-confirmed.json --dry-run
```

Run it without `--dry-run` on a copy of the folder; it edits the CSVs in place.
