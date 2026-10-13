"""Apply a person-confirmed list of field changes to CSV exports, old value first.

The shipped agents only audit and propose. This is the separate, human step
that comes after: someone reads the proposals, copies the ones they agree
with into a changes file, signs it, and runs this script.

    python tools/apply_changes.py examples/crm/crm-1 examples/apply/crm-1-confirmed.json --dry-run
    python tools/apply_changes.py <export-folder> <changes.json> --log <change-log.csv>

changes.json:

    {"approved_by": "Mia",
     "changes": [{"file": "partners.csv", "id": "P04", "field": "last_contact",
                  "old": "2026-09-12", "new": "2026-10-05", "finding": "C3 P04"}]}

What it refuses, all checked before anything is written (all or nothing):
no approver; a file outside the folder; an id that matches no row or more than
one; an unknown field or the id column itself; a current value that no longer
equals "old" (someone changed it since the proposal). It can't create or
delete rows. Every applied change is appended to the change log with the old
value, the new value, who approved it and when. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_COLUMNS = ["applied_at", "file", "id", "field", "old", "new", "approved_by", "finding"]


class ChangeError(ValueError):
    pass


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def plan(folder: Path, spec: dict) -> tuple[list[dict], dict]:
    """Validate every change and return them with the file they touch resolved."""
    approver = str(spec.get("approved_by", "")).strip()
    changes = spec.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ChangeError("changes file has no 'changes' list")
    tables: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    planned = []
    for n, ch in enumerate(changes, start=1):
        where = f"change {n}"
        who = str(ch.get("approved_by", approver)).strip()
        if not who:
            raise ChangeError(f"{where}: no approved_by; nothing is applied without a named person")
        name = str(ch.get("file", ""))
        if not name or Path(name).name != name or not name.endswith(".csv"):
            raise ChangeError(f"{where}: file must be a CSV name inside the folder, got {name!r}")
        path = folder / name
        if not path.is_file():
            raise ChangeError(f"{where}: {name} not found in {folder}")
        if name not in tables:
            tables[name] = load_csv(path)
        columns, rows = tables[name]
        id_col, field = columns[0], str(ch.get("field", ""))
        if field not in columns or field == id_col:
            raise ChangeError(f"{where}: {name} has no editable field {field!r}")
        matches = [r for r in rows if r[id_col] == str(ch.get("id", ""))]
        if len(matches) != 1:
            raise ChangeError(f"{where}: {name} has {len(matches)} rows with {id_col}={ch.get('id')!r}, need exactly 1")
        if "old" not in ch or "new" not in ch:
            raise ChangeError(f"{where}: needs both 'old' and 'new'")
        current = matches[0][field]
        if current != str(ch["old"]):
            raise ChangeError(f"{where}: {name} {ch['id']} {field} is {current!r} now, "
                              f"proposal expected {ch['old']!r}; re-run the audit")
        planned.append({"file": name, "id": str(ch["id"]), "field": field, "old": current,
                        "new": str(ch["new"]), "approved_by": who, "finding": str(ch.get("finding", "")),
                        "_row": matches[0]})
    return planned, tables


def apply(folder: Path, spec: dict, log: Path, at: str | None = None, dry_run: bool = False) -> list[dict]:
    planned, tables = plan(folder, spec)
    if dry_run:
        return planned
    at = at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    new_log = not log.exists()
    with log.open("a", newline="", encoding="utf-8") as f:  # log first: old value before new value
        w = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        if new_log:
            w.writeheader()
        for p in planned:
            w.writerow({"applied_at": at, **{k: p[k] for k in LOG_COLUMNS if k != "applied_at"}})
    for p in planned:
        p["_row"][p["field"]] = p["new"]
    for name, (columns, rows) in tables.items():
        with (folder / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    return planned


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder", type=Path)
    ap.add_argument("changes", type=Path)
    ap.add_argument("--log", type=Path, help="change log CSV (default: <folder>/change-log.csv)")
    ap.add_argument("--dry-run", action="store_true", help="validate and print, write nothing")
    args = ap.parse_args(argv)
    try:
        spec = json.loads(args.changes.read_text(encoding="utf-8"))
        done = apply(args.folder, spec, args.log or args.folder / "change-log.csv", dry_run=args.dry_run)
    except (ChangeError, OSError, json.JSONDecodeError) as e:
        print(f"refused, nothing written: {e}", file=sys.stderr)
        return 2
    verb = "would apply" if args.dry_run else "applied"
    for p in done:
        print(f"{verb}: {p['file']} {p['id']} {p['field']}: {p['old']!r} -> {p['new']!r} "
              f"(approved by {p['approved_by']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
