# mise-fy an Existing Project

Guidance on converting an existing project to be Mise-managed, or auditing one that already is.

## Rules and Best Practices:

1. **Know the target.** The ideal end-state layout (file tree + every supporting file) is in [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md); the canonical config is [`assets/mise.toml`](../assets/mise.toml). Convert _toward_ that picture.
2. **Inventory before editing.** Discover what already manages tools/env/tasks/hooks/CI, don't assume (list below).
3. **Plan, then convert.** Map each piece to its mise equivalent and note conflicts before touching files.
4. **Lay down the structure**: Some project might have no need for specific sections but we include them so the path of least resistance is extending the patterns we embedded.

## Notes & Gotchas:

- **`~/.tool-versions` is not global** in mise (unlike asdf); global config is `~/.config/mise/config.toml`.
- **Trust trips fresh clones**, `mise trust` (or `trusted_config_paths`) is needed before `[env]`/tasks load.
- **Remove old managers only after** the mise path is verified, parallel mechanisms drift.

## Procedure

### 1. Discover** existing projects

#### Development
Explore Development and or Contribution section in README.md, AGENTS.md, or CLAUDE.md and trace references to understand how running the project locally, in the CI, in testing, or in Production.

#### Tools & Runtimes
1. Explore how the repo local dependencies are installed. Read its README.md or AGENTS/CLAUDE.md look for installation instructions, and or (`.tool-versions` (asdf), `.nvmrc`/`.node-version`, `.python-version`, `.ruby-version`, `Brewfile`).
2. Explore existing tools versions (node version, npm version, mise version)
3. Explore if Repository relies on Docker (or Podman), check if it's installed.
4. Flag lazy / uncommon tools. For each tool, ask "does *everyone* need this on `mise install`, or only some workflows?" Decision order:
   1. single task needs it → **task-scoped tool** (`[tasks.x] tools.foo`).
   2. several tasks/`./bin/` scripts need it but not everyone, or it's an off-registry binary → **tool stub**; shared toolchain → plain `[tools]`.
   3. Ref:  Decision + lockfile gotchas: [`tools.md`](tools.md#lazy-install-for-uncommon-tools).

#### Tasks
Explore how the repo manage repetitive tasks. Look for Makefile, package.json (or similar) scripts. Check tasks run by the CI or references in README.md or AGENTS.md.
**Flag watch candidates** while you're here: any existing watch/rerun loop (`nodemon`, `webpack --watch`, `cargo watch`, etc) maps to `mise watch <task>` + accurate `sources` drop the bespoke watcher and pin `watchexec` in `[tools]`. (See [`tasks.md`](tasks.md#watch).)

#### CI & Hooks

Explore the CI, and Local Validations / Tests / Setup / Linters and identify what's already being done, and what can we add. Read [`ci.md`](ci.md) (and Github's if using github actions).

### 2. Plan**. Map each to its mise target:

For each, we need to identify the path to convert to mise. You need to ask the user how open are we to big-bang changes, vs gradual iterative changes.
Iterative changes mean we can have interim phase where mise live side by side with other system (e.g asdf, .tool-versions, .ruby-version, whatever) with a plan to migrate.
You need to converse with the user, and grill them until you reach common understanding of the pros, cons, and what and how you're going to convert each area.

Depending on user request, you might suggest new additions (like introduction of hk for pre-commit, as well as other linters)

**3. Convert**. Per area, follow the matching reference, converse with user when required.

**4. Verify**. Run `mise install` then `mise doctor` (clean?); `mise run <task>` for each; fresh-clone smoke test.

**5. Document it** (README + AGENTS.md). The migration isn't done until the docs onboard a **human** and an **agent**: how to install mise, set up, run tasks, and (for agents) extend the setup, including hk if added. Follow [`docs.md`](docs.md); copy from [assets/README.md](../assets/README.md) and [assets/AGENTS.md](../assets/AGENTS.md).

**6. Retrospective lint** (existing repos only). Hooks only gate _future_ commits; the existing tree was never linted, so the first contributor to touch an old file gets ambushed by unrelated failures. Do a one-time whole-tree pass now with `--all`. **This can be large and noisy** (especially `typos`/`betterleaks` false positives, and big auto-format diffs), so don't just run `--fix` blindly. Surface it to the user and let them choose:

- **Let the user know** the scope first: `mise run check --all` (report-only) shows how much is outstanding before anything changes.
- **Offer a subagent** to do it properly: triage the report, apply safe auto-fixes (`mise run check --all --fix`) as a separate "retrospective lint" commit kept off the feature work, populate ignore scaffolds (`typos.toml`, `.betterleaks.toml`) for confirmed false positives, and flag anything needing a human call.
- **Or hand the user a prompt** to run themselves / paste to a fresh agent, e.g.:
  > "Run `mise run check --all` on this repo. Triage the failures: apply mechanical auto-fixes via `mise run check --all --fix` in a standalone commit, add confirmed false positives to `typos.toml` / `.betterleaks.toml` rather than disabling steps, and list anything that needs my decision. Don't mix these fixes into unrelated changes."

Keep this off `pre-push`/CI gates until the tree is clean, otherwise the first CI run fails on legacy debt.

## Example Checklist

- [ ] Inventoried existing tool/env/task/hook/CI mechanisms
- [ ] `mise.toml` `[tools]` covers all runtimes; old version files removed
- [ ] Lazy/uncommon tools placed by the decision order (single-task → task-scoped; multi-task-but-not-everyone/off-registry → `./bin/` stub; shared → `[tools]`); lockfile implication noted (task-scoped tools aren't in `mise.lock`; stubs self-lock via `--lock`)
- [ ] Lockfile decision made (`mise.lock` committed if enabled)
- [ ] `[env]` replaces `.envrc`/manual exports; secrets policy applied; shell `${VAR:-default}` fallbacks converted to `{ default = ... }`.
- [ ] Secret redaction applied
- [ ] Tasks migrated; lint/test/build runnable via `mise run`
- [ ] Bespoke file-watchers (nodemon/`--watch`/cargo-watch) replaced by `mise watch` + `sources`; `watchexec` pinned if used
- [ ] Pre-commit hooks configured, and have a CI counterpart.
- [ ] Retrospective lint run (`mise run check --all`) and existing debt triaged/cleared before gating CI
- [ ] CI uses `jdx/mise-action` and runs the same tasks
- [ ] CI auto-fix variant decided: report-only by default; opt-in write-access variant raised interactively or suggested without blocking when autonomous ([`ci/github.md`](ci/github.md#optional-auto-fix-prs))
- [ ] `mise.local.toml` git-ignored; `mise trust` works for a fresh clone
- [ ] `mise doctor` clean; fresh-clone smoke test passes
- [ ] README + AGENTS.md/CLAUDE.md onboard a human and an agent per [`docs.md`](docs.md) (install, setup, run-via-mise + discovery, hk if used, how to extend).
- [ ] Old managers (asdf/direnv/pre-commit/etc.) removed once verified

## Docs:

- [configuration](https://mise.jdx.dev/configuration.html)
- [faq](https://mise.jdx.dev/faq.html)
