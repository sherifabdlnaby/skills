---
name: cicd
description: >
  Use when setting up, shaping, or auditing a project's CI/CD: a build/test/scan pipeline, a
  release pipeline, or publishing an artifact (container image, binary, bundle) with signing/attestation.
  Optionally use the skill to transform a repo's CI/CD to the recommended shape, aka (cicd-fy).
license: MIT
argument-hint: "Cicd-fy this project | Audit CI/CD | Add a release pipeline"
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# cicd

CI/CD patterns and the why behind them. Flex them to fit the app and the user's requests.

- The principles are platform-agnostic; **GitHub Actions is the reference implementation**
- Check `references/`](references/) recipes and [`assets/`](assets/.github/workflows/) workflows are GHA,
  the philosophy holds on any CI system.
- This skill uses `mise` as the task runner; substitute the project's own (e.g. Make) the patterns hold tho.

# How to use the Skill

The skill uses progressive disclosure: each area routes to a `references/` file holding the actual rules and recipes.
Read the matching one **before** planning or building that pipeline, not after.
SKILL.md alone is not enough. Plan ahead, and read all references you'll need!

## When to read references

Always read at-least 1 reference from the router below. Depending on your goal you might want to read more than 1 reference.
Be eager to load local .md references. Do not load online links/references unless you really need to, default to trust your knowledge. Only load online reference when you need to learn more.

## Router

**CI checks** (lint / test / validation workflows) -> [`references/checks.md`](references/checks.md)
CI Tasks best practices.

**Releases** (versioning, tagging, notes, RCs) -> [`references/releases.md`](references/releases.md)
Label-driven bump, auto-tag on merge, the gate + preview comment, generated notes and label taxonomy,
release candidates, the release-drafter draft variant.

**Publish, sign, attest** (shipping any artifact) -> [`references/publish.md`](references/publish.md)
Keyless cosign via OIDC, provenance + SBOM attestation, the publish gate, the Verify + Install release footer.

**Artifact recipes** (build + publish per deliverable) -> [`references/artifacts/`](references/artifacts/):
Best practices based on what you're building.

- Go library / binary -> [`artifacts/go.md`](references/artifacts/go.md)
- Container image -> [`artifacts/docker.md`](references/artifacts/docker.md)
- Packaged artifact (bundle/zip attached to a Release) -> [`artifacts/packaged.md`](references/artifacts/packaged.md)

**Platform notes & gotchas** -> [`references/platforms/`](references/platforms/):

- GitHub Actions -> [`platforms/github.md`](references/platforms/github.md)

**CI repo hygiene** (repo settings & upkeep) -> [`references/hygiene.md`](references/hygiene.md)
Branch protection / rulesets + required checks, merge method, label seeding, action-pin upkeep, CODEOWNERS, protected environments, timeouts, badges, pruning dead
workflows.

**Community control & hygiene** (stale PRs/issues, locking old threads, abandoned branches) -> [`references/community.md`](references/community.md)

**Cicd-fy an existing repo** (set up, reshape, or audit) -> [`references/cicd-fy.md`](references/cicd-fy.md)
Inventory -> plan with the user -> convert -> verify -> document, plus the full audit checklist.
References every other doc.

**Local tool / pre-commit-hook setup**: if available, use mise-fy skill

## Principles & Doctrine

1. **CI reuses local commands.** CI runs the same tasks you run locally (e.g `mise run build` or `make build`), args aside.
   If you must diverge, articulate to the user why. ([`checks.md`](references/checks.md))
2. **Releases are label-driven and auto-tagged.** The merged PR's label decides the bump; the pipeline
   tags and publishes from the merge, gated and previewed on the PR. Mechanics — and the unlabeled-PR
   policy to settle with the user — in [`releases.md`](references/releases.md).
3. **Sign and attest what you publish.** Provenance attestation for every artifact; a keyless signature
   on top for what lives in a registry. why: consumers can prove where an artifact came from and pin to
   exact versions. ([`publish.md`](references/publish.md))
4. **Releases are immutable.** Every artifact is uploaded and signed before the release goes public.
   ([`publish.md` — the publish gate](references/publish.md#the-publish-gate))
5. **Build & publish are runtime-shaped.** Use the runtime's specialized releaser e.g. GoReleaser (Go),
   buildx/build-push (images), the registry's own publish for packages over hand-rolled scripts. The
   [artifact pages](references/artifacts/) carry each recipe.

## Always

Hardening that holds for every workflow, on any CI platform. The GitHub mechanics and gotchas behind
each live in [`platforms/github.md`](references/platforms/github.md); demonstrated in
[`assets/`](assets/.github/workflows/).

- **Pin dependencies immutably** (actions by commit SHA, tools/packages by lockfile).
- **Least privilege**: read-only by default, each job widened to only what it uses.
- **Credentials don't outlive the step that needs them.**
- **Concurrency by intent.** PR/check runs cancel superseded. Publish jobs **queue, never cancel**.
  why: cancelling mid-publish leaves a half-pushed tag or image.
- **Authenticate tool installs and API calls** so they dodge anonymous rate limits.
