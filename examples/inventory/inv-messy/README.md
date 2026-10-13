# inv-messy: a home-goods shop with multi-unit stock

The source of truth is `stock-master.csv` (with an on-hand quantity per item), next to two marketplace exports with their own column names (`sku` / `Item ID`, `state` / `Listing status`, `qty_listed` / `Available`), free-text statuses (`Active`, `Sold out`, `paused till Feb`, `Reserved - pickup Fri`), dates in mixed formats and a notes column. 9 item ids.

Every item is invented. The planted cases are not listed here, so a run against this folder is blind. The expected findings were written by hand before any run, in [`tests/answer_keys/inv-messy.json`](../../../tests/answer_keys/inv-messy.json); the scored blind run is in [`examples/runs/inv-messy/`](../../runs/inv-messy/).

```bash
python tools/reference_check.py inventory examples/inventory/inv-messy   # refuses: missing columns
```
