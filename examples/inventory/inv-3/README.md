# inv-3: a bookshop, inventory system plus three channels

The source of truth is called `inventory.csv` here, next to `shop-north.csv`, `shop-south.csv` and `auction-site.csv`, so neither the agent nor the checker can rely on a fixed file name. It adds a duplicate row and an auction status (`ended`). 9 item ids.

Every item is invented. The planted cases are not listed here, so a run against this folder is blind. The expected findings are in [`tests/answer_keys/inv-3.json`](../../../tests/answer_keys/inv-3.json), outside this folder so copying the inputs never copies the answers. The scored blind run is in [`examples/runs/inv-3/`](../../runs/inv-3/).

```bash
python tools/reference_check.py inventory examples/inventory/inv-3   # what the written rules produce
```
