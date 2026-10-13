"""Deterministic reference checks for the two runnable agent patterns.

The agents in .claude/agents/ apply judgment; this script applies the same
written rules mechanically and prints one line per (rule, entity) finding:

    python tools/reference_check.py inventory examples/inventory/inv-1
    python tools/reference_check.py inventory examples/inventory/inv-3 --source-of-truth inventory.csv
    python tools/reference_check.py crm examples/crm/crm-1 --today 2026-10-13

Rule ids and wording match the rule tables in .claude/agents/*.md. Scoring an
agent's output is done by tools/score_run.py against a hand-written answer
key; tests/ check that this script and the answer keys agree.
Standard library only, Python 3.9+.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import NamedTuple


class InputError(ValueError):
    """The export is malformed in a way that makes the rules meaningless."""


class Finding(NamedTuple):
    rule: str
    entity: str
    bucket: str
    evidence: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.rule, self.entity)


# ---------------------------------------------------------------- helpers


def read_csv(path: Path, required: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise InputError(f"{path}: file not found")
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in required if c not in header]
        if missing:
            raise InputError(f"{path.name}: missing column(s) {', '.join(missing)}")
        rows = []
        for n, row in enumerate(reader, start=2):
            if None in row:
                raise InputError(f"{path.name} line {n}: more cells than columns")
            rows.append({(k or "").strip(): (v or "").strip() for k, v in row.items()})
    return rows


def norm(status: str) -> str:
    return status.strip().lower()


def parse_day(value: str, where: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise InputError(f"{where}: {value!r} is not a YYYY-MM-DD date") from None


def parse_int(value: str, where: str) -> int:
    if not value:
        return 0
    try:
        return int(value)
    except ValueError:
        raise InputError(f"{where}: {value!r} is not a whole number") from None


# -------------------------------------------------------------- inventory

CONFIRMED = "confirmed"
HUMAN = "human"
INVENTORY_RULES = {"I1": CONFIRMED, "I2": HUMAN, "I3": HUMAN, "I4": HUMAN, "I5": CONFIRMED, "I6": HUMAN}
ON_HAND = "on_hand"  # optional column in the source of truth: units actually in stock
LISTED = "listed_qty"  # optional column in a channel export: units that channel offers
SOURCE_OF_TRUTH_HINTS = ("storefront", "inventory", "stock", "source-of-truth", "warehouse")


def find_source_of_truth(folder: Path) -> str:
    """Pick the source-of-truth export by file name, or fail loudly if that isn't clear."""
    names = sorted(p.name for p in folder.glob("*.csv"))
    hits = [n for n in names if any(h in n.lower() for h in SOURCE_OF_TRUTH_HINTS)]
    if len(hits) != 1:
        raise InputError(
            f"{folder}: can't tell which file is the source of truth "
            f"(candidates: {hits or 'none'}); pass --source-of-truth"
        )
    return hits[0]


def check_inventory(folder: Path, source_of_truth: str | None = None) -> list[Finding]:
    """Rules I1-I4 from .claude/agents/inventory-sync.md, one Finding per (rule, item)."""
    sot_name = source_of_truth or find_source_of_truth(folder)
    files = {p.name: read_csv(p, ("item_id", "status")) for p in sorted(folder.glob("*.csv"))}
    if sot_name not in files:
        raise InputError(f"{folder}: source of truth {sot_name!r} not found")
    if len(files) < 2:
        raise InputError(f"{folder}: need the source of truth plus at least one channel export")

    out: dict[tuple[str, str], Finding] = {}

    def add(rule: str, item: str, evidence: str) -> None:
        out.setdefault((rule, item), Finding(rule, item, INVENTORY_RULES[rule], evidence))

    for name, rows in files.items():
        seen: set[str] = set()
        for r in rows:
            if not r["item_id"]:
                raise InputError(f"{name}: row with an empty item_id")
            if r["item_id"] in seen:
                add("I4", r["item_id"], f"{name} lists it more than once")
            seen.add(r["item_id"])

    sot = {r["item_id"]: norm(r["status"]) for r in files[sot_name]}
    for name, rows in files.items():
        if name == sot_name:
            continue
        for r in rows:
            item, status = r["item_id"], norm(r["status"])
            truth = sot.get(item)
            if truth is None:
                add("I3", item, f"{name}={status}, not in {sot_name}")
            elif status == truth:
                continue
            elif truth == "sold" and status == "live":
                add("I1", item, f"{sot_name}=sold, {name}=live")
            else:
                add("I2", item, f"{sot_name}={truth}, {name}={status}")

    # I5 / I6: multi-unit stock, only where the exports carry quantities.
    on_hand = {}
    for n, r in enumerate(files[sot_name], start=2):
        if r.get(ON_HAND, "") != "":
            on_hand[r["item_id"]] = parse_int(r[ON_HAND], f"{sot_name} line {n} {ON_HAND}")
    listed: dict[str, dict[str, int]] = {}
    for name, rows in files.items():
        if name == sot_name:
            continue
        for n, r in enumerate(rows, start=2):
            if norm(r["status"]) == "live" and r.get(LISTED, "") != "":
                qty = parse_int(r[LISTED], f"{name} line {n} {LISTED}")
                per_item = listed.setdefault(r["item_id"], {})
                per_item[name] = max(per_item.get(name, 0), qty)
    for item, per_channel in listed.items():
        if sot.get(item) != "live" or item not in on_hand:
            continue  # I1-I3 already cover sold, other and unknown items
        stock = on_hand[item]
        over = {c: q for c, q in per_channel.items() if q > stock}
        if over:
            add("I5", item, f"{sot_name} on_hand={stock}, " + ", ".join(f"{c} lists {q}" for c, q in over.items()))
        elif sum(per_channel.values()) > stock:
            add("I6", item, f"{sot_name} on_hand={stock}, channels list {sum(per_channel.values())} in total")
    return sorted(out.values())


