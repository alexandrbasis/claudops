---
description: Execute structured TDD implementation following task documents
---

# Start Implementation Command

## PRIMARY OBJECTIVE
You are a Professional Full-Stack Developer executing structured implementation. Implement features systematically with comprehensive tracking on feature branches. You might be asked to: Start Implementation from scratch, Continue Implementation or address code review results. Just clarify what was done before any work.
Consider requirements carefully.

## CONSTRAINTS
- Follow existing task document in `tasks/` directory
- ⚠️ Git writes require explicit user permission:
  - Do **NOT** create commits, push branches, open PRs, merge, rebase, or otherwise modify git state unless the user explicitly approves it.

## Implementation Guidelines

- Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.
- Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.
- Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs).
- Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task.

## WORKFLOW STEPS

### **STEP 0: Context Loading**

**Purpose**: Load project context before implementation. 

0. **Decide the work mode** (must be explicit):
   - **Start**: new implementation from task docs
   - **Continue**: continue an existing branch/partial implementation
   - **Code Review**: address review comments on an existing PR/branch

   If mode is not stated, ask the user which one.

1. **Invoke context-loader skill**:
   ```
   Use Skill tool:
   skill: "context-loader"
   args: "[task_document_path]"
   ```

2. **Review context summary**:
   ```
   Read the generated CONTEXT_SUMMARY.md
   - Related modules found
   - Patterns to follow
   - Key files to reference
   ```

3. **Announce context loaded**:

---

### **STEP 1: Task Validation**

1. **Ask user**: "Which task to implement? Provide task name or path." If it was not provided
   - List tasks in `tasks/` if unclear

2. **Validate document**:
   - Confirm the task exists (either a single `.md` file OR a `tasks/task-YYYY-MM-DD-slug/` directory).
   - Confirm scope is unambiguous:
     - Clear acceptance criteria
     - Clear “done” definition (what must be true for completion)
   - Confirm task status is appropriate (e.g., "Ready for Implementation" vs "Draft") and ask before proceeding if unclear.
   - Confirm Linear issue exists and is referenced (ID/link).
   - Confirm there is an implementation plan (even if small): impacted components + test plan.


### **STEP 2: Setup**
Note: Skip this step when continuing implementation or addressing Code Review Results

#### **Status Updates**
1. **Update task status** to "In Progress" with timestamp
2. **Create feature branch** (name must follow repo convention): `feature/wyt-[ID]-[slug]`
3. **Update task document** with branch name
4. **Permission gate**: If any git operation is required (branch creation, commit, push), ask for explicit approval first.

### **STEP 3: Implementation**

#### **Parallelization (optional)**

If you believe part of the work can be done safely in parallel, use the `parallelization` skill:

- `.claude/skills/parallelization/SKILL.md`

---

#### **Sequential Mode**

#### **Before Each Step:**
1. **Announce**: "Starting Step [N]: [Description]"
2. **Review requirements**: Acceptance criteria, tests, artifacts

#### **During Implementation (TDD Approach):**
1. **Follow agreed Test Plan**: Implement tests based on the Test Plan approved during task creation (Gate 2)
2. **TDD Red-Green-Refactor Cycle**: Follow strict Test-Driven Development:
   - **RED**: Write failing tests first according to approved test plan
   - **GREEN**: Write minimal code to make tests pass
   - **REFACTOR**: Clean up code while keeping tests green
3. **Implement tests by approved categories**:
   - **Business Logic Tests**: As/if defined in approved test plan
   - **State Transition Tests**: As/if defined in approved test plan
   - **Error Handling Tests**: As/if defined in approved test plan
   - **Integration Tests**: As/if defined in approved test plan
   - **User Interaction Tests**: As/if defined in approved test plan
4. **Testing tools**:
   - Prefer silent scripts in AI-agent mode (backend): `npm run test:silent`, `npm run test:unit:silent`, `npm run test:integration:silent`, `npm run test:e2e:silent`
   - Local runs are fine with `npm run test` when you need full output
   - `npm run test:ci` when the Postgres-backed integration suite is required
   - `npm run test:db:start|migrate|stop` scripts to spin up and tear down the Supabase-compatible test DB
5. **TDD Verification**: All tests from approved plan must pass before proceeding to next step

#### **After Each Step:**
1. **Record the step outcome** (single lightweight entry):
   ```markdown
   - [x] ✅ Step [N]: [Description] - Completed
     - **Files**: `path/a.ts`, `path/b.spec.ts` (required)
     - **Tests**: [command run + result] OR "skipped: [reason]" (required)
     - **Notes**: [key decision / caveat] (optional)
   ```

2. **Commit changes (permission gate)**:
   - If the user has **not explicitly approved** git writes: ask for permission **before** any `git` command.
   - If approved and the step is complete: `git add [files] && git commit -m "feat|fix|refactor: [step summary]"`

### **STEP 4: Completion**

#### **Final Verification**
1. **Run quality gates via agent**:
   - Use Task tool with subagent_type: "automated-quality-gate"
   - Provide `task_path` (absolute path to `tasks/task-YYYY-MM-DD-slug/`) and current `branch`
   - Agent runs format/lint/types/tests/build and writes a Quality Gate Report in the task directory



#### **Finalize Task Document**
1. **Update status** to "Ready for Review" with timestamp
2. **Verify all checkboxes are accurate**
3. **Add implementation summary**

### **Step 5: Prepare for Code Review**
1. **Permission gate (required)**:
   - Creating a PR and pushing branches requires **explicit user approval** for git writes.
   - If approval is not given, stop and ask for permission before proceeding.

2. **Validate task documentation**:
   - Use Task tool with subagent_type: "task-pm-validator"
   - Provide the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)

3. **Create PR + sync Linear (single path)**:
   - Use Task tool with subagent_type: "create-pr-agent"
   - Provide the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)
   - This agent handles PR creation and updates the task document with PR links. For Linear updates use the `cc-linear` skill (`.claude/skills/cc-linear/SKILL.md`).
