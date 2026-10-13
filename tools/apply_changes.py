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

Rows are found by their id column: "id_column" on the change if given, else
the column named after the file (partners.csv -> partner_id), else a column
called "id". It is never assumed to be the first column.

What it refuses, all checked before anything is written (all or nothing):
no approver; a file outside the folder; an id that matches no row or more than
one; an unknown field or the id column itself; two changes to the same field of
the same row (one would silently overwrite the other); a current value that no
longer equals "old" (someone changed it since the proposal); an unfinished
earlier apply (see below). It can't create or delete rows.

How it writes: every changed CSV goes to a temporary file next to it first.
Then a journal (<log>.pending) records the planned changes with their old
values, the temporary files replace the originals (os.replace, atomic per
file), the changes are appended to the change log, and the journal is
removed. If anything fails half way, the journal stays behind and the next run
refuses to start until a person has compared it with the files and deleted it.
Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
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


def id_column(name: str, columns: list[str], given: str | None) -> str:
    if given:
        if given not in columns:
            raise ChangeError(f"{name} has no id column {given!r}")
        return given
    stem = Path(name).stem.lower()
    for candidate in (f"{stem[:-1]}_id" if stem.endswith("s") else "", f"{stem}_id", "id"):
        if candidate and candidate in columns:
            return candidate
    raise ChangeError(f"{name}: can't tell which column is the id; add \"id_column\" to the change")


def journal_path(log: Path) -> Path:
    return log.with_name(log.name + ".pending")


def plan(folder: Path, spec: dict) -> tuple[list[dict], dict]:
    """Validate every change and return them with the file they touch resolved."""
    approver = str(spec.get("approved_by", "")).strip()
    changes = spec.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ChangeError("changes file has no 'changes' list")
    tables: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    planned = []
    targets: dict[tuple[str, str, str], int] = {}
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
        id_col, field = id_column(name, columns, ch.get("id_column")), str(ch.get("field", ""))
        if field not in columns or field == id_col:
            raise ChangeError(f"{where}: {name} has no editable field {field!r}")
        row_id = str(ch.get("id", ""))
        target = (name, row_id, field)
        if target in targets:
            raise ChangeError(f"{where}: change {targets[target]} already sets {name} {row_id} {field}; "
                              "two changes to one field would overwrite each other, combine them")
        targets[target] = n
        matches = [r for r in rows if r[id_col] == row_id]
        if len(matches) != 1:
            raise ChangeError(f"{where}: {name} has {len(matches)} rows with {id_col}={row_id!r}, need exactly 1")
        if "old" not in ch or "new" not in ch:
            raise ChangeError(f"{where}: needs both 'old' and 'new'")
        current = matches[0][field]
        if current != str(ch["old"]):
            raise ChangeError(f"{where}: {name} {row_id} {field} is {current!r} now, "
                              f"proposal expected {ch['old']!r}; re-run the audit")
        planned.append({"file": name, "id": row_id, "field": field, "old": current,
                        "new": str(ch["new"]), "approved_by": who, "finding": str(ch.get("finding", "")),
                        "_row": matches[0]})
    return planned, tables


def apply(folder: Path, spec: dict, log: Path, at: str | None = None, dry_run: bool = False) -> list[dict]:
    journal = journal_path(log)
    if journal.exists():
        raise ChangeError(f"{journal.name} exists: an earlier apply did not finish. Compare it with the files "
                          "and the change log, then delete it")
    planned, tables = plan(folder, spec)
    if dry_run:
        return planned
    at = at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    entries = [{"applied_at": at, **{k: p[k] for k in LOG_COLUMNS if k != "applied_at"}} for p in planned]
    for p in planned:
        p["_row"][p["field"]] = p["new"]

    temps: list[tuple[Path, Path]] = []
    try:
        for name, (columns, rows) in tables.items():
            tmp = folder / f".{name}.tmp"
            with tmp.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
                f.flush()
                os.fsync(f.fileno())
            temps.append((tmp, folder / name))
    except OSError:
        for tmp, _ in temps:
            tmp.unlink(missing_ok=True)
        raise

    journal.write_text(json.dumps({"applied_at": at, "changes": entries}, indent=2), encoding="utf-8")
    for tmp, dest in temps:
        os.replace(tmp, dest)  # if this fails half way, the journal stays and blocks the next run

    new_log = not log.exists()
    with log.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=LOG_COLUMNS, lineterminator="\n")
        if new_log:
            w.writeheader()
        w.writerows(entries)
    journal.unlink()
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
        print(f"refused or stopped: {e}", file=sys.stderr)
        return 2
    verb = "would apply" if args.dry_run else "applied"
    for p in done:
        print(f"{verb}: {p['file']} {p['id']} {p['field']}: {p['old']!r} -> {p['new']!r} "
              f"(approved by {p['approved_by']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
