"""Check a staged-draft outreach queue against the draft-first-outreach rules.

    python tools/outreach_check.py examples/outreach/queue.json
    python tools/outreach_check.py examples/outreach/queue.json --hash D03   # hash to approve a draft

The agent only adds drafts to the queue. A person approves a draft by putting
their name, the time and the SHA-256 of the exact body they read on it; the
person (never the agent) sends it and records sent_at and sent_by. This
script is the deterministic check after the fact. One finding per (rule, draft):

  O1 sent unapproved   sent_at is set, but approved_by / approved_at is empty
                       or the approval is later than the send
  O2 edited after OK   the body's SHA-256 is not the approved_sha256, so what
                       went out (or will) is not what the person read
  O3 agent sent        sent_by is the agent; publishing is a human action
  O4 too soon          the same contact got another sent draft less than
                       cooldown_days earlier
  O5 excluded          the destination is on the queue's exclude list

Exit code 1 if anything is found, 2 on malformed input. Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

AGENT_NAMES = {"agent", "bot", "automation"}


class InputError(ValueError):
    pass


def body_hash(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def when(value: str, where: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise InputError(f"{where}: {value!r} is not an ISO date-time") from None


def load(path: Path) -> dict:
    try:
        queue = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path.name}: {e}") from None
    drafts = queue.get("drafts")
    if not isinstance(drafts, list) or not drafts:
        raise InputError(f"{path.name}: needs a non-empty 'drafts' list")
    ids = [str(d.get("id", "")) for d in drafts]
    if "" in ids or len(set(ids)) != len(ids):
        raise InputError(f"{path.name}: every draft needs a unique id")
    for d in drafts:
        for k in ("contact", "destination", "body"):
            if not d.get(k):
                raise InputError(f"{path.name}: draft {d['id']} has no {k}")
    return queue


def check(queue: dict) -> list[tuple[str, str, str]]:
    cooldown = int(queue.get("cooldown_days", 30))
    exclude = {e.lower() for e in queue.get("exclude", [])}
    out: dict[tuple[str, str], str] = {}
    sent: list[tuple[datetime, str, str]] = []
    for d in queue["drafts"]:
        did = str(d["id"])
        sent_at = when(d.get("sent_at", ""), f"draft {did} sent_at")
        approved_at = when(d.get("approved_at", ""), f"draft {did} approved_at")
        if sent_at:
            if not d.get("approved_by") or approved_at is None:
                out[("O1", did)] = "sent without an approval"
            elif approved_at > sent_at:
                out[("O1", did)] = f"approved {approved_at} after it was sent {sent_at}"
            if str(d.get("sent_by", "")).strip().lower() in AGENT_NAMES:
                out[("O3", did)] = f"sent_by={d['sent_by']!r}"
            sent.append((sent_at, did, d["contact"].lower()))
        if d.get("approved_sha256") and d["approved_sha256"] != body_hash(d["body"]):
            out[("O2", did)] = "body differs from the approved version"
        if d["destination"].lower() in exclude:
            out[("O5", did)] = f"destination {d['destination']!r} is excluded"
    sent.sort()
    last: dict[str, datetime] = {}
    for at, did, contact in sent:
        if contact in last and (at - last[contact]).days < cooldown:
            out[("O4", did)] = f"{contact} was sent another draft {(at - last[contact]).days} days earlier"
        last[contact] = at
    return sorted((rule, did, why) for (rule, did), why in out.items())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("queue", type=Path)
    ap.add_argument("--hash", metavar="DRAFT_ID", help="print the SHA-256 to approve this draft's current body")
    args = ap.parse_args(argv)
    try:
        queue = load(args.queue)
        if args.hash:
            match = [d for d in queue["drafts"] if str(d["id"]) == args.hash]
            if not match:
                raise InputError(f"no draft {args.hash!r}")
            print(body_hash(match[0]["body"]))
            return 0
        findings = check(queue)
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for rule, did, why in findings:
        print(f"{rule}  {did:<6} {why}")
    print(f"\n{len(findings)} findings." if findings else "All clear: every sent draft was approved as sent.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
