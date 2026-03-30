---
name: quick
description: >-
  Quick implementation for small tasks without ceremony. Use when asked to 'quick fix',
  'just do it', 'small change', 'quick task', or when the change touches fewer than 5
  files and doesn't need formal planning.
  NOT for new features (use /ct + /si), NOT for tasks needing Linear tracking.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /quick — Lightweight Task Mode

> **Announcement**: Begin with: "I'm using the **quick** skill for a lightweight task."

Fast-path implementation with quality checks but no ceremony.

## When to Use
- Bug fixes with known root cause
- Config changes, env updates
- Small refactors (rename, extract, inline)
- Adding a validation rule, fixing a query
- Anything that touches **<5 files** and has **clear scope**

## When NOT to Use (redirect)
- New feature or module → `/ct` + `/si`
- Change needs Linear tracking → `/ct` + `/si`
- Change touches >5 files → `/ct` + `/si`
- Unclear scope or multiple approaches → `/brainstorm` or `/nf`

---

## Workflow

### STEP 1: Scope Gate
Before starting, verify this is truly a quick task:
- Count expected files to change. If >5, suggest `/ct` + `/si` instead.
- If the change requires a new module/service/table, suggest `/ct` + `/si` instead.
- If the user insists, proceed — but note the risk.

### STEP 2: Quick Plan
State in **3-5 bullet points** what will change:
```
Quick plan:
- Fix: [what's wrong / what needs to change]
- Files: [list of files to modify]
- Test: [how to verify it works]
```

Get user confirmation before proceeding.

### STEP 3: Implement
- Make changes directly — no task document needed
- **Follow TDD for any logic changes** (same bright-line rules as /si):
  - Write a FAILING test first that specifies the expected behavior
  - If you wrote production code before a failing test: delete it and restart with RED
  - Implement the minimal fix to make the test pass (GREEN)
  - Verify test passes: `npm run test:unit:silent`
  - "Tests after" is not TDD — it produces confirmation tests, not specification tests
- For non-logic changes (config, docs, formatting): just make the change

### STEP 4: Verify
Run quality checks from the appropriate directory:

**Backend changes:**
```bash
cd backend && npm run format:check && npm run lint:check && npx tsc --noEmit && npm run test:unit:silent
```

**Mobile app changes:**
```bash
cd mobile-app && npx tsc --noEmit
```

If any check fails, fix it before proceeding.

**Evidence requirement**: Do not claim the task is done without running these checks and confirming they pass. The `stop-verification-evidence` hookify rule enforces this.

### STEP 4.5: De-Sloppify (if logic changes were made)
If STEP 3 included logic changes (not just config/docs), run a quick de-sloppify pass:
1. Identify changed files: `git diff --name-only`
2. Run `/simplify` skill (`Skill tool → skill: "simplify"`) — it reviews changed files for slop: console.logs from debugging, commented-out code, redundant defensive checks, dead imports. Removes them without refactoring logic.
3. If fixes applied, re-run STEP 4 verification checks.

### STEP 5: Commit
Ask user permission, then create a single conventional commit:
```
<type>(<scope>): <summary>
```

Types: `fix`, `refactor`, `chore`, `docs`, `test`

---

## What /quick Does NOT Do
- Create task documents
- Create Linear issues
- Run review agents
- Create PRs (user can do this separately or ask)
- Update ROADMAP/STATE files

## Guardrails

Follow the shared reference: `.claude/docs/references/deviation-rules.md`

This covers: auto-fix vs ask matrix, 3-attempt limit, scope boundaries, and paralysis guard rules.
