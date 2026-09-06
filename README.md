<p align="center">
  <img src=".github/assets/logo.svg" alt="Hand-rolled sushi" width="240" />
</p>

<h1 align="center">Skills</h1>

<p align="center"><em>My hand-rolled AI Skills I use every day.</em></p>

<p align="center">
  <a href="https://skills.sh/sherifabdlnaby/skills"><img src="https://skills.sh/b/sherifabdlnaby/skills" alt="skills.sh" /></a>
  <a href="https://github.com/sherifabdlnaby/skills/actions/workflows/check.yml"><img src="https://github.com/sherifabdlnaby/skills/actions/workflows/check.yml/badge.svg" alt="Checks" /></a>
</p>

Hand-rolled Skills, and other AI bits I build from my own day-to-day experience.

## Skills

1. [coding](skills/coding/) | My coding and docs conventions and taste. Loaded first on anything that touches code or docs.
2. [mise-fy](skills/mise-fy/) | Encode `mise` best practices. And Transform projects into using mise + hk for a good dev setup!
3. [cicd-fy](skills/cicd-fy/) | CI/CD patterns: build/test/scan, label-driven releases, changelogs from PRs, and publishing signed + attested artifacts.
4. [git](skills/git/) | My git conventions and PR workflow.
   - [watch-pr](skills/variants/watch-pr/) | Babysit a PR: respond to reviews and fix CI, until green (or `forever`).
5. [kubernetes-debug](skills/kubernetes-debug/) | WIP: Failure mode when debugging k8s
6. [afk](skills/afk/) | Letting the agent know I am no longer gonna be there to answer questions (un-grill-me lol).
   - [afk-careful](skills/variants/afk-careful/) | Conservative with its autonomy.
   - [afk-yolo](skills/variants/afk-yolo/) | Max non-destructive autonomy.
   - [afk-soon](skills/variants/afk-soon/) | I am leaving soon, ask all ur questions now...
7. [review](skills/review/) | WIP: Review patterns.
8. [scaffold-skill](skills/scaffold-skill/) | Author skills the way I like them: progressive disclosure, routers, voice, and descriptions that actually trigger.
9. [grilling](skills/grilling/) | [Matt Pocock](https://github.com/mattpocock/skills)'s relentless interview, forked to ask through the `AskUserQuestion` tool instead of markdown.
   - [grill-me](skills/grill-me/) | Start the interview by hand.

### Vendored

Skills I didn't write but use daily, vendored under [`skills/vendor/`](skills/vendor/) so the plugin ships one set instead of asking you to install them separately. Thanks to
[mattpocock/skills](https://github.com/mattpocock/skills), [humanlayer/skills](https://github.com/humanlayer/skills), [blader/humanizer](https://github.com/blader/humanizer), and
[github/gh-stack](https://github.com/github/gh-stack).

[`skills-lock.json`](skills-lock.json) is the list, and `mise run skills:sync` rebuilds the directory from it. It records where each skill comes from, not which version, so a sync takes whatever
upstream has now.

## Models

I mostly use (`opus-4.8|5`,`gpt 5.5`,`gpt 5.6 sol|terra`, and `grok 4.5`), weaker models might not work as good, especially that I rely on model's world knowledge over explicit examples.

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

This repo is managed by [mise](https://mise.jdx.dev): it pins every tool, exposes the tasks, and
wires the git hooks, so you only deal with mise once.

<details>
<summary><b>First time on this machine — install and activate mise</b></summary>

```bash
brew install mise                                  # or: apt/dnf/pacman install mise, winget install jdx.mise
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc     # bash: mise activate bash >> ~/.bashrc
mise doctor                                        # confirm the install is healthy
```

Other install methods: [installation docs](https://mise.jdx.dev/installing-mise.html).

</details>

You also need the [`gh` CLI](https://cli.github.com) logged in (`gh auth status`) — mise doesn't
install it, and the `pinact` check step borrows its token to resolve action tags to SHAs. Without
it that step runs unauthenticated and gets rate-limited.

One-time setup, from the repo root:

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

The same `check` task runs in the pre-commit hook and in CI. lychee checks local/relative links only by default (see `.config/lychee.toml`).

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

There's nothing to verify or download: the marketplaces install the repo at the tag.

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).
