---
name: ct
description: >-
  Use when a feature, enhancement, or scoped task is clear enough for technical
  planning and the next step is an implementation-ready technical decomposition
  before coding. Trigger on requests like 'create task', 'technical
  decomposition', 'plan implementation', 'break this into implementation steps',
  or after `/nf` or `/product` when the user is ready to plan the build. NOT
  for feature discovery (use /nf), product docs (use /product), brainstorming
  (use /brainstorm), or implementation itself (use /si).
argument-hint: [feature-name | task-name]
allowed-tools: Task, Skill, AskUserQuestion, Read, Glob, Grep, Edit, Write, Bash
---

# Create Task Command

> **Announcement**: Begin with: "I'm using the **ct** skill for technical task creation."

## PRIMARY OBJECTIVE
Create implementation-ready technical documentation that a developer can execute with confidence. Work backward from expected behavior: clarify scope, inspect existing patterns, write the test plan first, then derive implementation steps. Keep the plan concrete, traceable, and free of time estimates.

## CORE PRINCIPLES
- **Test plan first** — define what proves the work is done before describing how to build it
- **Clarify ambiguity before decomposition** — unresolved gray areas become bad plans
- **Follow existing patterns** — extend proven structures before inventing new ones
- **Protect scope** — new ideas become follow-ups, not stealth additions
- **Discover repo conventions** — prefer searching the actual workspace over assuming fixed paths
- **Stay executable** — name files, commands, dependencies, and completion signals explicitly
- **Context is compacted automatically** — for long sessions, save the in-progress decomposition to disk as you go; do not stop early due to token concerns


## Control Gates

### GATE 0: Confirm the Task Is Ready for Technical Planning
**Complete before writing the plan:**

- If no argument is provided, ask what task or feature should be planned
- Determine whether the request is actually ready for decomposition:
  - **Still fuzzy / exploratory** → route to `/nf` or `/brainstorm`
  - **Missing product framing** (goals, business rules, success metrics) → route to `/product`
  - **Ready to build** → continue
- Ask enough clarifying questions to name:
  - objective
  - primary actor or system touchpoint
  - success criteria
  - boundaries / out-of-scope items
  - dependencies, constraints, or non-negotiables
- Exclude time estimates from the plan — this doc is a technical contract, not a schedule; estimates expire fast and mislead consumers of the doc

**Exit criteria:** The task can be stated as a single clear implementation objective with known boundaries.

---

### GATE 1: Discover Source Material and Prior Art
**Complete before codebase exploration:**

Search for inputs instead of assuming one repository layout. Prefer the project's existing document conventions if they already exist.

**Look for (run these Glob calls in a single turn — they are independent):**
- Discovery docs: `**/discovery-*.md`
- Product docs: `**/JTBD-*.md`, `**/PRD*.md`, `**/*requirements*.md`
- Architecture notes: `**/ADR*.md`, `**/*architecture*.md`, `**/*decision*.md`
- Existing plans: `**/tech-decomposition-*.md`, `**/*implementation-plan*.md`
- Optional supporting artifacts: prototypes, flow diagrams, issue links, design notes

**Read the closest relevant artifacts and extract:**
- Canonical task / feature name
- Requirements and success criteria
- Constraints, blockers, and non-negotiables
- Open questions or unresolved markers such as `[NEEDS CLARIFICATION: ...]`
- Prior plan patterns worth reusing for structure or level of detail

**Load shared glossary**: If `product-docs/UBIQUITOUS_LANGUAGE.md` exists, read it. Use its canonical terms throughout the tech-decomposition — module names, behaviors, and acceptance criteria should match the glossary verbatim. If terms in the source PRD/discovery contradict the glossary, flag the conflict and propose canonical phrasing rather than silently inheriting drift.

**Architectural vocabulary**: Load `.claude/skills/architecture-language/LANGUAGE.md` before describing module changes. Use **module / interface / seam / adapter / depth** exactly — don't drift into "component", "service", "API", or "boundary".

**Output location rule:**
- Prefer the repo's current convention for task docs
- If no convention exists, default to:
  `tasks/task-YYYY-MM-DD-[feature-name]/tech-decomposition-[feature-name].md`

**Exit criteria:** You know which inputs are authoritative and where the output doc should live.

---

### GATE 1.5: Requirements Quality and Scope Check
**Complete after reading source material, before decomposition:**

Review the inputs like "unit tests for English." Validate the quality of the requirements themselves, not just their technical feasibility.

| Dimension | What to check |
|-----------|---------------|
| `[Completeness]` | Are major user/system scenarios covered? |
| `[Clarity]` | Can the requirement be interpreted more than one way? |
| `[Consistency]` | Do docs or constraints contradict each other? |
| `[Measurability]` | Can success be objectively verified? |
| `[Coverage]` | Are error states, boundaries, permissions, and edge cases defined? |
| `[Gap]` | What important behavior is still missing from the inputs? |

