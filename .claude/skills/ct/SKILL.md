---
name: ct
description: >-
  Create technical task documentation for developer implementation.
  Use when asked to 'create task', 'technical decomposition', 'plan implementation',
  'task documentation', 'decompose feature', 'prepare for implementation',
  'break down this feature', or when the user has a feature ready for technical
  planning. Also trigger when the user has completed feature discovery (/nf) and
  wants to move to the implementation planning phase, or when a JTBD/PRD exists
  and the next step is a technical plan.
argument-hint: [feature-name]
allowed-tools: Agent, Skill, AskUserQuestion, Read, Glob, Grep, Edit, Write, Bash, TodoWrite
---

# Create Task Command

> **Announcement**: Begin with: "I'm using the **ct** skill for technical task creation."

## PRIMARY OBJECTIVE
Create implementation-ready technical documentation for developer implementation. Thoroughly understand the user's idea, review the codebase with Explore sub-agent and all necessary related documents. Adopt a TDD-first workflow where the test plan is authored first and guides the technical decomposition. Exclude any time estimates. Ask clarifying questions when requirements are ambiguous.

**Routing — wrong skill?**
- Feature discovery/interview → `/nf`
- Product documentation (JTBD/PRD) → `/product`
- Implementation/coding → `/si`
- Brainstorming → `/brainstorm`
- PR review comments → `/prc`

## Control Gates

### GATE 0: Context Gathering & Requirements Understanding
**Complete BEFORE technical decomposition:**

**STEP 1: Check for pre-work documentation**

Look for existing documentation:
- `tasks/task-YYYY-MM-DD-[feature-name]/JTBD-[feature-name].md` (User needs analysis)
- `tasks/task-YYYY-MM-DD-[feature-name]/discovery-[feature-name].md` (Feature discovery from /nf)
- `product-docs/PRD/PRD-[feature-name].md` (Product requirements)
- `docs/ADR/` for relevant Architecture Decision Records

**STEP 2: Check for visual prototype approval (if discovery exists)**

If `discovery-[feature-name].md` exists, check for `vp-approval.md` in the same task directory:

**IF `vp-approval.md` exists with "Status: APPROVED":**
- Read playground file for additional context
- Note any "Key Decisions Confirmed" and "Notes for Technical Decomposition"
- Proceed to STEP 3

**IF `vp-approval.md` exists with "Status: REJECTED":**
- **STOP**: "Visual prototype was rejected. Run `/nf` to refine discovery, then `/vp` to get visual approval before technical decomposition."

**IF discovery exists BUT no `vp-approval.md`:**
- Ask user via AskUserQuestion: "Discovery document found but no visual prototype. Options:"
  - **Skip visual approval** - Proceed directly to technical decomposition (for backend-only or urgent tasks)
  - **Create visual prototype** - Run `/vp` first to visualize and approve the design

**STEP 3: Gather context**

**IF pre-work documentation exists:**
- Read all available documents (JTBD, PRD, ADR)
- **Scan for unresolved `[NEEDS CLARIFICATION: ...]` markers** — if found, present each to user via `AskUserQuestion` and resolve before proceeding. Unresolved markers block tech decomposition.
- Use Explore sub-agent to understand affected codebase (see guidance below)
- Confirm readiness with user

**IF NO pre-work documentation:**
- Ask user to describe the task/feature
- Ask clarifying questions about objective, users, acceptance criteria
- Use Explore sub-agent to understand affected codebase (see guidance below)
- Summarize understanding and confirm with user

**Explore sub-agent guidance** — direct it to investigate:
- Existing patterns in affected directories (how are similar features built?)
- Database schema relevant to the feature (Prisma models in `backend/prisma/`)
- API contracts and DTOs near the change area
- Test patterns used in the affected module
- For mobile: existing components in `mobile-app/src/shared/ui/` and `mobile-app/src/features/`

**STEP 3.5: Reference prior art**

Scan `tasks/completed/` for similar tasks. Read their tech-decomposition to:
- Match the level of detail the team expects
- Identify patterns that worked well (e.g., test plan structure, step granularity)
- Avoid repeating past mistakes noted in review docs

