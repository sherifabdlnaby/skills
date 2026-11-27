# Evals

These evals measure two things. Run them on two refs (for example `origin/main` and your branch) to see if a change helps or hurts.

- **Work on this repo**: does a fresh agent find and do the maintenance work (which files to change, which `mise` task to run, which rule applies)? Changes to `AGENTS.md`, a task, or a doc
  move this.
- **The skills in a project that uses them**: does the agent load the right skill, and open the reference page the skill routes to, before it starts the work? Changes to a skill's
  description, its router, or a hook move this.

## How it works

[`run.py`](run.py) runs headless Claude Code (`claude -p`) once for each case in [`cases.toml`](cases.toml), in a throwaway `git worktree` of the ref. It then grades the result with
deterministic checks. No model does the grading.

- **Clean room**: the agent gets only what the repo gives it (`AGENTS.md`, project settings). `--setting-sources project` keeps out your user `CLAUDE.md`, plugins, and skills, and
  `autoMemoryEnabled: false` keeps out auto-memory. Worktrees live in the system temp dir, outside `$HOME`, so no `CLAUDE.md` from a parent directory loads.
- **Your checkout stays untouched**: without `--ref`, the runner snapshots the working tree (uncommitted and untracked files included) into a dangling commit, and the worktrees start from it.
  The snapshot is `HEAD` in each worktree, so `git diff` shows only the agent's changes.
- **`nav` cases** ask a question with read-only tools. Each regex in `must` has to match the final answer, and none in `must_not` may match.
- **`task` cases** let the agent edit its own worktree (no commit, push, or `gh`). Each command in `checks` then runs in that worktree; exit 0 is a pass.
- **`skill` cases** run in a throwaway project that [`sandbox/init.sh`](sandbox/init.sh) builds, with the ref loaded as a plugin (`--plugin-dir`). The runner reads the tool calls of the
  session. A case passes when each skill in `load` was loaded and each page in `read` was opened before the agent acted, and no skill in `not_load` was loaded at all. The agent acts at the
  first call that matches `act` and ran. A call that a hook blocked is not the act: the agent can still load the skill and try again.
- **The sandbox is safe to act in**: its `origin` is a local folder, [`sandbox/bin/gh`](sandbox/bin/gh) stands in for the GitHub CLI and posts nothing, and your git config stays out. A
  `skill` run stops as soon as its grade cannot change, so most runs take a few seconds.

The runner prints a table and a summary per kind, plus the token count of the instruction files every session loads at the ref. For `skill` cases it also prints one rate per check
(`load git 18/18`). It writes the full records, with raw answers, tool calls, and per-check output, to `evals/results/` (git-ignored). It deletes the transcript Claude Code saves for each
run, so eval sessions do not pile up in your history.

## Run

You need `claude` on `PATH`, signed in. Then:

```sh
mise run eval --ref origin/main --label main          # baseline
mise run eval --label branch                          # your working tree
mise run eval --case add-skill --trials 3             # one case, three runs
mise run eval --kind skill --model opus --trials 3    # only the skill cases
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
- A `skill` case takes `load`, `not_load` (lists of skill names), `read`, and `act`:

  ```toml
  [[case]]
  id = "git-commit-then-pr"
  kind = "skill"
  setup = "git switch --quiet --create greet-punctuation && echo '# more' >> README.md"
  before = ["commit this"]                              # earlier turns of the same session
  prompt = "push it and open a PR"
  load = ["git", "ai-disclosure"]
  act = '\bgh\s+pr\s+create\b'
  read = ['git/references/pull-requests\.md', 'git/references/pr-body\.md']
  ```

  `act` and each `read` entry are regexes. They match one line per tool call, `<Tool> <its main argument>`: `Bash git commit -m x`, `Edit /path/mise.toml`, `Read /path/commits.md`. Take
  the expected pages from the router in the skill's `SKILL.md`. Add a `not_load` case beside a new `load` case when a near miss is likely: it catches a description that fires too often.
- Check the expected answer against the repo, then run the case once with `--case <id>`.

## What a pass does not show

The `skill` cases run short sessions in a clean room. In that setup Sonnet and Opus load every skill, and a vague description does not change that. Real sessions miss a skill in another
place: deep in a long session, when the work starts as a side effect and the prompt does not name it. These cases cannot see that. Treat them as a regression check for descriptions,
routers, and hooks, and measure long sessions from real transcripts.

## Cost

Each run is a real Claude Code session, billed to the signed-in account. The summary line and the records show the cost per run and per kind. `nav` and `skill` runs are short; `task` runs that call
`mise run check` take longer and cost more. Multiply by `--trials` and by the number of refs you compare.
