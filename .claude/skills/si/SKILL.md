---
name: si
description: >-
  Execute structured TDD implementation following task documents or bug fixing.
  Use whenever the user wants to start, continue, or resume implementation from tasks/ directory,
  fix a bug, or says things like 'implement this', 'work on WYT-XX', 'build the feature',
  'start coding', 'pick up where I left off', 'let's implement the task', 'code this up',
  'make it work', 'develop the feature', 'start the task', or references a specific task
  directory or tech-decomposition document. Also use when the user has a tech-decomposition
  ready and wants to begin coding.
argument-hint: [task-directory]
allowed-tools: [Agent, AskUserQuestion, Edit, Read, Write, Bash, Glob, Grep, Skill, TodoWrite]
---

# Start Implementation Command

> **Announcement**: Begin with: "I'm using the **si** skill for structured TDD implementation."

## PRIMARY OBJECTIVE

Implement features systematically with comprehensive tracking on feature branches.

Two primary modes:
1. **Start** — Begin implementation from a task document
2. **Continue** — Resume in-progress implementation

Additionally, a **Bug Fix** path exists for quick fixes without full task ceremony.

For PR review comments, use `/prc` instead. If review feedback requires significant rework needing task-level tracking, update the task document with new requirements and use Continue mode.

## CONSTRAINTS

- Follow existing task document in `tasks/` directory
- Git writes require explicit user permission — accidental commits or pushes disrupt workflow and are hard to undo cleanly. Do **NOT** create commits, push branches, open PRs, merge, rebase, or otherwise modify git state without approval.

---

## STEP 0: Mode Detection

Determine the correct mode before doing anything else.

1. **Resolve the task**: If `$ARGUMENTS` provided, locate it. Otherwise ask: "Which task to implement?"
2. **Read the task document** and check signals:

| Signal | Mode |
|--------|------|
| Status = "Draft"/"Ready for Implementation" + no feature branch | **Start** |
| Status = "In Progress" + feature branch exists + unchecked steps remain | **Continue** |
| No task document, user describes a bug | **Bug Fix** |

3. **Announce**: "Detected mode: **[mode]**. Proceeding."

---

## STEP 1: Task Validation

1. **Validate document**:
   - Confirm task exists (single `.md` file OR `tasks/task-YYYY-MM-DD-slug/` directory)
   - Confirm scope: clear acceptance criteria and "done" definition
   - Confirm task status is appropriate — ask before proceeding if unclear
   - Confirm Linear issue exists and is referenced (ID/link). If no Linear issue, continue with the task document in `tasks/`.
   - Confirm implementation plan exists: impacted components + test plan

---

## STEP 2: Setup

### Start Mode

1. **Update task status** to "In Progress" with timestamp
2. **Update Linear issue** (see `.claude/skills/cc-linear/SKILL.md`):
   ```bash
   .claude/scripts/linear-api.sh update-status WYT-XX "In Progress"
   .claude/scripts/linear-api.sh add-comment WYT-XX "Implementation started. Branch: feature/wyt-XX-slug"
   ```
3. **Create feature branch** (permission gate): `feature/wyt-[ID]-[slug]`
4. **Update task document** with branch name

### Continue Mode: State Recovery

