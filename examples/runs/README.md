# Blind runs

One folder per dataset. `output.md` is the agent's final answer, unedited except for LF line endings; `run.json` says when it ran, which model, the exact command and prompt, which tools the session had, and which files the agent was given (with SHA-256 hashes that a test checks against the files in this repo). The runs are kept apart from the input folders so copying an input folder never copies an answer.

How each run was done: [`tools/blind_run.py`](../../tools/blind_run.py) makes an empty folder holding only a copy of the agent definition and the dataset's CSVs, and starts a fresh, non-interactive Claude Code session there (model: sonnet). The agent definition's body is the whole system prompt. `--tools Read,Grep,Glob` leaves the session no way to write, edit or run anything, and `--safe-mode` keeps CLAUDE.md files, skills, plugins, hooks and MCP servers out. Claude Code still adds its own short environment block (folder, platform, date, account e-mail). No pattern doc, no dataset README, no answer key, no earlier output. The harness, not the agent, saves the answer. Nothing is edited afterwards, and no run was dropped: every run made with the current prompts is here.

The two messy datasets were run three times each: the main `output.md` plus `repeats/run-2/` and `repeats/run-3/`, each with its own `run.json`. The tests pin the score of every one.

```bash
python tools/score_run.py --all --per-rule
```

All runs here were made on 2026-10-14 with agent prompts that contain no string from any dataset (a test enforces that). An earlier set of runs used prompts that quoted strings from the messy datasets; those runs are in git history, not here.

`earlier/` folders hold runs made before the agent definitions had rule ids and a findings block. They can't be scored by the current scorer and are kept for the record.