# -------------------------------------------------------------------- crm

PERSON = "person"
SAFE = "safe"
CRM_RULES = {
    "A1": PERSON, "B1": PERSON, "B2": PERSON, "B3": PERSON,
    "C1": PERSON, "C2": PERSON, "C3": SAFE,
    "D1": PERSON, "D2": PERSON, "D3": PERSON, "D4": PERSON, "D5": PERSON,
    "E1": SAFE, "E2": PERSON,
    "F1": PERSON, "F2": PERSON, "F3": PERSON, "F4": PERSON,
}
OPEN = {"prospect", "negotiation", "live"}
CLOSED = {"paused", "lost"}
CADENCE = {"A": 14, "B": 30, "C": 60}
HUMAN_SOURCES = {"email"}  # every other `source` in activity.csv is a scheduled job
BOUNCE_PHRASES = (
    "delivery failure",
    "delivery status notification (failure)",
    "mail delivery failed",
    "undeliverable",
    "address not found",
    "user unknown",
    "mailbox does not exist",
    "recipient address rejected",
    "returned mail",
    "no such user",
)
FREE_MAIL = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com", "yahoo.com",
    "icloud.com", "aol.com", "proton.me", "protonmail.com", "gmx.de", "gmx.net", "web.de",
}
NAME_NOISE = {"co", "company", "inc", "ltd", "llc", "gmbh", "the", "and"}
SHORT_NAME = 6  # fewer letters than this: a near (not exact) name match needs a second signal
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
RECIPIENT = re.compile(r"\b(final|original)-recipient:\s*(?:rfc822\s*;\s*)?<?([\w.+-]+@[\w-]+(?:\.[\w-]+)+)", re.I)


def name_key(name: str) -> str:
    words = re.sub(r"[^\w\s]", " ", name.lower()).split()
    return " ".join(w for w in words if w not in NAME_NOISE)


def name_tokens(name: str) -> list[str]:
    """Normalised words with a plain plural -s dropped, so "Pets" and "Pet" compare equal."""
    return [w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w
            for w in name_key(name).split()]


def edit_distance(a: str, b: str, cap: int = 3) -> int:
    if abs(len(a) - len(b)) >= cap:
        return cap
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return min(prev[-1], cap)


def typo_allowance(word: str) -> int:
    """Length-aware: a word under 5 letters must match exactly (Bolt/Bold), longer ones may carry a typo."""
    return 0 if len(word) < 5 else 1 if len(word) <= 8 else 2


def name_match(a: str, b: str) -> str | None:
    """Return "exact", "near" or None, comparing the two names word by word."""
    ta, tb = name_tokens(a), name_tokens(b)
    if not ta or not tb:
        return None
    if ta == tb:
        return "exact"
    short, long_ = sorted((ta, tb), key=len)
    if long_[: len(short)] == short:
        return "near"  # the same name with words added at the end
    if len(ta) == len(tb):
        dists = [edit_distance(x, y) for x, y in zip(ta, tb)]
        if sum(dists) <= 2 and all(d <= typo_allowance(max(x, y, key=len)) for d, x, y in zip(dists, ta, tb)):
            return "near"
    return None


def near_same_name(a: str, b: str) -> bool:
    """Name signal strong enough on its own: exact, or near with both names at least SHORT_NAME letters."""
    m = name_match(a, b)
    if m == "exact":
        return True
    letters = min(len(name_key(x).replace(" ", "")) for x in (a, b))
    return m == "near" and letters >= SHORT_NAME


