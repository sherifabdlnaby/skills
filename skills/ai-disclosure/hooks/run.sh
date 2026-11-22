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

# Coarse on purpose: anything the guard could treat as a post must match, so it may
# also match a read (`gh pr view`, `gh api user`), which the guard then lets through.
# `\\` and `\n` cover a JSON-escaped line continuation between the words. The word
# boundary keeps prose in the payload ("read through issue list") from matching.
printf '%s' "$PAYLOAD" | grep -Eq '(^|[^[:alnum:]_.-]|\\[nt])gh([[:space:]]|\\[nt\\])+(pr|issue|api)([[:space:]]|\\[nt\\]|$)' || exit 0

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

if command -v python3 >/dev/null 2>&1; then
  set -- python3 -E -s "$DIR/guard" "$PROTOCOL"
elif command -v uv >/dev/null 2>&1; then
  set -- uv run --no-project --quiet python3 -E -s "$DIR/guard" "$PROTOCOL"
else
  deny "Blocked by the ai-disclosure hook: it needs python3 to check this GitHub post for an AI disclosure, and this machine has none. Tell the user to install it (macOS: xcode-select --install, Linux: the python3 package of the distro, e.g. apt install python3), then retry. $SKILL $OPT_OUT"
fi

if ! VERDICT="$(printf '%s' "$PAYLOAD" | "$@" 2>/dev/null)"; then
  deny "Blocked by the ai-disclosure hook: its guard failed on this command, so it could not check the GitHub post for an AI disclosure. Tell the user (python3 3.9 or newer is required), then retry. $SKILL $OPT_OUT"
fi
[ -n "$VERDICT" ] && printf '%s\n' "$VERDICT"
exit 0
