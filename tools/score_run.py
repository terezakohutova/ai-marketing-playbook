"""Score an agent run against a hand-written answer key.

The agent must end its output with one fenced ```findings block holding a
JSON list of {"rule", "entity", "bucket"} objects (see .claude/agents/*.md).
Only that block is scored; the prose around it is for people.

    python tools/score_run.py tests/answer_keys/crm-1.json examples/runs/crm-1/output.md
    python tools/score_run.py --all          # every examples/runs/<dataset>/output.md

A finding counts as caught only if its (rule, entity) pair is in the key with
the same bucket. Everything else in the block is a wrong flag: unknown rules,
catch-all or malformed entities ("all", "P01-P10", "P01, P02"), wrong buckets
and findings the key doesn't have. Precision and recall are reported overall
and per rule. Standard library only, Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_check import CRM_RULES, INVENTORY_RULES  # noqa: E402

RULES = {"crm": CRM_RULES, "inventory": INVENTORY_RULES}
ITEM = re.compile(r"^[A-Za-z]+-\d+$")
PARTNER = re.compile(r"^P\d+$")
CONTACT = re.compile(r"^C\d+$")
PAIR = re.compile(r"^(P\d+)\+(P\d+)$")
JOB = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$")  # e.g. nightly-sync; a bare word like "all" fails
BLOCK = re.compile(
    r"^(?P<fence>`{3,}|~{3,})[ \t]*(?:json[ \t]+)?findings[ \t]*\r?\n(?P<body>.*?)^(?P=fence)[ \t]*$",
    re.M | re.S,
)


class ScoreError(ValueError):
    """The output has no usable findings block."""


def entity_ok(pattern: str, rule: str, entity: str) -> str | None:
    """Return the normalised entity, or None if it isn't one single valid id for that rule."""
    if pattern == "inventory":
        return entity if ITEM.match(entity) else None
    if rule == "A1":
        return entity if JOB.match(entity) else None
    if rule == "B1":
        m = PAIR.match(entity)
        if not m or m.group(1) == m.group(2):
            return None
        return "+".join(sorted(m.groups(), key=lambda p: (len(p), p)))
    if rule in ("B2", "E1"):
        return entity if CONTACT.match(entity) else None
    if rule == "B3":
        return entity if PARTNER.match(entity) or CONTACT.match(entity) else None
    return entity if PARTNER.match(entity) else None


def parse_findings(text: str) -> list[dict]:
    blocks = list(BLOCK.finditer(text))
    if not blocks:
        raise ScoreError("no ```findings block in the output")
    if len(blocks) > 1:
        raise ScoreError(f"{len(blocks)} ```findings blocks; expected exactly one")
    try:
        data = json.loads(blocks[0].group("body"))
    except json.JSONDecodeError as e:
        raise ScoreError(f"findings block is not valid JSON: {e}") from None
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise ScoreError("findings block must be a JSON list of objects")
    return data


@dataclass
class RuleScore:
    tp: int = 0
    fp: int = 0
    fn: int = 0


@dataclass
class Score:
    tp: list = field(default_factory=list)
    fp: list = field(default_factory=list)  # (rule, entity, reason)
    fn: list = field(default_factory=list)
    per_rule: dict = field(default_factory=dict)

    @property
    def precision(self) -> float:
        # No flags at all: 1.0 when nothing was expected (a correct "all clear"),
        # 0.0 when something was (silence is not precise, it is a miss).
        n = len(self.tp) + len(self.fp)
        if n:
            return len(self.tp) / n
        return 0.0 if self.fn else 1.0

    @property
    def recall(self) -> float:
        n = len(self.tp) + len(self.fn)
        return len(self.tp) / n if n else 1.0


