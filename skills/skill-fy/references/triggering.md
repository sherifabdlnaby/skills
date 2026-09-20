# Description and Triggering

Covers: what a description is for, the levers that move trigger rate, anti-triggers, manual-only descriptions, measuring on the real installed skill, prompts that never fire cold.

## What a description is for

The description is a context pointer loaded every turn. It exists to trigger, not to summarize: only what gets an agent who merely knows some keywords to reach the skill.
Write it last, once the tasks are real (why: written first, it bakes in branches the body ends up not having).

## Levers

Measured on this repo's git skill, holding keywords constant (Claude Code, Opus 4.8, cold single-turn prompts, verified 2026-07):

- **Concrete lead verb first.** "Load when about to commit, branch, push..." fires more than "Load when git work is anywhere in the conversation's future...". Abstract framing at the front
  costs fires.
- **Double the trigger.** State the load condition up front, then close with a second statement of it ("Load as early as possible, the moment X is anywhere in the chat's future.").
  A terse single statement under-triggers.
- **Words the user actually types.** A leading word that lives in the owner's prompts and codebase links the agent to the skill; a synonym they never use is dead weight.
- **One identity sentence.** What the skill carries, so the agent knows what it is loading. Internals (sections, page names) stay out.
- **Anti-trigger only for a common misfire.** A tool touched constantly earns its "don't load for routine use that isn't changing config"; a rare misfire doesn't earn the words.
- **Manual-only means neutral.** With `disable-model-invocation: true` the user is the index: one plain line, no trigger phrasing (why: some harnesses ignore the flag, and a trigger-rich
  description auto-fires the skill anyway).

Dropping the first two levers cost the git skill a measurable share of its fires with no gain in specificity; restoring them brought the rate back.

## Measuring

Measure the real installed skill, on the harness the owner actually runs. The recipe below is Claude Code's; other harnesses need their own runner, the metric holds.

1. **Eval set.** Should-trigger prompts phrased the way the owner types, plus near-miss prompts that share keywords but must not fire. Keep it beside the skill (e.g. `evals/trigger-eval.json`).
2. **Runner.** Spawn `claude -p "<prompt>" --output-format stream-json --verbose` from the repo root, in the real config, with `CLAUDECODE` removed from the environment. Parse the first
   assistant tool turn: a trigger is a `Skill` tool use naming the skill, or a `Read` of its SKILL.md.
3. **Repeat.** Three runs per prompt. Pass-rate hides confidence drops, so the metric is **total fires on should-trigger prompts**, with zero fires on the near-miss set as the specificity floor.
4. **A/B.** Installed skills are symlinks to the working tree, so edit the description in place, run, then `git checkout` it to restore. Run conditions one after the other; the swap is global.
5. **Busy context.** Prepend filler to each prompt to simulate a long session; a description that only fires cold is not done.

## Gotchas

- **The synthetic-command harness reads false non-triggers.** A runner that injects a `<skill>-<uuid>` command and counts only that name sees nothing when the real skill is installed:
  the model fires the real one every time. Measure the installed skill.
- **`CLAUDE_CONFIG_DIR` isolation breaks auth.** The login isn't in the config-dir files. Run in the real config instead.
- **"Do X, then commit" never fires cold.** The model starts on X and never makes a turn-1 skill decision. Not a description problem; the skill loads when the commit happens. Chasing it in
  the description over-triggers elsewhere.
- **Convention skills resist cold evals.** A coding-style skill scores near zero on single-turn prompts because the model just codes. Judge those on behavior with and without the skill in a
  long-context run, not on triggering.
