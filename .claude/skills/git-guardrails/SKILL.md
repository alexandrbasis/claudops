---
name: git-guardrails
description: >-
  Inspect, install, customize, or troubleshoot the harness-level git safety
  hook that blocks dangerous git operations (push, branch -D, checkout .)
  before they execute. Use when the user wants to change which git commands
  are blocked, verify the guard is wired up, or set it up after a fresh clone.
disable-model-invocation: true
---

# Git Guardrails

> **Status: DISABLED.** The hook script exists at `.claude/hooks/guards/git-guardrails.sh` but is **not wired** into `settings.json`. It does nothing until re-enabled. See "Re-enable" below.

> **Upstream**: Adapted from [mattpocock/skills/git-guardrails-claude-code](https://github.com/mattpocock/skills/tree/main/git-guardrails-claude-code). Implements harness-level git safety — prompts cannot reliably enforce this, only PreToolUse hooks can.

This skill manages the git-safety hook at `.claude/hooks/guards/git-guardrails.sh`.

## Re-enable

Add the following entry to the `Bash`-matcher hooks array in `.claude/settings.json` under `hooks.PreToolUse`:

```json
{
  "type": "command",
  "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/guards/git-guardrails.sh"
}
```

Place it first in the array for fail-fast (so dangerous commands are rejected before logging/validation hooks fire). Remove the DISABLED banner at the top of the script.

## What's blocked

Active out of the box (no configuration needed):

- `git push` — any variant. The user pushes manually after reviewing the diff/PR.
- `git branch -D` / `git branch --delete -f` — force-delete branches discards unmerged work.
- `git checkout .` / `git restore .` / `git checkout -- .` — discarding all working-tree changes.

Already covered by the sibling `bash-guard.sh` (universal rules, always-active section):

- `git reset --hard`
- `git push --force` / `-f` (the `--force` variant — `git-guardrails.sh` blocks the rest)
- `git clean -fd` / `-fx`
- `rm -rf /`, `rm -rf ~`, `rm -rf .`
- `curl | sh` / `wget | bash`

When blocked, Claude sees `BLOCKED: …` on stderr with exit 2 and stops — the user runs the command manually if intended.

## Verify it's wired

```bash
# Should be referenced in PreToolUse → Bash hooks:
jq '.hooks.PreToolUse[] | select(.matcher == "Bash") | .hooks[].command' .claude/settings.json

# Smoke test — should print the BLOCKED message and exit 2:
echo '{"tool_input":{"command":"git push origin main"}}' | .claude/hooks/guards/git-guardrails.sh
echo "exit: $?"   # expect: 2
```

## Add or remove patterns

Edit `.claude/hooks/guards/git-guardrails.sh` directly. Each rule is a `grep -qE` block followed by `echo "BLOCKED: …" >&2; exit 2`. Rules are independent — add or remove freely.

When adding a rule, also add a smoke-test line above and confirm exit 2.

## Removing the guard entirely

1. Edit `.claude/settings.json` and remove the `git-guardrails.sh` entry from `hooks.PreToolUse[*].hooks` where the matcher is `Bash`.
2. The script file can stay on disk — it does nothing without the wire-up.

Don't disable on a whim — every blocked command reflects an incident or a near-miss.

## Why harness-level, not prompt-level

A CLAUDE.md instruction "do not run `git push`" is unreliable: the model can ignore it under pressure, and the user can't audit it. A PreToolUse hook is the only enforcement that actually fires every time. This is a load-bearing safety primitive — keep it.
