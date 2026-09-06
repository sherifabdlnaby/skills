# kubernetes-debug

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-240%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 240 tokens" />
  <img src="https://img.shields.io/badge/Total-1%2C513%20tokens-2ea44f?style=flat-square" alt="Total: 1,513 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                                                 |  Tokens |
| ---------------------------------------------------- | ------: |
| [`SKILL.md`](SKILL.md)                               |   `240` |
| [`references/debugging.md`](references/debugging.md) | `1,273` |

<!-- token-estimates:end -->

`kubernetes-debug` provides a disciplined way to investigate Kubernetes failures without mistaking normal reconciliation for a broken cluster or treating a controller-owned symptom as the root cause.

[Read the canonical skill instructions.](SKILL.md)

## What it provides

The workflow starts from desired state and current status conditions, identifies the controller responsible for the next transition, and follows ownership and field management before forming a
hypothesis. Evidence is observed more than once and tested against facts that could disprove the diagnosis. Events remain useful clues, but they are not treated as current truth.

This approach distinguishes a system that is making progress from one repeating the same failure. It also directs remediation to the layer that owns the state, such as Git for a GitOps-managed object,
an operator's custom resource, or an HPA specification.

## Boundaries and tradeoffs

- A warning, pending pod, or failed scheduling event can be temporary while another controller makes progress. Waiting without checking that controller is as weak as declaring failure too early.
- Direct edits to controller-owned resources are often reverted and can destroy useful evidence.
- Pod deletion is not a general restart strategy. Prefer eviction when a restart is required, and change desired state when fixing the underlying problem.
- Force deletion and storage attachment cleanup can create data-safety risks; they require proof that normal reconciliation cannot finish.
- Some similar symptoms have opposite causes, such as temporary capacity provisioning versus an unsatisfiable scheduling constraint. The responsible controller's status is the discriminator.

## Example requests

- "Why is this pod still Pending when cluster autoscaling is enabled?"
- "Investigate this CrashLoopBackOff without deleting the pod first."
- "Why does my Deployment edit keep reverting?"
- "Determine whether this rollout is progressing or deadlocked."
- "Debug a namespace stuck in Terminating."