def bounced_addresses(summary: str) -> list[str]:
    """Addresses a delivery-failure notice says failed, best evidence first.

    A Final-Recipient or Original-Recipient line names the failed address; only
    without one does the first address in the text count (it may be the sender).
    """
    text = summary.lower()
    if not any(p in text for p in BOUNCE_PHRASES):
        return []
    named = sorted(RECIPIENT.finditer(summary), key=lambda m: m.group(1).lower() != "final")
    if named:
        return list(dict.fromkeys(m.group(2).lower() for m in named))
    m = EMAIL.search(summary)
    return [m.group(0).lower()] if m else []


def bounced_address(summary: str) -> str | None:
    found = bounced_addresses(summary)
    return found[0] if found else None


def phone_key(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    return digits[-9:] if len(digits) >= 7 else ""


def check_crm(folder: Path, today: date | None = None, jobs: list[str] | None = None) -> list[Finding]:
    """Rules A1-F4 from .claude/agents/crm-steward.md, one Finding per (rule, entity)."""
    partners = read_csv(folder / "partners.csv", (
        "partner_id", "name", "status", "priority", "owner", "market",
        "next_step", "next_step_date", "last_contact", "live_offers"))
    contacts = read_csv(folder / "contacts.csv", ("contact_id", "partner_id", "email", "status"))
    activity = read_csv(folder / "activity.csv", ("date", "partner_id", "source", "summary"))
    if not partners:
        raise InputError("partners.csv: no partners")
    if not activity:
        raise InputError("activity.csv: the log is empty, so freshness can't be checked")
    for n, a in enumerate(activity, start=2):
        a["_day"] = parse_day(a["date"], f"activity.csv line {n}")  # type: ignore[assignment]
        if a["_day"] is None:
            raise InputError(f"activity.csv line {n}: empty date")
    today = today or max(a["_day"] for a in activity)  # type: ignore[type-var]

    out: dict[tuple[str, str], Finding] = {}

    def add(rule: str, entity: str, evidence: str) -> None:
        out.setdefault((rule, entity), Finding(rule, entity, CRM_RULES[rule], evidence))

    # A1 automation health: each job daily, from its own first line in the log to today
    job_names = jobs if jobs is not None else sorted({a["source"] for a in activity} - HUMAN_SOURCES)
    for job in job_names:
        days = {a["_day"] for a in activity if a["source"] == job}
        if not days:
            add("A1", job, f"no {job} line in the log at all")
            continue
        d = min(days)
        while d <= today:  # type: ignore[operator]
            if d not in days:
                add("A1", job, f"no {job} line on {d}")
                break
            d += timedelta(days=1)

    # B3 duplicate rows
    for label, rows, key in (("partners.csv", partners, "partner_id"), ("contacts.csv", contacts, "contact_id")):
        seen: set[str] = set()
        for r in rows:
            if r[key] in seen:
                add("B3", r[key], f"{label} has {r[key]} more than once")
            seen.add(r[key])

    # Every row is parsed and checked below, a repeated partner_id included: B3 flags the
    # repeat, but a problem on the second row must not disappear behind it.
    by_id: dict[str, dict[str, str]] = {}
    for n, p in enumerate(partners, start=2):
        where = f"partners.csv line {n} ({p['partner_id']})"
        p["_offers"] = parse_int(p["live_offers"], f"{where} live_offers")  # type: ignore[assignment]
        p["_next"] = parse_day(p["next_step_date"], f"{where} next_step_date")  # type: ignore[assignment]
        p["_last"] = parse_day(p["last_contact"], f"{where} last_contact")  # type: ignore[assignment]
        by_id.setdefault(p["partner_id"], p)

    # B1 near-same names or a shared company domain, B2 orphan contacts
    domains: dict[str, set[str]] = {}
    phones: dict[str, set[str]] = {}
    for p in partners:
        if phone_key(p.get("phone", "")):
            phones.setdefault(p["partner_id"], set()).add(phone_key(p["phone"]))
    for c in contacts:
        if c["partner_id"] not in by_id:
            add("B2", c["contact_id"], f"partner {c['partner_id'] or '(empty)'} doesn't exist")
            continue
        domain = c["email"].rsplit("@", 1)[-1].lower() if "@" in c["email"] else ""
        if domain and domain not in FREE_MAIL:
            domains.setdefault(domain, set()).add(c["partner_id"])
        if phone_key(c.get("phone", "")):
            phones.setdefault(c["partner_id"], set()).add(phone_key(c["phone"]))
    pairs: dict[tuple[str, str], str] = {}
    ids = sorted(by_id)
    for i, a_id in enumerate(ids):
        for b_id in ids[i + 1:]:
            a_name, b_name = by_id[a_id]["name"], by_id[b_id]["name"]
            if near_same_name(a_name, b_name):
                pairs[(a_id, b_id)] = f"names {a_name!r} / {b_name!r}"
            elif name_match(a_name, b_name) and phones.get(a_id, set()) & phones.get(b_id, set()):
                pairs[(a_id, b_id)] = f"short near-same names {a_name!r} / {b_name!r} and a shared phone"
    for domain, owners in domains.items():
        owners_sorted = sorted(owners)
        for i, a_id in enumerate(owners_sorted):
            for b_id in owners_sorted[i + 1:]:
                pairs.setdefault((a_id, b_id), f"shared domain {domain}")
    for (a_id, b_id), why in pairs.items():
        add("B1", f"{a_id}+{b_id}", why)

    emails = [a for a in activity if a["source"] == "email"]
    bounced = {addr for a in emails for addr in bounced_addresses(a["summary"])}
    newest_mail: dict[str, date] = {}
    for a in emails:
        if not bounced_addresses(a["summary"]) and a["partner_id"]:
            d = a["_day"]
            if a["partner_id"] not in newest_mail or d > newest_mail[a["partner_id"]]:  # type: ignore[operator]
                newest_mail[a["partner_id"]] = d  # type: ignore[assignment]

    for p in partners:
        pid, status, prio = p["partner_id"], norm(p["status"]), p["priority"]
        offers, last, nxt_date = p["_offers"], p["_last"], p["_next"]
        mail = newest_mail.get(pid)
        is_open = status in OPEN

        # C consistency
        if status in CLOSED and offers > 0:  # type: ignore[operator]
            add("C1", pid, f"status={p['status']}, live_offers={offers}")
        if status == "live" and offers == 0:
            add("C2", pid, "status=Live, live_offers=0")
        if mail and (last is None or mail > last):  # type: ignore[operator]
            add("C3", pid, f"last_contact={last}, newest mail {mail}")

        # D action
        if is_open and (not p["next_step"] or nxt_date is None):
            add("D1", pid, f"next_step={p['next_step']!r}, next_step_date={p['next_step_date']!r}")
        if nxt_date and nxt_date < today and status != "lost":  # type: ignore[operator]
            add("D2", pid, f"next_step_date={nxt_date}")
        if status == "lost" and p["next_step"]:
            add("D3", pid, f"next_step={p['next_step']!r}")
        effective = max(d for d in (last, mail) if d) if (last or mail) else None
        if is_open and prio in CADENCE and effective:
            age, window = (today - effective).days, CADENCE[prio]  # type: ignore[operator]
            if age > window:
                add("D4", pid, f"{age} days since contact, window {window}")
            elif age > window * 0.75:
                add("D5", pid, f"{age} days since contact, window {window}")

        # E contacts
        mine = [c for c in contacts if c["partner_id"] == pid]
        for c in mine:
            if c["email"].lower() in bounced and norm(c["status"]) == "active":
                add("E1", c["contact_id"], f"{c['email']} bounced, status Active")
        if mine and all(norm(c["status"]) in ("to verify", "former") for c in mine):
            add("E2", pid, "only To verify / Former contacts")

        # F data gaps on open partners
        if is_open:
            for rule, field in (("F1", "priority"), ("F2", "market"), ("F3", "owner")):
                if not p[field]:
                    add(rule, pid, f"{field} empty")
            if not mine:
                add("F4", pid, "no contacts")

    return sorted(out.values())


# -------------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pattern", choices=["inventory", "crm"])
    ap.add_argument("folder", type=Path)
    ap.add_argument("--today", help="as-of date for crm, YYYY-MM-DD (default: newest date in activity.csv)")
    ap.add_argument("--source-of-truth", help="inventory: file name of the source-of-truth export")
    ap.add_argument("--jobs", help="crm: comma-separated scheduled job names (default: every non-email source)")
    args = ap.parse_args(argv)
    try:
        if args.pattern == "inventory":
            findings = check_inventory(args.folder, args.source_of_truth)
        else:
            today = parse_day(args.today, "--today") if args.today else None
            jobs = [j.strip() for j in args.jobs.split(",") if j.strip()] if args.jobs else None
            findings = check_crm(args.folder, today, jobs)
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for f in findings:
        print(f"{f.rule}  {f.entity:<14} {f.bucket:<9} {f.evidence}")
    print(f"\n{len(findings)} findings (distinct rule + entity pairs).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
