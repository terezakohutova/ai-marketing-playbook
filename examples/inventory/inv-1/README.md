# inv-1: one storefront, two marketplaces

Three exports in the shape a seller dashboard produces: `storefront.csv` is the source of truth for what is actually in stock (the files don't say so; the agent has to work it out), `marketplace-a.csv` and `marketplace-b.csv` list the same items on two marketplaces. 11 item ids.

Every item is invented. The planted cases are not listed here, so a run against this folder is blind. The expected findings are in [`tests/answer_keys/inv-1.json`](../../../tests/answer_keys/inv-1.json), outside this folder so copying the inputs never copies the answers. The scored blind run is in [`examples/runs/inv-1/`](../../runs/inv-1/).

```bash
python tools/reference_check.py inventory examples/inventory/inv-1   # what the written rules produce
```