### Analytics Coverage Check (CONDITIONAL)
**Trigger:** If the task touches user-facing screens or flows.
- Invoke `/analytics` skill to review event coverage
- Ensure new screens have corresponding analytics events planned
- Reference `mobile-app/src/shared/analytics/AnalyticsEvents.ts` for existing event catalog

---

### GATE 0.3: Requirements Quality Check ("Unit Tests for English")
**Complete AFTER context gathering (GATE 0), BEFORE ambiguity resolution.**

**Skip if**: No pre-work documentation exists (user described task directly — quality check not applicable).

**Purpose**: Validate the QUALITY of requirements themselves — not technical feasibility, but document completeness, clarity, and consistency. Inspired by spec-driven development "unit tests for English" methodology.

**STEP 1: Analyze spec documents**

Read all gathered spec documents (discovery, JTBD, PRD) and evaluate against quality dimensions:

| Dimension | What to check |
|-----------|--------------|
| `[Completeness]` | Are all user scenarios covered? Are edge cases addressed? |
| `[Clarity]` | Are requirements unambiguous? Can they be interpreted only one way? |
| `[Consistency]` | Do requirements contradict each other? |
| `[Measurability]` | Can success criteria be objectively verified? |
| `[Coverage]` | Are error states, permissions, and boundaries defined? |
| `[Gap]` | What's obviously missing that should be specified? |

**STEP 2: Generate quality checklist**

Produce 5-10 checklist items tagged with quality dimensions:

```markdown
## Requirements Quality Check
- [ ] Are authentication requirements defined for all protected endpoints? [Coverage]
- [ ] Is the error handling behavior specified for network failures? [Gap]
- [ ] Do the sorting requirements conflict with the pagination spec? [Consistency]
- [ ] Can "fast response time" be measured? Define a threshold. [Measurability]
```

**STEP 3: Present to user**

Present unchecked items via `AskUserQuestion`:
- **Acknowledge gaps and proceed** — gaps are noted but don't block planning
- **Fix requirements first** — go back to update discovery/JTBD docs before tech decomposition

**Exit criteria**: User has reviewed quality findings and decided how to proceed.

---

### GATE 0.5: Ambiguity Resolution (Gray Areas)
**Complete AFTER context gathering (GATE 0), BEFORE UI planning or tech decomposition.**

