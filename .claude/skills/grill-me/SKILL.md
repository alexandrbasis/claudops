---
name: grill-me
description: Use when a plan, design, or discovery document needs stress-testing for hidden assumptions, scope gaps, unresolved branches, or ambiguous wording; also when the user explicitly says "grill me".
---

# Grill Me

Pressure-test a plan or design until the remaining ambiguity is explicit, bounded, and easy to communicate.

## Core Behavior

- First, enumerate every candidate risk you can see across all categories
  below (scope, states/flows, assumptions, wording, decision branches) — keep
  this internal list so nothing drops silently. A later step filters to what
  is worth asking.
- Then surface one focused question at a time, ordered by what most changes
  the feature shape if answered wrong — the user must be able to answer
  without re-reading the whole thread; batched questions get half-answered
  or ignored.
- For each question, provide your recommended answer or default position.
- If a question can be answered from the codebase or docs, explore there
  instead of asking the user.
- Prefer exposing hidden assumptions over inventing extra scope — the goal
  is to sharpen an existing plan, not to bolt on new features under the
  guise of stress-testing.

## When Invoked From Discovery

Scan every section of the discovery document (scope, flows, states,
constraints, out-of-scope, open questions, risks) — not only the first
section or headline. Then prioritize:

- Unclear scope boundaries
- Missing states, flows, or edge cases
- Hidden assumptions
- Ambiguous wording a new reader could misinterpret
- Decision branches that materially change the feature shape

Avoid:
- Deep implementation detail unless it changes scope, user experience, risk, or constraints
- Speculative product expansion that should instead be captured as out of scope

## Stop Condition

Stop when:
- The main branches of the decision tree are resolved or explicitly cut
- The remaining ambiguity is minor and non-blocking
- The caller can clearly document flow, scope, constraints, and risks

## Return To Caller

When the stop condition is met, finish by returning this compact summary
(so the caller — typically `/nf` or `/ct` — can paste it into the doc
without editing):

- Clarifications made
- Scope cuts or out-of-scope decisions
- Hidden assumptions uncovered
- Wording fixes or ambiguity reductions
- Remaining risks or blockers