1. **Check for HANDOFF.md**: Look for `HANDOFF.md` in the task directory.
   - **If found**: Load it first. Read the "Files to Read First" section to rebuild context quickly. Use it as the primary state source (it's more current than task doc checkmarks). After successfully resuming, rename to `HANDOFF-[date].md` to archive.
   - **If absent**: Fall back to the standard recovery below.
2. **Switch to feature branch**: Check out the branch referenced in the task doc
3. **State reconciliation**: Verify actual code state matches task doc checkmarks
   - Run `git status` + `git stash list` to detect uncommitted/stashed work
   - If uncommitted changes exist, ask user: "Found uncommitted changes. Stash, commit, or discard?"
   - If stashes exist, ask user if they should be applied
4. **Scan task document**: Identify completed (checked) vs remaining (unchecked) steps
5. **Check test state**: `npm run test:silent` to see current pass/fail
   - If tests fail on checked steps, flag: "Tests failing for previously completed Step [N]. Fix before proceeding?"
6. **Read recent commits**: `git log --oneline -10` to understand prior work
7. **Identify the next unchecked step** in the task document
8. **Announce**: "Resuming at Step [N]: [Description]. Previous steps completed: [list]."

---

## STEP 3: Implementation

### Skill Loading (once, at start of STEP 3)

If the task touches `mobile-app/`:
- Check the task doc for a "Skill Compliance" section (created by `/ct`)
- Load referenced skills (e.g., `react-native-expo-mobile`, `design-tokens`, `component-library`)
- These skills contain patterns that were specified during planning — following them ensures consistency between plan and code

For unfamiliar APIs or patterns, use Agent (Explore) to research before implementing.

### Parallelization (optional)

If work can be done safely in parallel, use `.claude/skills/parallelization/SKILL.md`.

**Wave detection**: Check the task document for wave annotations (e.g., `— **Wave 1**`, `— **Wave 2**`). If present, group steps by wave number and execute all same-wave steps in parallel before advancing to the next wave. If no wave annotations exist, fall back to the decision matrix below.

**When to parallelize:**
- Steps that modify different modules/directories with no shared state
- Independent test suites (e.g., unit tests for different services)
- Steps annotated with the same wave number

**When NOT to:**
- Steps that modify the same files or depend on prior step's output
- Database migrations (order matters)
- Steps that share test fixtures or database state

### Sequential Mode

#### Before Each Step:
1. **Announce**: "Starting Step [N]: [Description]"
2. **Review**: acceptance criteria, tests, artifacts for this step

#### During Implementation (TDD):

Strict TDD catches regressions immediately and documents expected behavior through tests — especially valuable when multiple steps build on each other.

#### TDD Bright-Line Rules (Non-Negotiable)

These rules close known rationalization loopholes. "I'll write tests after" is the most common excuse for skipping TDD — it feels reasonable but systematically produces weaker tests that mirror implementation rather than specify behavior.

1. **Test file BEFORE implementation file**: The `.spec.ts` or `.test.ts` file must be created (with at least one failing test) BEFORE the corresponding implementation file is created or modified. If you wrote production code first, STOP and delete it.
2. **No retroactive test-writing**: If you wrote production code before a failing test existed for that behavior, delete the production code and start over with RED. "Tests after" verify what you built, not what you should build — they are not TDD.
3. **One behavior per RED-GREEN cycle**: Each cycle tests exactly one behavior. If your GREEN step touches more than one function, the test is too broad.
4. **Failing test must fail for the RIGHT reason**: Before writing GREEN code, verify the test fails because the behavior is missing, not because of a syntax error or import problem.

1. **Follow agreed Test Plan** from the task document
2. **TDD Red-Green-Refactor Cycle**:
   - **RED**: Write failing tests first per approved test plan
   - **GREEN**: Write minimal code to make tests pass
   - **REFACTOR**: Clean up while keeping tests green
3. **Update docs DURING code writing** — check if your change requires doc updates:
   - Adds/removes/modifies an API endpoint? → Update `backend/docs/`
   - Changes an architectural pattern? → Check `docs/adr/`
   - Alters UI behavior or flows? → Check `mobile-app/docs/`
   - Edits `AGENTS.md` or `CLAUDE.md`? → Run `/sync`
4. **Testing tools**:
   - Silent scripts (default for AI): `npm run test:silent`, `npm run test:unit:silent`, `npm run test:integration:silent`, `npm run test:e2e:silent`
   - Full output (debugging): `npm run test`
   - CI suite (Postgres-backed): `npm run test:ci`
   - DB lifecycle: `npm run test:db:start|migrate|stop`
5. **Verification**: All tests from approved plan must pass before proceeding

### Paralysis Guard
If you make **5+ consecutive Read/Grep/Glob calls without any Edit/Write/Bash action**:
1. STOP exploring
2. State your current understanding in one paragraph
3. State what's blocking you from writing code
4. Either start writing code (you likely have enough context) or ask the user for clarification

The task document is the source of truth. Do not endlessly explore the codebase.

#### After Each Step:
1. **Update task document** (REQUIRED):
   - Mark step checkbox: `- [ ]` → `- [x]`
   - Add **Changelog** entry
   - Update **Tests** field with command + result
   - Mark Test Plan checkboxes if applicable
   - **Parallel mode**: workers must not edit shared docs; orchestrator updates once after merge

   ```markdown
   - [x] Sub-step 3.1: Update CreateSessionUseCase logic
     - **Tests**: Test Suite 3 - PASS
     - **Changelog**: Injected WordGroupService, added validateGroupHasSufficientWords()
   ```

2. **Commit (permission gate)**:
   - Ask permission **before** any `git` command
   - Conventional commits with issue reference:
     - Code + tests: `feat(scope): [summary]` + `Refs: WYT-123`
     - Docs-only: `docs(scope): update [doc name]` + `Refs: WYT-123`
   - Tightly coupled doc changes may share the code commit

### Self-Verification (after each step)
Before marking a step complete, verify your claims:
1. All files listed in the step actually exist on disk (run `ls <file>`)
2. All tests mentioned can be found and pass (run them)
3. If a commit was claimed, verify with `git log -1 --oneline`
4. If a module was created, verify it compiles (`npx tsc --noEmit`)
5. If TDD was required, verify test file timestamps precede implementation file timestamps (`ls -lt`)

Do NOT claim completion without evidence. The `stop-verification-evidence` hookify rule enforces this — attempting to stop without verification will be blocked.

#### Error Recovery
- **Tests fail**: Fix the failing code, re-run tests. Do NOT skip or delete failing tests.
- **Quality gate fails**: Read the Quality Gate Report, address each failure, re-run.
- **Task document incomplete**: Ask user to clarify missing criteria before proceeding.

### Deviation Rules, Attempt Limit & Scope Boundary

Follow the shared reference: `.claude/docs/references/deviation-rules.md`

This covers: auto-fix vs ask matrix, 3-attempt limit, scope boundaries, and paralysis guard rules.

---

## STEP 4: Completion

### Code Simplification (Optional)
1. **Ask user**: "Run /simplify pass before quality gate?"
   - If yes: `Skill tool → skill: "simplify"`
   - If no: skip to Final Verification
2. If changes made: run tests + commit (permission gate): `refactor(scope): simplify implementation`

### De-Sloppify Pass (Automatic)
After code simplification (or skipping it), automatically run a de-sloppify pass on changed files:
1. Identify files changed in this implementation: `git diff --name-only $(git merge-base HEAD main)..HEAD`
2. Run `/simplify` skill (`Skill tool → skill: "simplify"`) — it will review changed files and clean up slop: console.logs left from debugging, commented-out code, redundant defensive checks (e.g., null checks on non-nullable types), dead imports, and test slop (leftover `.only`, `console.log` in tests).
3. This is **non-blocking** — if `/simplify` finds nothing, proceed. If it finds issues and applies fixes, re-run tests before continuing.
4. Commit de-sloppify changes separately (permission gate): `refactor(scope): de-sloppify pass`

### Final Verification
Run quality gates via Agent tool with subagent_type: "automated-quality-gate". Provide:
- `task_path`: absolute path to task directory
- `branch`: current feature branch name
- `test_commands`: which test suites to run (from task doc's Test Plan)
- Context: "Run full quality gate: lint, types, tests, coverage"

### Goal-Backward Verification (if Must Haves exist)

If the task document has a `## Must Haves` section, run the goal-verifier agent AFTER the quality gate passes:

```
Agent tool → subagent_type: "goal-verifier"
  task_document_path: [path to tech-decomposition]
  must_haves: [list from task doc's ## Must Haves section]
```

- If all must_haves are `VERIFIED`: proceed to finalization
- If any are `NOT_MET`: fix the gap before finalizing (this is a blocking check)
- If `BLOCKED`: report to user for guidance

This catches the "all steps passed but the goal was missed" failure mode — forward verification checks each step, but goal verification checks the holistic outcome.

### Finalize Task Document
1. **Update status** to "Ready for Review" with timestamp
2. **Update Linear**: `.claude/scripts/linear-api.sh update-status WYT-XX "In Review"`
3. **Verify all checkboxes** are accurate
4. **Add implementation summary**

---

## STEP 5: Prepare for Code Review

1. **Permission gate**: Push + PR require explicit user approval
2. **Validate task docs**: Agent tool → subagent_type: "task-pm-validator"
3. **Create PR + sync Linear (single path)**:
   - Use Task tool with subagent_type: "create-pr-agent"
   - Provide the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)
   - This agent handles PR creation and updates the task document with PR links. For Linear updates use the `cc-linear` skill (`.claude/skills/cc-linear/SKILL.md`).

---

## BUG FIX MODE

A lightweight path for fixing bugs without full task ceremony. The goal is to fix quickly while still maintaining quality through TDD.

For complex bugs where the root cause isn't obvious, consider `/dbg` first to instrument and diagnose before switching to Bug Fix mode here.

1. **Understand the bug**: reproduction steps, expected vs actual behavior
2. **Create branch** (permission gate): `fix/wyt-[ID]-[slug]` or `fix/[slug]`
3. **TDD**:
   - Write a failing test that reproduces the bug
   - Fix with minimal code changes
   - Verify: test passes + no regressions (`npm run test:silent`)
4. **Commit** (permission gate): `fix(scope): [what was fixed]` + `Refs: WYT-XX` if applicable
5. **Skip**: task doc updates, Linear updates, quality gate (unless complex)
6. **Optional**: Offer to create a PR directly

---

## ERROR RECOVERY

### Tests fail
Fix the failing code, re-run. Do NOT skip or delete failing tests. If the same test fails repeatedly, investigate root cause — check test setup, fixtures, database state.

### Quality gate fails
Read the Quality Gate Report. Address each failure systematically, re-run after fixes.

### Task document incomplete
Ask user to clarify missing criteria. Do not guess at acceptance criteria.

### Merge conflicts
1. Inform the user about the conflict
2. Offer to rebase or merge (with permission)
3. Resolve carefully, preserving both sets of changes
4. Re-run tests after resolution

### Flaky vs real failures
If a test fails intermittently: re-run once. If it passes on retry, flag as potentially flaky. If it fails consistently, treat as real.

### When to escalate
If stuck after 2-3 attempts at the same issue, tell the user what you've tried and ask for guidance rather than continuing to iterate blindly.
