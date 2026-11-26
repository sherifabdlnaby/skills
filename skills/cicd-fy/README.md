# cicd-fy

[All skills](../)

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
