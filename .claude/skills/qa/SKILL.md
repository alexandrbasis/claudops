---
name: qa
description: >-
  Interactive QA session where the user reports bugs conversationally and the
  agent files them as tracker issues (GitHub or Linear) one by one or as a
  dependency-linked breakdown. Explores the codebase in the background for
  context and domain language. Use when user wants to "do QA", "report bugs",
  "file issues from a QA pass", or runs through multiple problems at once.
  NOT for single-bug triage (use /triage-issue) or interactive debug (/dbg).
allowed-tools: [Read, Grep, Glob, Bash, Task, Skill, AskUserQuestion]
---

# QA Session

> **Upstream**: Adapted from [mattpocock/skills/qa](https://github.com/mattpocock/skills/blob/main/qa/SKILL.md). Adapted to use this repo's `Explore` agent, `cc-linear`/`gh` integration, and `UBIQUITOUS_LANGUAGE.md` convention.

Run an interactive QA session. The user describes problems they're encountering. You clarify lightly, explore the codebase for context, and file tracker issues that are durable, user-focused, and use the project's domain language. **No fixes applied.**

## Pick the tracker once, at the start

Detect Linear (look for `cc-linear` config / `LINEAR_TEAM_ID` / Linear references in recent issues) vs GitHub Issues. If ambiguous, ask once: `AskUserQuestion`: "File via Linear or GitHub Issues for this session?" — then keep that choice for the whole session.

## For each issue the user raises

### 1. Listen and lightly clarify

Let the user describe the problem in their own words. Ask **at most 2-3 short clarifying questions**:

- What they expected vs what actually happened
- Steps to reproduce (if not obvious)
- Whether it's consistent or intermittent

Do NOT over-interview. If the description is clear enough to file, move on.

### 2. Explore the codebase in the background

While the user describes the next issue, kick off an `Agent` (subagent_type=Explore) for the previous one. Goal is **not** to fix — it's to:

- Learn the domain language used in that area (cross-check with `product-docs/UBIQUITOUS_LANGUAGE.md` if it exists)
- Understand what the feature is supposed to do
- Identify the user-facing behavior boundary

Context helps you write a better issue. The issue itself must NOT reference specific files, line numbers, or internal implementation details.

### 3. Assess scope: single issue or breakdown?

Before filing, decide whether this is a **single issue** or a **breakdown** into multiple issues.

**Break down** when:

- The fix spans multiple independent areas (e.g., "form validation is wrong AND success message is missing AND redirect is broken")
- There are clearly separable concerns that different people/agents could work on in parallel
- The user describes multiple distinct failure modes or symptoms

**Keep as a single issue** when:

- It's one behavior wrong in one place
- The symptoms all stem from the same root behavior

### 4. File the issue(s)

Use `gh issue create` or invoke `/cc-linear` (whichever was picked at the start). **Do NOT ask the user to review first** — file and share URLs.

#### Single-issue template

```
## What happened

[Actual behavior the user experienced, in plain language]

## What I expected

[Expected behavior]

## Steps to reproduce

1. [Concrete numbered steps a developer can follow]
2. [Use domain terms from UBIQUITOUS_LANGUAGE.md, not internal module names]
3. [Include relevant inputs, flags, or configuration]

## Additional context

[Extra observations from the user or from background exploration —
e.g. "this only happens in the Docker layer, not the filesystem layer".
Use domain language; do not cite files.]
```

#### Breakdown template (per sub-issue)

```
## Parent

#<parent-issue-number> (if a tracking issue was created) or "Reported during QA session"

## What's wrong

[This specific behavior problem — just this slice, not the whole report]

## What I expected

[Expected behavior for this slice]

## Steps to reproduce

1. [Steps specific to THIS issue]

## Blocked by

- #<issue-number> (if this issue can't be fixed until another is resolved)

Or "None — can start immediately" if no blockers.

## Additional context

[Observations relevant to this slice]
```

When creating a breakdown:

- **Prefer many thin issues over few thick ones** — each independently fixable and verifiable
- **Mark blocking relationships honestly** — if B genuinely can't be tested until A is fixed, say so. If they're independent, mark both as "None — can start immediately"
- **Create issues in dependency order** so you can reference real issue numbers in "Blocked by"
- **Maximize parallelism** — multiple people / `/si` runs should be able to grab different issues simultaneously

### 5. Rules for all issue bodies

- **No file paths or line numbers** — they go stale
- **Use the project's domain language** (check `product-docs/UBIQUITOUS_LANGUAGE.md` if it exists)
- **Describe behaviors, not code** — "the sync service fails to apply the patch", not "applyPatch() throws on line 42"
- **Reproduction steps are mandatory** — if you can't determine them, ask the user once
- **Keep it concise** — a developer should be able to read the issue in 30 seconds

After filing, print all issue URLs (with blocker relationships summarized) and ask: "Next issue, or are we done?"

### 6. Continue the session

Keep going until the user says they're done. Each issue is independent — don't batch them.

## Distinction from sibling skills

| Skill | Mode | Output |
|---|---|---|
| `/dbg` | Interactive single-bug debug, may fix | Fixed bug or hypothesis |
| `/triage-issue` | Single bug → root cause + TDD plan, no fix | One tracker issue |
| `/qa` | Multiple bugs reported conversationally, no fix | Multiple tracker issues, possibly with blocker links |
