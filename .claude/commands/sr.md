---
description: Conduct comprehensive code review before PR merge
---

# Start Review Command

## PRIMARY OBJECTIVE

Professional code review using specialized agents. Ensure quality, architectural compliance, and requirements fulfillment before merge.

## WORKFLOW

### GATE 1: Task Identification

1. **Ask**: "Which task to review? Provide task path or PR URL."

2. **Validate**:
   - Task document exists with "Implementation Complete" status
   - **STOP if**: "In Progress" or missing PR information
   - Linear issue referenced, steps marked complete

3. **Update Linear** using `cc-linear` skill:
   ```bash
   cc --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID]:
   1. Set status to 'In Review'
   2. Add comment: '🔍 Code review started - Task: [path]'"
   ```

### GATE 2: Automated Quality Gate

**ACTION**: Invoke `automated-quality-gate` agent

```
Task directory: [path]
Run all quality checks (lint, types, tests, coverage) and report pass/fail.
```

- **STOP if GATE_FAILED** → Return to developer with fixes list

### GATE 3: Approach Review

**ACTION**: Invoke `senior-approach-reviewer` agent

```
Task directory: [path]
Review approach, requirements fulfillment, architecture fit, TDD compliance (git history).
```

- **STOP if NEEDS_REWORK** → Return to developer with issues

### GATE 4: Parallel Code Review

**ACTION**: Invoke these 5 agents **IN PARALLEL**:

1. **`security-code-reviewer`**:
   ```
   Review security: OWASP, input validation, auth. Task: [path]
   ```

2. **`code-quality-reviewer`**:
   ```
   Review quality: SOLID, DRY, patterns, DDD layers. Task: [path]
   ```

3. **`test-coverage-reviewer`**:
   ```
   Review tests: coverage gaps, edge cases, quality. Task: [path]
   ```

4. **`documentation-accuracy-reviewer`**:
   ```
   Review docs: accuracy, completeness. Task: [path]
   ```

5. **`performance-reviewer`**:
   ```
   Review performance: bottlenecks, N+1 queries, efficiency. Task: [path]
   ```

### GATE 5: Synthesis & Decision

**TEMPLATE**: Use `@docs/product-docs/templates/code-review-template.md`

1. **Read template** from `docs/product-docs/templates/code-review-template.md`
2. **Aggregate findings** from all agents:
   - Quality Gate (GATE 2)
   - Approach Review (GATE 3)
   - All 5 Code Review agents (GATE 4)
3. **Apply severity markers** `[CRITICAL]`, `[MAJOR]`, `[MINOR]`, `[INFO]` within each agent section
4. **Consolidate issues** into severity categories with source agent attribution
5. **Apply decision matrix** (see below)
6. **Create** `Code Review - [Task].md` in task directory using template structure

### GATE 6: Linear & Completion

1. **Update status**:
   ```bash
   cc --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to '[Ready to Merge | Needs Fixes | In Review]'"
   ```

2. **Add results comment**:
   ```bash
   cc --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
   '✅ Code review completed
   **Status**: [APPROVED/NEEDS FIXES/NEEDS DISCUSSION]
   **Issues**: [X critical, Y major, Z minor]
   **Review Doc**: [path]'"
   ```

3. **Notify user** of outcome and next steps

## DECISION MATRIX

| Critical | Major | Decision |
|----------|-------|----------|
| 0 | 0-2 | APPROVED |
| 0 | 3+ | NEEDS FIXES |
| 1+ | any | NEEDS FIXES |

**Severity Levels**:
- `[CRITICAL]` - Must fix before merge (blocks approval)
- `[MAJOR]` - Should fix (3+ blocks approval)
- `[MINOR]` - Nice to fix (does not block)
- `[INFO]` - Observations (does not block)

**Status Mapping**:
- APPROVED → "Ready to Merge"
- NEEDS FIXES → "Needs Fixes"
- NEEDS DISCUSSION → Keep "In Review"

## OUTPUT

Single `Code Review - [Task].md` created in task directory using template from `@docs/product-docs/templates/code-review-template.md`.

**Contains**:
- Pre-Review validation (Quality Gate + Approach Review)
- Code Review findings from 5 specialized agents (with inline severity markers)
- Consolidated issues checklist with agent attribution
- Decision with severity counts and next steps
