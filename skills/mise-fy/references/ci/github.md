# CI: GitHub Actions

Running Mise-managed tools and tasks on GitHub Actions. General, platform-agnostic CI rules live in [`../ci.md`](../ci.md); this file is GitHub-specific.

Use `jdx/mise-action@v4`: it installs mise + tools, runs `mise install`, and caches.
The canonical workflow lives at [.github/workflows/check.yml](../../assets/.github/workflows/check.yml) (report-only, `contents: read`). Copy and adapt it. A heavier opt-in variant that opens PRs with the fixes lives alongside it; see [Optional: auto-fix PRs](#optional-auto-fix-prs).

## Rules and Best Practices:

1. **Pin actions to a commit SHA**, with the version in a trailing comment (`uses: owner/action@<sha> # v1.2.3`). Tags are mutable; SHAs aren't.
2. **Scope `permissions`** to the minimum. Report-only linting needs `contents: read`, plus `pull-requests: write` to post the fix-hint comment. The opt-in [auto-fix variant](#optional-auto-fix-prs) additionally needs `contents: write` to push the fix branch.
3. **Cancel superseded runs** with a `concurrency` group keyed on the PR number or ref so a new push stops the old run.
4. Set the GitHub token via `GITHUB_TOKEN` env / `github_token` input so tool installs don't hit API rate limits.

## The lint workflow pattern

The reference workflow reports failures and points the author at the fix; it never touches the PR's code:

- **Scope by event.** PRs lint only changed files (`mise run check --pr`); the daily `schedule` lints everything (`mise run check --all`). A manual `workflow_dispatch` defaults to `--all` but exposes a `scope` choice input to pick `--pr` instead. Checkout with `fetch-depth: 0` so `--pr` can diff against the default branch.
- **No fail-fast** is the task default, so one run reports every failing step, not just the first.
- **Report only.** CI never auto-fixes. On failure the check step emits a `::error::` annotation telling the author to run `mise run check --fix` locally, and exits non-zero so the check goes red.
- **One sticky comment.** A single `actions/github-script` step keeps exactly one PR comment (matched by an HTML marker): it posts/updates the comment with the `mise run check --fix --pr` hint when the check fails, and **deletes** it once the check passes. No inline suggestions, no comment spam.

## Optional: auto-fix PRs

An **opt-in** variant that, instead of only reporting, opens a PR with the fixes whenever `mise run check --fix` changes something ([check.autofix.yml](../../assets/.github/workflows/check.autofix.yml)). Ship it **instead of** `check.yml`, only where wanted, since it needs `contents: write` + `pull-requests: write`.

**Whether to add it is the user's call** (it grants CI write access):

- **Default to report-only `check.yml`** (`contents: read`, suits any repo).
- **Planning interactively:** offer the variant, let the user pick.
- **Working autonomously:** install the read-only default, don't block, mention the variant afterward.

How it works (all `gh` CLI, no extra action):

- **Same scope** as report-only: PRs fix `--pr`, `schedule`/dispatch fix `--all`; the PR body notes its provenance (`#<n>` vs the `--all` sweep).
- **Stable branch per target.** `TARGET` is `github.head_ref` (PR) or `github.ref_name`; fixes force-push to `bot/ci/<TARGET>` and a PR opens with `base: <TARGET>`, so PR fixes target the PR branch and `main`/schedule target `main`. The stable name updates the existing PR instead of opening a second.
- **Self-closing.** A clean run closes the PR, deleting its branch and the sticky comment. A fixed commit identity and date hold unchanged fixes at the same SHA, so the push is a no-op that won't re-notify subscribers.
- **Still fails CI.** A fix PR doesn't green the run; the job exits non-zero whenever anything was fixed or a step failed.

Caveats (why it's opt-in):

- Needs `contents: write` + `pull-requests: write`, exactly what some repos won't grant, hence the `contents: read` default.
- **No fork support** (by design): a fork PR carries a read-only token and can't push, so it detects the fork and falls back to the `::error::` annotation, staying off `pull_request_target`.
- **The fix PR runs no CI of its own** under `GITHUB_TOKEN` (token-made PRs don't trigger `on: pull_request`). That's fine since it's clean `--fix` output, and it also blocks recursion; a `bot/ci/*` guard backs that up for PAT users.

## Notes & Gotchas:

- **`mise-action` defaults**: `install` true, `cache` true, `github_token` defaults to `github.token`. So **caching and version pinning are already handled**: you only deal with checksums/attestation manually if you drop the action and install mise yourself (see [`../ci.md`](../ci.md#verifying-the-mise-install); `gh attestation verify … --repo jdx/mise` works out of the box on GitHub runners).
- **Cache key** should hash `mise.toml` + `mise.lock`; stale keys reinstall silently. `mise-action` does this for you; only set `cache_key` to override.
- **`persist-credentials: false`** on checkout unless a later step pushes with the checkout token.
- **`check --pr` silently passes in CI unless you set `origin/HEAD`.** hk's `--pr` is shorthand for `--from-ref DEFAULT_BRANCH --to-ref HEAD`, and it resolves `DEFAULT_BRANCH` from the remote's `origin/HEAD` symbolic ref. The Actions checkout never sets `origin/HEAD` (you'll see `fatal: ref refs/remotes/origin/HEAD is not a symbolic ref` in the log), so hk falls back to diffing the branch against its own upstream: **0 files, every check passes green** even with real lint errors. `fetch-depth: 0` doesn't help; neither does materializing a local branch (hk reads `origin/HEAD`, not a local ref). Fix: when scope is `--pr`, point the symbolic ref at the base right before running check: `git remote set-head origin "$BASE_REF" >/dev/null 2>&1 || true` with `BASE_REF` from `github.event.pull_request.base.ref || github.event.repository.default_branch` (passed via `env`, not interpolated). The reference workflow does this inline at the top of the `Run check` step — the `|| true` covers a manual `--pr` dispatch on the default branch, where the diff is an empty no-op.
- **Never interpolate `${{ … }}` straight into a `run:` block.** Values like `github.ref_name`, branch names, or PR titles can carry shell metacharacters; zizmor flags this `template-injection` (High). Pass them via the step's `env:` and reference the shell var instead: `env: { REF_NAME: ${{ github.ref_name }} }`, then `$REF_NAME` in the script. The reference workflow does exactly this. zizmor's auto-fix for it is held back as "unsafe", so apply the env indirection by hand.
- **Pin `shellcheck` next to `actionlint`.** actionlint shells out to shellcheck to lint `run:` blocks; unpinned, the mise shim errors (`No version is set`) and the scripts go unchecked. Add both to `[tools]`.

## Minimal job

Just gate the PR; see the asset for the full report + sticky-comment flow:

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

## Docs:

- [jdx/mise-action](https://github.com/jdx/mise-action)
- [continuous-integration](https://mise.jdx.dev/continuous-integration.html)
