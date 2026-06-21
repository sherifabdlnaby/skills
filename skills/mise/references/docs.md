# Project Docs (README & AGENTS.md)

mise-fy-ing or auditing a project isn't finished until the docs teach a **human** and an **agent** how to install mise, set the project up, drive it, and (for agents) extend it. Two audiences, two files:

- **README.md**: onboard a human. Refer to [assets/README.md](../assets/README.md) for inspiration.
- **AGENTS.md / CLAUDE.md** -> onboard an agent. Refer to [assets/AGENTS.md](../assets/AGENTS.md) for inspiration.

## Rules and Best Practices:

- **Teach discovery, don't enumerate everything.** Show one or two examples (`mise run check`, `mise run test`) and point at the discovery path: `mise tasks` lists all, `mise run <task> --help` shows a task's flags.
- **Point at the source of truth.** Tools/tasks/env live in `mise.toml`. Docs teach how to *read and run* it, they don't duplicate it.
- **Concise and dense.** One short section should make a contributor productive. No tour.
- **Examples should be the examples expected to be run the most**.
- **Only mention hk if the repo uses it.**
- **Declare external prerequisites mise can't install.** If the project needs a daemon/service outside mise's scope (a running Docker engine, a database server, a k8s cluster — see [`tools.md`](tools.md)), say so up front: what to install and how to confirm it's running. mise sets up the toolchain; these are the things `mise run setup` can't.

## Notes & Gotchas:

1. If the Repo have a different structure to expose these information, and it's clean, then use it.

## README.md (humans)

Cover, in order (mirror [assets/README.md](../assets/README.md)):

1. **Declare mise as dependency**, in a collapsible section show install steps (brew preferred), and then link to install steps. Guide user to also activate and confirm with doctor.
2. **Prerequisites mise can't install** (only if any); external daemons/services like a Docker engine or DB server — what to install and how to confirm it's up. Skip the section entirely when there are none.
3. **Set up the project**; `mise trust` then `mise run setup`, and whatever get the user running.
4. **Everyday commands**; a tiny list with `check`/`lint` and `test`, and `mise tasks` to find the rest.
5. **Git hooks** (hk if exists): Give a quick intro that the repo has it, where to find it, how to run locally (e.g mise run check) for example.

## AGENTS.md / CLAUDE.md (agents)

Everything the README covers, plus how to *work in* and *extend* the setup. Keep it to one dense block (reference [assets/AGENTS.md](../assets/AGENTS.md)):

- **Setup**: `mise trust && mise run setup`. Tools/tasks/env all come from `mise.toml`. Never install a tool by hand or add an ad-hoc script; add a mise tool/task instead.
- **Run via mise**: `mise run check` before declaring done, `mise run test`; discover with `mise tasks`, inspect flags with `mise run <task> --help`.
- **Hooks** (hk only): commits run `hk`, the same `check` CI runs. Fix with `mise run check --fix`; don't disable steps to get a commit through.
- **Extending the setup**: Refer the agent where to find tasks, add them, and how to extend hooks.

## Audit checklist

- [ ] README: install mise, activate + `mise doctor`, `mise trust` + `mise run setup`, everyday commands.
- [ ] External prerequisites (Docker engine, DB server, etc.) declared in README/AGENTS when the project depends on them — not stuffed into `[tools]`.
- [ ] AGENTS.md / CLAUDE.md: setup, run-via-mise + discovery, hk (if used), how to extend (mise skill).
- [ ] Examples not enumerations; `mise tasks` taught as the discovery path.
- [ ] hk mentioned only when the repo actually uses it.
