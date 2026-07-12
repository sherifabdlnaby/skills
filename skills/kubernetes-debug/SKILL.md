---
name: kubernetes-debug
description: >
  Use for Kubernetes Debugging Sessions
license: MIT
argument-hint: "[debug <resource> | investigate <symptom>]"
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# kubernetes-debug

Route first: the debugging procedure lives in a `references/` file. Open the matching one before investigating; reading it late means redoing the diagnosis.

## Router

**Debugging / investigating** (why is X Pending / CrashLooping / not ready / reverted / 503ing / not scaling / not provisioning) -> [`references/debugging.md`](references/debugging.md)

## Guidelines

1. Kubernetes is not synchronous system; it is a set of controllers, each reconciling its own desired state, it's common for controllers to not be aware the others exist even if they depend on it.
Never read one controller's local complaint as the system's verdict, judge a converging system by a single frame, or trust a single source of evidence (events, especially).
2. Use `evict` instead of Pod Deletion for restarts.
