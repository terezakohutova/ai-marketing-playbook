"""Run one shipped agent blind on one dataset and save what it says, with provenance.

    python tools/blind_run.py crm-messy --work-dir <somewhere-outside-this-repo>

What it does:

1. Makes an empty run folder <work-dir>/<dataset>/ holding only `agent.md`
   (a copy of the agent definition) and `export/` (a copy of the dataset's
   CSVs). No pattern doc, no dataset README, no answer key, no checker.
2. Starts a fresh Claude Code session in that folder, non-interactive:
   the agent definition's body is the whole system prompt, the tool list is
   the one in its frontmatter (`--tools Read,Grep,Glob`: the session has no
   Write, Edit, Bash or web tool at all), and `--safe-mode` keeps CLAUDE.md
   files, skills, plugins, hooks and MCP servers out.
3. Saves the session's final answer as examples/runs/<dataset>/output.md
   (line endings normalised to LF, nothing else changed) and writes
   run.json with the exact command, prompt and SHA-256 of every file given.

The agent never writes a file; this harness does. Needs the `claude` CLI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT = ("Do the task your instructions describe on the exports in the folder export/ in the current "
          "directory. Read only files inside the current directory. Your final answer is saved verbatim "
          "as your output, so make it your complete output, exactly as you would present it to the person "
          "who asked.")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_agent(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise ValueError("agent file has no frontmatter")
    head, body = text[4:].split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, body.lstrip("\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dataset", help="answer key name, e.g. crm-1 or inv-messy")
    ap.add_argument("--work-dir", type=Path, required=True, help="where the empty run folder is made")
    ap.add_argument("--model", default=None, help="default: the agent's frontmatter model")
    ap.add_argument("--timeout", type=int, default=1200)
    args = ap.parse_args(argv)

    key = json.loads((ROOT / "tests" / "answer_keys" / f"{args.dataset}.json").read_text(encoding="utf-8"))
    agent_rel = f".claude/agents/{'crm-steward' if key['pattern'] == 'crm' else 'inventory-sync'}.md"
    agent_text = (ROOT / agent_rel).read_text(encoding="utf-8")
    meta, body = split_agent(agent_text)
    tools = ",".join(t.strip() for t in meta["tools"].split(","))
    model = args.model or meta.get("model", "sonnet")

    run_dir = args.work_dir.resolve() / args.dataset
    if run_dir.exists():
        shutil.rmtree(run_dir)
    (run_dir / "export").mkdir(parents=True)
    shutil.copyfile(ROOT / agent_rel, run_dir / "agent.md")
    given = [{"path": "agent.md", "copy_of": agent_rel, "sha256": sha256(ROOT / agent_rel)}]
    for csv_path in sorted((ROOT / key["folder"]).glob("*.csv")):
        shutil.copyfile(csv_path, run_dir / "export" / csv_path.name)
        given.append({"path": f"export/{csv_path.name}", "copy_of": f"{key['folder']}/{csv_path.name}",
                      "sha256": sha256(csv_path)})

    cli = shutil.which("claude")
    if not cli:
        print("error: the claude CLI is not on PATH", file=sys.stderr)
        return 2
    flags = ["--model", model, "--tools", tools, "--safe-mode", "--strict-mcp-config",
             "--no-session-persistence"]
    if meta.get("effort"):
        flags += ["--effort", meta["effort"]]
    cmd = [cli, "-p", PROMPT, *flags, "--system-prompt", body]
    done = subprocess.run(cmd, cwd=run_dir, capture_output=True, text=True, encoding="utf-8",
                          timeout=args.timeout)
    if done.returncode != 0 or not done.stdout.strip():
        print(f"error: claude exited {done.returncode}: {done.stderr.strip()[:500]}", file=sys.stderr)
        return 2
    out = done.stdout.replace("\r\n", "\n").rstrip("\n") + "\n"

    dest = ROOT / "examples" / "runs" / args.dataset
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "output.md").write_text(out, encoding="utf-8", newline="\n")
    meta_out = {
        "dataset": args.dataset,
        "date": date.today().isoformat(),
        "runner": "tools/blind_run.py: a fresh, non-interactive Claude Code session (claude -p), one run, no retries",
        "model": model,
        "command": "claude -p <prompt> " + " ".join(flags) + " --system-prompt <body of agent.md>",
        "system_prompt": "the body of agent.md after its frontmatter, nothing else",
        "prompt": PROMPT,
        "tools_available": tools.split(","),
        "read_only": "enforced by the CLI: --tools leaves the session only these tools, so it cannot write, "
                     "edit or run anything; the harness saves the final answer as output.md",
        "context": "--safe-mode: no CLAUDE.md, skills, plugins, hooks or MCP servers. Claude Code still adds "
                   "its own environment block (working directory, platform, date, account e-mail).",
        "run_dir": "<run-dir>, an empty folder outside this repo holding only the files below",
        "files_given": given,
        "not_given": ["the pattern doc", "dataset README", "answer keys", "earlier outputs", "the checker"],
        "output": "output.md: the session's final answer, line endings normalised to LF, otherwise unedited",
        "output_sha256": sha256(dest / "output.md"),
    }
    (dest / "run.json").write_text(json.dumps(meta_out, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"saved examples/runs/{args.dataset}/output.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
