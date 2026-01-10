---
description: Full development orchestrator - implements, reviews, iterates until approved, creates PR
---

# Development Orchestrator Command

## Objective
Orchestrate complete development workflow from task document to merged PR using sub-agents. You are the **main conductor** managing validation, test writing, criterion-by-criterion implementation, reviews, and PR creation.

## Key Principle: Iterative Implementation

Work is done **incrementally**, not all at once:
1. **Tests first** - All tests written before any implementation
2. **One criterion at a time** - Implement, validate, then next
3. **Quick feedback loops** - Catch issues early, fix immediately

## Shared Memory: Task Directory

All agents read/write to the **task directory** as shared memory:

```
tasks/task-YYYY-MM-DD-[feature]/
├── tech-decomposition-[feature].md    ← Requirements (read by all)
├── discovery-[feature].md             ← Alternative: Feature spec (created by /nf)
├── JTBD-[feature].md                  ← Alternative: Jobs-to-be-Done (legacy)
├── Pre-Flight Validation - [Task].md  ← Created by task-validator
├── TEST_PLAN.md                       ← Created by test-developer
├── IMPLEMENTATION_LOG.md              ← Updated by implementation-developer
├── Code Review - [Task].md            ← Final review (consolidates all findings)
└── Integration Test Report - [Task].md ← Created by integration-test-runner
```

**Note**: Quality Gate and Approach Review data are returned inline by agents and integrated into `Code Review - [Task].md`. No separate files are created for these.

**Wythm Context**: Before starting, agents should review:
- `backend/docs/project-structure.md` - DDD/Clean Architecture patterns
- `backend/docs/tests-structure.md` - Testing conventions

---

## Workflow Overview

```
/dev (you are here - orchestrator)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 0: Pre-Flight Validation                     │
│  Agent: task-validator                              │
│  Output: Pre-Flight Validation - [Task].md          │
│                                                     │
│  IF NOT_READY → Report issues, STOP                 │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 1a: Test Writing (ALL criteria)              │
│  Agent: test-developer                              │
│  - Writes failing tests for ALL acceptance criteria │
│  - One commit per criterion's tests                 │
│  - All tests should FAIL (no implementation yet)    │
│  Output: TEST_PLAN.md + test files                  │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 1b: Implementation Loop (ONE at a time)      │
│                                                     │
│  FOR EACH criterion:                                │
│    ┌───────────────────────────────────────────┐    │
│    │ implementation-developer                  │    │
│    │ - Implement ONE criterion                 │    │
│    │ - Make tests pass                         │    │
│    │ - Quick validation (tests, lint, types)   │    │
│    └───────────────────────────────────────────┘    │
│              ↓                                      │
│    ┌───────────────────────────────────────────┐    │
│    │ Validation passed?                        │    │
│    │ YES → Next criterion                      │    │
│    │ NO  → Fix, then re-validate               │    │
│    └───────────────────────────────────────────┘    │
│                                                     │
│  Output: IMPLEMENTATION_LOG.md (updated per crit.)  │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 2: Automated Quality Gates                   │
│  Agent: automated-quality-gate                      │
│  Output: Returns data inline (for Code Review)      │
│                                                     │
│  IF GATE_FAILED → Fix specific criterion            │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 3: Senior Approach Review                    │
│  Agent: senior-approach-reviewer                    │
│  - TDD compliance verified from git history         │
│  Output: Returns data inline (for Code Review)      │
│                                                     │
│  IF NEEDS_REWORK → Back to specific criterion       │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 4: Code Review (Parallel Validators)         │
│  Agent: code-review-orchestrator                    │
│    ├─> security-code-reviewer                       │
│    ├─> code-quality-reviewer                        │
│    ├─> test-coverage-reviewer                       │
│    └─> documentation-accuracy-reviewer              │
│  Output: Code Review - [Task].md                    │
│                                                     │
│  IF NEEDS_FIXES → Fix specific issues               │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 5: Integration Testing                       │
│  Agent: integration-test-runner                     │
│  Output: Integration Test Report - [Task].md        │
│                                                     │
│  IF INTEGRATION_FAILED → Fix integration issues     │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  PHASE 6: PR Creation                               │
│  Agent: create-pr-agent + task-pm-validator         │
└─────────────────────────────────────────────────────┘
    │
    ▼
  DONE - PR ready for human review
```

---

## Phase 0: Pre-Flight Validation

### Step 0.1: Task Identification
1. **Ask user**: "Which task to develop? Provide task path or name."
   - List tasks in `tasks/` if unclear
2. **Locate task directory** and verify it exists

### Step 0.2: Launch task-validator Agent

```
subagent_type: "task-validator"

Prompt: "Validate task at [TASK_DIRECTORY_PATH] is ready for implementation.

Check:
1. Task document exists with all required sections
2. Requirements are clear and unambiguous
3. Scope is bounded (not open-ended)
4. Dependencies are available
5. Acceptance criteria are testable

Save validation report to task directory.

Return JSON: {status, validation_doc, completeness_score, clarity_score, blockers, summary}"
```

