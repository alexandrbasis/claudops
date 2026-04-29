#!/bin/bash
# Bash Guard — Block dangerous shell commands before execution.
#
# Event:     PreToolUse
# Matcher:   Bash
# Blocking:  Yes (exit 2 blocks the command)
# Wired:     No (project-specific — configure PROTECTED_DIRS and DB patterns first)
#
# Universal rules (always active): destructive rm on root/home/system dirs,
# git destructive ops, force push, clean, pipe-to-shell, download-then-execute,
# bulk deletion via find/xargs, scripts from /tmp, secret-egress (pipe + redirect
# + scp/rsync + cp/mv/dd/install/ditto/tee), eval ANSI-C escape.
# Project-specific rules (configurable): protected directories, database
# commands, test command enforcement.
# Obfuscation hardening: $IFS expansions, ALL quote types (single+double),
# backslash escapes, brackets/parens normalized BEFORE regex matching.
#
# Configuration:
#   PROTECTED_DIRS       — pipe-separated dir names to protect from rm -rf, e.g. "node_modules|src|dist"
#   DB_DANGER_PATTERN    — regex for destructive DB commands, empty to disable
#   DB_SAFE_CMD          — suggested safe alternative for DB changes
#   DB_MIGRATE_PATTERN   — regex for migration commands needing safety flag
#   DB_MIGRATE_SAFE_FLAG — safety flag to suggest
#   TEST_SILENT_PATTERN  — regex for test commands that need silent variant, empty to disable
#   TEST_SILENT_SUFFIX   — suffix to suggest (default: ":silent")
#
# To enable, add to .claude/settings.json hooks.PreToolUse:
#   {
#     "matcher": "Bash",
#     "hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/guards/bash-guard.sh"}]
#   }

set -euo pipefail

# === CONFIGURE FOR YOUR PROJECT (updated by /setup wizard) ===
PROTECTED_DIRS="{{PROTECTED_DIRS}}"              # pipe-separated dirs to protect from rm -rf, e.g. "node_modules|src|dist"
SYSTEM_DIRS="/etc|/var|/usr|/bin|/sbin|/lib|/opt|/Users|/home|/Library|/System|/private|/Volumes|/dev|/boot|/root"
DB_DANGER_PATTERN="{{DB_DANGER_PATTERN}}"        # regex for destructive DB commands, empty to disable
DB_SAFE_CMD="{{DB_SAFE_CMD}}"                    # safe alternative command to suggest
DB_MIGRATE_PATTERN="{{DB_MIGRATE_PATTERN}}"      # regex for migration commands needing safety flag
DB_MIGRATE_SAFE_FLAG="{{DB_MIGRATE_SAFE_FLAG}}"  # safety flag to suggest
TEST_SILENT_PATTERN="{{TEST_SILENT_PATTERN}}"    # regex for test commands that need silent variant, empty to disable
TEST_SILENT_SUFFIX="{{TEST_SILENT_SUFFIX}}"

# --- Read command from stdin ---
COMMAND=$(jq -r '.tool_input.command')

# --- P4-4 + V-R3-7,8 fix: detect ANSI-C escape obfuscation in eval/bash -c/sh -c/zsh -c/printf
# BEFORE NORM strips backslashes. Generalized from `eval` only to all common shell-evaluation
# entry points; also catches an ANSI-C string piped to a shell.
if echo "$COMMAND" | grep -qE "(eval|(bash|sh|zsh)[[:space:]]+-c|printf[[:space:]])[[:space:]]*\\\$'[^']*\\\\(x[0-9a-fA-F]{2}|[0-7]{3}|u[0-9a-fA-F]{4})"; then
  echo "BLOCKED: ANSI-C escape sequences (\\xNN, \\NNN, \\uNNNN) in eval/bash -c/sh -c/zsh -c/printf — likely obfuscation. Run the command directly." >&2
  exit 2
fi
if echo "$COMMAND" | grep -qE "\\\$'[^']*\\\\(x[0-9a-fA-F]{2}|[0-7]{3}|u[0-9a-fA-F]{4})[^']*'.*\\|[[:space:]]*(bash|sh|zsh)([[:space:]]|$)"; then
  echo "BLOCKED: ANSI-C escape string piped to a shell — likely obfuscation." >&2
  exit 2
fi

# --- Normalize obfuscation tricks before regex matching ---
# - \${IFS}, \$IFS expansions   → single space (V1 fix)
# - All quotes (single+double)  → stripped (P4-3 fix; collapses 'cmd', "cmd", c""md → cmd)
# - Backslash escapes           → stripped (\cmd → cmd)
# - Parens/brackets/braces      → spaces (so wrapper(cmd) becomes wrapper cmd — boundary intact)
NORM_COMMAND=$(printf '%s' "$COMMAND" \
    | sed -E 's/\$\{IFS[^}]*\}/ /g' \
    | sed -E 's/\$IFS/ /g' \
    | tr -d '\\' \
    | tr -d '"' \
    | tr -d "'" \
    | tr '(){}[],' ' ')

