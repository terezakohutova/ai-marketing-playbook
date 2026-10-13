"""Deterministic reference checks for the two runnable patterns.

The agents in .claude/agents/ apply judgment; this script applies the same
written rules mechanically, so an agent run can be scored against them:

    python tools/reference_check.py inventory examples/sample-run
    python tools/reference_check.py crm examples/crm-audit --today 2026-10-13
    python tools/reference_check.py crm examples/crm-audit --against examples/crm-audit/audit-output.md

With --against, it exits non-zero if any rule-derived finding is missing
from the agent's output. Standard library only, Python 3.9+.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------- helpers


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def norm(status: str) -> str:
    return status.strip().lower()


# -------------------------------------------------------------- inventory

CONFIRMED = "confirmed discrepancy"
HUMAN = "needs a human call"


def check_inventory(folder: Path, source_of_truth: str = "storefront.csv") -> dict[str, dict]:
    """Return {item_id: {"bucket": ..., "channels": {file: status}}} for every item that isn't clean.

    Rules (from .claude/agents/inventory-sync.md):
    - source of truth says sold, a channel says live -> confirmed discrepancy
    - a channel shows sold or any other status the source of truth doesn't
      corroborate, or lists an item the source of truth doesn't have -> needs a human call
    - an item a channel doesn't list at all is not a discrepancy
    """
    sot = {r["item_id"]: norm(r["status"]) for r in read_csv(folder / source_of_truth)}
    channels = {
        p.name: {r["item_id"]: norm(r["status"]) for r in read_csv(p)}
        for p in sorted(folder.glob("*.csv"))
        if p.name != source_of_truth
    }
    findings: dict[str, dict] = {}
    all_items = set(sot).union(*[set(c) for c in channels.values()])
    for item in sorted(all_items):
        truth = sot.get(item)
        bucket = None
        evidence = {}
        for name, listing in channels.items():
            if item not in listing:
                continue
            status = listing[item]
            evidence[name] = status
            if truth is None or status == truth:
                if truth is None:
                    bucket = HUMAN if bucket is None else bucket
                continue
            if truth == "sold" and status == "live":
                bucket = CONFIRMED if bucket in (None, CONFIRMED) else bucket
            else:
                bucket = HUMAN
        if bucket:
            findings[item] = {"bucket": bucket, "source_of_truth": truth, "channels": evidence}
    return findings


# -------------------------------------------------------------------- crm

OPEN = {"prospect", "negotiation", "live"}
CADENCE = {"A": 14, "B": 30, "C": 60}
SCHEDULED = ("nightly-sync", "morning-digest")


def parse_day(s: str) -> date | None:
    return date.fromisoformat(s) if s else None


def check_crm(folder: Path, today: date) -> list[tuple[str, str, str]]:
    """Return sorted (partner_id or 'ALL', section letter, check) tuples.

    Rules (from .claude/agents/crm-steward.md, sections A-F).
    """
    partners = read_csv(folder / "partners.csv")
    contacts = read_csv(folder / "contacts.csv")
    activity = read_csv(folder / "activity.csv")
    ids = {p["partner_id"] for p in partners}
    out: set[tuple[str, str, str]] = set()

    # A. automation health: every scheduled job logs a line every day up to today
    first = min(parse_day(a["date"]) for a in activity)
    for job in SCHEDULED:
        days = {parse_day(a["date"]) for a in activity if a["source"] == job}
        d = first
        while d <= today:
            if d not in days:
                out.add(("ALL", "A", f"{job} missing"))
                break
            d += timedelta(days=1)

    # B. integrity: one e-mail domain on several partners, contacts without a partner
    by_domain: dict[str, set[str]] = {}
    for c in contacts:
        by_domain.setdefault(c["email"].split("@")[-1].lower(), set()).add(c["partner_id"])
        if c["partner_id"] not in ids:
            out.add((c["partner_id"], "B", "contact points at missing partner"))
    for owners in by_domain.values():
        if len(owners) > 1:
            for pid in owners:
                out.add((pid, "B", "possible duplicate"))

    emails = [a for a in activity if a["source"] == "email"]
    bounced = {
        m.group(0).lower()
        for a in emails
        if "delivery failure" in a["summary"].lower()
        for m in [re.search(r"[\w.+-]+@[\w.-]+", a["summary"])]
        if m
    }

    for p in partners:
        pid, status, prio = p["partner_id"], norm(p["status"]), p["priority"]
        offers = int(p["live_offers"] or 0)
        last = parse_day(p["last_contact"])
        mails = [parse_day(a["date"]) for a in emails if a["partner_id"] == pid
                 and "delivery failure" not in a["summary"].lower()]

        # C. consistency
        if status in ("paused", "lost") and offers > 0:
            out.add((pid, "C", "closed status with live offer"))
        if status == "live" and offers == 0:
            out.add((pid, "C", "live status without offer"))
        if mails and (last is None or max(mails) > last):
            out.add((pid, "C", "last_contact older than newest mail"))

        # D. action
        nxt, nxt_date = p["next_step"], parse_day(p["next_step_date"])
        if status in OPEN:
            if not nxt or not nxt_date:
                out.add((pid, "D", "no next step or date"))
            if prio in CADENCE and last:
                age, window = (today - last).days, CADENCE[prio]
                if age > window:
                    out.add((pid, "D", "cold"))
                elif age > window * 0.75:
                    out.add((pid, "D", "cooling"))
        if nxt_date and nxt_date < today and status != "lost":
            out.add((pid, "D", "next step overdue"))
        if status == "lost" and nxt:
            out.add((pid, "D", "lost partner with next step"))

        # E. contacts
        mine = [c for c in contacts if c["partner_id"] == pid]
        for c in mine:
            if c["email"].lower() in bounced and norm(c["status"]) == "active":
                out.add((pid, "E", f"bounced contact {c['contact_id']} still active"))
        if mine and all(norm(c["status"]) in ("to verify", "former") for c in mine):
            out.add((pid, "E", "no verified current contact"))

        # F. data gaps on open partners
        if status in OPEN:
            for field in ("priority", "market", "owner"):
                if not p[field]:
                    out.add((pid, "F", f"missing {field}"))
            if not mine:
                out.add((pid, "F", "missing contact"))

    return sorted(out)


def crm_missing_from(output_md: str, findings: list[tuple[str, str, str]]) -> list[tuple[str, str, str]]:
    """Findings with no table row in the agent's output naming that partner and section."""
    rows = [r for r in output_md.splitlines() if re.match(r"\|\s*F\d+\s*\|", r)]
    missing = []
    for pid, section, check in findings:
        hit = False
        for r in rows:
            cells = [c.strip() for c in r.strip("|").split("|")]
            if section in [x.strip() for x in cells[1].split("/")] and (pid == "ALL" and "all" in cells[2].lower() or pid in cells[2]):
                hit = True
                break
        if not hit:
            missing.append((pid, section, check))
    return missing