### Handle Result
- **ready** → Proceed to Phase 1a
- **needs_clarification** → Present ambiguous items to user, await clarification
- **not_ready** → Present blockers, do NOT proceed until resolved

### Step 0.3: Linear Status Update
```bash
cc --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Progress'"
```

---

## Phase 1a: Test Writing

### Launch: test-developer Agent

```
subagent_type: "test-developer"

Prompt: "Write failing tests for ALL acceptance criteria in [TASK_DIRECTORY_PATH].

PROTOCOL:
1. Read task document and extract ALL acceptance criteria
2. Create TEST_PLAN.md with test mapping
3. For EACH criterion:
   a. Write comprehensive test cases (happy path + edge cases)
   b. Verify tests FAIL (no implementation yet)
   c. Commit: "test: add tests for [criterion description]"
   d. Update TEST_PLAN.md
4. All tests should be FAILING at the end

Output: TEST_PLAN.md + test files committed

Return JSON: {
  status, test_plan, criteria_covered,
  test_files, test_cases_total,
  all_tests_failing, commits, summary
}"
```

### Handle Result
- **complete** → All tests written and failing, proceed to Phase 1b
- **blocked** → Present blockers to user
- **needs_clarification** → Relay questions about expected behavior

### Verify Before Proceeding
```bash
# All tests should FAIL (expected)
npm run test
# Expected output: X failed, 0 passed
```

---

## Phase 1b: Implementation Loop

### Overview
Implement criteria ONE AT A TIME. After each criterion:
1. Launch implementation-developer for ONE criterion
2. Check validation result
3. If passed → next criterion
4. If failed → fix, then re-validate
5. Repeat until all criteria complete

### Implementation Loop Protocol

```python
criteria = get_criteria_from_task_document()
current = 1
max_fix_attempts = 3

while current <= len(criteria):
    # Launch implementation-developer for ONE criterion
    result = launch_agent("implementation-developer",
        mode="IMPLEMENT_CRITERION",
        criterion_number=current,
        criterion_description=criteria[current].description,
        test_file=criteria[current].test_file
    )

    if result.status == "criterion_complete":
        # Validation passed, move to next
        log_progress(current, "complete")
        current += 1
        fix_attempts = 0

    elif result.status == "validation_failed":
        fix_attempts += 1
        if fix_attempts > max_fix_attempts:
            # Escalate to user
            ask_user("Criterion {current} failing after {max_fix_attempts} attempts. Continue or intervene?")
        else:
            # Re-invoke to fix
            launch_agent("implementation-developer",
                mode="FIX_VALIDATION",
                error=result.validation_error
            )

    elif result.status == "blocked":
        ask_user(result.blockers)
        # Wait for user input before continuing
```

### For Each Criterion

```
subagent_type: "implementation-developer"

Prompt: "Implement criterion [N] of [TOTAL]: [DESCRIPTION]

MODE: IMPLEMENT_CRITERION

Tests are in: [TEST_FILE_PATH]
Task directory: [TASK_DIRECTORY_PATH]

1. Read test file to understand expected behavior
2. Write MINIMAL code to make tests pass
3. Run validation:
   - Tests for this criterion pass
   - All tests pass (no regression)
   - Lint clean
   - Types correct
4. Commit: "feat: implement [description]"
5. Update IMPLEMENTATION_LOG.md

Return JSON: {
  status, criterion, validation,
  files_changed, commit, next_criterion, summary
}"
```

### After Each Criterion - Orchestrator Checks

```
Criterion [N] Result:
├─ Status: [criterion_complete | validation_failed | blocked]
├─ Tests: [X/Y passing]
├─ Lint: [passed | failed]
├─ Types: [passed | failed]
└─ Commit: [hash]

Progress: [N/TOTAL] criteria complete
Next: Criterion [N+1]: [description]
```

### Validation Failed - Fix Loop

```
subagent_type: "implementation-developer"

Prompt: "Fix validation failure for criterion [N].

MODE: FIX_VALIDATION

Error type: [test | lint | typecheck]
Error message: [ERROR_MESSAGE]
File: [FILE_PATH]

Fix the issue and re-run validation.

Return JSON: {status, validation, commit, summary}"
```

### Phase 1b Complete When
- All criteria implemented
- All tests passing
- All validations passing

---

## Phase 2: Automated Quality Gates

### Launch: automated-quality-gate Agent

```
subagent_type: "automated-quality-gate"

Prompt: "Run full quality gates for task at [TASK_DIRECTORY_PATH].

GATES:
1. Full test suite with coverage
2. Lint check
3. Type check
4. Coverage threshold (70%)
5. Build verification

Return JSON: {status, gates, coverage_percentage, summary, markdown_snippet}
Note: Agent returns data inline (no file created). Integrate into Code Review."
```

### Handle Result
- **gate_passed** → Proceed to Phase 3
- **gate_failed** → Identify which criterion caused failure, fix with implementation-developer

---

## Phase 3: Senior Approach Review

