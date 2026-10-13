# inv-2: a print shop, storefront plus two marketplaces

Same file layout as inv-1, different items (prints). It adds an item that is stale on one channel and in an unknown state on the other at the same time, a source of truth with a status other than live or sold, and an unknown item that a channel already shows as sold. 10 item ids.

Every item is invented. The planted cases are not listed here, so a run against this folder is blind. The expected findings are in [`tests/answer_keys/inv-2.json`](../../../tests/answer_keys/inv-2.json), outside this folder so copying the inputs never copies the answers. The scored blind run is in [`examples/runs/inv-2/`](../../runs/inv-2/).

```bash
python tools/reference_check.py inventory examples/inventory/inv-2   # what the written rules produce
```
