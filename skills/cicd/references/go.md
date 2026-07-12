# Go library / binary

Two shapes, very different CD needs.

## Library (imported via `go get`)

**Rollback is `retract`.** A bad published version can't be unpublished; add a `retract` directive to
`go.mod` and tag a new patch. why: the proxy is immutable, so you steer consumers off the bad tag rather
than deleting it.

## Binary / CLI (a downloadable executable, maybe an image)

Now you have artifacts to build, sign, and attest. Use **GoReleaser** ->
[`.goreleaser.yml`](../assets/.goreleaser.yml): it cross-compiles, checksums, generates an SBOM, and
keyless-signs the checksums with cosign.

The release workflow follows the shared version contract (labels -> bump -> tag; RCs by hand; see
[`release.yml`](../assets/.github/workflows/release.yml)), then instead of `mise run build` it:

- grants `contents: write` + `id-token: write` + `attestations: write` (+ `packages: write` if it also
  pushes an image);
- installs cosign (`sigstore/cosign-installer`) and syft (`anchore/sbom-action/download-syft`);
- runs `goreleaser release --clean` (add `--draft` if you gate publishing).

`release.prerelease: auto` in the config means a `-rc.N` tag publishes as a prerelease with no extra
flags. For an image, either let GoReleaser build it (`dockers_v2` + `docker_signs`) or hand off to
[`publish-sign.yml`](../assets/.github/workflows/publish-sign.yml) — don't do both.

Attest the binaries too: run `actions/attest-build-provenance` over `dist/checksums.txt` so a downloader
can `gh attestation verify <binary> --owner <you>`.
