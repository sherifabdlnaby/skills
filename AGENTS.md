# AGENTS.md

## Toolchain (mise)

This project uses [**mise**](https://mise.jdx.dev) to pin tools, expose tasks, and wire git hooks. `mise.toml` is the source of truth. Don't install tools by hand or add ad-hoc scripts; add a mise
tool or task instead.

**Setup** (once, and per new worktree): `mise trust && mise run setup`.

**Run via mise.** Run `mise run check` before you call work done. A few examples, not the full list:

```sh
mise run check          # all linters/formatters/validators (alias: lint); add --fix to auto-fix
mise run test           # placeholder (no automated tests yet)
mise tasks              # discover every task
mise run <task> --help  # a task's flags
```

Prefer `mise run <task>` over calling the tool directly, so local, hooks, and CI stay in sync.

## Git hooks (hk)

Commits run [hk](https://hk.jdx.dev), the same `check` CI runs, to format and lint staged files. Fix failures with `mise run check --fix`. Don't disable steps to push a commit through;
`git commit --no-verify` skips hooks for a WIP commit. `mise run setup` installs the hooks into
git *config* (`hook.<name>.command`) — `.git/hooks/` stays empty, that doesn't mean they're absent.

## Extending the setup

Changing tools, tasks, env, or hooks? Edit the config, don't bolt on scripts, then run `mise run check`. Where things live:

- **`mise.toml`**: the source of truth for `[tools]`, `[tasks]`, `[env]`/`[vars]`, `[settings]`, and `[hooks]`.
- **`mise.lock`**: resolved versions plus checksums. Commit it; regenerate with `mise install` after a `[tools]` change.
- **`.config/`**: everything that would otherwise clutter the root — `hk.pkl` plus each linter's config (`typos.toml`, `lychee.toml`, `rumdl.toml`, `yamllint.yml`, `betterleaks.toml`). Tools that
  can't find a config there are pointed at it from `.config/hk.pkl`.
- **`.config/hk.pkl`**: the pre-commit and `check` pipeline (linters and formatters, in Pkl). Add or edit a lint step here.
- **`.config/mise/`**: project-local mise state (the setup stamp is gitignored). File tasks can live in `.config/mise/tasks/`.

## Vendored skills

`skills/vendor/` holds other people's skills; `skills-lock.json` says which. Both are machine-owned. Adding names a repo outside this one, so it stays a plain CLI call followed by a sync:

```sh
npx skills add <owner>/<repo> -l              # what does it carry?
npx skills add <owner>/<repo> -s <skill> -y   # one -s per skill; it does not split on commas
mise run skills:sync
```

The rest are tasks, and each re-syncs itself:

| Intent                | Command                           |
| --------------------- | --------------------------------- |
| update one, or all    | `mise run skills:update [skill…]` |
| remove                | `mise run skills:remove <skill>…` |
| rebuild from the lock | `mise run skills:sync`            |

Afterwards bump both manifest versions, since the plugin's content moved.

The sync replaces `skills/vendor/` wholesale, which is why editing the lock or the directory by hand does not survive one. A skill you want to own belongs in `skills/` as yours.

Run the removal through the task, never as a bare `npx skills remove`. Unpinned, the CLI deletes the named skill from every agent layout it knows, and one of those layouts puts project skills in
`skills/` — the directory our own skills live in. The task pins the agent so only `.agents/skills` is in reach; a bare call silently deletes `skills/<name>` when a vendored name matches one of ours.

The lock names a source, not a version: no entry carries a ref, and `computedHash` is recorded but never checked. Every sync therefore fetches the upstream default branch, so treat one as an
upgrade and read `git diff skills/vendor` before committing it.

Linters skip the directory (`**/vendor/**` in `.config/hk.pkl`), which is what lets upstream formatting survive a sync. The CLI installs into agent dirs and takes no flag to aim elsewhere, so the
sync moves its output out of `.agents/` and `.claude/skills/` and deletes both; they stay gitignored because in the tree they load every vendored skill a second time, as project skills.

## Skill READMEs

Every skill has a regular `README.md` for humans who are deciding whether and how to use it. Write from the skill and its references, but explain the problem, outcome, operating shape, and important
tradeoffs instead of copying prompt text or addressing an executing agent. Include a direct link to `SKILL.md`, which remains the canonical agent instructions.

Owned skills keep that prose beside the skill. Curated pages for vendored skills live under `.config/skill-readmes/vendor/` because `skills:sync` replaces `skills/vendor/`; the generator materializes
them after each sync. Keep generated token-estimate blocks intact and update them only with `mise run tokens --fix`.

## CI not visible in the tree

Beyond `.github/workflows/`: CodeQL default setup, Dependabot alerts + security updates, secret
scanning with push protection, and a `main` ruleset requiring the `check` job are configured in
repo settings. Don't scaffold replacements for them.

## Releases

Shipping a change under `skills/` or `hooks/` needs both manifest versions bumped to the same
value (`.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`) — `mise run version:check`
enforces this pre-push and in CI. A release cuts itself: merging a version bump to `main` tags and
publishes automatically; there's no separate release step to run by hand.
