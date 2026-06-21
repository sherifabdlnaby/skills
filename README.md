<p align="center">
  <img src="assets/logo.svg" alt="Hand-rolled sushi" width="240" />
</p>

<h1 align="center">Skills</h1>

<p align="center"><em>My hand-rolled AI Skills I use every day.</em></p>

<p align="center">
  <a href="https://skills.sh/sherifabdlnaby/skills"><img src="https://skills.sh/b/sherifabdlnaby/skills" alt="skills.sh" /></a>
</p>

Hand-rolled Skills, and other AI bits I build from my own day-to-day experience.

Needless to say, this is opinionated. And encode _my_ conventions, not best practice for everyone.

## Skills

1. [git](skills/git/)   | My git conventions and PR watching ("babysitting").
2. [mise](skills/mise/) | Encode `mise` best practices. And Transform projects into using mise + hk for a good dev setup!

## Models

I mostly use `opus-4.8` and `gpt 5.5`, weaker models might not work as good, especially that I rely on model's world knowledge over explicit examples.

## Installation

`npx skills` for just the skills. The plugin to get my whole setup.

### npx skills (recommended)

Installs skills into any SKILL.md-aware agent. You don't need a plugin host.

```bash
npx skills add sherifabdlnaby/skills              # all skills
npx skills add sherifabdlnaby/skills --skill git  # just one (git or mise)
npx skills list sherifabdlnaby/skills             # see what's available
```

### Claude Code (plugin) (WIP)

```bash
/plugin marketplace add sherifabdlnaby/skills
/plugin install skills@sherif-plugins
```

Update with `/plugin marketplace update sherif-plugins`; manage from `/plugin`.

---

## Development

This repo is managed by [mise](https://mise.jdx.dev). One-time setup:

```bash
mise run setup   # installs tools (mise install) and self-installs the pre-commit hook
```

Linters, formatters, and validators (ruff, actionlint, zizmor, pinact, betterleaks, typos, and lychee for dead links) run via [hk](https://hk.jdx.dev):

```bash
mise run check          # report on staged files (alias: mise run lint)
mise run check --fix    # apply fixes
mise run check --all    # whole repo (what CI runs)
```

The same `check` task runs in the pre-commit hook and in CI (`.github/workflows/check.yml`). lychee checks local/relative links only by default (see `lychee.toml`).
