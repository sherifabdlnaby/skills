# Skills

Personal and Opinionated Skills, Commands, and any AI related _stuff._ Stuff that works for me, but I also generic enough to be shared with the world.

I iterate over these skills to suit my needs. Skills aren't designed to have full coverage of whatever topic they cover. It's layers of iterations my LLMs miss.

## Forked Skills

The repo will contain forked skills (e.g grill-me) that I sometimes have to tweak a little bit. Forked skill will include UPSTREAM.md file with the upstream's metadata.

## Development

This repo is managed by [mise](https://mise.jdx.dev). One-time setup:

```bash
mise run setup   # installs tools (mise install) and self-installs the pre-commit hook
```

Linters, formatters, and validators (ruff, actionlint, zizmor, pinact, betterleaks, typos, and **lychee** for dead links) run via [hk](https://hk.jdx.dev):

```bash
mise run check          # report on staged files (alias: mise run lint)
mise run check --fix    # apply fixes
mise run check --all    # whole repo (what CI runs)
```

The same `check` task runs in the pre-commit hook and in CI (`.github/workflows/check.yml`). lychee checks local/relative links only by default (see `lychee.toml`).
