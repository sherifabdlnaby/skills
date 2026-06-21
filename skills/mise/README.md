# Mise-fy 👨🏻‍🍳

Best-practices, tips, and gotchas to maximize the use of [mise](https://mise.jdx.dev) (along-side [hk](http://hk.jdx.dev/)) distilled from experience building dev (& CI) setups that ✨just works ✨ for diverse teams at different levels that you and your agents would love to use!

**The skill has two modes to trigger for:**
1. Provide tips & gotchas to agents when working with Mise. (duhh!)
2. **_Mise-fy_** 🪄 an existing project to recommended structure.

Read the Skill's [.MD](./SKILL.md) file, as well as each topic's reference in [./references](references) to learn more about what the skill encodes.

TODO: Skill overlap with a "GOOD Local setup" skill, but it's focused on just mise (which make most of it!)
TODO: Use with opus 4.8 or gpt 5.5
## When it kicks in

The skill triggers when you add a tool, pin a runtime, edit `mise.toml`, wire up pre-commit, set up CI, or convert a whole project to mise. You don't have to say "mise" out loud. "Pin the node version" or "add a lint task" is enough.

It stays out of the way for routine use (`mise run`, `mise install`, `mise x`) that isn't changing config.

## How it's laid out

Progressive disclosure. `SKILL.md` is a thin router that points at one reference per area, each read only when the task needs it:

- `install.md`: machine setup, shell activation, shims for non-interactive shells
- `tools.md` (+ `runtimes/`): installing, pinning, updating tools and runtimes, the lockfile
- `env.md`: `[env]`, dotenv, secrets, templating, redaction, PATH
- `tasks.md`: TOML vs file tasks, `depends`/`wait_for`, `sources`/`outputs` caching, parallelism
- `hk.md`: `hk.pkl` pre-commit hooks, `check` vs `fix`, builtins, custom steps
- `ci.md` (+ `ci/github.md`): shims, caching, pinning, and tokens in CI
- `mise-fy.md`: migrate an existing project off asdf/Makefile/custom scripts, with an audit checklist
- `docs.md`: what to put in README and AGENTS.md so the setup is discoverable
- `reference-setup-and-patterns.md`: an annotated example tree and `mise.toml` to copy from

Underneath all of that sits a short "always applies" floor: config trust, `min_version`, GitHub rate-limit settings, and the shim gotchas that explain most local-vs-CI mismatches.

## Scope of a change

Narrow request, narrow edit. A one-tool change touches only the practices around that tool plus the safety floor, with maybe a suggestion or two for adjacent improvements. Ask it to "mise-fy" or audit a project and it goes wide: every reference, every recommendation.
