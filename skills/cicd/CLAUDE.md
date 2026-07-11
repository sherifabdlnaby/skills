# Agent instructions for the `cicd` skill

- `SKILL.md` is guidance + a router: keep the `## Router` entries in sync with the `references/*.md` files
  (one entry per file, a one-line list of what it covers, no procedure text; procedures live in the
  reference or the asset).
- After editing any `.md` file in this skill, run `rumdl check skills/cicd/<file>` and fix what it flags.
- Every workflow under `assets/.github/` must pass `actionlint` and `zizmor`. Run them after editing an
  asset.
- A `references/*.md` page explains an asset's non-obvious lines; it never restates the asset's YAML.
  Change the asset, not a copy of it in prose.
- Hardening canon is **mise-fy** `references/ci/github.md`. This skill names the ideas and makes its assets
  comply; it does not restate the mechanics. If a hardening rule changes, it changes there. Exception:
  the release-job rules in SKILL.md's `## Always` (release/publish permission sets, queue-not-cancel
  concurrency) are cicd's own — mise-fy's guidance is lint-scoped and has no counterpart for them.
