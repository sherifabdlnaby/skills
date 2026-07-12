# Releases

The version contract: how a merge becomes a tag, a release, and notes. The default model is
**label-driven auto-tag** ([`release.yml`](../assets/.github/workflows/release.yml) its header carries
the full case table).

## The default model: label -> bump -> tag

- **Label decides the bump.** On merge to the default branch, the merged PR's label decides the bump
  (`major` > `minor` > `patch`, and `skip-release` aborts); the pipeline tags and pushes as the CI
  identity (`github-actions[bot]`). Release runs queue so back-to-back merges tag serially (rapid-merge
  caveat in [`platforms/github.md`](platforms/github.md#gotchas)).
- **Gate + preview on the PR.** The PR job fails when no bump label is set and keeps one comment
  showing the exact version a merge would cut, recomputed on every label change; the release job
  refreshes open PRs' previews after each stable release so they never go stale. An unlabeled PR that
  merges anyway falls back to `minor` (patch is too easy to ship by accident; major is costly under
  immutable releases). **Ask the user** whether that gate/fallback pair fits or they want a different
  unlabeled-PR policy.
- **Publish with generated notes.** `gh release create <tag> --generate-notes`. release-drafter's
  `autolabeler` ([config](../assets/.github/release-drafter.yml)) applies *category* labels
  (enhancement/bug/ci/docs) on PRs, and [`.github/release.yml`](../assets/.github/release.yml) (GitHub's
  native notes config) groups the notes — OR use conventional commits to infer. Tailor the category and
  autolabeler taxonomy to the repo's real change types. Bump and category labels are separate axes: one
  sizes the version, the other groups the notes.
- **The pipeline stamps the version.** Avoid hardcoded versions in files that need a per-PR edit; the
  publishing pipeline writes the tag into the file (e.g. `package.json`) at build time instead of
  expecting it in the commit. why: a version-in-commit turns every release into a conflict-prone bump PR.

NOTE: Different projects might need different model. This is the simples starter model.
However some other project might prefer manually triggered releases, or nightly releases, converse with user.

## Release candidates

`workflow_dispatch` with a `prerelease` flag (or an explicit `vX.Y.Z-rc.N`): emit `-rc.N`,
publish `--prerelease` and **not** `--latest`. why: an rc must never steal `latest` or a moving alias
from the last stable. The next stable release passes `--notes-start-tag <last-stable>` so its notes
cover the whole line, not just rc -> final. (GoReleaser projects need a regeneration step to keep that
promise — [`artifacts/go.md`](artifacts/go.md).)

## Manual releases (dispatch)

Every release workflow carries a `workflow_dispatch` with an explicit `version` input, whatever the
model (label-driven, manifest-driven, drafted). The input wins over any computed bump and is used
verbatim (v-prefixed if missing); a `-` in it marks a pre-release and follows the rc rules above. Pass
it via `env`, never interpolated — it's user-controlled. Make the tag-existence check a clean no-op so
a re-dispatch is idempotent, and guard the job to the default branch — a dispatch can be pointed at
any ref, and a topic branch must not get tagged.

**Dispatch permission is repo-wide, not per-actor**: anyone with write access can run it. When a
manual release needs an approval step, gate the tag/publish job behind a protected environment with
required reviewers ([`hygiene.md`](hygiene.md)); a tag ruleset restricting who may create `v*` tags
blocks the push itself as a harder backstop.

## Alternative: the release-drafter draft model

When you want curated notes over auto-generated ones: a continuous draft prerelease with categorized
sections and a `version-resolver`, published by a human ->
[`auto-release.yml`](../assets/.github/workflows/auto-release.yml). The bump and category label
taxonomies must align. Trade-off: a human publishing is what triggers the build, so the release is
public before its assets land — the [publish gate](publish.md#the-publish-gate) holds strictly only in
the auto-tag model.

## Notes & Gotchas:

- **Rollback is per-artifact**, never a rewritten release: Go `retract`, image alias re-point, delete
  release + tag for a Release asset. Each [artifact page](artifacts/) carries its own.
- **Rapid merges can drop a queued release run** (one pending slot per concurrency group): its changes
  still land in the next release's notes, but its bump label isn't consumed
  ([`platforms/github.md`](platforms/github.md#gotchas)).
- **Token-created tags and releases fire no workflows** on GitHub (recursion guard) — plan what the
  release job must do inline vs what an `on: release` workflow can pick up
  ([`platforms/github.md`](platforms/github.md#gotchas)).
- Prefer Immutable Releases. This changes how releases are prepared (e.g Artifact publishing has to finish first before publishing) so attestation would work.
- **Seed the labels the release model depends on.** Create `major (red)`/`minor (green)`/`patch (blue)`/`skip-release (yellow)` plus
  the category labels (`gh label create`) as part of setup.
