# mise-fy

[All skills](../)

`mise-fy` helps make a project's development setup reproducible, discoverable, and consistent across local work, git hooks, and CI. It covers mise configuration, pinned tools, tasks, environment
variables, dependency setup, local services, lifecycle hooks, hk pre-commit checks, and CI integration.

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
- mise manages project tools, and through its experimental daemons the local services a project runs, such as a database or a cache, with a separate stack (ports and data) per git worktree. Privileged
  services such as container engines or Kubernetes clusters remain documented prerequisites.
- Project configuration with tasks, hooks, environment logic, or templates requires explicit trust on a fresh clone.
- Reproducibility needs deliberate version policy, a committed lockfile, and lock data for every CI platform. Floating versions are not made safe by a lockfile alone.
- Task-scoped tools reduce setup cost but have weaker lockfile behavior. Shared tools improve consistency but increase every contributor's install.
- The default CI check reports failures with read-oriented permissions and annotates findings on the PR diff. An
  auto-fix pull-request workflow is optional because it needs repository write access.
- A full-tree lint pass can expose substantial existing debt. It should be reviewed before broad automatic fixes or new blocking gates are enabled.

## Example requests

- "Add and pin Node and pnpm through mise without breaking Corepack users."
- "Create a cached build task with arguments and shell completion."
- "Set up hk pre-commit checks and run the same check task in GitHub Actions."
- "Run Postgres, Redis, and our API locally with one command, and let each git worktree run its own copy."
- "Audit this mise configuration for trust, lockfile, and CI problems."
- "Mise-fy this project and replace its current tool and task setup."
