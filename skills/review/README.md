# review

[All skills](../)

[Canonical skill instructions](SKILL.md)

Use `/review` to require a local review panel before work is considered complete. By default, one reviewer sees the full session context and one starts fresh with only the task and branch diff. Larger
panels add independent reviewers with distinct concerns, and strong cross-model review may be used when available.

Reviews run in parallel. Valid findings are fixed, unsupported findings are rejected with reasons, and disputed points are raised to you. Fixes receive one focused re-review before the gate opens.

Invoke `/review` for the default two reviewers, or pass a count such as `/review 3`. More reviewers provide broader scrutiny but cost more time and model usage; fresh reviewers also lack conversation
context by design.
