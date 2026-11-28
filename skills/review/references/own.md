# Your own work, before handoff

Covers: scope, who fixes, redesign-sized findings, the handoff note.

- **Scope**: the files you were given, else the branch diff against its merge-base with the base branch, working tree included.
- **Once per handoff.** Run it when the change is code-ready, right before it goes to the user or to review. A later small fix (a review round, a rebase) does not run it again; a large new diff
  does.
- **The author fixes, a reviewer reports.** The agent that wrote the code fixes each raised breach in place, then reruns the checks the fix touches. A subagent or any agent that did not write it
  reports its findings to the caller and edits nothing. When the context says otherwise (the user asked for a report, the fix needs their call), follow it.
- **Opinions go to the user.** Attended: list them for the user to pick. Unattended: put them in the report, unapplied.
- **A redesign-sized finding goes first.** When an overall finding means a different approach, fix no lines it would replace. Attended: present it and wait. Unattended: report it as open.
- **Done** when each raised breach is fixed, or reported with the reason it stays, and the repo's checks pass.

## The handoff note

One short block in the handoff message: that review ran and at which level, what it fixed, then what is open (overall first) and the opinions. Leave out what passed.
