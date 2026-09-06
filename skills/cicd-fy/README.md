# cicd-fy

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C408%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,408 tokens" />
  <img src="https://img.shields.io/badge/Total-30%2C288%20tokens-2ea44f?style=flat-square" alt="Total: 30,288 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                                                                               | Tokens |
| -------------------------------------------------------------------------------------------------- | -----: |
| [`SKILL.md`](SKILL.md)                                                                             |  1,408 |
| [`assets/.github/dependency-review-config.yml`](assets/.github/dependency-review-config.yml)       |    318 |
| [`assets/.github/release-drafter.yml`](assets/.github/release-drafter.yml)                         |    935 |
| [`assets/.github/release.yml`](assets/.github/release.yml)                                         |    269 |
| [`assets/.github/workflows/auto-release.yml`](assets/.github/workflows/auto-release.yml)           |    457 |
| [`assets/.github/workflows/build-test-scan.yml`](assets/.github/workflows/build-test-scan.yml)     |  1,202 |
| [`assets/.github/workflows/build.yml`](assets/.github/workflows/build.yml)                         |    591 |
| [`assets/.github/workflows/check.autofix.yml`](assets/.github/workflows/check.autofix.yml)         |  2,016 |
| [`assets/.github/workflows/check.yml`](assets/.github/workflows/check.yml)                         |  1,238 |
| [`assets/.github/workflows/dependency-review.yml`](assets/.github/workflows/dependency-review.yml) |    358 |
| [`assets/.github/workflows/publish-sign.yml`](assets/.github/workflows/publish-sign.yml)           |  1,380 |
| [`assets/.github/workflows/release.yml`](assets/.github/workflows/release.yml)                     |  5,369 |
| [`assets/.goreleaser.yml`](assets/.goreleaser.yml)                                                 |    546 |
| [`assets/CONTRIBUTING.md`](assets/CONTRIBUTING.md)                                                 |    454 |
| [`references/artifacts/docker.md`](references/artifacts/docker.md)                                 |  1,118 |
| [`references/artifacts/go.md`](references/artifacts/go.md)                                         |    928 |
| [`references/artifacts/packaged.md`](references/artifacts/packaged.md)                             |    659 |
| [`references/checks.md`](references/checks.md)                                                     |    709 |
| [`references/cicd-fy.md`](references/cicd-fy.md)                                                   |  2,412 |
| [`references/community.md`](references/community.md)                                               |  1,088 |
| [`references/docs.md`](references/docs.md)                                                         |    805 |
| [`references/hygiene.md`](references/hygiene.md)                                                   |  1,842 |
| [`references/platforms/github.md`](references/platforms/github.md)                                 |  1,438 |
| [`references/publish.md`](references/publish.md)                                                   |    630 |
| [`references/releases.md`](references/releases.md)                                                 |  1,304 |
| [`references/security.md`](references/security.md)                                                 |    814 |

<!-- token-estimates:end -->

`cicd-fy` helps design, audit, or reshape CI/CD so local checks, pull-request gates, releases, and published artifacts form one reliable system. It covers release versioning, repository settings,
security scanning, artifact signing, provenance, SBOMs, and contributor documentation without treating workflow YAML as the whole solution.

[Read the canonical skill instructions.](SKILL.md)

## What it provides

The guidance is platform-neutral, with GitHub Actions as the reference implementation. The intended result is a pipeline where CI runs the same commands as local development, dependencies and
permissions are tightly controlled, release behavior is explicit, and consumers can verify what they download.

The skill supports two modes:

- **Guidance mode** applies focused practices to one task, such as adding a check workflow, reviewing action permissions, or signing a container image.
- **Transformation mode** inventories an existing repository, agrees on a target release model, converts the system in safe stages, verifies it, and updates the relevant project documentation.

Transformation usually moves from inexpensive hardening to shared checks, then release and publishing changes. Existing release paths stay usable until the replacement has been proved. The files under
`assets/` are reference workflows and configuration templates to adapt to the repository and artifact type; they are not a universal bundle to copy unchanged.

## Boundaries and tradeoffs

- GitHub-specific mechanics do not limit the core model, but other CI platforms need equivalent implementations.
- Label-driven automatic releases are the default shape, not a mandatory choice. Changing a release contract requires agreement on version labels, unlabeled pull requests, approvals, and release
  candidates.
- Report-only security checks are safer for an established repository with existing findings. Blocking gates should be enabled deliberately after the backlog is understood.
- Report-only checks avoid source changes but can still need pull-request write access for status comments. Automated fix pull requests need broader write access and do not support fork contributions
  in the same way.
- Immutable releases require artifacts, signatures, and attestations to finish before publication. Human-curated draft releases trade that guarantee for review of release notes.
- Artifact pipelines differ: Go libraries may need only a tag, while binaries, bundles, and container images need different build, rollback, signing, and multi-platform strategies.

## Example requests

- "Audit this repository's CI/CD and identify unsafe permissions or release gaps."
- "Add pull-request checks that run the same commands developers run locally."
- "Create a label-driven release pipeline with release candidates."
- "Publish this multi-architecture image with an SBOM, provenance, and keyless signing."
- "Reshape this repository's CI/CD without breaking the next release."
