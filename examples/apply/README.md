# Applying confirmed proposals

[`crm-1-confirmed.json`](crm-1-confirmed.json) holds the two "safe to apply" proposals from the [crm-1 run](../runs/crm-1/output.md), as they would look after a person read them and said yes. [`tools/apply_changes.py`](../../tools/apply_changes.py) applies such a file: it checks every change first (named approver, row exists exactly once by its id column, no two changes to the same field, current value still equals the proposal's old value). Then it writes each changed CSV to a temporary file, records the planned changes in a journal, swaps the temporary files in, appends old and new values to the change log and removes the journal. If a run stops half way, the journal stays and the next run refuses to start until a person has looked.

```bash
python tools/apply_changes.py examples/crm/crm-1 examples/apply/crm-1-confirmed.json --dry-run
```

Run it without `--dry-run` on a copy of the folder; it edits the CSVs in place.
