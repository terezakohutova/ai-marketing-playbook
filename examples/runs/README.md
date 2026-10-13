# Blind runs

One folder per dataset. `output.md` is the agent's final answer, unedited except for LF line endings; `run.json` says when it ran, which model, the exact command and prompt, which tools the session had, and which files the agent was given (with SHA-256 hashes that a test checks against the files in this repo). The runs are kept apart from the input folders so copying an input folder never copies an answer.

How each run was done: [`tools/blind_run.py`](../../tools/blind_run.py) makes an empty folder holding only a copy of the agent definition and the dataset's CSVs, and starts a fresh, non-interactive Claude Code session there (model: sonnet). The agent definition's body is the whole system prompt. `--tools Read,Grep,Glob` leaves the session no way to write, edit or run anything, and `--safe-mode` keeps CLAUDE.md files, skills, plugins, hooks and MCP servers out. Claude Code still adds its own short environment block (folder, platform, date, account e-mail). No pattern doc, no dataset README, no answer key, no earlier output. The harness, not the agent, saves the answer. One run per dataset, no retries, nothing edited afterwards.

```bash
python tools/score_run.py --all --per-rule
```

`earlier/` folders hold runs made before the agent definitions had rule ids and a findings block. They can't be scored by the current scorer and are kept for the record.
