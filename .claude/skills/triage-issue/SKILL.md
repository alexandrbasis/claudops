---
name: triage-issue
description: >-
  Investigate a reported bug, find its root cause, and file a tracker issue
  (GitHub or Linear) with a TDD-based fix plan. Mostly hands-off — minimize
  questions to the user. Does NOT apply the fix. Use when user reports a bug
  and wants it tracked, mentions "triage", "file an issue", or "investigate
  and plan a fix". NOT for interactive debugging (use /dbg) or batch QA
  sessions (use /qa).
allowed-tools: [Read, Grep, Glob, Bash, Task, Skill, AskUserQuestion]
---

# Triage Issue

> **Upstream**: Adapted from [mattpocock/skills/triage-issue](https://github.com/mattpocock/skills/blob/main/triage-issue/SKILL.md). Adapted to use this repo's `Explore` agent, `tdd/` skill, and `cc-linear`/`gh` integration.

Investigate a reported problem, find the root cause, and create a tracker issue with a TDD fix plan. **This skill does NOT apply the fix** — it produces a durable, grabbable issue that `/si` or another agent can pick up later.

## Process

### 1. Capture the problem

If the user has not described the issue, ask **one** question:

> "What's the problem you're seeing?"

Do **not** ask follow-ups yet. Start investigating immediately.

### 2. Explore and diagnose

Use the `Agent` tool with `subagent_type=Explore` to investigate the codebase. Goal:

- **Where** the bug manifests (entry points, UI, API responses)
- **What** code path is involved (trace the flow)
- **Why** it fails (root cause, not symptom)
- **What** related code exists (similar patterns, tests, adjacent modules)

Look at:

- Related source files and their dependencies
- Existing tests (what's tested, what's missing)
- Recent changes to affected files (`git log` on relevant files)
- Error handling in the code path
- Similar patterns elsewhere in the codebase that work correctly

Load `product-docs/UBIQUITOUS_LANGUAGE.md` if it exists — use its terms in the issue body.

### 3. Identify the fix approach

Based on investigation, determine:

- The minimal change needed to fix the root cause
- Which modules/interfaces are affected (use `architecture-language/LANGUAGE.md` vocabulary — module, interface, seam)
- What behaviors need to be verified via tests
- Whether this is a regression, missing feature, or design flaw

### 4. Design TDD fix plan

Create an ordered list of RED-GREEN cycles aligned with `.claude/skills/tdd/SKILL.md`. Each cycle is one vertical slice:

- **RED**: a specific test that captures the broken/missing behavior
- **GREEN**: the minimal code change to make that test pass

Rules:

- Tests verify behavior through public interfaces, not implementation details
- One test at a time, vertical slices (NOT all tests first, then all code)
- Each test should survive internal refactors
- Include a final refactor step if needed
- **Durability**: only suggest fixes that would survive radical codebase changes. Describe behaviors and contracts, not internal structure. Tests assert on observable outcomes (API responses, UI state, user-visible effects), not internal state. A good suggestion reads like a spec; a bad one reads like a diff.

### 5. Pick the tracker

If this repo uses Linear (look for `cc-linear` config / Linear references in recent issues / `LINEAR_TEAM_ID` in env), invoke `/cc-linear` to file the issue. Otherwise use `gh issue create`.

If unclear, ask once: `AskUserQuestion`: "File via Linear or GitHub Issues?" Options: "Linear" / "GitHub" / "Skip — output the body only".

### 6. Create the issue

Use the template below. **Do NOT ask the user to review before creating** — file it and share the URL.

```
## Problem

A clear description of the bug or issue, including:
- What happens (actual behavior)
- What should happen (expected behavior)
- How to reproduce (if applicable)

## Root Cause Analysis

What you found during investigation:
- The code path involved
- Why the current code fails
- Any contributing factors

Do NOT include specific file paths, line numbers, or implementation details
that couple to current code layout. Describe modules, behaviors, and contracts
instead. The issue should remain useful even after major refactors.

## TDD Fix Plan

A numbered list of RED-GREEN cycles:

1. **RED**: Write a test that [describes expected behavior]
   **GREEN**: [Minimal change to make it pass]

2. **RED**: Write a test that [describes next behavior]
   **GREEN**: [Minimal change to make it pass]

...

**REFACTOR**: [Any cleanup needed after all tests pass]

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] All new tests pass
- [ ] Existing tests still pass

## Handoff

Pick up with `/si <this issue>` to implement.
```

After creating the issue, print the issue URL and a one-line summary of the root cause.

## Scope boundaries

- Does NOT apply the fix (handoff to `/si`)
- Does NOT include file paths or line numbers in the issue body
- Does NOT ask follow-up questions during investigation — go to the code first
- Does NOT use this for interactive debugging — that's `/dbg`
- Does NOT use this for batch bug-reporting sessions — that's `/qa`

## Distinction from sibling skills

| Skill | Purpose | Output |
|---|---|---|
| `/dbg` | Interactive debug — runtime evidence, instrumentation, may apply fix | Fixed bug or hypothesis |
| `/triage-issue` | Investigate and file ONE issue with TDD plan; no fix | Tracker issue with TDD plan |
| `/qa` | Conversational QA session, multiple bugs at once | Multiple tracker issues with blocker links |
