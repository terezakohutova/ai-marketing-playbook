# crm-1: a small brand's partner database

As of **2026-10-13** (also the newest date in `activity.csv`). Three exports, the way a small team's CRM would export them: `partners.csv` (status, priority, owner, next step, live offers), `contacts.csv` (people and the status of their address) and `activity.csv` (e-mails plus the nightly sync and the morning digest, which should each log one line every day).

10 partners, 11 contacts. The sample the README preview comes from.

Every name, address and number is invented. The planted problems are not listed here, so a run against this folder is blind. The expected findings are in [`tests/answer_keys/crm-1.json`](../../../tests/answer_keys/crm-1.json), outside this folder; the scored blind run is in [`examples/runs/crm-1/`](../../runs/crm-1/).

```bash
python tools/reference_check.py crm examples/crm/crm-1   # what the written rules produce
```
