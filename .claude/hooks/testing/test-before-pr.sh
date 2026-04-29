#!/bin/bash
# Test Before PR — Block PR creation unless tests (and optionally build) pass.
#
# Event:     PreToolUse
# Matcher:   Bash
# Blocking:  Yes (exit 2 blocks the PR creation)
# Wired:     No (project-specific — configure at least one scope first)
#
# Only triggers on commands containing "gh pr create".
# Runs scope-specific test/build checks based on what files the PR touched.
# Skips a scope if no files in that scope changed (avoids false-positive
# blocks — e.g. a docs-only PR no longer triggers backend tests).
#
# === HOW THE TWO-SCOPE MODEL WORKS ===
# This template ships with TWO independent scopes (BACKEND, MOBILE) you can
# wire to different parts of a monorepo. Each scope has three settings:
#   <SCOPE>_PATH_FILTER  — egrep regex matched against `git diff --name-only
#                          $BASE_REF...HEAD` paths. If no changed file matches,
#                          the scope is skipped entirely. Use '.*' to always run.
#   <SCOPE>_TEST_CMD     — shell command run from the project root via `eval`.
#                          Empty string = skip tests for this scope.
#   <SCOPE>_BUILD_CMD    — optional build/typecheck (e.g. `tsc --noEmit`).
#                          Empty string = skip build for this scope.
#
# Single-app projects? Use BACKEND only and leave the MOBILE_* values empty
# (set MOBILE_TEST_CMD="" and MOBILE_BUILD_CMD="") — the scope short-circuits.
# More than two scopes? Duplicate the run_scope call at the bottom and add a
# matching 3-line config block above.
#
# === EXAMPLES ===
# Single Node project (no monorepo):
#   BACKEND_PATH_FILTER='.*'
#   BACKEND_TEST_CMD='npm run test:silent'
#   BACKEND_BUILD_CMD='npx tsc --noEmit'
#   MOBILE_PATH_FILTER=''
#   MOBILE_TEST_CMD=''
#   MOBILE_BUILD_CMD=''
#
# Backend + mobile monorepo:
#   BACKEND_PATH_FILTER='^backend/'
#   BACKEND_TEST_CMD='cd backend && npm run test:silent'
#   BACKEND_BUILD_CMD='cd backend && npx tsc --noEmit'
#   MOBILE_PATH_FILTER='^mobile-app/'
#   MOBILE_TEST_CMD='cd mobile-app && npm test -- --silent'
#   MOBILE_BUILD_CMD='cd mobile-app && npx tsc --noEmit'
#
# Python + Go services:
#   BACKEND_PATH_FILTER='^api/.*\.py$'
#   BACKEND_TEST_CMD='cd api && pytest -q'
#   BACKEND_BUILD_CMD=''
#   MOBILE_PATH_FILTER='^worker/.*\.go$'
#   MOBILE_TEST_CMD='cd worker && go test ./...'
#   MOBILE_BUILD_CMD='cd worker && go build ./...'
#
# === RUNTIME ENV VARS ===
#   SKIP_TEST_BEFORE_PR=true  — bypass entirely (use sparingly, for WIP PRs)
#   TEST_BEFORE_PR_BASE       — git ref to diff against (default: origin/main)
#
# To enable, add to .claude/settings.json hooks.PreToolUse:
#   {
#     "matcher": "Bash",
#     "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/testing/test-before-pr.sh", "timeout": 300}]
#   }

set -euo pipefail

# === CONFIGURE FOR YOUR PROJECT (updated by /setup wizard) ===
# Scope 1 (typically backend or main service)
BACKEND_PATH_FILTER='{{BACKEND_PATH_FILTER}}'   # e.g. '^backend/' or '.*' for single-app projects
BACKEND_TEST_CMD='{{BACKEND_TEST_CMD}}'         # e.g. 'cd backend && npm run test:silent' (empty = skip tests)
BACKEND_BUILD_CMD='{{BACKEND_BUILD_CMD}}'       # e.g. 'cd backend && npx tsc --noEmit' (empty = skip build)

# Scope 2 (typically mobile/frontend; leave all three empty to disable)
MOBILE_PATH_FILTER='{{MOBILE_PATH_FILTER}}'     # e.g. '^mobile-app/' (empty = scope disabled)
MOBILE_TEST_CMD='{{MOBILE_TEST_CMD}}'           # e.g. 'cd mobile-app && npm test -- --silent' (empty = skip tests)
MOBILE_BUILD_CMD='{{MOBILE_BUILD_CMD}}'         # e.g. 'cd mobile-app && npx tsc --noEmit' (empty = skip build)

# --- Allow bypass via env var ---
if [ "${SKIP_TEST_BEFORE_PR:-false}" = "true" ]; then
  exit 0
fi

# --- Only trigger on gh pr create ---
COMMAND=$(jq -r '.tool_input.command // ""')
if ! echo "$COMMAND" | grep -q 'gh pr create'; then
  exit 0
fi

# --- Determine changed files (against the merge base with origin/main) ---
# Three-dot syntax = diff between merge-base(origin/main, HEAD) and HEAD,
# i.e. "what this branch has changed since it diverged from main".
# Falls back to working-tree diff if origin/main is unreachable.
BASE_REF="${TEST_BEFORE_PR_BASE:-origin/main}"
CHANGED_FILES=$(git diff --name-only "${BASE_REF}...HEAD" 2>/dev/null \
                || git diff --name-only HEAD 2>/dev/null \
                || true)

if [ -z "$CHANGED_FILES" ]; then
  echo "[test-before-pr] No changed files detected vs $BASE_REF — running ALL configured scopes." >&2
  CHANGED_FILES_FALLBACK=true
else
  CHANGED_FILES_FALLBACK=false
fi

# --- Per-scope runner ---
# Returns 0 (pass / skipped) or 2 (blocked).
run_scope() {
  local name="$1" filter="$2" test_cmd="$3" build_cmd="$4"

  # Scope is fully disabled when nothing is configured to run
  if [ -z "$test_cmd" ] && [ -z "$build_cmd" ]; then
    return 0
  fi

  # Skip scope if its filter doesn't match any changed file (and we have a diff)
  if [ "$CHANGED_FILES_FALLBACK" != "true" ] && [ -n "$filter" ]; then
    if ! echo "$CHANGED_FILES" | grep -qE "$filter"; then
      echo "[test-before-pr] $name: no changed files match '$filter' — skipping." >&2
      return 0
    fi
  fi

  if [ -n "$test_cmd" ]; then
    echo "[test-before-pr] $name: running tests ($test_cmd)..." >&2
    if ! eval "$test_cmd" 2>&1 | tail -20; then
      echo "BLOCKED: $name tests are failing. Fix all test failures before creating a PR." >&2
      return 2
    fi
  fi

  if [ -n "$build_cmd" ]; then
    echo "[test-before-pr] $name: running build/typecheck ($build_cmd)..." >&2
    if ! eval "$build_cmd" 2>&1 | tail -10; then
      echo "BLOCKED: $name build/typecheck is failing. Fix before creating a PR." >&2
      return 2
    fi
  fi

  return 0
}

run_scope "BACKEND" "$BACKEND_PATH_FILTER" "$BACKEND_TEST_CMD" "$BACKEND_BUILD_CMD" || exit $?
run_scope "MOBILE"  "$MOBILE_PATH_FILTER"  "$MOBILE_TEST_CMD"  "$MOBILE_BUILD_CMD"  || exit $?

echo "[test-before-pr] All applicable checks passed. Proceeding with PR creation." >&2
exit 0
