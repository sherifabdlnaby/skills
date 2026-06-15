# mise-fy an Existing Project

Guidance on converting an existing project to be Mise-managed, or auditing one that already is.

## Rules and Best Practices:

0. **Know the target.** The end-state layout (file tree + every supporting file) is [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md); the canonical config is [`assets/mise.toml`](../assets/mise.toml). Convert _toward_ that picture.
1. **Inventory before editing.** Discover what already manages tools/env/tasks/hooks/CI, don't assume (list below).
2. **Plan, then convert.** Map each piece to its mise equivalent and note conflicts before touching files.

## Notes & Gotchas:

- **`~/.tool-versions` is not global** in mise (unlike asdf); global config is `~/.config/mise/config.toml`.
- **Trust trips fresh clones**, `mise trust` (or `trusted_config_paths`) is needed before `[env]`/tasks load.
- **Remove old managers only after** the mise path is verified, parallel mechanisms drift.

## Procedure

**1. Discover** existing projects

### Tools
Explore how the repo local setup is managed. Read its README.md or AGENTS/CLAUDE.md look for installation instructions, and or (`.tool-versions` (asdf), `.nvmrc`/`.node-version`, `.python-version`, `.ruby-version`, `Brewfile`).

### Tasks
Explore how the repo manage repetitive tasks. Look for Makefile, package.json (or similar) scripts.

### CI & Hooks
Explore if repo has pre-commit hooks, validation tasks either local or in the CI.

**2. Plan**. Map each to its mise target:

For each, we need to identify the path to convert to mise (+hk). You need to ask the user how open are we to big-bang changes, vs seamless iterative changes.
Iterative changes mean we can have interim phase where mise live side by side with other system (e.g asdf, .tool-versions, .ruby-version, whatever).
You need to converse with the user, and grill them until you reach common understanding of the pros, cons, and what and how you're going to convert each area.

**3. Convert**. Per area, follow the matching reference, converse with user when required.

**4. Verify**. Run `mise install` then `mise doctor` (clean?); `mise run <task>` for each; fresh-clone smoke test.

**5. Update README.md**. Add guide to how to install mise itself, run setup, run linters/checks/tests. Refer to [README.md](../assets/README.md)

**6. Update AGENTS.md or CLAUDE.md with guidance on how to use mise, existence of hk and pre-commit hooks if added, and references to guide Agent extend the setup.

**7. Retrospective lint** (existing repos only). Hooks only gate _future_ commits — the existing tree was never linted, so the first contributor to touch an old file gets ambushed by unrelated failures. Do a one-time whole-tree pass now with `--all`. **This can be large and noisy** (especially `typos`/`betterleaks` false positives, and big auto-format diffs), so don't just run `--fix` blindly — surface it to the user and let them choose:

- **Let the user know** the scope first: `mise run check --all` (report-only) shows how much is outstanding before anything changes.
- **Offer a subagent** to do it properly: triage the report, apply safe auto-fixes (`mise run check --all --fix`) as a separate "retrospective lint" commit kept off the feature work, populate ignore scaffolds (`typos.toml`, `.betterleaks.toml`) for confirmed false positives, and flag anything needing a human call.
- **Or hand the user a prompt** to run themselves / paste to a fresh agent, e.g.:
  > "Run `mise run check --all` on this repo. Triage the failures: apply mechanical auto-fixes via `mise run check --all --fix` in a standalone commit, add confirmed false positives to `typos.toml` / `.betterleaks.toml` rather than disabling steps, and list anything that needs my decision. Don't mix these fixes into unrelated changes."

Keep this off `pre-push`/CI gates until the tree is clean, otherwise the first CI run fails on legacy debt.

## Checklist

- [ ] Inventoried existing tool/env/task/hook/CI mechanisms
- [ ] `mise.toml` `[tools]` covers all runtimes; old version files removed
- [ ] Lockfile decision made (`mise.lock` committed if enabled)
- [ ] `[env]` replaces `.envrc`/manual exports; secrets policy applied.
- [ ] Secret redaction applied
- [ ] Tasks migrated; lint/test/build runnable via `mise run`
- [ ] Pre-commit hooks configured, and have a CI counterpart.
- [ ] Retrospective lint run (`mise run check --all`) and existing debt triaged/cleared before gating CI
- [ ] CI uses `jdx/mise-action` and runs the same tasks
- [ ] `mise.local.toml` git-ignored; `mise trust` works for a fresh clone
- [ ] `mise doctor` clean; fresh-clone smoke test passes
- [ ] README / docs onboarding mentions `mise install`, and how to get the project set up.
- [ ] AGENTS.md updated.
- [ ] Old managers (asdf/direnv/pre-commit/etc.) removed once verified

## Docs:

- [configuration](https://mise.jdx.dev/configuration.html)
- [faq](https://mise.jdx.dev/faq.html)
