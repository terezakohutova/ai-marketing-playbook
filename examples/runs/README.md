# Blind runs

One folder per dataset. `output.md` is the agent's output, copied byte for byte; `run.json` says when it ran, which model, the exact prompt, and which files the agent was given (with SHA-256 hashes that match the files in this repo). The runs are kept apart from the input folders so copying an input folder never copies an answer.

How each run was done: a fresh Claude Code subagent (model: sonnet) in an empty folder holding only a copy of the agent definition and the dataset's CSVs. No pattern doc, no dataset README, no answer key, no earlier output. Read-only access was set by the prompt, not by a sandbox. One run per dataset, no retries, nothing edited afterwards.

```bash
python tools/score_run.py --all --per-rule
```

`earlier/` folders hold runs made before the agent definitions had rule ids and a findings block. They can't be scored by the current scorer and are kept for the record.