def score(key: dict, predicted: list[dict]) -> Score:
    pattern = key["pattern"]
    rules = RULES[pattern]
    expected = {(f["rule"], f["entity"]): f["bucket"] for f in key["findings"]}
    s = Score(per_rule={r: RuleScore() for r in rules})
    seen: set[tuple[str, str]] = set()

    for obj in predicted:
        rule = str(obj.get("rule", "")).strip().upper()
        raw = str(obj.get("entity", "")).strip()
        bucket = str(obj.get("bucket", "")).strip().lower()
        if rule not in rules:
            s.fp.append((rule or "?", raw, "unknown rule"))
            continue
        entity = entity_ok(pattern, rule, raw)
        if entity is None:
            s.fp.append((rule, raw, "not one valid entity id (catch-all or malformed)"))
            s.per_rule[rule].fp += 1
            continue
        if (rule, entity) in seen:
            continue  # repeating a finding is noise, not a second finding
        seen.add((rule, entity))
        if (rule, entity) not in expected:
            s.fp.append((rule, entity, "not in the answer key"))
            s.per_rule[rule].fp += 1
        elif bucket != expected[(rule, entity)]:
            s.fp.append((rule, entity, f"wrong bucket {bucket or '(none)'!r}"))
            s.per_rule[rule].fp += 1
        else:
            s.tp.append((rule, entity))
            s.per_rule[rule].tp += 1

    caught = set(s.tp)
    for rule, entity in sorted(expected):
        if (rule, entity) not in caught:
            s.fn.append((rule, entity))
            s.per_rule[rule].fn += 1
    return s


def score_file(key_path: Path, output_path: Path) -> Score:
    key = json.loads(key_path.read_text(encoding="utf-8"))
    return score(key, parse_findings(output_path.read_text(encoding="utf-8")))


def fmt(x: float) -> str:
    return f"{x:.2f}"


def report(name: str, s: Score, verbose: bool = True) -> str:
    lines = [f"{name}: precision {fmt(s.precision)} ({len(s.tp)}/{len(s.tp) + len(s.fp)}), "
             f"recall {fmt(s.recall)} ({len(s.tp)}/{len(s.tp) + len(s.fn)})"]
    if verbose:
        for rule, entity in s.fn:
            lines.append(f"  missed      {rule} {entity}")
        for rule, entity, why in s.fp:
            lines.append(f"  wrong flag  {rule} {entity}: {why}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("key", nargs="?", type=Path, help="answer key JSON")
    ap.add_argument("output", nargs="?", type=Path, help="agent output (Markdown with a findings block)")
    ap.add_argument("--all", action="store_true", help="score every examples/runs/<dataset>/output.md")
    ap.add_argument("--per-rule", action="store_true", help="also print precision and recall per rule")
    ap.add_argument("--min-precision", type=float, default=0.0)
    ap.add_argument("--min-recall", type=float, default=0.0)
    args = ap.parse_args(argv)

    if args.all:
        jobs = [(ROOT / "tests" / "answer_keys" / f"{p.parent.name}.json", p)
                for p in sorted((ROOT / "examples" / "runs").glob("*/output.md"))]
        if not jobs:
            print("error: no runs found under examples/runs/", file=sys.stderr)
            return 2
    elif args.key and args.output:
        jobs = [(args.key, args.output)]
    else:
        ap.error("give an answer key and an output, or --all")

    failed = False
    totals: dict[str, Score] = {}
    for key_path, out_path in jobs:
        name = out_path.parent.name if args.all else str(out_path)
        try:
            s = score_file(key_path, out_path)
        except (ScoreError, OSError, json.JSONDecodeError) as e:
            print(f"{name}: error: {e}")
            failed = True
            continue
        print(report(name, s))
        pattern = json.loads(key_path.read_text(encoding="utf-8"))["pattern"]
        t = totals.setdefault(pattern, Score(per_rule={r: RuleScore() for r in RULES[pattern]}))
        t.tp += s.tp
        t.fp += s.fp
        t.fn += s.fn
        for r, rs in s.per_rule.items():
            t.per_rule[r].tp += rs.tp
            t.per_rule[r].fp += rs.fp
            t.per_rule[r].fn += rs.fn
        if s.precision < args.min_precision or s.recall < args.min_recall:
            failed = True

    if len(jobs) > 1 or args.per_rule:
        print()
        for pattern, t in totals.items():
            print(report(f"{pattern} total", t, verbose=False))
            if args.per_rule:
                for r, rs in t.per_rule.items():
                    p = rs.tp / (rs.tp + rs.fp) if rs.tp + rs.fp else None
                    rc = rs.tp / (rs.tp + rs.fn) if rs.tp + rs.fn else None
                    print(f"  {r}: tp {rs.tp} fp {rs.fp} fn {rs.fn}  precision "
                          f"{fmt(p) if p is not None else '-'}  recall {fmt(rc) if rc is not None else '-'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
