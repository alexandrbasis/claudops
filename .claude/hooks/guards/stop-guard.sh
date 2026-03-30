#!/bin/bash
# Guard: stop-time verification checks (once per session, 24h TTL)
# Replaces hookify rules: stop-verification-evidence, stop-uncommitted
STATE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/logs"
STATE_FILE="$STATE_DIR/.stop-guard-fired"

# Once-per-session: skip if already fired within 24h
if [ -f "$STATE_FILE" ]; then
  FILE_AGE=$(( $(date +%s) - $(stat -f %m "$STATE_FILE" 2>/dev/null || echo 0) ))
  if [ "$FILE_AGE" -lt 86400 ]; then
    exit 0
  fi
fi

# Mark as fired
mkdir -p "$STATE_DIR"
touch "$STATE_FILE"

# Rule: stop-verification-evidence — block until verified
echo "VERIFICATION CHECK: Before stopping, confirm your claims:" >&2
echo "1. Files exist: ls <file> for every file you created/modified" >&2
echo "2. Tests pass: run the test command, confirm exit code 0" >&2
echo "3. Build succeeds: npx tsc --noEmit if you changed TypeScript" >&2
exit 2
