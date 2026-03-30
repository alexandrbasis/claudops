# Deviation Rules — Shared Reference

> **Single source of truth** for scope boundaries, auto-fix policies, and attempt limits.
> Referenced by: `/si`, `/quick`, `/parallelization`, `developer-agent`

---

## Auto-Fix vs Ask

While implementing, you WILL discover issues not in the plan. Follow these rules:

### Auto-fix (no permission needed)

- Bugs in code you just wrote (wrong logic, type errors, null pointers)
- Missing input validation or null checks for your code
- Blocking issues (missing imports, wrong dependency versions)
- Security holes in your code (injection, auth bypass)

### Ask the user first

- New database table (not column — columns are auto-fix)
- Major schema changes
- Switching libraries or frameworks
- Breaking API contract changes
- Architectural pattern changes

---

## Scope Boundary

- Only fix issues **DIRECTLY caused by the current task's changes**
- Pre-existing warnings, lint errors, or failures in unrelated files → log to task doc under "Deferred Issues", do NOT fix
- After fixing, always verify the fix doesn't break anything else

---

## Attempt Limit

Track fix attempts per failing test or error:

- After **3 attempts** at the same error with meaningfully different approaches:
  1. STOP trying to fix
  2. Document what was tried and what failed in the task doc
  3. Ask the user: "I've attempted to fix [error] 3 times. Options: (1) Try a different approach, (2) Skip and flag as blocked, (3) You provide guidance"
- Each attempt MUST try a meaningfully different approach. Retrying the same fix is not an attempt.
- Do NOT enter infinite retry loops.

---

## Paralysis Guard

If you make **5+ consecutive Read/Grep/Glob calls without any Edit/Write/Bash action**:
1. STOP exploring
2. State your current understanding in one paragraph
3. State what's blocking you from writing code
4. Either start writing code (you likely have enough context) or ask the user for clarification

The task document is the source of truth. Do not endlessly explore the codebase.
