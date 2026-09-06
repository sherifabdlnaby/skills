# gh-stack

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-2%2C070%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 2,070 tokens" />
  <img src="https://img.shields.io/badge/Total-6%2C873%20tokens-2ea44f?style=flat-square" alt="Total: 6,873 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                                             | Tokens |
| ---------------------------------------------------------------- | -----: |
| [`SKILL.md`](SKILL.md)                                           |  2,070 |
| [`references/commands.md`](references/commands.md)               |  2,242 |
| [`references/stack-design.md`](references/stack-design.md)       |    946 |
| [`references/troubleshooting.md`](references/troubleshooting.md) |  1,615 |

<!-- token-estimates:end -->

`gh-stack` manages a linear chain of dependent Git branches and pull requests with GitHub's `gh stack` extension. Each pull request shows one reviewable layer while later layers build on the work
below it. See [`SKILL.md`](SKILL.md) for the canonical agent instructions.

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
