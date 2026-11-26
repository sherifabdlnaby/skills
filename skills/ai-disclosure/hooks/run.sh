#!/bin/sh
# Hook launcher: run.sh <protocol>, with the harness payload on stdin.
#
# Every shell command the agent runs passes through here, so the common case stays in
# plain sh: a payload that cannot be a GitHub post exits before Python starts. The rest
# goes to the guard (hooks/guard). When the guard cannot run (no python3, or it
# crashed), a possible post is blocked rather than let through undisclosed, with a
# message that says how to fix it. Those denials are the one place outside
# hooks/guard/harness.py that writes each protocol's verdict shape; keep them in step.
set -u

PROTOCOL="${1:-}"

[ "${AI_DISCLOSURE:-}" = off ] && exit 0

PAYLOAD="$(cat)"

# Must match anything the guard treats as a post. pr/issue verbs mirror `_POSTING` in
# guard/github.py (keep in step); `gh api` stays coarse and the guard lets reads through.
# `\\` and `\n` cover a JSON-escaped line continuation; the word boundary skips prose.
# A repo flag may sit between the noun and the verb (`gh pr -R o/r comment`).
printf '%s' "$PAYLOAD" | grep -Eq '(^|[^[:alnum:]_.-]|\\[nt])gh([[:space:]]|\\[nt\\])+(api|(pr|issue)(([[:space:]]|\\[nt\\])+(-R|--repo)(=|([[:space:]]|\\[nt\\])+)?[^[:space:]\\]+)?([[:space:]]|\\[nt\\])+(create|comment|edit|review))([[:space:]]|\\[nt\\]|$)' || exit 0

DIR="$(cd "$(dirname "$0")" && pwd)"

deny() { # deny <message>; it must not contain `"` or `\`
  case "$PROTOCOL" in
    cursor) printf '{"permission":"deny","agent_message":"%s","user_message":"%s"}\n' "$1" "$1" ;;
    *) printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"%s"}}\n' "$1" ;;
  esac
  exit 0
}

SKILL='Load the ai-disclosure skill for the disclosure line.'
OPT_OUT='Opt out only with a reason (the user waived the line, or the repo forbids it): put AI_DISCLOSURE=off in front of gh for this one command.'

command -v python3 >/dev/null 2>&1 || command -v uv >/dev/null 2>&1 ||
  deny "Blocked by the ai-disclosure hook: it needs python3 to check this GitHub post for an AI disclosure, and this machine has none. Tell the user to install it (macOS: xcode-select --install, Linux: the python3 package of the distro, e.g. apt install python3), then retry. $SKILL $OPT_OUT"

# Version manager shims resolve python3 from the working directory; `/` keeps a local
# config out of it. The guard gets the command's directory from the payload.
cd /
guard() { VERDICT="$(printf '%s' "$PAYLOAD" | "$@" -E -s "$DIR/guard" "$PROTOCOL" 2>/dev/null)"; }
if ! guard python3 && ! guard uv run --no-project --quiet python3; then
  # The guard reads the per-command opt-out; without it, match it coarsely.
  case "$PAYLOAD" in *AI_DISCLOSURE=off*) exit 0 ;; esac
  # Rerun for the error text; the runs above discard stderr.
  WHY="$(printf '%s' "$PAYLOAD" | python3 -E -s "$DIR/guard" "$PROTOCOL" 2>&1 >/dev/null |
    head -n 1 | tr -cd '[:print:]' | tr -d '"\\')"
  deny "Blocked by the ai-disclosure hook: its guard failed on this command, so it could not check the GitHub post for an AI disclosure (error: ${WHY:-none printed}). Tell the user, then retry. $SKILL $OPT_OUT"
fi
[ -n "$VERDICT" ] && printf '%s\n' "$VERDICT"
exit 0
