# Packaged artifact

A project whose deliverable is a file you attach to a GitHub Release: a bundle, a zip, a single binary, a
plugin package.

## The build contract

The pipeline never knows how to build your artifact; it calls build tool `mise run build --version <tag>`. That task:

- stamps the version into the artifact (e.g. into a manifest), building a throwaway copy so the working
  tree stays clean;
- drops the finished file(s) under `build/`.

CI then checksums `build/*`, attests them, and uploads them. Keeping the build in a task means the release
job and a local `mise run build` produce the identical artifact.

## Two ways to release (pick one)

- **Auto-tag on merge** (default) -> [`release.yml`](../assets/.github/workflows/release.yml). The bump
  label on the merged PR tags a version, builds, and publishes with generated notes. The build/attest/
  upload steps live at the end of `release.yml`; nothing extra to add.
- **Draft, then publish** -> [`auto-release.yml`](../assets/.github/workflows/auto-release.yml) (draft) +
  [`build.yml`](../assets/.github/workflows/build.yml). release-drafter keeps a curated draft; a human
  publishes it, and `on: release: published` fires `build.yml` to build + attach. Use this when you want
  to eyeball notes before shipping. Trade-off: publishing is the trigger, so the release is public and
  asset-less for the minute the build takes — the strict
  [publish gate](../SKILL.md#publish-sign-attest) holds only in the auto-tag model, where
  `gh release create` runs after the build.

## Attest the bundle too

The sign/attest principle is artifact-agnostic
([SKILL.md](../SKILL.md#publish-sign-attest)). A packaged artifact does not get to skip
it: generate `checksums.txt` over `build/*` and run `actions/attest-build-provenance` on the set, so a
downloader can `gh attestation verify <file> --owner <you>`. why: a bundle pulled from a Release is exactly
the kind of artifact provenance is for. Signing the bundle with cosign is optional for a Release asset
(attestation already binds it to your pipeline); reach for it only if consumers ask for a detached
signature.

## Notes

- **`cache: false` on the build's mise setup.** A one-shot release build has no cache to reuse and a
  poisoned cache would taint the artifact (zizmor `cache-poisoning`).
- **`gh release upload --clobber`** so re-running the job replaces assets instead of erroring.
- **RC of a bundle** just tags `-rc.N` and publishes `--prerelease`; the same `build` task runs. There is
  nothing image-like to re-point, so no extra care beyond not marking it `--latest` (release.yml handles
  that).
