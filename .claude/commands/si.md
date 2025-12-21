---
description: Execute structured TDD implementation following task documents
---

# Start Implementation Command

## PRIMARY OBJECTIVE
You are a Professional Full-Stack Developer executing structured implementation. Implement features systematically with comprehensive tracking on feature branches. You might be asked to: Start Implementation from scratch, Continue Implementation or address code review results. Just clarify what was done before any work.
Consider requirements carefully.

## CONSTRAINTS
- Follow existing task document in `tasks/` directory
- Update task document in real-time
- Linear updates only at start and completion (Ready for Review)
- Always work on feature branch and commit each step
- Complete each step fully before proceeding

## Implementation Guidelines

- Avoid over-engineering. Only make changes that are directly requested or clearly necessary. Keep solutions simple and focused.
- Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.
- Don't add error handling, fallbacks, or validation for scenarios that can't happen. Trust internal code and framework guarantees. Only validate at system boundaries (user input, external APIs).
- Don't create helpers, utilities, or abstractions for one-time operations. Don't design for hypothetical future requirements. The right amount of complexity is the minimum needed for the current task.

## WORKFLOW STEPS

### **STEP 1: Task Validation**

1. **Ask user**: "Which task to implement? Provide task name or path." If it was not provided
   - List tasks in `tasks/` if unclear

2. **Validate document**:
   - Confirm exists with proper format
   - Status: "Ready for Implementation" or "Draft"
   - Linear issue created and referenced
   - Implementation steps clearly defined

3. **Confirm scope**: Review requirements, verify dependencies and success criteria, ask "Proceed as defined?"

### **STEP 2: Setup**
Note: Skip this step when continuing implementation or addressing Code Review Results

#### **Status Updates**
1. **Update task status** to "In Progress" with timestamp
2. **Update Linear** using `cg-linear` skill pattern:
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Progress'"
   ```
   **Reference**: See `.claude/skills/cg-linear/SKILL.md` for details
3. **Create feature branch**: `git checkout -b feature/[task-id]-[slug]`
4. **Update task document** with branch name

#### **Pre-Implementation**
1. **Review project docs** and affected codebase areas
2. **Verify existing test patterns** and check recent changes
3. **Setup test environment** and verify test runner works

### **STEP 3: Implementation**

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
   - **Business Logic Tests**: As\If defined in approved test plan
   - **State Transition Tests**: As\If defined in approved test plan
   - **Error Handling Tests**: As\If defined in approved test plan  
   - **Integration Tests**: As\If defined in approved test plan
   - **User Interaction Tests**: As\If defined in approved test plan
4. **Testing tools**:
   - `npm run test` / `npm run test -- --coverage` (Jest with ts-jest)
   - `npm run test:ci` when the Postgres-backed integration suite is required
   - `npm run test:db:start|migrate|stop` scripts to spin up and tear down the Supabase-compatible test DB
5. **TDD Verification**: All tests from approved plan must pass before proceeding to next step

#### **After Each Step:**
1. **Update progress**:
   ```markdown
   - [x] ✅ Step [N]: [Description] - Completed
     - **Notes**: [Key decisions, challenges]
   ```

2. **Add changelog**:
   ```markdown
   ### Changelog:

   [ISO-Timestamp] — [Icon] [Action] [file/path]: [detailed description of changes]

   Icons:
   - ✳️ Created (new files)
   - ♻️ Updated (modified files)
   - 🗑️ Deleted (removed files)
   - 🔧 Fixed (bug fixes)
   - ✅ Tests (test additions/updates)

   Example entries:
   2025-09-27T20:35Z — ✳️ Created src/models/schedule.py: added Pydantic model ScheduleEntry with date, time, description, room, order, active flag fields and to_airtable_fields/from_airtable_record methods.

   2025-09-27T20:35Z — ✅ Created tests/unit/test_models/test_schedule.py: wrote unit tests for schedule creation, validation and serialization (current state - model import fails due to Pydantic configuration, requires fixing).

   2025-09-27T20:35Z — ♻️ Updated src/models/__init__.py: exported ScheduleEntry and expanded model package description.
   ```

3. **Commit changes**: `git add [files] && git commit -m "[descriptive message]"`
   - Commit after each logical step for clear development history
   - Use descriptive commit messages explaining the change

### **STEP 4: Completion**

#### **Final Verification**
1. **Run complete test suite** using the project's npm script and capture actual output:
   ```bash
   cd backend
   npm run test -- --coverage
   ```
   If other packages are affected, run their `npm run test` scripts as well and record the logs in the task document.
2. **Verify success criteria**


#### **Finalize Task Document**
1. **Update status** to "Ready for Review" with timestamp
2. **Complete changelog** and verify all checkboxes
3. **Add implementation summary**

### **Step 5: Prepare for Code Review**
1. **Update Linear status** (separate from comment):
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Review'. Do NOT modify description."
   ```

2. **Add completion comment** (separate call):
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
   'Implementation completed.
   - Key changes: [list main changes]
   - Test coverage: [X]%
   - Technical notes: [any notable decisions]
   PR ready for review.'"
   ```
   **Important**: Always use separate prompts for status updates and comments to prevent description overwrite.
   **Reference**: See `.claude/skills/cg-linear/SKILL.md` for details on separate operations.

3. **Prepare the task document for the Code review and clean it up**
4. **Push feature branch**: `git push origin feature/[branch-name]`
#### **Call task-pm-validator to validate task documentation**:
   - Use Task tool with subagent_type: "task-pm-validator"
   - Provide task-pm-validator the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)
   - Agent will validate documentation completeness and accuracy before code review
#### **Call create-pr-agent to create a PR**:
   - Use Task tool with subagent_type: "create-pr-agent"
   - **IMPORTANT**: Provide the exact task document path (e.g., `tasks/task-2025-01-15-feature-name.md`)
   - Agent will create PR, update task document with PR links, and sync with Linea
#### **Present completion**
"Implementation complete. All tests passing with [X]% coverage. Task documentation validated. PR created and ready for code review."

## ERROR HANDLING

1. **Document blocker** in task notes
2. **Update Linear** with issue info
3. **Ask user** for guidance with solutions
4. **Set status** to "Blocked" if stuck