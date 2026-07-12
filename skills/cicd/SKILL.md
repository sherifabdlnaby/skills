---
name: cicd
description: >
  Use when setting up, shaping, or auditing a project's CI/CD: a build/test/scan pipeline, a
  release pipeline, or publishing an artifact (container image, binary, bundle) with signing/attestation.
license: MIT
argument-hint: "[release | build | publish | sign | audit]"
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# cicd

CI/CD patterns and the why behind them. Flex them to fit the app and the user's requests.
- Uses Github Actions as a reference.
- Patterns live here; the exact recipes live in [`references/`](references/) pages and
  [`assets/`](assets/.github/workflows/) workflows, route via the [Router](#router).
- This skill uses `mise` as the task runner; substitute the project's own (e.g. Make) — the patterns hold.

## Principles

1. **CI reuses local commands.** CI runs the same tasks you run locally (e.g `mise run build` or `make build`), args aside.
    If you must diverge, articulate to the user why.
2. **Name workflows by purpose, not `ci.yml`.** `build.yml`, `release.yml`, `build-test-scan.yml`. why: a
   glance at the Actions tab should say what runs.
3. **Checks run on PR + a `schedule` sweep + `workflow_dispatch`.** (Daily for lint, weekly for heavy builds.)
   why: the cron catches rot on the default branch (a dep, base image, or pinned action going bad)
   between PRs; manual dispatch is the escape hatch.
4. **Releases are label-driven and auto-tagged.** The merged PR's label decides the bump; the pipeline
   tags and publishes from the merge. A CI gate fails unlabeled PRs, and a sticky comment previews the
   version a merge would cut, recomputed on every label change and refreshed after each release; an
   unlabeled PR that merges anyway falls back to `patch`. Ask the user whether that gate/fallback pair
   fits or they want a different unlabeled-PR policy. Mechanics in [Releases](#releases).
5. **Avoid hardcoded versions in files** that need to be modified per PR. Publishing pipeline should modify file (e.g. `package.json`'s version) instead of expecting it in the commit.
6. **Sign and attest what you publish.** Provenance attestation for every artifact; a keyless signature
   on top for what lives in a registry. why: consumers can prove where an artifact came from and pin to
   exact versions. Mechanics in [Publish, sign, attest](#publish-sign-attest).
7. **Releases are immutable.** Every artifact is uploaded and signed before the release goes public.
   Mechanics in [Publish, sign, attest](#publish-sign-attest).
8. **Build & publish are runtime-shaped.** Use the runtime's specialized releaser — GoReleaser (Go),
   buildx/build-push (images), the registry's own publish for packages — over hand-rolled scripts. The
   [Router](#router) page carries each recipe.
9. **Ship x86-64 and ARM64.** Prefer a native runner per arch over emulation (QEMU only where one job
   must emit a single multi-arch manifest). why: emulated builds are slow and can miscompile.

## CI checks

The common workflows: linters, tests, validations.

- **Same command as local.** The lint workflow runs the project's own check task (`mise run check`), the
  test workflow its test task — thin YAML wrappers, nothing re-encoded. Wire the same checks as
  pre-commit hooks too, so CI and hook stay aligned; they differ only in scope (staged files vs branch
  diff vs whole tree).
- **Failing checks help the author.** When fixable: an auto-fix PR (bot branch, self-closing) and/or
  one sticky PR comment saying exactly what to run locally (`mise run check --fix --pr`) — never just
  a red X.
- Reference workflows: [`check.yml`](assets/.github/workflows/check.yml) (report-only, sticky comment) and
  [`check.autofix.yml`](assets/.github/workflows/check.autofix.yml) (auto-fix PR) -> use one or the
  other; github actions gotchas in [`references/github.md`](references/github.md). A test workflow is the same thin
  shape: checkout -> tools -> `mise run test`.

## Releases

The default model ([`release.yml`](assets/.github/workflows/release.yml) — its header carries the full
case table):

- **Label → bump.** On merge to the default branch, the merged PR's label decides the bump (`major` >
  `minor` > `patch`, and `skip-release` aborts); tag and push as `github-actions[bot]`. Release runs
  queue so back-to-back merges tag serially (rapid-merge caveat in
  [`references/github.md`](references/github.md)).
- **Gate + preview on the PR.** The PR job fails when no bump label is set and keeps one sticky comment
  showing the exact version a merge would cut; the release job refreshes open PRs' previews after each
  stable release so they never go stale.
- **Publish with generated notes.** `gh release create <tag> --generate-notes`. release-drafter's
  `autolabeler` ([config](assets/.github/release-drafter.yml)) applies *category* labels
  (enhancement/bug/docs) on PRs, and [`.github/release.yml`](assets/.github/release.yml) (GitHub's
  native notes config) groups the notes OR use conventional commits to infer.
- **Release candidates are manual.** `workflow_dispatch` with a `prerelease` flag (or an explicit
  `vX.Y.Z-rc.N`): emit `-rc.N`, publish `--prerelease` and **not** `--latest`. The next stable release
  passes `--notes-start-tag <last-stable>` so its notes cover the whole line, not just rc→final.

Alternative, when you want curated notes over auto-generated ones: the **release-drafter draft** model —
a continuous draft prerelease with categorized sections and a `version-resolver`, published by a human;
the bump and category label taxonomies must align. See
[`assets/.github/workflows/auto-release.yml`](assets/.github/workflows/auto-release.yml). Trade-off: a
human publishing is what triggers the build, so the release is public before its assets land — the
[publish gate](#publish-sign-attest) holds strictly only in the auto-tag model.

## Publish, sign, attest

The artifact-agnostic principle; mechanics live in [`docker.md`](references/docker.md) (image digest)
and [`go.md`](references/go.md) (binary checksums).

- **Keyless, via OIDC.** Sign with `cosign` using the workflow's GitHub OIDC identity, no private key to
  hold or rotate.
- **Attest provenance always; SBOM where it applies.** `actions/attest-build-provenance` (SLSA) over the
  published subject (an image by `subject-name`+`subject-digest`, or a checksums file) for every
  artifact. `actions/attest-sbom` for artifacts that carry dependencies — images and compiled binaries;
  a packaged bundle's checksums get provenance alone.
- **Gate the publishing.** Flip a draft release public only after every artifact is pushed and signed. why: a
  half-published release must never look final.
- **Document verification.** Put the consumer's `cosign verify` (OIDC issuer + identity regexp) and
  `gh attestation verify` commands in the Release body. why: an unverifiable signature protects no one.

## Always

Hardening that holds for every workflow, on any CI platform. The GitHub mechanics and gotchas behind
each live in [`references/github.md`](references/github.md); demonstrated in
[`assets/`](assets/.github/workflows/).

- **Pin dependencies immutably** (actions by commit SHA, tools/packages by lockfile).
- **Least privilege**: read-only by default, each job widened to only what it uses.
- **Credentials don't outlive the step that needs them.**
- **Concurrency by intent.** PR/check runs cancel superseded. Publish jobs **queue, never cancel**.
  why: cancelling mid-publish leaves a half-pushed tag or image.
- **Authenticate tool installs and API calls** so they dodge anonymous rate limits.

## Router

Read the runtime page before building that pipeline; it carries the exact actions, tags, and commands.

**Go library / binary** -> [`references/go.md`](references/go.md)
Race-detector version matrix, module semver tags (no CD for a library), optional GoReleaser for signed
binaries + SBOM + attestation, `retract` for rollback, module caching.

**Container image** -> [`references/docker.md`](references/docker.md)
Native multi-arch CI matrix (amd64 + arm64 runners; QEMU only for the release push), `metadata-action`
tag strategy, Trivy -> SARIF, buildx `gha` cache, registry push, cosign-on-digest + provenance/SBOM
attest, un-tag/re-point rollback.

**Packaged artifact** (bundle/zip attached to a Release) -> [`references/packaged.md`](references/packaged.md)
Build a versioned bundle with `mise run build --version`, attach it (and its attested checksums) to the
Release on publish; the release-drafter draft variant.

**GitHub Actions notes & gotchas** -> [`references/github.md`](references/github.md)
Pin/permissions/concurrency mechanics; token-event recursion, pending-slot drop, fork tokens, `edited`
type, GHCR case, release-build caching.

**Audit a repo's CI/CD** -> [`references/audit.md`](references/audit.md)
Inventory -> compare -> plan with the user; the full checklist (checks, hardening, release, artifacts).

**Local tool / pre-commit-hook setup** (what `mise run check` is made of) -> the **mise-fy** skill.
The CI side lives here: [CI checks](#ci-checks) and its two check workflows.

**Local git, commits, PRs, reviews** -> the **git** skill.
