# <Task>

Covers: <the page's sections, comma-separated; doubles as this page's contents line in the router>.

<!-- Safety first: rules that prevent damage lead the page, before workflow. -->

## <Rule area>

- **<Rule.>** <mechanics>. (why: <only when it stops a wrong move>)
- **<Rule that leans on another page.>** <short restatement here, standalone>; full mechanics in
  `<other-page>.md#<anchor>`, read that too.

## <Workflow, when the task is a sequence>

1. <step>
2. <step; a step that branches to a nested variant page links it: Node -> `runtimes/node.md`>

**<What the command does>**

```sh
gh pr create [--fill] [--base <branch>] [--draft]   # synopsis
gh pr create --fill --base main                     # usual call
```

## Inventory

<!-- Keep when the task consumes a lot of state: one wide read into a file, then local queries. -->

```sh
state=$(mktemp) && gh pr view --json number,title,state,reviews,statusCheckRollup,files > "$state"
jq '.reviews[] | {author: .author.login, state}' "$state"
jq '.statusCheckRollup[] | select(.conclusion != "SUCCESS") | .name' "$state"
```

## Gotchas

- **<Symptom>.** <mechanism>. Discriminator: <how to tell it from its lookalike>. Fix: <fix>.

## On failure

<!-- The slow path: symptom, quick fix, then the page for the rest. The workflow above never mentions prerequisites. -->

- **`gh: command not found`** -> install it, then rerun; `setup.md#install`.
- **`gh auth login` required** -> `gh auth login`; details in `setup.md#auth`.
- **<Symptom the workflow did not predict>** -> `troubleshooting.md#<anchor>`.