# ============================================================
# UNIVERSAL RULES (always active, not configurable)
# ============================================================

# Block destructive rm on root or home directory
if echo "$NORM_COMMAND" | grep -qE 'rm[[:space:]]+(-[a-zA-Z]*[rRfF][a-zA-Z]*)+[[:space:]]+(\/|~)[[:space:]]*$'; then
  echo "BLOCKED: rm targets root or home directory." >&2
  exit 2
fi

# Block destructive rm on current directory
if echo "$NORM_COMMAND" | grep -qE 'rm[[:space:]]+(-[a-zA-Z]*[rRfF][a-zA-Z]*)+[[:space:]]+\.[[:space:]]*$'; then
  echo "BLOCKED: rm targets current directory." >&2
  exit 2
fi

# Block rm targeting critical system directories (V2 fix).
# After P4-3 NORM strips quotes and brackets, python -c "os.system('rm -rf /etc')"
# becomes "python -c os.system rm -rf /etc" — rm is space-bounded and V2 catches it.
if echo "$NORM_COMMAND" | grep -qE "(^|[[:space:]&|;])rm[[:space:]]+(-[^[:space:]]+[[:space:]]+)*($SYSTEM_DIRS)([[:space:]]|/|$)"; then
  echo "BLOCKED: rm targets critical system directory. Refusing for safety." >&2
  exit 2
fi

# V-R3-1 fix: rm targeting $HOME / ${HOME} / ~/path — V2 only catches literal /Users|/home,
# but $HOME expands at runtime and obfuscates the same destination.
if echo "$NORM_COMMAND" | grep -qE "(^|[[:space:]&|;])rm[[:space:]]+(-[^[:space:]]+[[:space:]]+)*(\\\$HOME|\\\$\{HOME\}|~)/"; then
  echo "BLOCKED: rm targets \$HOME (env-var expansion). Use a literal path scoped under the project, not the user's home." >&2
  exit 2
fi

# Block git hard reset
if echo "$NORM_COMMAND" | grep -qE 'git[[:space:]]+reset[[:space:]]+--hard'; then
  echo "BLOCKED: git hard reset discards all uncommitted changes. Use 'git stash' to save changes first." >&2
  exit 2
fi

# Block git force push (allow --force-with-lease)
if echo "$NORM_COMMAND" | grep -qE 'git[[:space:]]+push[[:space:]]+.*(-f|--force)([[:space:]]|$)' \
   && ! echo "$NORM_COMMAND" | grep -qE -- '--force-with-lease'; then
  echo "BLOCKED: git force push can overwrite remote history. Use --force-with-lease for safer operation." >&2
  exit 2
fi

# Block git clean -fd / -fx
if echo "$NORM_COMMAND" | grep -qE 'git[[:space:]]+clean[[:space:]]+.*-[a-z]*[fx]'; then
  echo "BLOCKED: git clean permanently removes untracked files. Use 'git clean -n' to preview first." >&2
  exit 2
fi

# Block pipe-to-shell patterns (curl|sh, wget|bash)
if echo "$NORM_COMMAND" | grep -qE '(curl|wget)[[:space:]].*\|[[:space:]]*(sh|bash|zsh)'; then
  echo "BLOCKED: Piping remote content to shell is dangerous. Download first, review, then execute." >&2
  exit 2
fi

# Block download-then-execute pattern (V4 fix)
if echo "$NORM_COMMAND" | grep -qE '(curl|wget).*-(o|O)[[:space:]]+/tmp/' \
   && echo "$NORM_COMMAND" | grep -qE '(^|[[:space:]&|;])(bash|sh|zsh)[[:space:]]+/tmp/'; then
  echo "BLOCKED: Download-then-execute pattern detected. Download, inspect, then execute manually." >&2
  exit 2
fi

# Block executing scripts from /tmp directly (general hardening, broader than V4)
if echo "$NORM_COMMAND" | grep -qE '(^|[[:space:]&|;])(bash|sh|zsh)[[:space:]]+/tmp/'; then
  echo "BLOCKED: Executing scripts from /tmp/ — typically a download-then-execute pattern. Inspect the script first." >&2
  exit 2
fi

# DG1 + P4-6 (pipe form): credential read + pipe to network tool incl scp/rsync/sftp/ftp
if echo "$NORM_COMMAND" | grep -qE '(\.env|\.aws|\.ssh|/credentials|/secrets|id_rsa|id_ed25519|\.pem|\.gnupg|\.kube/config|\.docker/config)' \
   && echo "$NORM_COMMAND" | grep -qE '\|[[:space:]]*(curl|wget|nc|netcat|httpie|scp|rsync|sftp|ftp)'; then
  echo "BLOCKED: Credential file content piped to a network tool — likely exfiltration." >&2
  exit 2
fi

