"""Compare each hand-written answer key with what the mechanical checker produces.

    python tools/key_vs_checker.py

The keys are written by hand from the rule text and the data; the checker is a
second, mechanical opinion. They are not required to agree. This prints, per
dataset, whether they agree, every finding only one of them has, or the error
the checker stopped with. Standard library only.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_check import InputError, check_crm, check_inventory  # noqa: E402


def compare(key: dict, folder: Path | None = None) -> dict:
    """{"error": str} if the checker refused the data, else {"checker_only": [...], "key_only": [...]}."""
    folder = folder or ROOT / key["folder"]
    try:
        if key["pattern"] == "inventory":
            found = check_inventory(folder, key.get("source_of_truth"))
        else:
            found = check_crm(folder, date.fromisoformat(key["today"]))
    except InputError as e:
        return {"error": str(e)}
    got = {(f.rule, f.entity, f.bucket) for f in found}
    want = {(f["rule"], f["entity"], f["bucket"]) for f in key["findings"]}
    return {"checker_only": sorted(got - want), "key_only": sorted(want - got)}


def main() -> int:
    for path in sorted((ROOT / "tests" / "answer_keys").glob("*.json")):
        key = json.loads(path.read_text(encoding="utf-8"))
        r = compare(key)
        name = key["dataset"]
        if "error" in r:
            print(f"{name}: checker refused the data: {r['error']}")
        elif not r["checker_only"] and not r["key_only"]:
            print(f"{name}: key and checker agree ({len(key['findings'])} findings)")
        else:
            print(f"{name}: key and checker disagree")
            for f in r["key_only"]:
                print(f"  only in key      {' '.join(f)}")
            for f in r["checker_only"]:
                print(f"  only in checker  {' '.join(f)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
