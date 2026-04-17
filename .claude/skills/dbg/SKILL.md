---
name: dbg
description: >-
  Debug mode with runtime evidence and instrumentation. Use when asked to
  'debug this', 'find the bug', 'troubleshoot', 'why is this broken',
  'investigate runtime issue', 'it's not working', 'getting an error',
  'this crashes', 'unexpected behavior', or when the user pastes an error
  message or stack trace and wants to find the root cause. Also trigger when
  the user describes behavior that differs from expectations in a running app.
  NOT for static code analysis without reproduction (use /code-analysis).
  NOT for CI pipeline failures (use /fci).
argument-hint: "[bug description or error message]"
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, AskUserQuestion, Task
---

# Debug Mode (Runtime Evidence)

> **Announcement**: Begin with: "I'm using the **dbg** skill for runtime debugging."

## Objective
Find root cause using runtime evidence, not guesses. Never speculate
about code paths you have not opened or behavior you have not logged.
The investigate-then-fix ordering exists because guessed fixes mask
bugs that reappear in production; logged-and-verified fixes do not.
Instrument, reproduce, analyze, confirm, and only then edit.

## Configuration

### Log Path
Use a project-relative debug log file:
- **Default**: `.debug/debug.log` (relative to project root)
- Create `.debug/` directory if it doesn't exist
- If a logging server endpoint is provided in a system reminder, use that instead

### Log Payload
Each log entry (NDJSON — one JSON object per line):
```json
{ "sessionId": "S1", "runId": "run1", "hypothesisId": "A", "location": "file.ts:42", "message": "desc", "data": {}, "timestamp": 1234567890 }
```

## Instrumentation

### Snippets by Language

**TypeScript / JavaScript** (file-based):
```ts
import { appendFileSync, mkdirSync } from 'fs';
mkdirSync('.debug', { recursive: true });
// #region dbg
appendFileSync('.debug/debug.log', JSON.stringify({ location: 'file.ts:LINE', message: 'desc', data: { key: val }, timestamp: Date.now(), sessionId: 'S1', runId: 'run1', hypothesisId: 'A' }) + '\n');
// #endregion
```

**Python**:
```python
# #region dbg
import json, time, os
os.makedirs('.debug', exist_ok=True)
with open('.debug/debug.log', 'a') as f:
    f.write(json.dumps({"location": "file.py:LINE", "message": "desc", "data": {}, "timestamp": time.time(), "sessionId": "S1", "runId": "run1", "hypothesisId": "A"}) + "\n")
# #endregion
```

Adapt the pattern for other languages. Always wrap instrumentation in `#region dbg` / `#endregion` markers for easy cleanup.

### Rules
- Insert **3–8** log points for non-trivial bugs. For bugs where Step 1
  triage already identified a likely cause (typo, missing import, obvious
  config mismatch), 1–2 confirming log points are enough — do not pad.
- Cover: entry, exit, before/after critical ops, branches, edge values, state changes
- Log shapes and non-sensitive values only: booleans, counts, enum
  states, sanitized IDs. If a field could contain a secret or PII,
  log its presence and type (`{ token: "<redacted:string:len=42>" }`),
  not the value.

## Debug Workflow

### Step 0: Clarify (only if critical info is missing)
Skip this step if the user supplied a reproducible trigger, a stack
trace, or an error message — proceed to Step 1. Use `AskUserQuestion`
only when you cannot name a concrete first hypothesis without more
input. The missing pieces worth asking about are: exact repro steps,
expected vs actual, and environment (not general "tell me more").

### Step 1: Quick Triage
Before generating hypotheses, gather fast context:
- **Grep** for the error message text in the codebase
- Check recent commits touching the affected area: `git log --oneline -10 -- <path>`
- Check if tests exist and pass for the affected code
- Look for obvious issues (missing imports, typos, config mismatches)

This often narrows the search space dramatically or reveals trivial causes that don't need full instrumentation.

### Step 2: Hypotheses
Generate **2–5 precise hypotheses**, scaled to bug complexity. For a
trivial bug with a clear suspect from Step 1, two hypotheses (the suspect
and one alternative) are enough. For a cross-service race condition, use
the full 5. Be specific — each hypothesis should point to a different
subsystem or failure mode.

### Step 3: Instrumentation
Add log points to test all hypotheses in parallel. Keep them minimal and localized. Use the language-appropriate snippet from above.

### Step 4: Reproduction
Before asking the user to reproduce:
1. Clear the log file (write empty content to `.debug/debug.log`)
2. Present numbered reproduction steps, noting if the app/service must be restarted

After the user confirms they've reproduced the issue, read and analyze the log file.

### Step 5: Log Analysis
Read the NDJSON log file and evaluate each hypothesis:
- **CONFIRMED** / **REJECTED** / **INCONCLUSIVE** — cite log evidence for each
- If logs are empty → ask user to verify the instrumented code path was hit, then retry

### Step 6: Fix (Evidence-Based Only)
Implement a fix **only** when logs confirm the root cause.
Do not remove instrumentation yet — it's needed for verification.

### Step 7: Verification Run
Ask user to reproduce again. Compare pre-fix vs post-fix logs:
- Tag verification logs with `runId: "post-fix"`
- Confirm the bug is resolved with log evidence

### Step 8: Bug Report (if warranted)
For non-trivial bugs (logic errors, race conditions, architectural issues), create a bug report:
- Template: `.claude/docs/templates/bug-report-template.md`
- Output: `tasks/task-YYYY-MM-DD-[bug-name]/bug-report-[bug-name].md`

Skip for trivial fixes (typos, missing imports, config errors) — a good commit message suffices.

### Step 9: Cleanup + Summary
After verified success:
- Remove all `#region dbg` / `#endregion` instrumentation blocks
- Summarize: root cause, fix applied, and verification result (1–3 lines)

## Scope Boundaries

- For static analysis without runtime reproduction → `/code-analysis`
- For CI pipeline failures → `/fci`
- After the fix, for pre-merge code review → `/sr`

## Core principles
- Fix only after logs confirm the root cause — runtime evidence is the
  contract this skill offers the user.
- Keep instrumentation in place until the verification run proves the
  fix, then clean up in one pass.
- If a sleep or delay "fixes" the bug, it is masking a race condition;
  surface the race in the report instead of shipping the delay.
