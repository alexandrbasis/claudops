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

---

### GATE 2: Task Splitting Evaluation
**Complete AFTER plan review and BEFORE Linear creation:**

**ACTION:** Invoke task-splitter agent with the following prompt:

```
Evaluate if this task should be split into smaller sub-tasks.

Task directory: [absolute path to task folder, e.g., /Users/.../tasks/task-2025-10-16-feature-name/]

Please analyze tech-decomposition-[feature-name].md and provide your decision and reasoning.
```

---

### GATE 3: Linear Issue Creation
**Complete AFTER task splitting evaluation:**

**ACTION:** Use `cg-linear` skill pattern (see `.claude/skills/cg-linear/SKILL.md`):

```bash
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team:
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

```
tasks/task-YYYY-MM-DD-[feature-name]/
├── JTBD-[feature-name].md              (optional)
└── tech-decomposition-[feature-name].md (required)
```

**Document Structure**: See `@docs/product-docs/templates/technical-decomposition-template.md` for the complete format.

**Key Sections**:
- **Primary Objective**: Clear statement of what we're building
- **Test Plan**: TDD approach with Given/When/Then test cases
- **Implementation Steps**: Detailed steps with files, directories, and changelogs
- **Tracking & Progress**: Linear issue and PR details (updated during workflow)

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