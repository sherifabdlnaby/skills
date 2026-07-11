---
name: cicd
description: >
  Use when setting up or shaping a project's CI/CD on GitHub Actions: a build/test/scan pipeline, a
  release pipeline (label-driven version bump, tag on merge, generated release notes), or publishing an
  artifact (container image, binary, bundle) with signing/attestation (cosign, SLSA provenance, SBOM).
  Trigger on the intent even when "CI/CD" is unsaid, e.g. "release on merge", "publish a signed image".
  NOT for linter/formatter/pre-commit or mise tool setup (that's mise-fy), nor local git/PR flow (git).
license: MIT
argument-hint: "[release|build|publish|sign|changelog]"
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# cicd

CI/CD patterns ( and implementation ref via GitHub Actions) and why behind them. The `references/` runtime pages and `assets/` workflows carry references.
Local dev and linting are **mise-fy**'s; this skill starts where CI moves past linting: build, release, publish.

## Principles

The runtime-agnostic spine, whatever the language or artifact.

1. **CI reuses local, it doesn't reinvent it.** One task runs the checks (`mise run check`), one builds
   (`mise run build`), one sets up (`mise run setup`); CI calls those same tasks. why: a command
   re-encoded in YAML drifts from what you run locally, and the drift only shows up in a red pipeline.
2. **Name workflows by purpose, not `ci.yml`.** `build.yml`, `release.yml`, `build-test-scan.yml`. why: a
   glance at the Actions tab should say what runs, and each file stays single-purpose.
3. **Trigger on PR + a `schedule` sweep (daily for lint, weekly for heavy builds) + `workflow_dispatch`.**
   why: the cron catches rot on the default branch (a dep, base image, or pinned action going bad)
   between PRs; manual dispatch is the escape hatch.
4. **Releases are label-driven and auto-tagged.** The merged PR's label decides the bump; the pipeline
   tags and publishes from the merge. why: the version decision lives on the PR where the change is
   understood, not in a commit-message convention nobody enforces. Mechanics in [Releases](#releases).
5. **The GitHub Release body is the changelog.** No `CHANGELOG.md`. why: a hand-kept changelog rots and
   conflicts; generated notes are always in sync with what merged.
6. **Sign and attest what you publish.** Provenance attestation for every artifact; a keyless signature
   on top for what lives in a registry. why: consumers can prove it came from your pipeline, not a
   supply-chain detour. Mechanics in [Publish, sign, attest](#publish-sign-attest).

## Releases

The default model: one hand-rolled `release.yml`.

- **Label → bump.** On merge to the default branch, the merged PR's label decides the bump (`major` >
  `minor` > `patch`, default `patch`; `skip-release` aborts); tag and push as `github-actions[bot]`. The
  full case table (precedence, RC numbering, notes baseline) lives in the `release.yml` asset header.
- **Publish with generated notes.** `gh release create <tag> --generate-notes`. release-drafter's
  `autolabeler` applies *category* labels (enhancement/bug/docs) on PRs, and `.github/release.yml`
  (GitHub's native notes config, shipped as an asset) groups the notes by them — without it the labels
  decorate nothing. Bump labels drive the version; category labels only group the notes.
- **Release candidates are manual.** `workflow_dispatch` with a `prerelease` flag (or an explicit
  `vX.Y.Z-rc.N`): emit `-rc.N`, publish `--prerelease` and **not** `--latest`. The next stable release
  passes `--notes-start-tag <last-stable>` so its notes cover the whole line, not just rc→final.

Alternative, when you want curated notes over auto-generated ones: the **release-drafter draft** model —
a continuous draft prerelease with categorized sections and a `version-resolver`, published by a human;
the bump and category label taxonomies must align. See
[`assets/.github/workflows/auto-release.yml`](assets/.github/workflows/auto-release.yml).

## Publish, sign, attest

The artifact-agnostic principle; mechanics (image digest vs binary checksums) live in the runtime pages.

- **Keyless, via OIDC.** Sign with `cosign` using the workflow's GitHub OIDC identity, no private key to
  hold or rotate. The signer is the workflow itself, verifiable against
  `https://token.actions.githubusercontent.com`.
- **Attest provenance + an SBOM.** `actions/attest-build-provenance` (SLSA) and `actions/attest-sbom` over
  the published subject (an image by `subject-name`+`subject-digest`, or a checksums file). Every
  artifact gets both — image, binary, and the packaged bundle's checksums alike.
- **Gate the publish.** Flip a draft release public only after every artifact is pushed and signed. why: a
  half-published release must never look final.
- **Document verification.** Put the consumer's `cosign verify` (OIDC issuer + identity regexp) and
  `gh attestation verify` commands in the Release body. why: an unverifiable signature protects no one.

## Always

Hardening that holds for every workflow. Ideas, not recipes; the *how* lives in **mise-fy**
[`references/ci/github.md`](../mise-fy/references/ci/github.md) and is demonstrated in this skill's
`assets/`.

- **Pin actions to a commit SHA** with a `# vX.Y.Z` comment (pinact enforces it).
- **Least-privilege `permissions`,** declared read-only at the top, widened per job. Release/publish jobs
  need more than a check job: `contents: write` to tag+release; `id-token: write` + `attestations: write`
  + `packages: write` to sign, attest, and push. Grant each only in the job that uses it.
- **`persist-credentials: false`** on checkout, except the one job that pushes the tag (mark it
  `# zizmor: ignore[artipacked]` with the reason).
- **Concurrency by intent.** PR/check runs cancel superseded (`cancel-in-progress: true`). Publish jobs
  **queue, never cancel** (`cancel-in-progress: false` or no group). why: cancelling mid-publish leaves a
  half-pushed tag or image.
- **Never interpolate `${{ }}` into a `run:` block.** Pass values via `env:` and reference the shell var
  (zizmor `template-injection`).
- **Feed `GITHUB_TOKEN`** to tool installs and API calls so they dodge anonymous rate limits.

## Out of scope

**Dependency-bump bots** (supply-chain rests on SHA pins + mise's release-age cooldown + a committed
lockfile — mise-fy's turf, not Dependabot/Renovate), **monorepo path filters, cloud-OIDC deploys, and
GitHub Environments/approvals**.

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

**Linting / formatting / pre-commit / mise tool setup** -> the **mise-fy** skill (its `check.yml` /
`check.autofix.yml` assets and `references/ci/github.md`). This skill ships no check workflow.

**Local git, commits, PRs, reviews** -> the **git** skill.
