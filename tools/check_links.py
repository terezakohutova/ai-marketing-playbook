"""Fail if a relative Markdown link or image points at a missing file or a missing heading anchor.

    python tools/check_links.py

Anchors (`file.md#some-heading`, `#some-heading`) are checked against the
GitHub-style slugs of the target file's headings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.M | re.S)
HEADING = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t#]*$", re.M)


def strip_code(text: str) -> str:
    return re.sub(r"`[^`\n]*`", "", FENCE.sub("", text))


def slugs(md: Path) -> set[str]:
    out: set[str] = set()
    seen: dict[str, int] = {}
    for title in HEADING.findall(FENCE.sub("", md.read_text(encoding="utf-8"))):
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)  # link text only
        slug = re.sub(r"[^\w\- ]", "", title.lower().replace("`", "")).replace(" ", "-")
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        out.add(slug if n == 0 else f"{slug}-{n}")
    return out


def broken_links(root: Path = ROOT) -> list[str]:
    broken = []
    for md in sorted(root.rglob("*.md")):
        if ".git" in md.parts:
            continue
        for target in LINK.findall(strip_code(md.read_text(encoding="utf-8"))):
            if re.match(r"[a-z][a-z0-9+.-]*:", target):
                continue
            path, _, anchor = target.partition("#")
            dest = (md.parent / path) if path else md
            if not dest.exists():
                broken.append(f"{md.relative_to(root)} -> {target} (no such file)")
            elif anchor and dest.suffix == ".md" and anchor.lower() not in slugs(dest):
                broken.append(f"{md.relative_to(root)} -> {target} (no such heading)")
    return broken


if __name__ == "__main__":
    bad = broken_links()
    print("\n".join(bad) or "All relative links and anchors resolve.")
    sys.exit(1 if bad else 0)