### Launch: senior-approach-reviewer Agent

```
subagent_type: "senior-approach-reviewer"

Prompt: "Review implementation approach for task at [TASK_DIRECTORY_PATH].

VERIFY:
1. All acceptance criteria met
2. Solution approach is sound
3. Architecture fits codebase patterns
4. TDD compliance (from git history - tests committed before implementation)

Return JSON: {status, requirements_score, approach_score, tdd_compliance, summary}
Note: Agent returns data inline (no file created). Integrate into Code Review."
```

### Handle Result
- **APPROVED** → Proceed to Phase 4
- **MINOR_ADJUSTMENTS** → Fix specific issues, proceed to Phase 4
- **NEEDS_REWORK** → Identify affected criteria, rework with implementation-developer

---

## Phase 4: Code Review

### Launch: code-review-orchestrator Agent

```
subagent_type: "code-review-orchestrator"

Prompt: "Conduct code review for task at [TASK_DIRECTORY_PATH].

Launch parallel validators:
1. security-code-reviewer
2. code-quality-reviewer
3. test-coverage-reviewer
4. documentation-accuracy-reviewer

Return JSON: {status, review_doc, agent_results, totals, summary}"
```

### Handle Result
- **APPROVED** → Proceed to Phase 5
- **NEEDS_FIXES** → Fix issues with implementation-developer (max 3 iterations)

---

## Phase 5: Integration Testing

### Launch: integration-test-runner Agent

```
subagent_type: "integration-test-runner"

Prompt: "Run integration tests for task at [TASK_DIRECTORY_PATH].

TESTS:
1. E2E tests
2. Database migrations
3. Service health
4. Module integration

Return JSON: {status, report_doc, tests, critical_issues, summary}"
```

### Handle Result
- **INTEGRATION_PASSED** → Proceed to Phase 6
- **INTEGRATION_FAILED** → Present to user, fix with implementation-developer

---

## Phase 6: PR Creation

### Step 6.1: Validate Documentation
```
subagent_type: "task-pm-validator"
```

### Step 6.2: Create PR
```
subagent_type: "create-pr-agent"
```

### Step 6.3: Update Linear
```bash
cc --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Review'"
```

---

## Phase 7: Completion

Present to user:

```markdown
## Development Complete

**Task**: [Task Title]
**PR**: [PR_URL]
**Linear**: [ISSUE-ID]

### Workflow Summary
| Phase | Status | Output |
|-------|--------|--------|
| Pre-Flight | ✅ READY | Pre-Flight Validation - [Task].md |
| Test Writing | ✅ [N] tests | TEST_PLAN.md |
| Implementation | ✅ [N/N] criteria | IMPLEMENTATION_LOG.md |
| Quality Gates | ✅ PASSED | (integrated in Code Review) |
| Approach Review | ✅ APPROVED | (integrated in Code Review) |
| Code Review | ✅ APPROVED | Code Review - [Task].md |
| Integration | ✅ PASSED | Integration Test Report - [Task].md |

### Implementation Progress
| # | Criterion | Tests | Status |
|---|-----------|-------|--------|
| 1 | [Desc] | 5 | ✅ Complete |
| 2 | [Desc] | 3 | ✅ Complete |
| 3 | [Desc] | 4 | ✅ Complete |

### Metrics
- Test Coverage: [X]%
- Criteria: [N/N]
- TDD Compliance: ✅

### What's Next
1. Human code review on PR
2. After approval, run `/mp` to merge
```

---

## Error Handling

### Phase 1a: Test Writing Issues
- If unclear about expected behavior → ask user
- If tests can't be written → clarify requirements first

### Phase 1b: Implementation Loop Stuck
- Max 3 fix attempts per criterion
- After 3 failures → escalate to user
- User can: provide guidance, skip criterion, or abort

### Phase 2-5: Review Failures
- Identify which criterion is affected
- Fix with targeted implementation-developer call
- Max 3 iterations before escalation

---

## Error Recovery Protocol

### Resume After Failure
1. Read all docs in task directory
2. Check TEST_PLAN.md for test status
3. Check IMPLEMENTATION_LOG.md for implementation progress
4. Resume from last incomplete criterion or phase

### Checkpoint Commits
Every criterion gets its own commit:
- `test: add tests for [criterion]` (Phase 1a)
- `feat: implement [criterion]` (Phase 1b)

This allows easy rollback to any criterion.

---

## Success Criteria

- [ ] Pre-Flight: READY
- [ ] All tests written (failing initially)
- [ ] All criteria implemented (one at a time)
- [ ] All validations passing per criterion
- [ ] Quality Gates: PASSED
- [ ] Approach Review: APPROVED (TDD verified)
- [ ] Code Review: APPROVED
- [ ] Integration: PASSED
- [ ] PR created with traceability

---

## Guidelines

- Tests FIRST, then implementation
- ONE criterion at a time
- Validate after EACH criterion
- Quick feedback loops catch issues early
- TDD compliance verified from git history
- Max 3 fix attempts before escalation
- All progress saved to task directory
