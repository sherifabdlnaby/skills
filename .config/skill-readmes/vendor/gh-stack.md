# gh-stack

`gh-stack` manages a linear chain of dependent Git branches and pull requests with GitHub's `gh stack` extension. Each pull request shows one reviewable layer while later layers build on the work
below it. See [`SKILL.md`](../../../skills/vendor/gh-stack/SKILL.md) for the canonical agent instructions.

## Use

Ask to create, split, inspect, submit, synchronize, rebase, check out, or merge a stacked change. The skill also applies when work is already on a stack. The extension must be installed, and stacked
pull requests must be enabled for the repository before remote stack operations can work.

## Workflow

Plan the dependency order before editing, create the stack from the trunk upward, and keep one coherent concern in each branch. Submit the chain as linked pull requests, inspect state through
machine-readable output, and synchronize after the trunk or a lower layer changes. Changes to a lower branch are rebased through every branch above it. Stack merges use `gh stack merge`, not ordinary
pull-request merge commands.

Stacks are strictly linear; independent work belongs in a separate stack. Reordering and removal have no non-interactive path, so ancestry must be rewritten and the stack rebuilt. Several commands can
open prompts or a full-screen interface when run without explicit arguments, and repositories with several remotes need a selected push remote. Push and submit operations can partially succeed, while
merge is all-or-nothing for its selected range.

## Source

Vendored from GitHub's [`github/gh-stack`](https://github.com/github/gh-stack) repository (MIT).
