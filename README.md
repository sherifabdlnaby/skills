<p align="center">
  <img src="assets/logo.svg" alt="Hand-rolled sushi" width="240" />
</p>

<h1 align="center">Skills</h1>

<p align="center"><em>My hand-rolled AI Skills I use every day.</em></p>

<p align="center">
  <a href="https://skills.sh/sherifabdlnaby/skills"><img src="https://skills.sh/b/sherifabdlnaby/skills" alt="skills.sh" /></a>
</p>

Hand-rolled Skills, and other AI bits I build from my own day-to-day experience.

## Skills

1. [git](skills/git/) | My git conventions and PR workflow.
   - [watch-pr](skills/variants/watch-pr/) | Babysit a PR: respond to reviews and fix CI, until green (or `forever`).
2. [mise-fy](skills/mise-fy/) | Encode `mise` best practices. And Transform projects into using mise + hk for a good dev setup!
3. [cicd](skills/cicd/) | CI/CD patterns: build/test/scan, label-driven releases, changelogs from PRs, and publishing signed + attested artifacts.
4. [kubernetes-debug](skills/kubernetes-debug/) | The mental model that prevents misdiagnosing a converging cluster: independent controllers, events as weak evidence, converging-vs-stuck.
5. [afk](skills/afk/) | Autonomy contract for when I step away.
   - [afk-careful](skills/variants/afk-careful/) | Local-only and conservative.
   - [afk-yolo](skills/variants/afk-yolo/) | Max non-destructive autonomy.
   - [afk-soon](skills/variants/afk-soon/) | Ask clarifying questions first, then go afk.
6. [review](skills/review/) | Gate work behind a reviewer panel — fork-session + independent reviewers, cross-model when available.
7. [scaffold-skill](skills/scaffold-skill/) | Author skills the way I like them: progressive disclosure, routers, voice, and descriptions that actually trigger.
8. [grill](skills/grill/) | A relentless, one-question-at-a-time interview to sharpen a plan before you build it. Vendored from [Matt Pocock](https://github.com/mattpocock/skills), extended to ask through the `AskUserQuestion` tool.

The `afk`, `review`, `watch-pr`, and `grill` skills are manual-only (`disable-model-invocation: true`) — they exist to make me type less, not to auto-fire.

## Models

I mostly use (`opus-4.8`,`gpt 5.5`,`gpt 5.6 sol|terra`, and `grok 4.5`), weaker models might not work as good, especially that I rely on model's world knowledge over explicit examples.

## Installation

`npx skills` for just the skills. The plugin to get my whole setup.

### npx skills (recommended)

Installs skills into any SKILL.md-aware agent. You don't need a plugin host.

```bash
npx skills add sherifabdlnaby/skills              # all skills
npx skills add sherifabdlnaby/skills --skill git  # just one skill
npx skills list sherifabdlnaby/skills             # see what's available
```

### Claude Code (plugin)

```bash
/plugin marketplace add sherifabdlnaby/skills
/plugin install skills@sherif-plugins
```

Update with `/plugin marketplace update sherif-plugins`; manage from `/plugin`.

### Cursor (plugin)

```bash
/plugin marketplace add sherifabdlnaby/skills
/plugin install skills
```

Manage from `/plugin`. Same repo, same skills — Cursor reads `.cursor-plugin/`.

---

## Development

This repo is managed by [mise](https://mise.jdx.dev). One-time setup:

```bash
mise trust && mise run setup   # trust config, install tools, self-install the pre-commit hook
```

Linters, formatters, and validators run via [hk](https://hk.jdx.dev):

```bash
mise run check          # report on staged files (alias: mise run lint)
mise run check --fix    # apply fixes
mise run check --all    # whole repo
mise tasks              # discover every task
```

The same `check` task runs in the pre-commit hook and in CI. lychee checks local/relative links only by default (see `lychee.toml`).

## Releases

Claude/Cursor marketplaces install straight from git and key the plugin on the `version` field in
`.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` — there's no published artifact.
Cutting a release:

1. Bump both manifests' `version` to the same value in your PR. `mise run version:check` (also an
   `hk` pre-push gate) fails if shipped `skills/`/`hooks/` content changed without the bump.
2. Merge to `main`. CI notices the version moved past the latest `vX.Y.Z` tag and cuts the tag plus
   a GitHub release, with notes generated from merged PRs and grouped by label: `skill`, `hooks`,
   `fix`, `docs`, `ci`, `deps`.
3. No version bump ships no release. A PR's sticky comment previews which outcome a merge would
   produce.