If important gaps exist:
- Summarize them as 3-7 concrete checklist items tagged with the dimensions above
- Present them to the user with `AskUserQuestion`
- Options:
  - **Fix requirements first** — return to the source docs before planning
  - **Proceed with explicit decisions or blockers** — resolve what can be resolved and capture anything still stopping implementation

Do not hide requirement gaps inside implementation steps.

**Exit criteria:** Requirement gaps are either resolved or explicitly captured as implementation decisions or blockers.

---

### GATE 2: Explore the Codebase
**Complete before writing implementation steps:**

Launch **2-3 Explore agents in a single turn** (fan out in the same tool-call batch — do not sequence them), each with a specific mandate:

1. **Architecture & Patterns** — understand the change area:
   - Closest similar feature, module, or workflow
   - Relevant data models or persisted state
   - Shared abstractions, utilities, or base patterns worth reusing

2. **Change Surface** — identify what needs to be touched:
   - Files and directories that will need modification
   - API surfaces, contracts, background jobs, events, or integrations near the change
   - Test files and test patterns already used in the affected module

3. **Risks & Constraints** — find what could go wrong:
   - Likely failure modes and edge cases
   - Configuration touchpoints and integration boundaries
   - Dependencies that could break or require coordinated changes

**If the task is UI-heavy, also inspect:**
- Existing component composition patterns
- State management and navigation conventions
- Loading, empty, error, success, and accessibility states
- Visual/system constraints already used in the codebase

**Optional adjuncts:**
- If visual uncertainty blocks planning, use `/vp` or another design helper
- If the task changes a user-facing flow and the product tracks analytics, include analytics coverage in the plan

Return a short findings summary:
- existing patterns
- likely files / directories
- integration points
- constraints discovered

**Exit criteria:** The plan can be grounded in real codebase evidence instead of guesses.

---

### GATE 3: Resolve Ambiguity Before Decomposition
**Complete after exploration, before writing the plan:**

Identify gray areas across the inputs and codebase findings:
- Requirements that could be interpreted multiple ways
- Missing acceptance criteria or edge cases
- Technical choices with multiple valid approaches
- Unclear boundaries between current scope and future work

For each gray area:
1. **Resolve from docs or code** if the answer already exists
2. **Ask the user** when product or implementation judgment is required
3. **Mark as blocker/prerequisite** when external input is still missing

**Glossary updates**: if a new domain term appears during ambiguity resolution, or if a term needs sharpening, invoke `/ubiquitous-language` to update `product-docs/UBIQUITOUS_LANGUAGE.md` inline. The decomposition then uses the canonical term, and `/si` and reviewers inherit it.

Document non-trivial choices in the tech-decomposition file:

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | [gray area] | [chosen approach] | [why this is the right choice] |

**Scope guardrail:** This gate clarifies HOW to implement what is already in scope. It does not expand the task. If a new capability emerges, note it as a follow-up instead of folding it into the current plan.

**Exit criteria:** All meaningful ambiguities are resolved or marked as blockers. If an unresolved ambiguity would materially change implementation, the task is not ready for decomposition.

---

### GATE 4: Write the Technical Decomposition
**Complete after context, exploration, and ambiguity resolution:**

**Step 0: Load the Output Shape**
- Before drafting, read `.claude/docs/templates/technical-decomposition-template.md`
- Treat the template as the **output contract**:
  - it defines the expected structure and level of detail
  - the decomposition should contain exactly what is needed to fill it clearly
  - do not restate the template inside the document; use it as the source of truth for the final shape

**Required sections:**
- Linked Inputs / Context
- Primary Objective
- Must Haves
- Test Plan
- Technical Requirements
- Implementation Decisions (if any)
- Implementation Steps
- Dependencies / Risks / Blockers
- Tracking / Notes (optional)

**Planning rules:**
- **Entity lifecycle** (when the task creates, updates, or deletes entities): add a `## Entity Lifecycle` section covering:
  - Creation entry points: where can the entity be created?
  - Persistence defaults: which fields must be set, including semantic defaults (category, type, order, visibility)?
  - Immediate feedback: what confirms success to the user?
  - Canonical visibility: where should the entity appear after creation?
  - Cross-surface visibility: what other pages, lists, widgets, searches, or groupings must reflect it?
  - Data normalization: should existing misclassified or orphaned entities be migrated?
- **Constraint-to-UI traceability**: for every service-layer validation rule in the spec, require a mapped UI element — error message, disabled/hidden option, input hint, or highlighted field. If a validation rule has no corresponding UI affordance, flag it as a gap.
- Add `## Must Haves` immediately after the objective:
  ```markdown
  ## Must Haves
  Non-negotiable truths when this task is complete:
  - [ ] [Observable behavior 1]
  - [ ] [Interface, file, endpoint, or workflow truth 2]
  - [ ] [Constraint or invariant 3]
  ```
  These become the source of truth for goal-backward verification during implementation if that workflow exists.
