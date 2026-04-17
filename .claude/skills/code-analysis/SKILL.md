---
name: code-analysis
description: >-
  Deep code analysis with metrics, patterns, and recommendations. Use when asked
  to 'analyze this code', 'explore the codebase', 'code audit', 'tech debt assessment',
  'architecture review', 'codebase overview', 'show me the project structure',
  'where are the hotspots', 'code metrics', 'what patterns are used', 'how is
  this organized', 'code quality check', 'find complexity', 'module dependencies',
  or any request to understand, assess, or explore code quality and structure.
  Also triggers for pre-implementation codebase exploration and dependency analysis.
  NOT for code review before merge (use /sr). NOT for debugging (use /dbg).
  NOT for research on external technologies (use /deep-research).
argument-hint: "[scope: file, module, or project]"
context: fork
agent: Explore
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(wc *)
  - Bash(find *)
  - Bash(git log *)
  - Bash(git shortlog *)
  - Bash(git rev-list *)
  - Bash(ls *)
---

# Deep Code Analysis

> **Announcement**: Begin with: "I'm using the **code-analysis** skill for deep code analysis."

## Overview

Perform code analysis scoped to the depth tier in Step 1 (Quick / Standard / Deep). Stop as soon as you have enough evidence to fill the output template for that tier — do not expand scope beyond it. Since this runs in a forked context, be decisive: a focused 10-finding report beats a 40-finding report with filler.

## Scope Boundaries

This skill READS and REPORTS — it does not suggest code changes or write fixes.

- For pre-merge code review → `/sr`
- For debugging runtime issues → `/dbg`
- For researching external technologies → `/deep-research`

## 1. Determine Analysis Depth

Match the depth to the request — not every question needs a full audit:

| Mode | When | Scope |
|------|------|-------|
| **Quick** | "what's the structure?", "explore this module", overview requests | Steps 2-3 only |
| **Standard** | "analyze", "assess", "audit", "code quality" | Steps 2-5 |
| **Deep** | "full audit", "comprehensive analysis", "deep dive" | Steps 2-6 + dependency analysis |

When the request is ambiguous, pick the mode whose "When" column best matches the user's phrasing. If still unclear, use Standard.

## 2. Scope Discovery

Understand what you're analyzing before diving in. When multiple discovery commands in a step have no dependencies between them, batch them in one turn. Never use placeholders or guess missing parameters.

```bash
# Project structure overview
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) \
  ! -path "*/node_modules/*" ! -path "*/dist/*" ! -path "*/coverage/*" \
  | head -60

# Line counts by directory
find . -type f -name "*.ts" ! -path "*/node_modules/*" ! -path "*/dist/*" \
  | xargs wc -l | sort -rn | head -20
```

Read project context dynamically — don't assume the stack:
- `CLAUDE.md` at repo root for architecture overview
- `{{DOCS_DIR}}/AGENTS.md` for project-specific conventions
- `package.json` / `tsconfig.json` for actual dependencies and versions

If any `{{VARIABLE}}` placeholder in this skill or in `references/project-checks.md` is not populated (e.g. `{{SRC_DIR}}` is still literal), detect the real path by inspection (e.g. `ls` the repo root for `src/`, `lib/`, `app/`) before running any command. Do not run a command containing an unresolved `{{…}}` placeholder.

## 3. Architecture Analysis

- Identify layers and boundaries (read `{{DOCS_DIR}}/project-structure.md` for canonical structure)
- Map module dependencies and import relationships
- Find circular dependencies or layer violations
- Check adherence to documented patterns
- Assess module cohesion — does each module own a clear responsibility?

## 4. Code Quality Metrics

- **File size hotspots**: files > 300 lines warrant attention
- **Complexity indicators**: deeply nested logic, long parameter lists, large switch/if chains
- **Code duplication**: repeated patterns across modules
- **Naming consistency**: do conventions hold across the codebase?
- **Test-to-code ratio**: count test files vs source files per module

```bash
# Find large files
find . -name "*.ts" ! -path "*/node_modules/*" ! -path "*/dist/*" \
  -exec wc -l {} + | sort -rn | head -15

# Test file ratio
find . -name "*.ts" ! -name "*.spec.ts" ! -name "*.test.ts" \
  ! -path "*/node_modules/*" ! -path "*/dist/*" | wc -l
find . \( -name "*.spec.ts" -o -name "*.test.ts" \) \
  ! -path "*/node_modules/*" | wc -l
```

## 5. Tech Debt Assessment

- **TODO/FIXME inventory**: search for `TODO`, `FIXME`, `HACK`, `XXX` across source files
- **Deprecated patterns**: old approaches that should be migrated
- **Missing error handling**: bare catches, unhandled promise rejections
- **Incomplete implementations**: stubs, placeholder returns
- **Dependency health**: check `package.json` for outdated or unmaintained packages

## 6. Git History Insights (Deep mode only)

```bash
# Hotspots: most frequently changed files (high churn = risk)
git log --since="6 months ago" --format=format: --name-only \
  | grep -v '^$' | sort | uniq -c | sort -rn | head -20

# Recent contributors
git shortlog -sn --since="3 months ago"

# Commit velocity (activity trend)
git rev-list --count --since="3 months ago" HEAD
git rev-list --count --since="6 months ago" --until="3 months ago" HEAD

# Code ownership concentration (run for top hotspot files)
# git log --format='%aN' -- [file] | sort | uniq -c | sort -rn | head -3
```

## 7. Project-Specific Checks

For this project, run targeted checks. Read `references/project-checks.md` for detailed commands.

Key areas:
- **Architecture layer separation**: verify layer boundaries are respected (e.g., domain must NOT import from infrastructure)
- **Database schema health**: model count, index coverage, migration count (check {{SCHEMA_PATH}} if configured)
- **{{FRAMEWORK}} module boundaries**: providers/services stay within their module
- **Error handling**: consistent use of domain exceptions (not raw `Error` throws)
- **API surface**: endpoint inventory, guard/middleware coverage, DTO/contract definitions

## 8. Output Format

Adapt the report to the analysis depth from step 1. Only include sections relevant to the mode.

### Quick (overview only)

```
# Codebase Overview: [scope]

**Structure**: [high-level description]
**Size**: [file count, LOC]
**Key Modules**: [list with brief descriptions]

**Notable**: [1-2 observations]
```

### Standard

```markdown
# Code Analysis: [scope]

**Date**: [ISO date]

## Summary
[2-3 sentence overview]

## Metrics
| Metric | Value |
|--------|-------|
| Total Files | X |
| Lines of Code | X |
| Test/Code Ratio | X% |
| Tech Debt Items | X |

## Architecture Findings
### Strengths
- [finding]

### Concerns
Include every concern you found, labeled with severity. Do not pre-filter to only CRITICAL/MAJOR — a small number of MINOR items in the report is expected and useful.
- [severity: CRITICAL/MAJOR/MINOR] [confidence: high/med/low] [finding]

## Recommendations
1. [actionable recommendation]
2. [actionable recommendation]
```

### Deep (full report)

All Standard sections plus:

```markdown
## Git History Analysis
[churn hotspots, ownership, velocity trends]

## Dependency Analysis
[outdated deps, security concerns, bundle impact]

## Detailed Findings
[expandable sections for each analysis dimension]
```
