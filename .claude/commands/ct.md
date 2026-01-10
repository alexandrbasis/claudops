---
description: Create technical task documentation for developer implementation
---

# Create Task Command

## PRIMARY OBJECTIVE
Create implementation-ready technical documentation for developer implementation. Thoroughly understand the user's idea, review the codebase with Explore sub-agent and all necessary related documents. Adopt a TDD-first workflow where the test plan is authored first and guides the technical decomposition. Exclude any time estimates. Ask if anything is unclear. Think hard.

## Control Gates

### GATE 0: Context Gathering & Requirements Understanding
**Complete BEFORE technical decomposition:**

**STEP 1: Check for pre-work documentation**

Look for existing documentation:
- `tasks/task-YYYY-MM-DD-[feature-name]/JTBD-[feature-name].md` (User needs analysis)
- `product-docs/PRD/PRD-[feature-name].md` (Product requirements)
- `docs/ADR/` for relevant Architecture Decision Records

**STEP 2: Gather context**

**IF pre-work documentation exists:**
- Read all available documents (JTBD, PRD, ADR)
- Use Explore sub-agent to understand affected codebase
- Confirm readiness with user

**IF NO pre-work documentation:**
- Ask user to describe the task/feature
- Ask clarifying questions about objective, users, acceptance criteria
- Use Explore sub-agent to understand affected codebase
- Summarize understanding and confirm with user

**Note**: Deeply understand requirements before proceeding. Use Explore sub-agent extensively.

---

### GATE 1: Technical Decomposition & Test Plan Creation
**Complete AFTER context gathering:**

**FILE**: Create `tasks/task-YYYY-MM-DD-[kebab-case]/tech-decomposition-[feature-name].md`

**TEMPLATE**: Use `@docs/product-docs/templates/technical-decomposition-template.md`

Create technical implementation plan with **TEST PLAN FIRST** (TDD approach):
- Fill in Primary Objective based on JTBD/PRD or user input
- Define comprehensive Test Plan with Given/When/Then structure and include explicit instructions on which existing project test commands (e.g., backend `npm run test`) must be executed
- Detail Implementation Steps with specific files, directories, and changes
- Reference relevant ADRs if architectural decisions were made

**AUTOMATIC PLAN REVIEW:** After creating technical decomposition, automatically invoke agents:

- plan-reviewer
- architect-reviewer

**ITERATIVE FEEDBACK LOOP:** When plan-reviewer or architect-reviewer requires revisions:
1. Address feedback by updating technical decomposition OR ask user for clarification if needed
2. Re-submit with updated document + previous review for context + summary of changes
3. Repeat until plan-reviewer and architect-reviewer approve

**FINAL VALIDATION (after plan-reviewer & architect-reviewer approve):**

Run Codex for cross-AI validation of technical decomposition:

```bash
codex exec "Review the technical decomposition document at [task-directory]/tech-decomposition-[feature-name].md

As a senior technical lead, validate this implementation plan:

1. **Test Plan Quality**: Are tests comprehensive? Missing edge cases? TDD structure correct?
2. **Implementation Completeness**: All acceptance criteria covered? Clear file paths?
3. **Technical Accuracy**: Correct patterns for this codebase? Any architectural issues?
4. **Dependencies**: Are all dependencies identified? Correct order of operations?
5. **Risk Assessment**: Any overlooked technical risks or blockers?

Provide:
- Critical issues that must be fixed before implementation
- Suggestions for improvement
- Overall assessment: APPROVED / NEEDS REVISION

Be thorough - developers will implement exactly what's documented." -m gpt-5.2-codex --full-auto
```

**Process Codex feedback:**
- If NEEDS REVISION with critical issues → Update document, inform user
- If approved with suggestions → Present to user, optionally incorporate
- Add "Cross-AI Validation: PASSED" to document metadata when approved

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

**ACTION:** Use `cc-linear` skill pattern (see `.claude/skills/cc-linear/SKILL.md`):

```bash
cc --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team:
- title: '[Task Name from tech decomposition]'
- description: '[Summary from tech decomposition: objective, key requirements, acceptance criteria]'
- priority: [0-4, default 3]

Return the created issue ID and URL in format:
- Issue ID: WYT-XXX
- URL: https://linear.app/..."
```

**After creation:** Update task document's Tracking & Progress section with returned issue ID and URL.

**Note:** Prompt must be self-contained — spawned session has no context. Include all necessary info directly in the prompt.

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

**Document Structure**: See `@docs/product-docs/templates/technical-decomposition-template.md` for the complete format.

**Key Sections**:
- **Primary Objective**: Clear statement of what we're building
- **Test Plan**: TDD approach with Given/When/Then test cases
- **Implementation Steps**: Detailed steps with files, directories, and changelogs
- **Tracking & Progress**: Linear issue and PR details (updated during workflow)
- **Dependencies**: (for split tasks) Phase dependencies and blocking relationships

---

## FLEXIBILITY NOTES

**For Complex Features** (with full workflow):
- Expect JTBD, PRD, ADR documents to exist
- Technical decomposition builds on top of this foundation
- More detailed planning and review

**For Simple Tasks** (quick workflow):
- Gather requirements directly from user
- Create technical decomposition based on conversation
- Still follow TDD approach with test plan first
- Still get plan-reviewer and architect-reviewer approval