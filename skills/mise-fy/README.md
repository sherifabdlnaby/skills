# mise-fy

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-2%2C209%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 2,209 tokens" />
  <img src="https://img.shields.io/badge/Total-27%2C567%20tokens-2ea44f?style=flat-square" alt="Total: 27,567 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                                                                                       |  Tokens |
| ------------------------------------------------------------------------------------------ | ------: |
| [`SKILL.md`](SKILL.md)                                                                     | `2,209` |
| [`assets/AGENTS.md`](assets/AGENTS.md)                                                     |   `472` |
| [`assets/README.md`](assets/README.md)                                                     |   `600` |
| [`references/ci/github.md`](references/ci/github.md)                                       | `1,987` |
| [`references/ci.md`](references/ci.md)                                                     | `1,797` |
| [`references/docs.md`](references/docs.md)                                                 | `1,015` |
| [`references/env.md`](references/env.md)                                                   | `1,470` |
| [`references/hk.md`](references/hk.md)                                                     | `5,324` |
| [`references/hooks.md`](references/hooks.md)                                               |   `487` |
| [`references/install.md`](references/install.md)                                           |   `354` |
| [`references/mise-fy.md`](references/mise-fy.md)                                           | `2,012` |
| [`references/reference-setup-and-patterns.md`](references/reference-setup-and-patterns.md) | `2,041` |
| [`references/runtimes/node.md`](references/runtimes/node.md)                               | `1,452` |
| [`references/tasks.md`](references/tasks.md)                                               | `3,060` |
| [`references/tools.md`](references/tools.md)                                               | `3,287` |

<!-- token-estimates:end -->

`mise-fy` helps make a project's development setup reproducible, discoverable, and consistent across local work, git hooks, and CI. It covers mise configuration, pinned tools, tasks, environment
variables, dependency setup, lifecycle hooks, hk pre-commit checks, and CI integration.

[Read the canonical skill instructions.](SKILL.md)

## What it provides

The target experience is a fresh clone that can be trusted and set up with one documented command path, followed by stable task names for everyday work. Tool versions and checks stay in project
configuration instead of depending on each contributor's machine.

The skill supports two modes:

- **Guidance mode** handles focused changes to an existing mise setup, such as adding a runtime, improving a task, configuring environment values, or wiring hk into CI.
- **Transformation mode** inventories existing tool managers, scripts, hooks, and CI; maps them to mise; migrates in agreed stages; verifies a fresh setup; and updates human and project guidance.

A full transformation separates frequently run, offline-safe tasks from slower setup work. Local checks, hooks, and CI share the same task contract. The files under `assets/` show a coherent reference
setup, including `mise.toml`, hk configuration, CI workflows, and documentation sections. They are starting points that must be trimmed and adapted, not a package to apply unchanged.

## Boundaries and tradeoffs

- Routine use such as running `mise install` or an existing task does not need this skill; changes to mise, hk, hooks, or their CI setup do.
- mise manages project tools and client binaries, not privileged services such as container engines, databases, or Kubernetes clusters. Those remain documented prerequisites.
- Project configuration with tasks, hooks, environment logic, or templates requires explicit trust on a fresh clone.
- Reproducibility needs deliberate version policy, a committed lockfile, and lock data for every CI platform. Floating versions are not made safe by a lockfile alone.
- Task-scoped tools reduce setup cost but have weaker lockfile behavior. Shared tools improve consistency but increase every contributor's install.
- The default CI check reports failures with read-oriented permissions. An auto-fix pull-request workflow is optional because it needs repository write access.
- A full-tree lint pass can expose substantial existing debt. It should be reviewed before broad automatic fixes or new blocking gates are enabled.

## Example requests

- "Add and pin Node and pnpm through mise without breaking Corepack users."
- "Create a cached build task with arguments and shell completion."
- "Set up hk pre-commit checks and run the same check task in GitHub Actions."
- "Audit this mise configuration for trust, lockfile, and CI problems."
- "Mise-fy this project and replace its current tool and task setup."
