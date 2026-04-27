#!/bin/bash
# Git Guardrails — Block dangerous git operations at the harness level.
#
# Event:     PreToolUse
# Matcher:   Bash
# Blocking:  Yes (exit 2 blocks the command)
# Wired:     Yes (universal protection — no configuration needed)
#
# Adapted from mattpocock/skills/git-guardrails-claude-code
# (https://github.com/mattpocock/skills/tree/main/git-guardrails-claude-code)
#
# Blocks (in addition to bash-guard.sh which covers --force/--hard/clean):
#   - git push (any variant) — let the user push manually
#   - git branch -D / --delete -f
#   - git checkout . / git restore . / git checkout -- .
#
# Rationale: prompts cannot reliably enforce git safety; only the harness can.
# When blocked, Claude sees a message and stops — the user runs the command
# manually if intended.

set -euo pipefail

COMMAND=$(jq -r '.tool_input.command')

# Block all git push variants (not just --force).
# Claude does not have authority to push — user runs it manually after review.
if echo "$COMMAND" | grep -qE '(^|[[:space:]]|;|&&|\|\|)git[[:space:]]+push([[:space:]]|$)'; then
  echo "BLOCKED: git push is restricted at the harness level. Ask the user to push manually after they have reviewed the diff and the PR plan." >&2
  exit 2
fi

# Block git branch -D / --delete -f (force-delete branches)
if echo "$COMMAND" | grep -qE 'git[[:space:]]+branch[[:space:]]+(.*[[:space:]])?(-D|--delete[[:space:]]+(-f|--force))'; then
  echo "BLOCKED: git branch -D force-deletes a branch and discards unmerged work. Confirm with the user and use 'git branch -d' (lowercase) for safe deletes only." >&2
  exit 2
fi

# Block git checkout . / git restore . (discard all working-tree changes)
if echo "$COMMAND" | grep -qE 'git[[:space:]]+(checkout[[:space:]]+(--[[:space:]]+)?\.|restore[[:space:]]+\.)([[:space:]]|$)'; then
  echo "BLOCKED: discarding all working-tree changes wipes uncommitted work. Use 'git stash' if you need to set them aside, or 'git checkout -- <specific-file>'." >&2
  exit 2
fi

exit 0
