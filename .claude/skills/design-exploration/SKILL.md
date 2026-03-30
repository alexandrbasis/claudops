---
name: design-exploration
description: >-
  Explore codebase and design approaches before implementation. Use when asked
  'explore the design', 'how would this fit', 'design exploration', 'what patterns
  exist for', 'how is X implemented', or when another skill (brainstorm, nf) needs
  codebase context to ground a design proposal.
  NOT for code review (use /sr), NOT for static analysis (use /code-analysis).
context: fork
allowed-tools:
  - Read
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Design Exploration

> **Announcement**: Begin with: "I'm using the **design-exploration** skill for pre-implementation design exploration."

Gather codebase context and explore design approaches before implementation. This skill bridges the gap between "we have an idea" and "we have a concrete design" by grounding proposals in what actually exists in the codebase.

## When This Skill Runs

Typically invoked by `/brainstorm` or `/nf`, but can also run standalone when someone needs to understand how a feature fits into the existing architecture. The caller provides:
- Feature name and initial description
- Known constraints or requirements
- Specific areas to focus on (e.g., "focus on backend sessions module")

## Process

### Step 1: Parallel Context Gathering

Launch **2-3 Explore agents in parallel** (use `model: "haiku"` for speed) to scan different areas simultaneously. What to scan depends on the feature scope — see `references/exploration-checklist.md` for the full checklist.

**For backend features**, scan in parallel:
1. **Data model**: `backend/prisma/schema.prisma` — existing entities, relationships, enums
2. **Closest module**: Find the most similar existing module under `backend/src/` and study its full structure (domain → application → infrastructure → presentation layers)
3. **Shared patterns**: `backend/src/shared/` for reusable utilities, base classes, common types

**For mobile-app features**, scan in parallel:
1. **Navigation**: `mobile-app/app/` directory structure (Expo Router file-based routing)
2. **Components**: `mobile-app/src/components/` for reusable UI components
3. **State management**: Look for Zustand stores under `mobile-app/src/`

**For cross-cutting features** (both backend + mobile), launch agents for both areas.

### Step 2: Synthesize Findings

After agents return, compile a structured findings report:

```
## Codebase Findings

### Existing Patterns
- [Pattern name]: [Where it's used, how it works]

### Data Model
- [Relevant entities and relationships]

### Integration Points
- [Where new code connects to existing code]

### Constraints Discovered
- [Things the codebase enforces that the design must respect]
```

### Step 3: Propose Approaches

Present **2-3 design approaches** with trade-offs. Lead with your recommendation and explain why.

For each approach:
- **What**: Brief description (2-3 sentences)
- **How it fits**: Which existing patterns it follows
- **Trade-offs**: Pros and cons grounded in codebase evidence
- **Effort signal**: Relative complexity (low / medium / high)

### Step 4: Incremental Design Presentation

Once the user picks an approach (or you have a clear winner):

1. Present the design in **200-300 word sections**
2. After each section, check: "Does this look right so far?"
3. Cover these areas (skip irrelevant ones):
   - Architecture: which DDD layers are involved, new modules vs. extending existing
   - Data model: new entities, schema changes, migrations
   - API surface: new endpoints, DTOs, validation rules
   - Domain logic: business rules, domain services
   - UI components: screens, navigation, state management (mobile features)
   - Error handling: failure modes and recovery
   - Testing: what needs unit vs. integration vs. e2e tests

## Output Contract

When this skill completes, it returns to the caller:

1. **Key codebase findings** — existing patterns, data models, integration points discovered
2. **Design approach** — the chosen approach with architecture decisions made
3. **Open questions** — anything that needs further exploration or user decision
4. **Risk flags** — potential issues discovered during exploration (e.g., missing infrastructure, schema limitations)

## Key Principles

- **Evidence-based**: Every design recommendation references actual codebase patterns
- **YAGNI ruthlessly**: Strip unnecessary features from all proposals
- **Follow existing conventions**: New code should look like it belongs in the codebase
- **Multiple choice preferred**: Use `AskUserQuestion` with options when clarifying
- **Parallel exploration**: Always launch Explore agents simultaneously, not sequentially
