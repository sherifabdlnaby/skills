# Evals

These evals measure how well a fresh agent finds and does maintenance work in this repo: which files to change, which `mise` task to run, which rule applies. Run them on two refs (for
example `origin/main` and your branch) to see if a change to `AGENTS.md`, a task, or a doc helps or hurts.

## How it works

[`run.py`](run.py) runs headless Claude Code (`claude -p`) once for each case in [`cases.toml`](cases.toml), in a throwaway `git worktree` of the ref. It then grades the result with
deterministic checks. No model does the grading.

- **Clean room**: the agent gets only what the repo gives it (`AGENTS.md`, project settings). `--setting-sources project` keeps out your user `CLAUDE.md`, plugins, and skills, and
  `autoMemoryEnabled: false` keeps out auto-memory. Worktrees live in the system temp dir, outside `$HOME`, so no `CLAUDE.md` from a parent directory loads.
- **Your checkout stays untouched**: without `--ref`, the runner snapshots the working tree (uncommitted and untracked files included) into a dangling commit, and the worktrees start from it.
  The snapshot is `HEAD` in each worktree, so `git diff` shows only the agent's changes.
- **`nav` cases** ask a question with read-only tools. Each regex in `must` has to match the final answer, and none in `must_not` may match.
- **`task` cases** let the agent edit its own worktree (no commit, push, or `gh`). Each command in `checks` then runs in that worktree; exit 0 is a pass.

The runner prints a table and a summary per kind, plus the token count of the instruction files every session loads at the ref. It writes the full records, with raw answers and per-check
output, to `evals/results/` (git-ignored).

## Run

You need `claude` on `PATH`, signed in. Then:

```sh
mise run eval --ref origin/main --label main          # baseline
mise run eval --label branch                          # your working tree
mise run eval --case add-skill --trials 3             # one case, three runs
mise run eval --help                                  # every flag
```

A model answers differently from run to run. Use `--trials` above 1 before you trust a difference between two refs.

## Add a case

Append a `[[case]]` table to `cases.toml`:

```toml
[[case]]
id = "stale-tokens"
kind = "nav"
prompt = "CI says the token estimates in skills/README.md are stale. How do I fix it?"
must = ['mise run tokens --fix']
```

- Write the prompt as a user would, without hints at the answer.
- Write each regex so a correct answer in other words passes and a wrong one fails. Matching is case-insensitive and `.` matches newlines.
- A `task` case takes an optional `setup` shell command that runs before the agent, and a `[case.checks]` table of name to shell command. Compare against `git show HEAD:<path>` to check
  that the agent changed something.
- An optional `max_turns` overrides the default for the kind in `run.py`.
- Check the expected answer against the repo, then run the case once with `--case <id>`.

## Cost

Each run is a real Claude Code session, billed to the signed-in account. The summary line and the records show the cost per run and per kind. `nav` runs are short; `task` runs that call
`mise run check` take longer and cost more. Multiply by `--trials` and by the number of refs you compare.