- Define the **Test Plan before implementation steps**
- If discovery or product docs exist, do **not** restate `Feature Overview`, `Why This Exists`, `How It Works`, or scope sections in full. Translate them into `Must Haves`, `Technical Requirements`, `Implementation Decisions`, and `Implementation Steps`.
- Include explicit verification commands
- Treat `Technical Requirements` as the implementation-facing version of the source requirements
- Use `Implementation Decisions` only for real technical choices, resolved gray areas, or explicit trade-offs. If none were needed, write `No additional implementation decisions required.`
- Break work into clear steps and sub-steps with concrete files, directories, or modules
- State what each step changes and what it proves
- If source requirements exist, assign `REQ-XXX` IDs and tag the relevant steps
- If no formal requirements doc exists, still write explicit requirement statements in plain language
- Add optional wave annotations only when steps are genuinely independent
- Reference constraints or architecture decisions that shaped the plan
- Leave `Issue ID`, `Branch / PR`, `Split status`, and `Completion Summary` blank or omitted unless prior workflow steps produced real values — those fields are owned by later skills (`/si`, tracker integration) and must reflect reality
- Exclude time estimates — this doc is a technical contract, not a schedule; estimates expire fast and mislead consumers of the doc

#### Test Case Format (Given/When/Then)
- **Given**: preconditions already in place
- **When**: the action being exercised
- **Then**: the observable outcome that proves the behavior
- Prefer declarative behavior descriptions over click-by-click UI scripts

**Exit criteria:** A fresh developer could implement the task from the document without needing a separate planning meeting.

---

### GATE 5: Review and Strengthen the Plan
**Complete after the first draft exists:**

**Minimum self-check:**
- Does every must-have map to tests and steps?
- Are any steps scope creep?
- Are blockers and constraints explicit?
- Does the plan follow existing repo patterns?
- Is the test strategy sufficient for the change risk?

**Required review policy:**

| Complexity | Typical signal | Required review |
|------------|----------------|-----------------|
| Simple | 1-2 focused steps | `plan-reviewer` agent |
| Medium | 3-5 steps, multiple touchpoints | `plan-reviewer` agent + `senior-architecture-reviewer` agent |
| Complex | 6+ steps, architecture or cross-system risk | `plan-reviewer` agent + `senior-architecture-reviewer` agent + cross-AI validation |

> Reviewer agents should follow a coverage-then-filter pattern — surface every issue they find (with severity + confidence), and filter in a separate pass. Do not instruct them to report "only important" findings; 4.7 obeys that literally and recall drops.

Follow the review path for the complexity tier above — skipping it has historically produced plans that miss architecture risks and require re-decomposition.
For **Complex** plans, cross-AI validation is part of the required review path. Follow `.claude/docs/templates/cross-ai-protocol.md` if present.

**Additional validation branches and follow-ups:**
- Run `/analyze` when source specs exist and traceability matters
- If the project uses Linear or another tracker and the user wants synced tracking, create or update the issue with the appropriate integration skill/tool

**Feedback loop:** If review finds gaps, revise the decomposition, preserve the known risks and blockers, and re-run the relevant review path until the plan is ready.

**Exit criteria:** The plan is specific, scoped, and reviewable enough to proceed to task splitting evaluation.

---

### GATE 6: Task Splitting Evaluation
**Complete after the required review path and iterative feedback loop are finished:**

Invoke the `task-splitter` agent on the finalized parent plan so the splitting decision is made against the reviewed doc, not a draft. Provide:
- task directory path
- finalized `tech-decomposition-[feature-name].md` path

The `task-splitter` agent either:
- recommends **NO SPLIT** — keep the parent doc active and proceed to handoff
- creates `splitting-decision.md` — present the recommendation with `AskUserQuestion`

If the user approves splitting:
- invoke the `task-decomposer` agent with the task directory
- let it create phase folders and phase tech-decomposition docs aligned to the canonical template, retain the parent doc as reference, and update `splitting-decision.md`
- hand off using the phase documents

If the user declines splitting:
- keep the parent doc active
- proceed to handoff

**Exit criteria:** The task is confirmed as a single implementation unit or decomposed into approved phases.

---

## Output
Create `tech-decomposition-[feature-name].md` in the repo's existing task-doc convention, or in the fallback task directory if no convention exists.

After `GATE 6`, the active output is one of:
- the parent `tech-decomposition-[feature-name].md`, or
- phase-specific tech-decomposition documents created by the `task-decomposer` agent

## Handoff to Implementation

After the gates complete, present a concise summary:

```text
Task ready for implementation:
- Task: [task name]
- Doc: [path to active tech-decomposition or phase docs]
- Key decisions: [resolved / open]
- Traceability: [used / not applicable]
- Split status: [no split | split recommended but declined | phases created]
- Tracking: [optional issue link]

Next steps:
-> Start implementation: /si [task-directory or doc path]
```

## Flexibility Notes
- For small changes, keep the doc lean but still include `Must Haves`, `Test Plan`, and concrete implementation steps
- For large features, keep one parent objective and split only when execution would otherwise be unsafe or vague
- This skill keeps the decomposition core lightweight, but the required review path and the `task-splitter` / `task-decomposer` agent workflow are part of the standard completion path