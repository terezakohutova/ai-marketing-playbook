# crm-3: an outdoor brand's partners across a year end

As of **2027-01-15** (also the newest date in `activity.csv`). Three exports, the way a small team's CRM would export them: `partners.csv` (status, priority, owner, next step, live offers), `contacts.csv` (people and the status of their address) and `activity.csv` (e-mails plus the nightly sync and the morning digest, which should each log one line every day).

10 partner rows for 9 partners, 10 contacts. A clean automation log, a duplicated row, a near-same name that differs only by a legal suffix, a bounce whose address differs in case from the contact record, and several gaps on closed partners that should not be flagged.

Every name, address and number is invented. The free-mail addresses contain an underscore, which Gmail doesn't allow in a username, so none of them can belong to a real person. The planted problems are not listed here, so a run against this folder is blind. The expected findings are in [`tests/answer_keys/crm-3.json`](../../../tests/answer_keys/crm-3.json), outside this folder; the scored blind run is in [`examples/runs/crm-3/`](../../runs/crm-3/).

```bash
python tools/reference_check.py crm examples/crm/crm-3   # what the written rules produce
```
