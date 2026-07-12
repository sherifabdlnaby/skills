# GitHub Actions notes & gotchas

The GitHub mechanics behind [SKILL.md's `## Always`](../../SKILL.md#always) floor, plus platform gotchas. All demonstrated
in `assets/`; lint the workflows themselves with `actionlint` + `zizmor`.

## Mechanics

- **Pin**: `uses: owner/action@<40-char-sha> # vX.Y.Z`. Tags are mutable, SHAs aren't; `pinact`
  maintains the pins and `zizmor` flags a version comment that doesn't match its SHA.
- **Permissions**: top-level `permissions: contents: read`, widened per job. A check job adds
  `pull-requests: write` (the fix-hint comment). A release job adds `contents: write` (tag + release).
  Sign/attest/push adds `id-token: write` + `attestations: write` + `packages: write`.
- **Credentials**: `persist-credentials: false` on every checkout; only jobs that push with the checkout
  token (the release tag, the auto-fix branch) keep them, marked `# zizmor: ignore[artipacked]` with the
  reason — on its own line inside the step, never on the pin line (see Gotchas).
- **Concurrency**: PR groups keyed `<name>-${{ github.event.pull_request.number || github.ref }}` with
  `cancel-in-progress: true`; publish groups static with `cancel-in-progress: false`. A workflow mixing
  both events can key the group by `github.event_name`
  (see [`release.yml`](../../assets/.github/workflows/release.yml)).
- **Untrusted input**: pass through `env:` and reference the shell var; never `${{ }}` inside `run:`
  (zizmor `template-injection`; its auto-fix is marked unsafe, apply the indirection by hand). Repo-wide
  exceptions go in `.github/zizmor.yml` with a written justification.
- **Tokens**: feed `GITHUB_TOKEN` to tool installers (mise-action, Trivy DB pulls, pinact) and set
  `GH_TOKEN` for the `gh` CLI, so nothing hits anonymous rate limits.

## Annotations

Surface errors as annotations:

- **File/line via the tool's own GitHub format.** Most linters ship one (e.g. `ruff --output-format
  github`, golangci-lint's `github-actions` format); turn it on in CI and errors annotate the exact line
  in the PR diff. Scoping stays in the task; the format flag can be CI-only (env-gated).
- **Problem matcher** when the tool has no native format: register a regex matcher with
  `::add-matcher::path/matcher.json` at step start (and `::remove-matcher::` after) to turn plain output
  into file/line annotations.
- **`::error`/`::warning` workflow commands** for hand-rolled steps — `::error file=x,line=1,title=T::msg`
  anchors to code; bare `::error::msg` annotates the run. The check workflows emit the run-level summary
  this way.
- **SARIF upload** for security findings (Trivy in `build-test-scan.yml`): they annotate code in the
  Security tab and on PRs.

## Gotchas

- **`GITHUB_TOKEN` events don't recurse.** A tag or release created with the workflow token fires no
  other workflow (`on: push: tags`, `on: release` stay silent).
- **Fork PRs get a read-only token** regardless of declared permissions, so label/comment steps 403.
  Detect and skip, or accept the red step; `pull_request_target` lifts it but runs with elevated
  permissions against the base, avoid unless you know exactly why.
- **`pull_request` default types miss `edited`**, so title-regex autolabels go stale on retitle. Add
  `types: [opened, reopened, synchronize, edited]` where labels come from titles (plus
  `labeled, unlabeled` where a job reacts to label changes, like the bump gate/preview).
- **One pending run per concurrency group.** On rapid merges a superseded queued release run is
  dropped, not queued behind: its changes still land in the next release's notes, but its bump label
  isn't consumed — re-run the dropped run from the UI if that bump mattered.
- **The pin comment is machine-owned; nothing shares its line.** Text appended after `# vX.Y.Z` (a
  `zizmor: ignore[...]`, a note) stops Dependabot's comment rewrite on bump: stale comment, and
  `pinact --verify` fails the line. Suppressions go on their own line inside the finding's span
  (between `name:` and `uses:`, or in the `with:` block); above the step they do nothing.
- **GHCR image names must be lowercase.** `${{ github.repository }}` breaks the push when the owner or
  repo has capitals; hardcode a lowercase image name instead.
- **Release builds run with `cache: false`** on tool setup: a one-shot job has no cache to reuse, and a
  poisoned cache would taint the artifact (zizmor `cache-poisoning`).

## Check workflows

Notes for [`check.yml`](../../assets/.github/workflows/check.yml) /
[`check.autofix.yml`](../../assets/.github/workflows/check.autofix.yml) (ship one, not both):

- **Report-only** (`check.yml`) needs `contents: read` + `pull-requests: write` and suits any repo: it
  fails with a `::error::` and keeps one sticky marker comment pointing at `mise run check --fix --pr`,
  deleted when green.
- **Auto-fix** (`check.autofix.yml`) additionally needs `contents: write`: fixes force-push to a
  `bot/ci/<target>` branch as a self-closing PR with a frozen commit identity+date, so an unchanged fix
  is a no-op push that doesn't re-notify. It still fails the run — a fix PR doesn't green the check.
- **No fork support in auto-fix** (by design): fork tokens are read-only, so it detects the fork and
  falls back to the annotation instead of reaching for `pull_request_target`.
- **The fix PR triggers no CI of its own**: `GITHUB_TOKEN`-created PRs don't fire `on: pull_request`
  (same recursion rule as above), which also blocks loops; a `bot/ci/*` guard backs that up for PAT users.
