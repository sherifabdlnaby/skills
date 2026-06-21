# CI: GitHub Actions

Running Mise-managed tools and tasks on GitHub Actions. General, platform-agnostic CI rules live in [`../ci.md`](../ci.md); this file is GitHub-specific.

Use `jdx/mise-action@v4`: it installs mise + tools, runs `mise install`, and caches.
The canonical workflow lives at [.github/workflows/check.yml](../../assets/.github/workflows/check.yml). Copy and adapt it.

## Rules and Best Practices:

1. **Pin actions to a commit SHA**, with the version in a trailing comment (`uses: owner/action@<sha> # v1.2.3`). Tags are mutable; SHAs aren't.
2. **Scope `permissions`** to the minimum. Linting needs `contents: read`; posting the fix-hint comment on the PR needs `pull-requests: write`.
3. **Cancel superseded runs** with a `concurrency` group keyed on the PR number or ref so a new push stops the old run.
4. Set the GitHub token via `GITHUB_TOKEN` env / `github_token` input so tool installs don't hit API rate limits.

## The lint workflow pattern

The reference workflow reports failures and points the author at the fix; it never touches the PR's code:

- **Scope by event.** PRs lint only changed files (`mise run check --pr`); the daily `schedule` and `workflow_dispatch` lint everything (`mise run check --all`). Checkout with `fetch-depth: 0` so `--pr` can diff against the default branch.
- **No fail-fast** is the task default, so one run reports every failing step, not just the first.
- **Report only.** CI never auto-fixes. On failure the check step emits a `::error::` annotation telling the author to run `mise run check --fix` locally, and exits non-zero so the check goes red.
- **One sticky comment.** A single `actions/github-script` step keeps exactly one PR comment (matched by an HTML marker): it posts/updates the comment with the `mise run check --fix --pr` hint when the check fails, and **deletes** it once the check passes. No inline suggestions, no comment spam.
-
## Notes & Gotchas:

- **`mise-action` defaults**: `install` true, `cache` true, `github_token` defaults to `github.token`. So **caching and version pinning are already handled**: you only deal with checksums/attestation manually if you drop the action and install mise yourself (see [`../ci.md`](../ci.md#verifying-the-mise-install); `gh attestation verify … --repo jdx/mise` works out of the box on GitHub runners).
- **Cache key** should hash `mise.toml` + `mise.lock`; stale keys reinstall silently. `mise-action` does this for you; only set `cache_key` to override.
- **`persist-credentials: false`** on checkout unless a later step pushes with the checkout token.
- **`check --pr` needs the base branch as a _local_ ref.** A `pull_request` checkout leaves HEAD detached on the merge commit with the base only as `origin/<base>`, so hk's `--pr` (it diffs against the default branch) dies with `Failed to parse reference: main`. `fetch-depth: 0` alone doesn't fix it. Before the check step, materialize the branch: `git branch --force "$BASE_REF" "origin/$BASE_REF"` with `BASE_REF` from `github.event.pull_request.base.ref` (passed via `env`, not interpolated). The reference workflow has this step.
- **Never interpolate `${{ … }}` straight into a `run:` block.** Values like `github.ref_name`, branch names, or PR titles can carry shell metacharacters; zizmor flags this `template-injection` (High). Pass them via the step's `env:` and reference the shell var instead: `env: { REF_NAME: ${{ github.ref_name }} }`, then `$REF_NAME` in the script. The reference workflow does exactly this. zizmor's auto-fix for it is held back as "unsafe", so apply the env indirection by hand.

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
