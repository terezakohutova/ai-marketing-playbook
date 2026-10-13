# crm-2: a bike and homeware brand's partners

As of **2026-11-20** (also the newest date in `activity.csv`). Three exports, the way a small team's CRM would export them: `partners.csv` (status, priority, owner, next step, live offers), `contacts.csv` (people and the status of their address) and `activity.csv` (e-mails plus the nightly sync and the morning digest, which should each log one line every day).

12 partners, 14 contacts. Exercises the cases crm-1 doesn't: relationships cooling rather than cold, a Live partner with nothing live, a contact pointing at a partner that doesn't exist, open partners with no owner or no contact, a near-same name that is a typo plus a legal suffix, contacts on a free-mail domain, and bounce messages worded differently.

Every name, address and number is invented. The planted problems are not listed here, so a run against this folder is blind. The expected findings are in [`tests/answer_keys/crm-2.json`](../../../tests/answer_keys/crm-2.json), outside this folder; the scored blind run is in [`examples/runs/crm-2/`](../../runs/crm-2/).

```bash
python tools/reference_check.py crm examples/crm/crm-2   # what the written rules produce
```
