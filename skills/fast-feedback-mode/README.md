# fast-feedback-mode

[All skills](../)

[Canonical skill instructions](SKILL.md)

Use `/fast-feedback-mode` for a tight, interactive build-and-try loop. It makes only enough of each requested change for you to see or use it, reports back briefly, and waits for your next adjustment.
Where useful, a mock can expose the intended experience before slower supporting work is complete.

Tests, checks, formatting, documentation, and commits are deferred so they do not interrupt iteration. Say `finalize` when the direction is settled to request that deferred work; finalizing does not
imply a commit, which must be requested separately. This mode improves feedback speed at the cost of leaving the work unverified and incomplete until finalization.
