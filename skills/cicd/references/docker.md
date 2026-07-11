# Container image

Deliverable is a multi-arch image in a registry (GHCR), signed and attested. Two workflows:
[`build-test-scan.yml`](../assets/.github/workflows/build-test-scan.yml) gates every PR;
[`publish-sign.yml`](../assets/.github/workflows/publish-sign.yml) ships on release.

## Multi-arch: native for CI, QEMU for the push

- **Per-PR build/test/scan runs native**: an amd64 job on `ubuntu-latest` and an arm64 job on
  `ubuntu-24.04-arm`, no QEMU. why: emulated arm64 builds are minutes-slower and occasionally miscompile;
  a real runner is faster and truer, and you want that signal on every PR.
- **The release push uses one QEMU + buildx job** to build both platforms and produce a single manifest.
  why: a push is infrequent and needs one digest to sign, so simplicity beats the matrix+manifest-merge
  speed you cared about per-PR. (Matrix-build-then-merge is the faster alternative if release time hurts.)
- **arm64 runners are free for public repos, metered for private.** On a private repo, weigh the native
  matrix against QEMU for the PR builds too.

## Tags (metadata-action)

One consistent scheme: the version tag (`1.2.3`) always; moving aliases (`1.2`, `1`, `latest`) only for a
stable release, detected from the tag string itself (a `-` marks a pre-release — the release event's
`prerelease` field is empty on manual dispatch, the tag never lies). why: an `-rc.N` must never steal
`latest` or a major alias from the last stable image.

## Sign & attest (the how; principle is in SKILL.md)

- **cosign, keyless.** `cosign sign --yes <registry>/<image>@<digest>` signs by digest using the
  workflow's OIDC identity. No key. The signer is the workflow, provable at verify time.
- **Digest comes from the build.** `docker/build-push-action` exposes `steps.build.outputs.digest`; sign
  and attest that, not a tag (tags move, digests don't).
- **Provenance + SBOM.** `actions/attest-build-provenance` (SLSA) and `actions/attest-sbom` on
  `subject-name` + `subject-digest`, `push-to-registry: true` so the attestations live beside the image.
  SBOM is Syft `spdx-json`.
- **Verify (put in the Release body / README):**

  ```bash
  cosign verify \
    --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
    --certificate-identity-regexp="https://github.com/<owner>/<repo>/.*" \
    ghcr.io/<owner>/<repo>:<tag>
  gh attestation verify oci://ghcr.io/<owner>/<repo>:<tag> --owner <owner>
  ```

## Triggering the publish

`publish-sign.yml` runs on `release: published`. In the **draft model** a human publishes and it fires
normally. With **auto-tag-on-merge**, the release is created by `GITHUB_TOKEN`, and token-made events do
not trigger further workflows (recursion guard), so it will NOT fire on its own. Options: fold the
push/sign/attest steps into `release.yml`'s release job, publish via the draft model, or push the tag with
a PAT/app token. The `workflow_dispatch` input is there for manual re-runs.

Mind the publish gate (SKILL.md): any `release: published` path makes the notes public *before* the image
lands. To honor the gate strictly, fold the steps into `release.yml` so `gh release create` runs after the
image is pushed and signed — or create the release as a draft, run the publish steps, then
`gh release edit --draft=false`.

## Scan

Trivy scans the built image to SARIF, uploaded to the Security tab (`exit-code: 0` reports without failing
on a known CVE, `security-events: write` on that job only). Two pins for GHSA-69fq-xp46-6x23: the
`trivy-action` at `>= 0.35.0` (its older tags were force-pushed) and the Trivy CLI past the compromised
`0.69.4`-`0.69.6` builds.

## Cache & rollback

- **buildx `type=gha` cache**, scoped per platform so the two arches don't evict each other
  (`scope=${{ matrix.platform }}`).
- **Rollback** is re-pointing, not deleting: push a fixed image and move `latest`/the major alias back to
  a known-good digest. Never move a moving alias onto an `-rc`. The signed digests stay immutable and
  verifiable.
