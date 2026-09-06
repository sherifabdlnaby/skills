# Prototype

[Read the canonical skill instructions.](../../../skills/vendor/prototype/SKILL.md)

Some design questions are easier to answer by trying a small working model than by discussing them. Prototype creates disposable code that makes one uncertain choice concrete enough to test.

For business logic, state transitions, or data-shape questions, it builds one self-contained HTML demo. The demo exposes the full relevant state, free-play controls, and guided edge-case scenarios in domain language. For visual design questions, it builds several structurally different UI variants on one route, preferably inside the existing application context, with a URL-based switcher for comparison.

The result is deliberately not production code. It omits persistence, broad error handling, abstractions, and tests. A validated decision is rewritten into the real system; the full prototype is kept
off the main branch as a record of what was tested. This keeps fast experimental choices from becoming accidental production constraints.

```text
/prototype Show three different information hierarchies for the existing settings page.
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