# P4-5 + V-R3-2 fix: credential file redirected to outside project root (cat .env > /tmp/exfil).
# V-R3-2 adds /Users/, $HOME, ${HOME} — multi-user macOS allows staging to another user's homedir.
if echo "$NORM_COMMAND" | grep -qE '(\.env|\.aws|\.ssh|/credentials|/secrets|id_rsa|id_ed25519|\.pem|\.gnupg)' \
   && echo "$NORM_COMMAND" | grep -qE "(>|>>)[[:space:]]*(/tmp/|/var/|/Users/|\\\$HOME|\\\$\{HOME\}|~/|/dev/(stdout|stderr)|/Volumes/)"; then
  echo "BLOCKED: Credential file content redirected outside project — potential exfiltration staging." >&2
  exit 2
fi

# P4-6 fix: standalone scp/rsync/sftp/ftp with credential paths in args
if echo "$NORM_COMMAND" | grep -qE '(^|[[:space:]&|;])(scp|rsync|sftp|ftp)[[:space:]].*(\.env|\.aws|\.ssh|/credentials|/secrets|id_rsa|id_ed25519|\.pem|\.gnupg)'; then
  echo "BLOCKED: Credential file in scp/rsync/sftp/ftp argument — likely exfiltration." >&2
  exit 2
fi

# Block bulk deletion via find -delete / find -exec rm / xargs rm (V5 fix)
if echo "$NORM_COMMAND" | grep -qE 'find[[:space:]].*-delete([[:space:]]|$)'; then
  echo "BLOCKED: 'find -delete' performs bulk deletion. Review the find query and use rm explicitly." >&2
  exit 2
fi
if echo "$NORM_COMMAND" | grep -qE 'find[[:space:]].*-exec[[:space:]]+rm([[:space:]]|$)'; then
  echo "BLOCKED: 'find -exec rm' performs bulk deletion. Review and use rm explicitly." >&2
  exit 2
fi
if echo "$NORM_COMMAND" | grep -qE 'xargs[[:space:]]+(-[a-zA-Z]+[[:space:]]+)*rm([[:space:]]|$)'; then
  echo "BLOCKED: 'xargs rm' performs bulk deletion. Review explicitly." >&2
  exit 2
fi

# V-R4 fix: cp/mv/dd/install/ditto/tee with credential file + outside-project destination.
# These tools use positional args (cp/mv/dd/install/ditto) or pipe-write (tee), so they
# don't trip the `>` redirect rule (P4-5) or the network-tool keyword list (P4-6/DG1).
# Fires only when all three present: tool keyword + cred file + outside-project path —
# preserves within-project ops like `cp .env .env.bak` or `cat .env | tee .env.bak`.
if echo "$NORM_COMMAND" | grep -qE '(^|[[:space:]&|;])(cp|mv|dd|install|ditto)[[:space:]]|\|[[:space:]]*tee[[:space:]]' \
   && echo "$NORM_COMMAND" | grep -qE '(\.env|\.aws|\.ssh|/credentials|/secrets|id_rsa|id_ed25519|\.pem|\.gnupg)' \
   && echo "$NORM_COMMAND" | grep -qE "(/tmp/|/var/|/Users/|\\\$HOME|\\\$\{HOME\}|~/|/Volumes/)"; then
  echo "BLOCKED: Credential file in cp/mv/dd/install/ditto/tee with outside-project destination — likely exfiltration." >&2
  exit 2
fi

# ============================================================
# PROJECT-SPECIFIC RULES (configurable via constants above)
# ============================================================

# Rule: rm -rf on protected directories
if [ -n "$PROTECTED_DIRS" ]; then
  if echo "$NORM_COMMAND" | grep -qE 'rm[[:space:]]+(-[a-zA-Z]*[rRfF][a-zA-Z]*)+[[:space:]]' && echo "$NORM_COMMAND" | grep -qE "($PROTECTED_DIRS)"; then
    echo "BLOCKED: rm -rf targets protected directory. Use 'mv <path> ~/.Trash/' instead." >&2
    exit 2
  fi
fi

# Rule: destructive database commands
if [ -n "$DB_DANGER_PATTERN" ]; then
  if echo "$NORM_COMMAND" | grep -qE "$DB_DANGER_PATTERN"; then
    echo "BLOCKED: Destructive database command. Use: $DB_SAFE_CMD" >&2
    exit 2
  fi
fi

# Rule: database migration without safe flag
if [ -n "$DB_MIGRATE_PATTERN" ]; then
  if echo "$NORM_COMMAND" | grep -qE "$DB_MIGRATE_PATTERN" && ! echo "$NORM_COMMAND" | grep -q "$DB_MIGRATE_SAFE_FLAG"; then
    echo "BLOCKED: Database migration without $DB_MIGRATE_SAFE_FLAG. Use: $DB_SAFE_CMD" >&2
    exit 2
  fi
fi

# Rule: test command enforcement (require silent variant)
if [ -n "$TEST_SILENT_PATTERN" ]; then
  if echo "$NORM_COMMAND" | grep -qE "$TEST_SILENT_PATTERN" && ! echo "$NORM_COMMAND" | grep -q "$TEST_SILENT_SUFFIX"; then
    echo "BLOCKED: Use silent test variant. Add '$TEST_SILENT_SUFFIX' to the test command." >&2
    exit 2
  fi
fi

exit 0
