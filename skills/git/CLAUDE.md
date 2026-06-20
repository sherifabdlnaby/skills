# Agent instructions for the `git` skill

## Keep the Table of Contents in sync

`SKILL.md` has a `## Contents` table of contents with a one-line description per entry.

Whenever you **add, remove, rename, or re-order** a heading in `SKILL.md`, or **add/remove a `references/*.md` file** that the TOC points to, update the `## Contents` block in the same change:

- Mirror every `##`/`###` heading (skip the `## Contents` heading itself).
- Use GitHub anchor slugs: lowercase, spaces → `-`, drop punctuation (e.g. `AI Disclosure` → `#ai-disclosure`).
- Keep the short description after each entry (the text after the `:`), and update it when the section's purpose changes.
- There is no TOC generator in the toolchain (`rumdl` only lints), so this is maintained by hand. Run `rumdl check skills/git/SKILL.md` after editing.
