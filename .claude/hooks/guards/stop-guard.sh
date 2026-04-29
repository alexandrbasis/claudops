#!/bin/bash
# Stop Verification — Remind to verify work before ending a session.
#
# Event:     Stop
# Matcher:   (none)
# Blocking:  Yes (exit 2 blocks the first stop, fires once per 24h per session)
# Wired:     No (project-specific — configure verification steps for your stack)
#
# Fires once per session (24h TTL, signed with session_id to prevent pre-touch
# bypass — V14 fix). Reminds the agent to verify that files exist, tests pass,
# build succeeds, and (optionally) wiki is up to date before stopping.
#
# Suppresses the test/build reminder when the working tree has no source-code
# changes — addresses noisy reminders on docs-only or config-only work.
#
# === CONFIGURATION ===
#   VERIFY_FILES         — true/false: remind to ls each created/modified file
#   VERIFY_TESTS         — true/false: remind to run tests
#   VERIFY_BUILD         — true/false: remind to check build/typecheck
#   VERIFY_WIKI          — true/false: remind /wiki-update if wiki-relevant paths changed
#   TEST_CMD             — test command to suggest (e.g. 'npm run test:ci 2>&1 | tail -20')
#   BUILD_CMD            — build command to suggest (e.g. 'npx tsc --noEmit 2>&1 | tail -20')
#   CODE_CHANGE_PATTERN  — egrep regex; tests/build reminder fires only if the working
#                          tree has uncommitted changes matching this pattern. Use '.*'
#                          to always remind. Examples:
#                            single Node app:  '\.(ts|tsx|js|jsx)$'
#                            backend monorepo: '^backend/.*\.(ts|tsx|prisma)$'
#                            python service:   '\.py$'
#   WIKI_PATHS           — space-separated path prefixes that trigger the wiki reminder
#                          when changes touch them. Empty = wiki reminder always fires
#                          (when VERIFY_WIKI=true). Example: 'src docs/adr docs/architecture'
#
# To enable, add to .claude/settings.json hooks.Stop:
#   {
#     "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/guards/stop-guard.sh"}]
#   }

# === CONFIGURE FOR YOUR PROJECT (updated by /setup wizard) ===
VERIFY_FILES=true
VERIFY_TESTS=true
VERIFY_BUILD=true
VERIFY_WIKI=false                                 # set true once you have a /wiki-update workflow
TEST_CMD="{{STOP_TEST_CMD}}"                      # e.g. 'cd backend && npm run test:ci 2>&1 | tail -20'
BUILD_CMD="{{STOP_BUILD_CMD}}"                    # e.g. 'cd backend && npx tsc --noEmit 2>&1 | tail -20'
CODE_CHANGE_PATTERN="{{CODE_CHANGE_PATTERN}}"     # e.g. '\.(ts|tsx|js|jsx|py)$' — empty falls back to ".*"
WIKI_PATHS="{{WIKI_PATHS}}"                       # e.g. 'docs/adr docs/architecture' — empty = always remind

# --- Smart pre-condition: suppress test/build reminders when no code changed ---
# Only flips VERIFY_TESTS / VERIFY_BUILD off when the working tree has no
# uncommitted/staged changes matching CODE_CHANGE_PATTERN. Wiki check (below)
# and file-existence reminder remain unaffected.
EFFECTIVE_PATTERN="${CODE_CHANGE_PATTERN:-.*}"
CODE_CHANGED=false
if git diff --name-only HEAD 2>/dev/null | grep -qE "$EFFECTIVE_PATTERN" \
   || git diff --name-only --cached 2>/dev/null | grep -qE "$EFFECTIVE_PATTERN"; then
  CODE_CHANGED=true
fi
if [ "$CODE_CHANGED" = false ]; then
  VERIFY_TESTS=false
  VERIFY_BUILD=false
fi

# --- Once-per-session: skip if already fired in this session (V14 fix — pre-touch bypass) ---
# State file content: <session_id>:<timestamp>. Pre-touching the file with
# arbitrary content fails the session_id match and the guard fires anyway.
STATE_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/logs"
STATE_FILE="$STATE_DIR/.stop-guard-fired"

# Parse session_id from stdin JSON (Stop event provides session_id per docs)
INPUT=$(cat 2>/dev/null || true)
SESSION_ID=$(printf '%s' "$INPUT" | jq -r '.session_id // ""' 2>/dev/null || true)

if [ -f "$STATE_FILE" ] && [ -n "$SESSION_ID" ]; then
  STORED=$(head -n 1 "$STATE_FILE" 2>/dev/null)
  STORED_SID=$(printf '%s' "$STORED" | cut -d: -f1)
  STORED_TS=$(printf '%s' "$STORED" | cut -d: -f2)
  if [ "$STORED_SID" = "$SESSION_ID" ] && [ -n "$STORED_TS" ]; then
    NOW=$(date +%s)
    AGE=$(( NOW - STORED_TS ))
    if [ "$AGE" -lt 86400 ]; then
      exit 0
    fi
  fi
fi

# Mark as fired (with session signature to prevent pre-touch bypass)
mkdir -p "$STATE_DIR"
echo "${SESSION_ID:-unknown}:$(date +%s)" > "$STATE_FILE"

# --- Build verification message ---
echo "VERIFICATION CHECK: Before stopping, confirm your claims:" >&2

STEP=1
if [ "$VERIFY_FILES" = true ]; then
  echo "$STEP. Files exist: ls <file> for every file you created/modified" >&2
  STEP=$((STEP + 1))
fi
if [ "$VERIFY_TESTS" = true ]; then
  echo "$STEP. Tests pass: $TEST_CMD — confirm exit code 0" >&2
  STEP=$((STEP + 1))
fi
if [ "$VERIFY_BUILD" = true ]; then
  echo "$STEP. Build succeeds: $BUILD_CMD" >&2
  STEP=$((STEP + 1))
fi
if [ "$VERIFY_WIKI" = true ]; then
  # Check if any wiki-relevant path changed; empty WIKI_PATHS = always remind.
  WIKI_CHANGED=false
  if [ -z "$WIKI_PATHS" ]; then
    WIKI_CHANGED=true
  else
    for WPATH in $WIKI_PATHS; do
      if git diff --name-only HEAD 2>/dev/null | grep -q "^$WPATH" \
         || git diff --name-only --cached 2>/dev/null | grep -q "^$WPATH"; then
        WIKI_CHANGED=true
        break
      fi
    done
  fi
  if [ "$WIKI_CHANGED" = true ]; then
    echo "$STEP. Wiki may be stale: wiki-relevant files changed. Run /wiki-update to sync, or skip if changes are trivial." >&2
  fi
fi

exit 2
