"""Check a scheduled agent's run log against the rules in safe-scheduled-agents.md.

    python tools/run_log_check.py examples/scheduled/broken
    python tools/run_log_check.py examples/scheduled/healthy --today 2026-10-13

The folder holds `schedule.json` (which jobs exist, how often they run, what
each may write) and `run-log.csv` (one line per run, write, message, ...).
Rules, one finding per (rule, entity):

  S1 missed run      a daily job with no `run` line on some day from the oldest
                     log date to today, or a weekly job with more than 7 days
                     between runs or since its last run          entity: job
  S2 forbidden write a `write` to a table.field not on the job's may_write list
                                                                 entity: job/table.field
  S3 create/delete   a scheduled job created or deleted a record entity: job/table
  S4 no old value    a `write` that didn't record the value it replaced (a field
                     that really was empty is logged as "(empty)")
                                                                 entity: job/table.field
  S5 empty digest    an attention digest sent with 0 items (it should only fire
                     when a person has something to do)          entity: job/date

Exit code 1 if anything is found, 2 on malformed input. Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ACTIONS = {"run", "read", "write", "create", "delete", "message"}
COLUMNS = ("date", "job", "action", "target", "field", "old", "new", "items")


class InputError(ValueError):
    pass


def load(folder: Path) -> tuple[dict, list[dict[str, str]]]:
    try:
        schedule = json.loads((folder / "schedule.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"schedule.json: {e}") from None
    jobs = schedule.get("jobs")
    if not isinstance(jobs, dict) or not jobs:
        raise InputError("schedule.json: needs a non-empty 'jobs' object")
    for name, job in jobs.items():
        if job.get("every") not in ("day", "week"):
            raise InputError(f"schedule.json: job {name!r} needs \"every\": \"day\" or \"week\"")
    path = folder / "run-log.csv"
    if not path.is_file():
        raise InputError(f"{path}: file not found")
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise InputError(f"run-log.csv: missing column(s) {', '.join(missing)}")
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in reader]
    if not rows:
        raise InputError("run-log.csv: the log is empty; an empty log is itself the alarm")
    for n, r in enumerate(rows, start=2):
        try:
            r["_day"] = date.fromisoformat(r["date"])  # type: ignore[assignment]
        except ValueError:
            raise InputError(f"run-log.csv line {n}: {r['date']!r} is not a YYYY-MM-DD date") from None
        if r["action"] not in ACTIONS:
            raise InputError(f"run-log.csv line {n}: unknown action {r['action']!r}")
        if r["job"] not in jobs:
            raise InputError(f"run-log.csv line {n}: job {r['job']!r} is not in schedule.json")
        if r["items"] and not r["items"].isdigit():
            raise InputError(f"run-log.csv line {n}: items {r['items']!r} is not a whole number")
    return jobs, rows


def check(folder: Path, today: date | None = None) -> list[tuple[str, str, str]]:
    jobs, rows = load(folder)
    today = today or max(r["_day"] for r in rows)  # type: ignore[type-var]
    first = min(r["_day"] for r in rows)  # type: ignore[type-var]
    out: dict[tuple[str, str], str] = {}

    for name, job in jobs.items():
        runs = sorted({r["_day"] for r in rows if r["job"] == name and r["action"] == "run"})
        if job["every"] == "day":
            d = first
            while d <= today:  # type: ignore[operator]
                if d not in runs:
                    out.setdefault(("S1", name), f"no run on {d}")
                    break
                d += timedelta(days=1)
        else:
            points = runs + [today]
            gaps = [(b - a).days for a, b in zip(points, points[1:])]  # type: ignore[operator]
            if not runs or max(gaps, default=0) > 7:
                out.setdefault(("S1", name), f"weekly runs: {[str(d) for d in runs] or 'none'}")

    for r in rows:
        job, action, target = r["job"], r["action"], r["target"]
        allowed = set(jobs[job].get("may_write", []))
        if action == "write":
            key = f"{target}.{r['field']}"
            if key not in allowed:
                out.setdefault(("S2", f"{job}/{key}"), f"{r['date']}: not on may_write {sorted(allowed)}")
            if not r["old"]:
                out.setdefault(("S4", f"{job}/{key}"), f"{r['date']}: wrote {r['new']!r} without the old value")
        elif action in ("create", "delete"):
            out.setdefault(("S3", f"{job}/{target}"), f"{r['date']}: {action} {r['new'] or r['old']}")
        elif action == "message" and jobs[job].get("kind") == "digest" and r["items"] == "0":
            out.setdefault(("S5", f"{job}/{r['date']}"), "digest sent with 0 items")
    return sorted((rule, entity, why) for (rule, entity), why in out.items())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--today", help="as-of date, YYYY-MM-DD (default: newest date in the log)")
    args = ap.parse_args(argv)
    try:
        today = date.fromisoformat(args.today) if args.today else None
        findings = check(args.folder, today)
    except (InputError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for rule, entity, why in findings:
        print(f"{rule}  {entity:<40} {why}")
    clear = "All clear: every run present, every write allowed and logged."
    print(f"\n{len(findings)} findings." if findings else clear)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
