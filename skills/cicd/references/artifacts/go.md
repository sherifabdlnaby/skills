# Go library / binary

Two shapes, very different CD needs. CI checks are shared.

## CI checks (both shapes)

- **Test with the race detector across supported Go versions.** The test job runs the project's own
  task (`mise run test`, wrapping `go test -race ./...`) in a small matrix over the Go tool version:
  the pinned default plus the oldest the module supports (`go` directive in `go.mod`). why: a library's
  consumers build with their own toolchain; the matrix catches what the single pinned version can't.
- **Module caching.** `mise-action` caches the tools; cache Go's module/build dirs keyed on `go.sum`
  (`actions/cache` on `~/go/pkg/mod` + `~/.cache/go-build`) so the matrix doesn't re-download per leg.

## Library (imported via `go get`)

**CD is the semver tag.** release.yml's tag push is the whole delivery — the module proxy picks it up;
nothing to build, upload, or sign.

**Major bumps change the module path.** From v2 on, a tag only resolves if `go.mod`'s module path
carries the matching `/vN` suffix (and imports update with it). A `major`-labeled PR must contain that
path change — the auto-cut `v2.0.0` tag alone leaves consumers unable to `go get` it.

**Rollback is `retract`.** A bad published version can't be unpublished; add a `retract` directive to
`go.mod` and tag a new patch. why: the proxy is immutable, so you steer consumers off the bad tag rather
than deleting it.

## Binary / CLI (a downloadable executable, maybe an image)

Now you have artifacts to build, sign, and attest. Use **GoReleaser** ->
[`.goreleaser.yml`](../../assets/.goreleaser.yml): it cross-compiles, checksums, generates an SBOM, and
keyless-signs the checksums with cosign.

The release workflow follows the shared version contract (labels -> bump -> tag; RCs by hand; see
[`release.yml`](../../assets/.github/workflows/release.yml)), then swaps the build/attest/publish steps
for GoReleaser. `goreleaser release` creates the GitHub Release itself — drop the `gh release create`
step (it errors on the release GoReleaser already made) and let the config carry the notes and
prerelease behavior. The adapted release job:

- grants `contents: write` + `id-token: write` + `attestations: write` (+ `packages: write` if it also
  pushes an image);
- installs cosign (`sigstore/cosign-installer`) and syft (`anchore/sbom-action/download-syft`);
- runs `goreleaser release --clean` (add `--draft` if you gate publishing).

`release.prerelease: auto` in the config means a `-rc.N` tag publishes as a prerelease with no extra
flags. For an image, either let GoReleaser build it (`dockers_v2` + `docker_signs`) or hand off to
[`publish-sign.yml`](../../assets/.github/workflows/publish-sign.yml) — don't do both.

One contract caveat: GoReleaser's changelog runs since the *previous tag* — after an rc line, that's
the last rc, not the last stable, so the whole-line notes promise (`--notes-start-tag` in the shared
contract) doesn't survive as-is. If it matters, regenerate the body afterwards:
`gh api repos/<owner>/<repo>/releases/generate-notes -f tag_name=<tag> -f previous_tag_name=<last-stable> --jq .body |
gh release edit <tag> --notes-file -` (`gh release edit` has no `--generate-notes` flag of its own).

Attest the binaries too: run `actions/attest-build-provenance` with `subject-checksums:
dist/checksums.txt` — every entry in the file becomes a verifiable subject, so a downloader can
`gh attestation verify <archive> --owner <you>`. (`subject-path` pointed at the checksums file would
attest only the file itself; verifying a downloaded archive then fails.)
