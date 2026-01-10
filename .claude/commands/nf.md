---
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion, Task, Skill
argument-hint: [feature-name]
description: Detalize new feature through in-depth interview
---

# New Feature Detalization

## Objective
Conduct a comprehensive interview to fully understand and document a new feature using collaborative brainstorming, then create a formal specification.

## Guidelines
- Invoke brainstorming skill first for discovery and exploration
- **Use `AskUserQuestion` tool for ALL clarifications** - provides interactive options for user to choose from
- Ask non-obvious and thought-provoking questions
- Continue until the feature is fully understood
- Document everything in the specification file

## Workflow

### Step 1: Brainstorming Phase
**Invoke the `brainstorming` skill** which will:
- Use multiple Explore agents in parallel (Sonnet) to gather project context
- Ask questions to refine the idea (batch related questions)
- Propose 2-3 different approaches with trade-offs
- Present design incrementally (200-300 word sections) for validation

### Step 2: Deep-Dive Questions
After brainstorming, ask additional **non-obvious** questions if needed:

**Technical Implementation:**
- Edge cases and failure scenarios
- Performance implications at scale
- Integration points with existing systems
- Security and privacy implications

**UI/UX:**
- User mental models and expectations
- Error states and recovery flows
- Accessibility considerations

**Business & Product:**
- Success metrics and how to measure them
- MVP vs future scope boundaries
- Potential abuse scenarios

**Tradeoffs:**
- Complexity vs flexibility
- Development speed vs technical debt

### Step 3: Specification Writing

Use @docs/product-docs/templates/discovery-template.md

After brainstorming and interview completion:

1. **Create task directory**: `tasks/task-YYYY-MM-DD-[feature-name]/`
2. **Write specification**: Use template from `docs/product-docs/templates/discovery-template.md`
   - Output file: `discovery-[feature-name].md`
3. **Present summary** to user for confirmation

### Step 4: Codex Validation

After discovery document is created, run Codex for cross-AI validation:

```bash
codex exec "Review the feature discovery document at [task-directory]/discovery-[feature-name].md

As a senior product analyst, validate this discovery:

1. **Completeness**: Are all user scenarios covered? Missing edge cases?
2. **Consistency**: Any contradictions between sections?
3. **Clarity**: Are requirements specific enough for implementation?
4. **Feasibility**: Any technical concerns or risks not addressed?
5. **Scope**: Is MVP scope clearly defined vs future phases?

Provide:
- List of inconsistencies or gaps found
- Suggested clarifying questions for the user
- Overall assessment: APPROVED / NEEDS CLARIFICATION

Be critical - this is the last check before technical decomposition." -m gpt-5.2-codex --full-auto
```

**Process Codex feedback:**
- If NEEDS CLARIFICATION → Ask user the suggested questions, update discovery
- If issues found → Present to user, update document if confirmed
- Add "Cross-AI Validation: PASSED" note to discovery document when approved

## Output
`tasks/task-YYYY-MM-DD-[feature-name]/discovery-[feature-name].md`