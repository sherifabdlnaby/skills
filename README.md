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

Each line is a skill, then its variants, then what it does.

1. [coding](skills/coding/) | My coding and docs conventions and taste. Loaded first on anything that touches code or docs.
2. [mise-fy](skills/mise-fy/) | Encode `mise` best practices. And Transform projects into using mise + hk for a good dev setup!
3. [cicd-fy](skills/cicd-fy/) | CI/CD patterns: build/test/scan, label-driven releases, changelogs from PRs, and publishing signed + attested artifacts.
4. [git](skills/git/) | [watch-pr](skills/variants/watch-pr/) | [watch-pr-ci](skills/variants/watch-pr-ci/) | [watch-pr-comments](skills/variants/watch-pr-comments/) | My git conventions and PR
   workflow. The variants babysit a PR until green and quiet: CI and reviews, CI only, or reviews only.
5. [afk](skills/afk/) | [afk-careful](skills/variants/afk-careful/) | [afk-yolo](skills/variants/afk-yolo/) | [afk-soon](skills/variants/afk-soon/) | Letting the agent know I am no longer gonna be
   there to answer questions (un-grill-me lol). Careful, max non-destructive, or "ask all ur questions now, I am leaving soon".
6. [grilling](skills/grilling/) | [grill-me](skills/grill-me/) | [Matt Pocock](https://github.com/mattpocock/skills)'s relentless interview, forked to ask through the `AskUserQuestion` tool
   instead of markdown. `grill-me` starts it by hand.
7. [ask-me](skills/ask-me/) | How to ask me questions: in rounds, through the harness's question tool, with explanations where I can see them.
8. [what-happened](skills/what-happened/) | Catch me up on what changed since my last message, and what waits on me.
9. [wait-what](skills/wait-what/) | That last message did not land: say it again, plainer.
10. [fast-feedback-mode](skills/fast-feedback-mode/) | Act fast and keep me in the zone; tests, lints, and commits wait until I say finalize.
11. [review](skills/review/) | WIP: Review patterns.
12. [skill-fy](skills/skill-fy/) | Author skills the way I like them: progressive disclosure, routers, voice, and descriptions that actually trigger.
13. [ai-disclosure](skills/ai-disclosure/) | Adds an AI disclosure line to every GitHub post made as you: 🤖 Agent Decided, 📋 Human Planned, or 🤝 Human Guided, with the model and its thinking
    effort.
14. [... other vendored](skills/vendor/README.md) | Skills I didn't write but use daily, e.g. gh-stack, humanizer, and codebase-design. Thanks to their authors.

[`skills/`](skills/README.md) has what each skill costs in tokens.

Skills can depend on each other: `watch-pr` runs on top of `git`, for example.

## Plugins

The `skills` plugin is the whole stack: every skill above, vendored ones included, plus the hooks. Other plugins carry one piece of it for when you want only that piece:

- **`skills`**: everything.
- **`ai-disclosure`**: the AI disclosure skill and its hook.

Each plugin is complete on its own: it ships everything its skills need and depends on no other plugin.

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
/plugin install ai-disclosure@sherif-plugins   # or just this one
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
mise run check          # report on uncommitted changes (alias: mise run lint)
mise run check --fix    # apply fixes
mise run check --all    # whole repo
mise tasks              # discover every task
```

Commits run the fast commit gates on staged files, a push runs the slower push gates, and CI runs both as `mise run check`. lychee checks local/relative links only by default (see
`.config/lychee.toml`).

## Releases

Claude/Cursor marketplaces install straight from git and key each plugin on the `version` field in
its `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` — there's no published artifact.
Each plugin versions on its own: `skills` tags `vX.Y.Z`, any other `<name>-vX.Y.Z`. Cutting a release:

1. Bump both of the plugin's manifests to the same `version` in your PR: `mise run version:check --fix`
   writes the bump. `mise run version:check` (also an `hk` pre-push gate) fails if a plugin's shipped
   content changed without it.
2. Merge to `main`. CI notices the version moved past the plugin's latest tag and cuts the tag plus
   a GitHub release, with notes generated from merged PRs and grouped by label: `skill`, `hooks`,
   `fix`, `docs`, `ci`, `deps`.
3. No version bump ships no release. A PR's sticky comment previews which outcome a merge would
   produce.

There's nothing to verify or download: the marketplaces install the repo at the tag.

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).
