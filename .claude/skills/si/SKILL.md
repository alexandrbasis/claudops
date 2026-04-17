---
name: si
description: >-
  Use when starting, continuing, or resuming implementation from a tech-decomposition or task
  directory
argument-hint: [task-directory | tech-decomposition-path]
allowed-tools: [Agent, AskUserQuestion, Edit, Read, Write, Bash, Glob, Grep, Skill, TodoWrite]
---

# Start Implementation Command

> **Announcement**: Begin with: "I'm using the **si** skill for structured TDD implementation."

## PRIMARY OBJECTIVE

Implement from a technical decomposition with TDD, lightweight task-document updates, and a clean handoff into review.

## CONSTRAINTS

- Follow the active tech-decomposition / task document as the source of truth
- Document lifecycle: `Technical Review` → `In Progress` → `Implementation Complete`
- Context will be automatically compacted during long runs. Don't stop early due to token
  concerns — persist progress to the task document after each step so a fresh window can
  resume from the same state.

---

## STEP 1: Task Validation

1. **Validate document**:
   - Confirm task exists (direct `tech-decomposition-*.md` path OR task directory containing one)
   - Confirm required sections exist: `Primary Objective`, `Must Haves`, `Test Plan`, and `Implementation Steps`
   - Confirm task status is appropriate — ask before proceeding if unclear
   - Confirm requirements and steps are specific enough to implement without guessing
   - If the document is missing core structure, stop and ask the user to clarify

---

## STEP 2: Setup

### Start

1. **Update task status** to "In Progress" with timestamp
2. **Create feature branch** (permission gate) if needed: `feature/team-[ID]-[slug]` or the repo convention
3. **Update `Tracking`** with the branch name once it exists

---

## STEP 3: Implementation

### Parallelization

When two or more steps meet the "When to parallelize" criteria below, spawn all eligible developer-agent workers in a single assistant message via `.claude/skills/parallelization/SKILL.md`. Don't default to sequential — if the task document has wave annotations or independent modules, parallel is the expected path. Sequential is the fallback when independence is unclear.

**Worker doc-edit rule**: In parallel mode, worker subagents do not edit the task document or other shared files. The orchestrator consolidates all document updates once after the wave merges. Workers return their checkbox diffs in their final message.

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

#### During Implementation (TDD)

1. **Stay in scope**: implement what the step asks for, nothing more. Don't add abstractions, refactor adjacent code, or insert defensive error handling for cases that can't occur. Surrounding cleanup belongs in STEP 4, not inside the TDD loop.
2. **Follow the agreed Test Plan** from the task document
3. **RED before GREEN**: each new behavior starts with a failing test that fails for the right reason
4. **One behavior per cycle**: keep each RED → GREEN → REFACTOR loop narrow
5. **No retroactive tests**: if implementation got ahead of the test, stop and return to RED. If fixing that would require reverting shared or user-authored work, ask first instead of deleting blindly.
6. **Update docs during code changes**
7. **Use repo-appropriate verification commands** from the task doc or package scripts. Run the quiet variant for routine loops; switch to full output when actively debugging a failure.
8. **Verification gate**: the tests named for the active step must pass before you mark it complete

The task document is the source of truth — read the files it names, implement against its acceptance criteria, and stop exploring once you have the context needed for the current step.

#### Mutation & Async Safety Checks
When the current step creates, updates, or deletes entities, or involves async callbacks:

**Post-mutation UX checklist:**
- Is the async call awaited by the UI event handler (not fire-and-forget)?
- Does the caller show success feedback or navigate to a visible result?
- Does the caller refresh every local state snapshot that depends on the mutation?
- Are semantic defaults set (category, type, order, visibility) — not just technically required fields?
- If the current screen cannot display the new entity, is that intentional and documented?

**Async callback checklist:**
- Is the callback marked `async` and does it `await` the mutation?
- Does the caller have `try/catch` with a user-visible error state?
- Does a modal/dialog/overlay close only after the async chain resolves (not before)?
- If the operation can fail, is there a rollback or cleanup path for partial writes?

Skip these checks for steps that don't involve mutations or async UI interactions.

#### After Each Step:
1. **Update task document**:
   - Mark step checkbox: `- [ ]` → `- [x]`
   - Update the step `**Tests**` field with command + result, or an explicit skip reason
   - Mark Test Plan checkboxes if applicable
   - Refresh `Tracking` / `Notes` if branch, risks, scope, or follow-ups changed
   - If the task doc already uses a per-step changelog, keep it updated. Otherwise do not add a new legacy field.
   - **Parallel mode**: workers must not edit shared docs; orchestrator updates once after merge

   ```markdown
   - [x] Sub-step 3.1: Update CreateSessionUseCase logic
     - **Tests**: `{{TEST_CMD}} -- [test-filter]` - PASS
   ```

2. **Commit (permission gate)**:
   - Ask permission **before** git write operations (`commit`, branch creation / switch, stash apply / drop, `push`, `rebase`, `merge`). Read-only inspection such as `git status` or `git log` is fine.
   - Conventional commits with issue reference:
    - Code + tests: `feat(scope): [summary]` + `Refs: TEAM-123`
    - Docs-only: `docs(scope): update [doc name]` + `Refs: TEAM-123`
   - Tightly coupled doc changes may share the code commit

### Self-Verification (after each step)
Before marking a step complete, verify your claims across **every** file and test touched in that step — not just the first one listed:
1. Every file listed in the step exists on disk (run `ls` on each)
2. Every test mentioned can be found and passes (run them)
3. If a commit was claimed, verify with `git log -1 --oneline`
4. If a module or contract was created / changed, run the relevant build, typecheck, or validation command

---

## STEP 4: Completion

### Cleanup Pass
If the diff accumulated obvious slop, run a focused cleanup pass before the final quality gate:
1. Invoke the `/simplify` skill or do a targeted manual cleanup on changed files
2. Re-run the relevant tests after any cleanup
3. Commit cleanup changes separately only with approval

---

## STEP 5: Prepare for Code Review

1. **Permission gate**: Push + PR require explicit user approval
2. **If approved, create PR**
3. **Hand off to `/sr`** once the task document status is `Implementation Complete` and review context is ready

## Finalize Task Document
1. **Update status** to "Implementation Complete" with timestamp
2. **Verify all checkboxes** are accurate
3. **Add or refresh the Completion Summary** with:
   - what changed
   - verification evidence (commands + results, quality gate path / summary)
   - deferred follow-ups or known skips