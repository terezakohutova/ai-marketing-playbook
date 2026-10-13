# crm-messy: the same kind of partner database, exported badly

No README date: "today" is the newest date in the activity log, 2026-11-20. Three exports, but not in the shape the checker expects: renamed and extra columns (`stage`, `prio`, `due`, `last_touch`, `notes`, a `phone` column), dates in three formats (`2026-11-20`, `19.11.2026`, `Nov 18 2026`), free-text statuses, an e-mail channel with its own name, and a delivery-failure notice that doesn't use the usual phrases.

10 partners, 12 contacts. Every name, address and number is invented. The planted problems are not listed here, so a run against this folder is blind. The expected findings were written by hand before any run, in [`tests/answer_keys/crm-messy.json`](../../../tests/answer_keys/crm-messy.json); the scored blind run is in [`examples/runs/crm-messy/`](../../runs/crm-messy/).

```bash
python tools/reference_check.py crm examples/crm/crm-messy   # refuses: missing columns
python tools/key_vs_checker.py                                 # key vs checker, every dataset
```
