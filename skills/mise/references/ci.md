# CI

Guidance on running Mise-managed tools and tasks in CI.

The canonical GitHub workflow lives at [.github/workflows/check.yml][../assets/.github/workflows/check.yml] — copy and adapt it.

## Rules and Best Practices:

1. Use **shims**, not `mise activate`, in CI (non-interactive).
2. On GitHub, use `jdx/mise-action@v4`, it installs mise + tools, runs `mise install`, and caches.
3. **Run the same tasks as locally** (`mise run check`, `mise run test`), don't re-encode commands in YAML (see [`tasks.md`](tasks.md)). When local, the pre-commit hook, and CI all call one task, behaviour can't drift.
4. Pin tool versions and commit `mise.lock`; install with `install_args: "--locked"` so CI can't silently drift off the lockfile (see [`tools.md`](tools.md)).
5. Set a GitHub token (`GITHUB_TOKEN` env / `github_token` input) so tool installs don't hit API rate limits.
6. **Pin actions to a commit SHA**, with the version in a trailing comment (`uses: owner/action@<sha> # v1.2.3`). Tags are mutable; SHAs aren't.
7. **Scope `permissions`** to the minimum. Linting needs `contents: read`; posting fixes back to the PR needs `pull-requests: write`.
8. **Cancel superseded runs** with a `concurrency` group keyed on the PR number / ref so a new push stops the old run.

## The lint workflow pattern

The reference workflow does more than fail — it makes a failure fixable in one click:

- **Scope by event.** PRs lint only changed files; the daily `schedule` and `workflow_dispatch` lint everything (`mise run check --all`). Checkout with `fetch-depth: 0` so `--pr` can diff against the default branch.
- **No fail-fast** is the task default, so one run reports every failing step, not just the first.
- **One pass, two signals.** On a PR it runs `mise run check --fix --pr` _once_ and gates on both results: a **non-zero exit** means a violation nothing could auto-fix; a **dirty worktree** means fixes were applied. Failing on either catches every violation while only the fixable ones produce a diff — no second linting run needed.
- **Suggest the diff.** The applied (then unstaged) fixes are posted as review **suggestions** (`parkerbxyz/suggest-changes@v3`) the author can apply inline.
- **Self-cleaning.** `actions/github-script` resolves/dismisses the bot's stale lint reviews once checks pass, and folds superseded suggestion threads.

> Why gate on _both_ exit code and diff? `hk fix` (like most formatters) exits `0` after it successfully rewrites a file, so the exit code alone would go green on an auto-fixable PR. The `git diff` is what catches that case; the exit code is what catches non-fixable errors (e.g. an `actionlint` finding). Neither signal alone is sufficient — together they are.

## Notes & Gotchas:

- **`mise-action` defaults**: `install` true, `cache` true, `github_token` defaults to `github.token`.
- **Cache key** should hash `mise.toml` + `mise.lock`; stale keys reinstall silently.
- **Color is off in CI.** Set `CLICOLOR_FORCE: "1"` / `FORCE_COLOR: "1"` to keep linter output readable in the Actions log.
- **`persist-credentials: false`** on checkout unless a later step pushes with the checkout token.
- **No mise in the image?** `mise generate bootstrap` emits a self-contained install script.
- **`check --pr` needs the base branch as a _local_ ref.** A `pull_request` checkout leaves HEAD detached on the merge commit with the base only as `origin/<base>`, so hk's `--pr` (it diffs against the default branch) dies with `Failed to parse reference: main`. `fetch-depth: 0` alone doesn't fix it. Before the check step, materialize the branch: `git branch --force "$BASE_REF" "origin/$BASE_REF"` with `BASE_REF` from `github.event.pull_request.base.ref` (passed via `env`, not interpolated). The reference workflow has this step.
- **`mise.lock` is per-platform, and `mise lock` only locks the platform you run it on.** With `install_args: "--locked"`, CI on `linux-x64` then fails at the mise setup step with `No lockfile URL found for <tool>@<ver> on platform linux-x64`, even though it works on your Mac. Pre-populate every platform CI uses: `mise lock --platform linux-x64,macos-arm64` (add `windows-x64` if relevant), then commit the lockfile. Re-run it whenever you add or bump a tool.
- **Never interpolate `${{ … }}` straight into a `run:` block.** Values like `github.ref_name`, branch names, or PR titles can carry shell metacharacters; zizmor flags this `template-injection` (High). Pass them via the step's `env:` and reference the shell var instead — `env: { REF_NAME: ${{ github.ref_name }} }`, then `$REF_NAME` in the script. The reference workflow does exactly this. zizmor's auto-fix for it is held back as "unsafe", so apply the env indirection by hand.

If still can't fix your problems, check the docs references below.

## GitHub Actions

Minimal job (just gate the PR); see the asset for the full auto-fix/suggest flow:

```yaml
jobs:
  check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<sha> # v6   (fetch-depth: 0 if you use `check --pr`)
        with: { fetch-depth: 0 }
      - uses: jdx/mise-action@<sha> # v4   installs mise + tools, runs `mise install`, caches
        with: { install_args: "--locked" }
      - run: mise run check --pr # same task as local + pre-commit
```

Key `mise-action` inputs: `version`, `install`, `install_args`, `cache`, `cache_key`, `experimental`, `tool_versions`/`mise_toml` (inline config), `working_directory`, `github_token`.

## GitLab / other CI

```yaml
cache:
  - key: { prefix: mise-, files: [mise.toml, mise.lock] }
    paths: [$MISE_DATA_DIR]
script:
  - mise install --locked
  - mise run check --all
```

## Docs:

- [continuous-integration](https://mise.jdx.dev/continuous-integration.html)
- [jdx/mise-action](https://github.com/jdx/mise-action)