def inventory_missing_from(output_md: str, findings: dict[str, dict]) -> list[str]:
    """Items not listed under a heading that names their bucket ("confirmed" / "human")."""
    placed: dict[str, set[str]] = {}
    heading = ""
    for line in output_md.splitlines():
        if line.startswith("#"):
            heading = line.lower()
            continue
        for item in re.findall(r"\b[A-Z]+-\d+\b", line):
            placed.setdefault(item, set()).add(heading)
    keyword = {CONFIRMED: "confirmed", HUMAN: "human"}
    return [
        item for item, f in findings.items()
        if not any(keyword[f["bucket"]] in h for h in placed.get(item, ()))
    ]


# -------------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pattern", choices=["inventory", "crm"])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--today", type=date.fromisoformat, help="as-of date for crm (default: newest date in activity.csv)")
    ap.add_argument("--against", type=Path, help="agent output to score against the rule-derived findings")
    args = ap.parse_args(argv)

    if args.pattern == "inventory":
        findings = check_inventory(args.folder)
        for item, f in findings.items():
            print(f"{item}: {f['bucket']}  source_of_truth={f['source_of_truth']}  {f['channels']}")
        missing = inventory_missing_from(args.against.read_text(encoding="utf-8"), findings) if args.against else []
    else:
        today = args.today or max(parse_day(a["date"]) for a in read_csv(args.folder / "activity.csv"))
        findings = check_crm(args.folder, today)
        for f in findings:
            print("  ".join(f))
        missing = crm_missing_from(args.against.read_text(encoding="utf-8"), findings) if args.against else []

    print(f"\n{len(findings)} rule-derived findings.")
    if args.against:
        if missing:
            print(f"MISSING from {args.against}: {missing}")
            return 1
        print(f"All of them appear in {args.against}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
