# Debugging

## The thinking model

1. **Independent controllers, converging.** Each controller sees only its own job. The scheduler
that emits `FailedScheduling` does not know Karpenter is already provisioning a node; its event
is locally true and globally uninformed. Desired state is the contract; controllers pull observed
state toward it in loops, and the cluster may never reach a "stable" state at all. That is the
design, not a degradation.

2. **A snapshot is not a verdict.** Transient failure is the *mechanism* of convergence: retry
   loops, `Warning` events, and not-ready states during transitions are Kubernetes working, not
   breaking. Before concluding from any observation, ask whether you are looking at a system
   mid-transition.

3. **Truth lives in status conditions, not events.** `spec` is desired state; `.status.conditions`
and `observedGeneration` are current by construction, because the owning controller maintains
them. Events are the opposite: deduplicated (one object, a `count`, two timestamps), TTL'd (~1h
default), best-effort, and explicitly documented as supplemental. An event is a hint with a
timestamp about *where* to look, never proof of *what is true now*. A verdict resting mainly on
events is not a verdict.
   - Events tell you *where* to look next; they do not establish what is true now

4. **Neither wait nor panic: interrogate the responsible controller.** Declaring failure and
"it's eventually consistent, just wait" are both reflexes; the correct move is reading the
controller responsible for the next transition. Converging looks like new, distinct states
appearing (nodeclaim launched → node ready → pod bound). Stuck looks like the same error repeating,
or the responsible controller silent or erroring. Judge by progress markers, not clocks; the
system's own deadlines (`progressDeadlineSeconds`, `backoffLimit`, startup-probe budgets) are the
formal backstop.

5. **Discover who's in the room before diagnosing.** Walk `ownerReferences` up (and check their
events), check `managedFields` for who writes the contested field, and learn which reconcilers act
on this cluster (autoscaler, GitOps, operators, mutating webhooks) before forming any hypothesis.
`FailedScheduling` means "out of capacity" only in a cluster with no autoscaler; an edit that
reverts means an owner exists, not a bug.

6. **Act through desired state.** Mutating what a controller owns — deleting a pod as a fix,
`kubectl scale` under an HPA, editing a GitOps-managed object — is fighting the reconciler, and
the reconciler wins. Express every fix as desired state applied at the layer that owns it. If a
fix requires acting *against* a controller, either the diagnosis is wrong or you've found a
genuine edge case; say which.

7. **Re-observe, and try to refute yourself.** Observing twice, seconds apart, is a cheap and
legitimate diagnostic move, and "nothing is wrong, the system is mid-reconciliation" is a
legitimate conclusion. Form the hypothesis from conditions, then look for what would disprove it;
an early misread steers every subsequent command toward premise-confirming evidence.

## Gotchas catalog

### Reconciliation in progress (self-resolves -> but verify the resolver is progressing)

- **`FailedScheduling` with an autoscaler installed**; the scheduler doesn't know capacity is coming. Discriminator: Karpenter NodeClaim / CA `TriggeredScaleUp` progressing. The event alone never means "out of capacity".
- **`Multi-Attach error` / `FailedAttachVolume` after a *graceful* reschedule**; detach from the old node takes time (force-detach after ~6m). On a *dead* node it never self-resolves; that variant is in the next section.

### Lookalikes that are genuinely stuck (the inverse trap)

These read like the previous section but never self-resolve; the discriminator is always the responsible controller's own status.

- **`FailedScheduling` on an unsatisfiable constraint** (nodeSelector/affinity no node group
  can ever have, provisioner limits hit) identical to transient one. Discriminator: the
  provisioner says so (Karpenter events/logs: no instance type satisfies requirements).
- **Karpenter nominates but the pod never binds** > provision-terminate loops, or the nominated node fills first. `Nominated` events *look* like convergence; check NodeClaim churn.
- **`Multi-Attach error` with the old node dead/unresponsive** — no kubelet alive to detach; needs intervention (delete the stale VolumeAttachment).
- **Namespace stuck `Terminating`**: a finalizer whose controller is gone, or a dead aggregated APIService. A controller that no longer exists never reconciles.
- **Rollout deadlock by arithmetic**: `maxUnavailable: 0` + PDB + one failing new pod, or a stuck Terminating pod eating the surge budget.

### Signals that mean something else

WIP

## Remediation discipline

Diagnosis and remediation are one doctrine: act on desired state, through the owning controller.

- Deleting a pod "to fix it" treats a symptom, destroys the evidence (`--previous` is now something else), and the ReplicaSet recreates the problem. Legitimate only when *chosen deliberately* — e.g. skipping a backoff timer after the actual fix shipped.
- Force-deleting a Terminating pod removes it from the API without confirming the node stopped it; with StatefulSets that risks two writers. First find what's blocking: finalizer, dead node, long grace period.
- Under GitOps, the fix goes in Git; under an operator, in the CR; under an HPA, in the HPA spec. A `kubectl edit` on any of these gets reverted on the next sync.
