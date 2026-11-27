# AGENTS.md

Agent skills written by hand (`skills/`), other people's skills (`skills/vendor/`), hooks (`hooks/`), and the plugin manifests that ship them. [**mise**](https://mise.jdx.dev) pins the tools,
exposes the tasks, and wires the git hooks; `mise.toml` is the source of truth.

## Every change

- **Set up** once, and again in each new worktree: `mise trust && mise run setup`.
- **Work through mise.** `mise tasks` lists every task, `mise run <task> --help` its flags. A missing tool or script becomes a mise tool or task, so local runs, hooks, and CI stay in sync.
- **Finish** with `mise run check --fix`, `mise run version:check --fix`, then `mise run check`. The first formats and regenerates the token tables, the second bumps the plugin versions
  the change needs. A failure names its fix. `mise run test` runs the tests.
- **Hooks** ([hk](https://hk.jdx.dev)): a commit runs the commit gates on staged files, a push runs the push gates and the tests, CI runs all of them. Fix a failing step;
  `git commit --no-verify` is for a WIP commit. The hooks live in git config (`hook.<name>.command`), so an empty `.git/hooks/` is normal.
- **Machine-owned files** change through their command, also when they conflict in a rebase:

  | Files                                                                             | Command                                                       |
  | --------------------------------------------------------------------------------- | ------------------------------------------------------------- |
  | `skills/README.md`, `skills/vendor/README.md` (the only homes of token estimates) | `mise run tokens --fix`                                       |
  | `skills/vendor/`, `skills-lock.json`                                              | the `skills:*` tasks, see [Vendored skills](#vendored-skills) |
  | `mise.lock`                                                                       | `mise lock`, after any `[tools]` change                       |

## Skills of ours

A skill is a folder under `skills/` or `skills/variants/` that holds a `SKILL.md`. `mise run skills:check` enforces the folder shape, so it names what is missing when you add, remove, or
rename one.

- **Stand alone.** Users install one skill at a time: write each as if no other skill and no hook is present. A reference to another skill or a hook is an optional extra. Raise a hard
  dependency with the user.
- **`README.md` beside each `SKILL.md`**, for humans who decide whether and how to use the skill: the problem, the outcome, the operating shape, the tradeoffs. Write it from the skill,
  without its prompt text and without token counts. It links to `SKILL.md` (the canonical agent instructions) and up to `skills/`.
- **The root `README.md`** lists each skill by hand, variants on the same line.
- **Versions line.** A skill that teaches third-party tools (e.g. mise-fy) says in `SKILL.md` which release of each tool it was checked against, and when. Update the line only when a
  change comes from reading newer release notes.

## Vendored skills

| Intent                  | Command                                                                                         |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| see what a repo carries | `npx skills add <owner>/<repo> -l`                                                              |
| add                     | `npx skills add <owner>/<repo> -s <skill> -y` (one `-s` per skill), then `mise run skills:sync` |
| update one, or all      | `mise run skills:update [skill…]`                                                               |
| remove                  | `mise run skills:remove <skill>…`                                                               |
| rebuild from the lock   | `mise run skills:sync`                                                                          |

- **Remove through the task only.** A bare `npx skills remove` also deletes a skill of ours that has the same name.
- **A sync replaces `skills/vendor/` wholesale**, so a hand edit does not survive. A skill you want to own moves to `skills/` as ours.
- **Every sync is an upgrade.** The lock names a source, not a version, so a sync fetches upstream's default branch: read `git diff skills/vendor` before you commit.
- Linters skip `**/vendor/**`. Vendored skills get no README from us; `skills/vendor/README.md` is a generated index.

## Plugins and releases

| Plugin          | Root      | Ships                                        | Manifests                                                                |
| --------------- | --------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| `skills`        | `./`      | every skill, vendored included, and `hooks/` | `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`               |
| `ai-disclosure` | `skills/` | `skills/ai-disclosure/` only                 | `skills/.claude-plugin/plugin.json`, `skills/.cursor-plugin/plugin.json` |

- **A change to what a plugin ships needs both of its manifests bumped to the same version.** `skills/ai-disclosure/` ships in both plugins, so a change there bumps all four files.
  `mise run version:check --fix` writes the bumps (`--bump minor` or `major` for more than a patch); run it again after a rebase onto a `main` that took the same number. The push gate
  and CI fail without the bump.
- **A release cuts itself.** Merging a version bump to `main` tags and publishes; there is no release step to run.
- **Marketplaces** (`.claude-plugin/`, `.cursor-plugin/`, Codex's `.agents/plugins/`) list every plugin. A plugin carries only what sits inside its own folder, and Cursor needs a plugin's
  `skills` as a list.

## Tooling

Edit the config, then run `mise run check`.

| What                                                    | Where                                                                        |
| ------------------------------------------------------- | ---------------------------------------------------------------------------- |
| tools, tasks, env, settings, hooks                      | `mise.toml`; file tasks in `.config/mise/tasks/`                             |
| lint and format steps (commit, push, `check` pipelines) | `.config/hk.pkl`                                                             |
| a linter's own config                                   | `.config/`, wired from `.config/hk.pkl` when the tool does not find it there |
| evals for this file and the tasks                       | `evals/`: after a change here, `mise run eval` must hold its pass rate       |

Configured in the repo settings, outside the tree, so scaffold no replacement: CodeQL default setup, Dependabot alerts and security updates, secret scanning with push protection, and a
`main` ruleset that requires the `check` job.
