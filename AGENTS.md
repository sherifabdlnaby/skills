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
  | `agents/vendor/`                                                                  | `mise run agents:sync`                                        |

## Skills of ours

A skill is a folder with a `SKILL.md` that the `skills` list of a plugin manifest ships; one under a `vendor/` folder is not ours. Add a new skills folder in the manifests only:
`mise run skills:check` and `mise run tokens` follow them, and the check names what is missing when you add, remove, or rename a skill.

- **Plugins stand alone, skills may depend on each other.** A plugin ships everything its skills need and depends on no other plugin. Skills inside a plugin may depend on each other
  (e.g. `watch-pr` runs on top of `git`). Users can also install one skill on its own, so a skill that needs another names it where the agent reads it, and its README says so too.
- **Skills reach each other by name, never by file path.** A file the agent reads (`SKILL.md`, `references/`) links only to files inside its own skill folder; a path into another skill
  breaks when that skill is installed alone. To use another skill, name it so the agent loads it, which means the target must be model-invocable. A README is for humans and may link anywhere.
- **Invocation follows use.** A skill only the user types (a typing-saver like `wait-what` or `afk-soon`) sets `disable-model-invocation: true`; a skill another skill loads (`afk`,
  `watch-pr`, `no-comments`) stays model-invocable. Both keep a short, neutral description, so the model loads it when told to and not on its own.
- **`README.md` beside each `SKILL.md`**, for humans who decide whether and how to use the skill: the problem, the outcome, the operating shape, the tradeoffs. Write it from the skill,
  without its prompt text and without token counts. It links to `SKILL.md` (the canonical agent instructions) and up to the nearest folder above it that holds a `README.md`.
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
- **Subagents** live in `agents/vendor/`, because the skills CLI fetches skills only. Add a source line to the `agents:sync` task, run `mise run agents:sync`, and list the file under
  `agents` in `.claude-plugin/plugin.json` (Claude Code takes `.md` paths, not a folder). A sync fetches upstream's default branch too: read `git diff agents/vendor` before you commit.

## Plugins and releases

| Plugin          | Root      | Ships                                                          | Manifests                                                                |
| --------------- | --------- | -------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `skills`        | `./`      | every skill, vendored included, `agents/vendor/`, and `hooks/` | `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`               |
| `ai-disclosure` | `skills/` | `skills/ai-disclosure/` only                                   | `skills/.claude-plugin/plugin.json`, `skills/.cursor-plugin/plugin.json` |

- **A change to what a plugin ships needs both of its manifests bumped to the same version.** `skills/ai-disclosure/` ships in both plugins, so a change there bumps all four files.
  `mise run version:check --fix` writes the bumps (`--bump minor` or `major` for more than a patch); run it again after a rebase onto a `main` that took the same number. The push gate
  and CI fail without the bump.
- **A release cuts itself.** Merging a version bump to `main` tags and publishes; there is no release step to run.
- **Marketplaces** (`.claude-plugin/`, `.cursor-plugin/`, Codex's `.agents/plugins/`) list every plugin. A plugin carries only what sits inside its own folder, and Cursor needs a plugin's
  `skills` as a list.

## Tooling

Edit the config, then run `mise run check`.

| What                                                    | Where                                                                            |
| ------------------------------------------------------- | -------------------------------------------------------------------------------- |
| tools, tasks, env, settings, hooks                      | `mise.toml`; file tasks in `.config/mise/tasks/`                                 |
| lint and format steps (commit, push, `check` pipelines) | `.config/hk.pkl`                                                                 |
| a linter's own config                                   | `.config/`, wired from `.config/hk.pkl` when the tool does not find it there     |

Configured in the repo settings, outside the tree, so scaffold no replacement: CodeQL default setup, Dependabot alerts and security updates, secret scanning with push protection, and a
`main` ruleset that requires the `check` job.
