---
name: improve-codebase-architecture
description: >-
  Find deepening opportunities in a codebase — refactors that turn shallow
  modules into deep ones for better testability and AI-navigability. Use when
  the user wants to improve architecture, find refactoring opportunities,
  consolidate tightly-coupled modules, or make a codebase more testable.
  NOT for code review before merge (use /sr). NOT for spec/requirement gaps
  (use /ct). Reads but does not write code.
allowed-tools: [Read, Grep, Glob, Bash, Task, Skill]
---

# Improve Codebase Architecture

> **Upstream**: Adapted from [mattpocock/skills/improve-codebase-architecture](https://github.com/mattpocock/skills/tree/main/improve-codebase-architecture). Vocabulary and principles draw on Ousterhout (*A Philosophy of Software Design*) and Feathers (*Working Effectively with Legacy Code*). Adapted to use this repo's `tasks/` and `product-docs/` conventions instead of upstream's `CONTEXT.md` + `docs/adr/`.

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## Vocabulary

This skill uses the canonical architecture vocabulary in `.claude/skills/architecture-language/LANGUAGE.md`. Load it before suggesting candidates. Use the terms exactly — **module**, **interface**, **seam**, **adapter**, **depth**, **leverage**, **locality**. Don't drift into "component", "service", "API", or "boundary".

Key principles (full list in `architecture-language/LANGUAGE.md`):

- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

## Process

### 1. Explore

Read existing context first:

- `product-docs/UBIQUITOUS_LANGUAGE.md` — domain terms (use them when naming candidates)
- `product-docs/PRD/*.md` and `product-docs/JTBD/*.md` — which features are load-bearing
- Any active `tasks/task-*/tech-decomposition-*.md` — recent decisions in the area
- `CLAUDE.md` and `{{DOCS_DIR}}/project-structure.md` — architecture conventions

If any of these are missing, proceed silently — don't flag absence or suggest creating them upfront.

Then use the `Explore` agent (subagent_type=Explore) to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Dependency category** — see [DEEPENING.md](DEEPENING.md) (in-process / local-substitutable / remote-but-owned / true-external)

**Use `UBIQUITOUS_LANGUAGE.md` vocabulary for the domain, and `architecture-language/LANGUAGE.md` for the architecture.** If `UBIQUITOUS_LANGUAGE.md` defines "Order", talk about "the Order intake module" — not "the FooBarHandler", and not "the Order service".

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation (invoke `/grill-me`). Walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:

- **Naming a deepened module after a concept not in `UBIQUITOUS_LANGUAGE.md`?** Add the term via `/ubiquitous-language` right there.
- **Want to explore alternative interfaces for the deepened module?** See [INTERFACE-DESIGN.md](INTERFACE-DESIGN.md).
- **User rejects the candidate with a load-bearing reason?** Note it in the relevant `tasks/` doc or `product-docs/` so future architecture passes don't re-suggest the same thing. Skip ephemeral reasons ("not worth it right now") and self-evident ones.

### 4. Output

This skill READS and REPORTS — it does not write code or commit changes. The output is:

- A list of candidates (Step 2)
- Optionally, a deepened-module design (Step 3, after grilling)

If the user wants to act on a candidate:
- Small refactor → handoff to `/quick`
- Larger refactor → handoff to `/ct` to produce a tech-decomposition

## Scope boundaries

- Does NOT propose interfaces upfront — that comes only after the user picks a candidate
- Does NOT re-litigate decisions already documented in `product-docs/` or active `tasks/` docs
- Does NOT write code or modify files outside its own outputs
- Does NOT expand scope to include unrelated tech debt
