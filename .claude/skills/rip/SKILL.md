---
name: rip
description: >-
  Review implementation plan for business value alignment. Use when asked to
  'review my plan', 'walk through implementation', 'check plan against PRD',
  'review technical decomposition', or 'is my plan aligned with requirements'.
  NOT for code review (use /sr), NOT for creating tasks (use /ct),
  NOT for static code analysis (use /code-analysis).
argument-hint: [plan-file-path]
allowed-tools: Read, Grep, Glob, AskUserQuestion
---

# Review Implementation Plan (RIP)

> **Announcement**: Begin with: "I'm using the **rip** skill for implementation plan review."

Step-by-step review of implementation plan. Focus: **business value** through technical understanding.

## Protocol

### Phase 1: Analysis

Before responding:
1. Read the plan completely. If the argument is a directory or ambiguous path, Glob for plan-shaped files (`tech-decomposition-*.md`, `*implementation-plan*.md`) before giving up.
2. Study related code (Grep, Read) — verify, don't assume. Never comment on a file you have not opened; if the plan names a file, read it before evaluating the step that touches it.
3. Compare with PRD/business requirements — run alignment checklist:
   - Measurable outcomes/KPIs defined?
   - Scope matches PRD (no creep, no gaps)?
   - Risks or dependencies identified?
   - Each step ties to a user-facing outcome?
4. Determine business value of each step
5. If plan is ambiguous or missing context — use AskUserQuestion to clarify before proceeding

Record mismatches (extra features, missed requirements, logic conflicts) for discussion. Frame each as **facts + question** rather than a verdict — the plan author knows the product context you don't, and a question invites a fix instead of a defense.

**Review format:**

```
## Overview

**Business goal:** [what problem it solves]
**Scope:** [components] | [files] | [complexity]
**Plan:** [N steps with names]

**Warnings (include uncertain ones with confidence tag):**
- [Problem] — contradicts [source]

Ready for first step?
```

### Phase 2: Walkthrough

Default to a continuous walkthrough in one response (all steps, back-to-back) — 4.7 calibrates length well and one message is cheaper than N turns. Pause only when (a) the user asks you to pause, (b) you need to resolve a PRD mismatch before the next step makes sense, or (c) the plan has more than ~6 steps and a mid-review check-in improves comprehension.

**Step format:**

```
### Step [N]: [Name]

**Why:** [business reason]
**What:** [technical essence]
**Concepts:** [term]: [analogy]
**Impact:** [code] → [user-facing change]
**Code:** [if relevant]

**Warnings (include uncertain ones with confidence tag):**
- [PRD issue]
- **Question:** [clarification]

---
Questions? Next?
```

### Phase 3: Summary

```
## Summary

**Covered:** [recap]
**Value:** [why it matters to user]
**Concepts:** [list]

**Self-check:**
1. [Business question]
2. [Technical question]
```

## Rules

| Principle | Action |
|-----------|--------|
| Business-first | Start with "why for the user" |
| Simplicity | Term = analogy |
| Specificity | Real files/endpoints |
| Progress | Every 3-4 steps: "X of N" |
| Criticality | Surface every potential PRD mismatch, including uncertain ones; mark each with confidence (high/medium/low). Present them all in the Warning block — let the user decide what is in scope. |
| Constructiveness | Facts + question, no dismissiveness |

## Example

**Input:** Progress tracking plan

**Overview:**

> **Business goal:** Users see progress → motivation
> **Scope:** backend + DB | `src/modules/progress/` | medium
> **Plan:** 4 steps (model, API, logic, integration)
>
> **Warning:**
> - Plan doesn't mention visualization — PRD requires charts. Out of scope?
> - PRD: PDF export — not in plan. Include?

**Step 1:**

> **Why:** Store word learning history
> **What:** `WordProgress` table links user+word, stores metrics
> **Concepts:** Database schema = DB blueprint as code
> **Impact:** "Progress" screen → word-level stats
>
> **Warning:**
> - PRD: track repetition intervals (spaced repetition). Schema: only `lastSeen`, no history.
> - **Question:** Plan — current state only or full history?

## Related Skills

| Need | Use |
|------|-----|
| Review code before merge | `/sr` |
| Create implementation plan | `/ct` |
| Analyze code architecture | `/code-analysis` |
| Create/update PRD or JTBD | `/product` |
