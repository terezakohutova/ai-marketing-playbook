# Sample CRM export: a fictional small brand's partner database

As of **2026-10-13**. Three files, exported the way a small team's CRM would export them:

- `partners.csv`: one row per partner (status, priority, owner, next step, live offers).
- `contacts.csv`: people at each partner, with the status of their e-mail address.
- `activity.csv`: e-mails and automation runs (the nightly sync and the morning digest are supposed to log one line each, every day).

Every name, address and number here is invented. The data contains a handful of planted problems of the kinds the steward is meant to catch; they are not listed here on purpose, so a run against it is a blind test. [`audit-output.md`](audit-output.md) is the unedited output of a fresh agent given only `.claude/agents/crm-steward.md` and this folder.
