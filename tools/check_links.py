"""Fail if any relative Markdown link or image in the repo points at a file that doesn't exist.

    python tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")


def broken_links(root: Path = ROOT) -> list[str]:
    broken = []
    for md in sorted(root.rglob("*.md")):
        if ".git" in md.parts:
            continue
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for target in LINK.findall(text):
            if re.match(r"[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if not (md.parent / path).exists():
                broken.append(f"{md.relative_to(root)} -> {target}")
    return broken


if __name__ == "__main__":
    bad = broken_links()
    print("\n".join(bad) or "All relative links resolve.")
    sys.exit(1 if bad else 0)