**STEP 1: Identify gray areas**
Review all gathered context (discovery docs, PRD, JTBD, codebase exploration) and identify:
- Requirements that could be interpreted multiple ways
- Missing acceptance criteria or edge cases not covered
- Technical decisions with multiple valid approaches (e.g., sync vs async, REST vs GraphQL)
- Unclear scope boundaries (what's in v1 vs deferred)

**STEP 2: Resolve or escalate**
For each gray area:
1. **If resolvable from existing docs/code** — resolve it, state the decision and evidence
2. **If requires user judgment** — present 2-3 options via `AskUserQuestion` with trade-offs for each
3. **If requires external input** — flag as a prerequisite/blocker

**STEP 3: Document decisions**
Add an `## Implementation Decisions` section to the tech-decomposition document:

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | [gray area] | [chosen approach] | [why — reference to doc, constraint, or user choice] |

**Scope guardrail:** This gate clarifies HOW to implement what's already scoped — it does NOT expand scope. If the user suggests new capabilities during discussion: "That sounds like a separate task. I'll note it but keep this task focused on [original scope]."

**Exit criteria:** All identified gray areas are resolved or explicitly deferred with rationale. Proceed to GATE 0.7 (if UI task) or GATE 1 (if backend task).

---

### GATE 0.7: UI Planning Agent (CONDITIONAL)
**Complete AFTER /vp approval (if used), BEFORE technical decomposition:**

**Trigger:** IF task is UI-heavy (Figma design, screen components, styling, animations)

**Step 1: Determine if agent is needed**

| Signal | Use agent? |
|--------|-----------|
| Implement screen from Figma design | ✅ YES |
| Create UI components with styling/animations | ✅ YES |
| Design tokens mapping tasks | ✅ YES |
| HTTP provider / interceptor setup | ❌ NO |
| Zustand store implementation | ❌ NO |
| Navigation structure setup | ❌ NO |
| Backend / API changes only | ❌ NO |

**Step 2A: IF UI-heavy task**

Invoke `mobile-ui-planning-agent`:

```
Analyze UI requirements for [feature-name].

Feature name: [feature-name]
Task directory: [absolute path to task folder]

Available pre-work (check and use if exists):
- discovery-[feature-name].md (feature discovery)
- playground-[feature-name].html (visual prototype)
- vp-approval.md (visual prototype approval status)

Load skills: design-tokens, component-library, screen-flow, react-native-expo-mobile
Check existing components in mobile-app/src/shared/ui/ and mobile-app/src/features/

Output: ui-planning-analysis-[feature-name].md (consultative reference for tech-decomposition)
```

The agent creates `ui-planning-analysis-[feature-name].md` in the task directory.

**Task directory structure after GATE 0.7:**
```
tasks/task-YYYY-MM-DD-[feature-name]/
├── JTBD-[feature-name].md              (optional)
├── discovery-[feature-name].md         (optional, from /nf)
├── playground-[feature-name].html      (optional, from /vp)
├── vp-approval.md                     (optional, from /vp)
└── ui-planning-analysis-[feature-name].md  ← agent output
```

Tech-decomposition (GATE 1) will reference `ui-planning-analysis-[feature-name].md` as a consultative resource.

**Step 2B: IF NOT UI-heavy (architectural/infrastructure)**

- Skip agent
- Load skills manually if mobile-app files are touched:
  - `react-native-expo-mobile` — always for mobile-app
  - `design-tokens` — if UI styling involved

---

### GATE 1: Technical Decomposition & Test Plan Creation
**Complete AFTER context gathering:**

**FILE**: Create `tasks/task-YYYY-MM-DD-[kebab-case]/tech-decomposition-[feature-name].md`

**TEMPLATE**: Verify template exists at `docs/product-docs/templates/technical-decomposition-template.md`. If missing, search `docs/` recursively for `*decomposition*template*`.

Create technical implementation plan with **TEST PLAN FIRST** (TDD approach):
- **Check Project Constitution**: Read `docs/architecture/constitution.md` — reference relevant articles if the task involves architectural decisions (layer boundaries, database changes, mobile patterns). Include constitution gate checks in the tech decomposition where applicable.
- Fill in Primary Objective based on JTBD/PRD or user input
- **Add `## Must Haves` section** (after Primary Objective):
  ```markdown
  ## Must Haves
  Non-negotiable truths when this task is complete:
  - [ ] [Observable behavior 1]
  - [ ] [File X exists and exports Y]
  - [ ] [API endpoint Z returns correct response]
  ```
  These are verified backwards by the `goal-verifier` agent at the end of `/si` implementation.
- Define comprehensive Test Plan using Given/When/Then format (see below)
- Include explicit test commands (e.g., backend `npm run test`)
- Detail Implementation Steps with specific files, directories, and changes
- **Tag each step with `[REQ-XXX]`** linking to the requirement it fulfills from the discovery/JTBD/PRD doc (see template convention). Steps without a requirement tag may indicate scope creep. The `/analyze` skill (GATE 4) uses these tags for traceability verification.
- **Add optional wave annotations** to steps for parallel execution:
  ```markdown
  ### Step 1: Create domain entities — **Wave 1**
  ### Step 2: Create repository interfaces — **Wave 1**
  ### Step 3: Implement use case (depends on 1, 2) — **Wave 2**
  ```
  Same-wave steps execute in parallel. All must complete before next wave starts. If no waves, `/si` executes sequentially. Only annotate waves when steps are genuinely independent (different modules, no shared files).
- Reference relevant ADRs if architectural decisions were made

#### Test Case Format (Given/When/Then)
- **Given** (past tense): preconditions that are already set up
- **When** (present tense): the action being tested
- **Then** (future tense): the expected outcome
- Prefer **declarative behavior** descriptions over imperative UI steps

**If the plan touches `mobile-app/`:**
- Add a short "**Skill Compliance: react-native-expo-mobile**" section in the doc that lists which skill rule sections were applied (e.g., Core Rendering 1.x, Animation 3.x, React Compiler 8.x, UI 9.x).

**AUTOMATIC PLAN REVIEW:** Scale review intensity based on task complexity — this avoids unnecessary overhead for simple tasks while ensuring thorough review for complex ones.

| Complexity | Implementation Steps | Reviews Required |
|------------|---------------------|-----------------|
| Simple     | 1-2                 | plan-reviewer only |
| Medium     | 3-5                 | plan-reviewer + senior-architecture-reviewer |
| Complex    | 6+                  | plan-reviewer + senior-architecture-reviewer |

**ITERATIVE FEEDBACK LOOP:** When reviewers require revisions:
1. Address feedback by updating technical decomposition OR ask user for clarification if needed
2. Re-submit with updated document + previous review for context + summary of changes
3. Repeat until all required reviewers approve

**CROSS-AI VALIDATION:**

Invoke `/codex-cli`, `/gemini-cli`, and `/cursor-cli` skills in parallel.
Format output per `docs/product-docs/templates/cross-ai-protocol.md` (comparison table, validation, verdict).

- **FOCUS**: Tech decomposition review as senior technical lead — test plan quality, implementation completeness, technical accuracy, dependencies, risk assessment
- **FILE_REFS**: `tech-decomposition-[feature].md` + relevant codebase paths
- **OUTPUT**: Append consolidated verdict to tech decomposition document

If no CLI available: note "Cross-AI Validation: SKIPPED — approved by required reviewers" and proceed.

---

### GATE 2: Task Splitting Evaluation
**Complete AFTER plan review and BEFORE Linear creation:**

**STEP 2.1: Analyze task scope**

Invoke task-splitter agent:

```
Evaluate if this task should be split into smaller sub-tasks.

Task directory: [absolute path to task folder, e.g., /Users/.../tasks/task-2025-10-16-feature-name/]

Please analyze tech-decomposition-[feature-name].md and provide your decision and reasoning.
```

**STEP 2.2: Check splitting decision**

After task-splitter completes:

- **IF `splitting-decision.md` created with SPLIT RECOMMENDED:**
  1. Present the splitting decision summary to user
  2. Ask user: "Task splitter recommends splitting into N phases. Review splitting-decision.md and confirm: Proceed with decomposition?"
  3. **IF user approves:** Proceed to GATE 2.5
  4. **IF user rejects:** Proceed to GATE 3 (single Linear issue)

- **IF NO SPLIT RECOMMENDED:**
  - Proceed to GATE 3 (single Linear issue)

---

### GATE 2.5: Task Decomposition (if split approved)
**Complete ONLY IF task-splitter recommended split AND user approved:**

**ACTION:** Invoke task-decomposer agent:

```
Execute the approved splitting decision.

Task directory: [absolute path to task folder]

Create phase folders, generate phase tech-decompositions, and create Linear sub-issues.
```

**task-decomposer will:**
1. Create `phase-N-[name]/` folders for each phase
2. Generate full tech-decomposition document for each phase (extracted from parent)
3. Archive parent document as `initial-tech-decomposition-[feature]-ARCHIVED.md`
4. Create Linear sub-issues for each phase via cc-linear
5. Update phase docs with Linear IDs
6. Update splitting-decision.md with completion summary

**After GATE 2.5:** SKIP GATE 3 (Linear issues already created by decomposer)

---

### GATE 3: Linear Issue Creation
**Complete AFTER task splitting evaluation (ONLY if NOT split or user rejected split):**

**ACTION:** Use `linear-api.sh` (see `.claude/skills/cc-linear/SKILL.md`):

```bash
# For short descriptions:
.claude/scripts/linear-api.sh create-issue "[Task Name]" "[Summary: objective, requirements, acceptance criteria]" 3

# For long descriptions (stdin):
.claude/scripts/linear-api.sh create-issue "[Task Name]" "-" 3 <<'EOF'
## Context
[objective]

## Requirements
- [requirement 1]
- [requirement 2]

## Acceptance Criteria
- [ ] [criterion 1]
- [ ] [criterion 2]
EOF
```

**After creation:** Parse JSON response for `identifier` and `url`, update task document's Tracking & Progress section.

---

### GATE 4: Cross-Artifact Consistency Check
**Complete AFTER Linear issue creation (GATE 3) or task decomposition (GATE 2.5), BEFORE handoff.**

**Purpose**: Verify that the tech decomposition fully covers all requirements from spec documents. Catches drift between what was specified and what was planned — before implementation begins.

**ACTION**: Invoke the `/analyze` skill with the task directory:

The analyze skill will:
1. Read spec documents (discovery/JTBD/PRD) and tech decomposition
2. Build a traceability matrix: requirement → test case → implementation step
3. Flag gaps: `[UNCOVERED]`, `[UNTESTED]`, `[SCOPE CREEP]`, `[CONFLICT]`
4. Report verdict: ALIGNED or GAPS FOUND

**Handle verdict:**
- **ALIGNED** → Proceed to handoff
- **GAPS FOUND** → Present gaps to user via `AskUserQuestion`:
  - **Fix gaps** — update tech decomposition to cover missing requirements
  - **Acknowledge and proceed** — gaps are intentional, proceed to handoff
  - **Re-run /nf** — spec docs need revision

**Skip conditions**: No spec documents exist (task was created without `/nf` or `/product` docs).

---

## FINAL TASK DOCUMENT STRUCTURE

After all gates complete, task directory contains:

### Single Task (no split)
```
tasks/task-YYYY-MM-DD-[feature-name]/
├── JTBD-[feature-name].md              (optional)
└── tech-decomposition-[feature-name].md (required, with Linear issue)
```

### Split Task (after GATE 2.5)
```
tasks/task-YYYY-MM-DD-[feature-name]/
├── JTBD-[feature-name].md                        (optional)
├── SPEC-[feature-name].md                        (optional)
├── initial-tech-decomposition-[feature]-ARCHIVED.md  (archived parent)
├── splitting-decision.md                          (with completion summary)
├── phase-1-[name]/
│   └── tech-decomposition-phase-1-[name].md      (with Linear issue WYT-XXX)
├── phase-2-[name]/
│   └── tech-decomposition-phase-2-[name].md      (with Linear issue WYT-XXX)
└── phase-N-[name]/
    └── tech-decomposition-phase-N-[name].md      (with Linear issue WYT-XXX)
```

**Document Structure**: See `docs/product-docs/templates/technical-decomposition-template.md` for the complete format.

**Key Sections**:
- **Primary Objective**: Clear statement of what we're building
- **Test Plan**: TDD approach with Given/When/Then test cases
- **Implementation Steps**: Detailed steps with files, directories, and changelogs
- **Tracking & Progress**: Linear issue and PR details (updated during workflow)
- **Dependencies**: (for split tasks) Phase dependencies and blocking relationships

---

## HANDOFF TO IMPLEMENTATION

After all gates complete (0 → 0.3 → 0.5 → 0.7 → 1 → 2 → 2.5 → 3 → 4 → HANDOFF), present a summary to the user:

```
Task ready for implementation:
- Task: [task name]
- Linear: WYT-XXX
- Consistency: [ALIGNED | GAPS ACKNOWLEDGED]
- Doc: tasks/task-YYYY-MM-DD-[name]/tech-decomposition-[name].md

Next steps:
→ Start implementation: /si [task-directory]
→ Review plan alignment: /rip [task-directory]
→ Review plan visually: /plan-review
```

---

## FLEXIBILITY NOTES

**For Complex Features** (with full workflow):
- Expect JTBD, PRD, ADR documents to exist
- Technical decomposition builds on top of this foundation
- Reviews scaled by complexity table in GATE 1

**For Simple Tasks** (quick workflow):
- Gather requirements directly from user
- Create technical decomposition based on conversation
- Still follow TDD approach with test plan first
- Reviews scaled by complexity table in GATE 1 (typically plan-reviewer only)
