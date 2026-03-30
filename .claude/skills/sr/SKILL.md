---
name: sr
description: >-
  Conduct comprehensive code review before PR merge. Use when asked to
  'review code', 'start code review', 'review PR', 'check before merge',
  'pre-merge review', 'review my changes', 'look at my code', 'review this
  branch', 'is this ready to merge', 'check my implementation', or when
  a task document shows "Implementation Complete" status and needs review
  before merge. This is the primary code review workflow — always use it
  for pre-merge review, even for small changes. NOT for addressing review
  comments (use /prc), NOT for code exploration (use /code-analysis).
argument-hint: [task-path or PR-url]
allowed-tools: Agent, Skill, Read, Glob, Grep, Write, Edit, Bash, AskUserQuestion, TodoWrite
---

# Start Review Command

> **Announcement**: Begin with: "I'm using the **sr** skill for comprehensive code review."

## PRIMARY OBJECTIVE

Professional code review using specialized agents. Each agent writes findings directly to its designated section in a shared Code Review document, returning only a short summary to the orchestrator. This minimizes context window usage while producing a comprehensive, human-readable review.

## SHARED MEMORY PROTOCOL

Section markers let multiple agents write to the same document without coordinating — like separate lanes on a highway. Each agent owns its section exclusively, so Edit conflicts are avoided by design.

- **CR File**: `Code Review - [Task].md` in the task directory
- **Template**: `docs/product-docs/templates/code-review-template.md`
- **Section markers**: `<!-- SECTION:name -->` ... `<!-- /SECTION:name -->`
- **Known sections**: summary, quality-gate, spec-compliance, approach-review, security, code-quality, test-coverage, documentation, performance, cross-ai-validation, consolidated, decision, metadata
- **All agents**: Write directly to the CR file between their designated section markers using the Edit tool. Each agent's placeholder text is unique — use it as the `old_string` for Edit.
- **All agents return**: A short text summary (~1 sentence with severity counts), prefixed with the structured header from `.claude/docs/references/agent-return-protocol.md` (STATUS/SUMMARY/FINDINGS). Orchestrator pattern-matches on `## STATUS:` to determine next action.
- **Edit conflict recovery**: If an Edit fails (e.g., placeholder already replaced by a concurrent agent), re-read the CR file to get fresh content and retry once.

## WORKFLOW

### GATE 1: Task Identification

1. **Resolve task input**:
   - If `$ARGUMENTS` provided → use it directly as the task path or PR URL
   - If not provided → **AskUserQuestion**: "Which task to review? Provide task path or PR URL."

2. **Validate**:
   - Task document exists with "Implementation Complete" status
   - **STOP if**: "In Progress" or missing PR information
   - Linear issue referenced, steps marked complete (optional — skip if no Linear issue)

3. **Detect Existing Review**:
   - Search task directory for `Code Review - *.md` files
   - If found, read the file to check header **Status** and look for `<!-- CR-STATE:` block
   - If Status is `NEEDS FIXES` or `NEEDS_REWORK`:
     - Parse the `<!-- CR-STATE: {...} -->` JSON block to extract `review_commit` and `agents_with_findings`
     - **AskUserQuestion**: "Previous review found (Status: [STATUS], Round [N]). Choose:\n1. **Re-review** — re-run all agents on changes since last review, verify previous findings\n2. **Full review** — start fresh with a complete review"
     - If **Re-review**: set `INCREMENTAL_MODE = true`, store `PREV_CR_PATH`, `PREV_REVIEW_COMMIT`, and `PREV_AGENTS_WITH_FINDINGS`
     - If **Full review**: rename existing CR file with `(Round N)` suffix to preserve history, proceed normally
   - If Status is `APPROVED` or no existing CR file: proceed with normal full review

### GATE 1.5: Size Assessment

Determine review scope to avoid wasting tokens on trivial changes — running 7+ agents on a 10-line hotfix provides little value over a focused review.

1. Count `CHANGED_FILES` and total diff lines from the upcoming diff computation (peek with `git diff main...HEAD --stat`)
2. If changed files ≤ 3 AND diff lines ≤ 50:
   - **AskUserQuestion**: "Small PR detected ([N] files, [M] lines changed). Choose review scope:\n1. **Quick review** — quality gate + code quality + security only (faster, fewer tokens)\n2. **Full review** — all 7 agents (comprehensive)"
   - If **Quick review**: set `QUICK_MODE = true` — skip GATE 4 (approach review) and run only `security-code-reviewer` + `code-quality-reviewer` in GATE 5 (skip test-coverage, documentation, performance agents). Also skip GATE 7 (cross-AI validation).
3. Otherwise: proceed with full review

### STEP 2: Scaffold Code Review File

#### Full Review Mode (default)

1. **Read** template from `docs/product-docs/templates/code-review-template.md`
2. **Replace** header placeholders:
   - `[Task Title]` → task name from task document
   - `YYYY-MM-DD` → today's date
   - `[path/to/task-directory]` → actual task path
   - `[PR URL]` → PR URL from task document (or "N/A")
3. If renaming a previous CR file, do so before writing the new one
4. **Write** to `[task-directory]/Code Review - [Task].md`
5. Store the **absolute file path** as `CR_FILE_PATH` for all agent prompts

#### Incremental Re-Review Mode (INCREMENTAL_MODE = true)

1. **Re-use** the existing CR file at `PREV_CR_PATH` as `CR_FILE_PATH`
2. **Update** the header:
   - Date → today's date
   - Status → `RE-REVIEW IN PROGRESS`
   - Add `**Round**: N` (increment from CR-STATE round, or "2" if first re-review)
3. **Do NOT** clear existing section content — agents will update their own sections

### STEP 2.5: Compute Diff Context

Compute the PR diff ONCE before spawning any review agent. Scoping agents to changed code prevents noise from pre-existing issues — reviewers should focus on what the PR actually introduces, keeping feedback actionable.

**Path exclusions** (used in all git diff commands below):
```
-- . ':(exclude)package-lock.json' ':(exclude)*.lock' ':(exclude)*.generated.*' ':(exclude)prisma/migrations'
```

#### Full Review Mode (default)

1. **Changed files list**:
   ```bash
   git diff main...HEAD --name-only [PATH_EXCLUSIONS]
   ```
   Store as `CHANGED_FILES`.

2. **Full unified diff**:
   ```bash
   git diff main...HEAD [PATH_EXCLUSIONS]
   ```
   Store as `FULL_DIFF`.

   **Size guard**: If `FULL_DIFF` exceeds ~50,000 characters, truncate and note: "Diff truncated — agents should read files from CHANGED_FILES for full context."

3. **Current commit hash**:
   ```bash
   git rev-parse HEAD
   ```
   Store as `REVIEW_COMMIT_SHA`.

#### Incremental Re-Review Mode (INCREMENTAL_MODE = true)

1. **Verify previous commit is reachable**:
   ```bash
   git cat-file -t [PREV_REVIEW_COMMIT] 2>/dev/null
   ```
   If this fails (commit was amended/rebased/force-pushed), **fall back to Full Review** with a warning: "Previous review commit [SHA] is unreachable (likely due to rebase/amend). Running full review instead." Reset `INCREMENTAL_MODE = false` and use Full Review Mode above.

2. **Incremental changed files** (what changed since last review):
   ```bash
   git diff [PREV_REVIEW_COMMIT]...HEAD --name-only [PATH_EXCLUSIONS]
   ```
   Store as `INCREMENTAL_CHANGED_FILES`.

3. **Full PR changed files** (entire PR scope for context):
   ```bash
   git diff main...HEAD --name-only [PATH_EXCLUSIONS]
   ```
   Store as `CHANGED_FILES`.

4. **Full unified diff** (entire PR for agent context):
   ```bash
   git diff main...HEAD [PATH_EXCLUSIONS]
   ```
   Store as `FULL_DIFF` (with same size guard).

5. **Current commit hash**: `git rev-parse HEAD` → `REVIEW_COMMIT_SHA`

#### Both Modes

- **Write preliminary metadata** to `<!-- SECTION:metadata -->`:
  ```markdown
  **Review Commit**: [REVIEW_COMMIT_SHA]
  **Changed Files** ([N] files):
  - `path/to/file1.ts`
  - `path/to/file2.ts`
  ```
- **All agent prompts** in GATE 3, 4, and 5 MUST include `changed_files` and `full_diff`.
- In incremental mode, also include `incremental_changed_files` in GATE 4 and 5 prompts.

### STEP 2.7: Pre-Flight Verification
Before running any review agents, verify the implementation is actually complete:

1. **Files exist:** For each file in `CHANGED_FILES`, verify it exists on disk
2. **Tests pass:** Run `npm run test:silent` from `backend/` — must exit 0
3. **Branch is clean:** `git status --porcelain` must return empty (no uncommitted changes)
4. **Build succeeds:** Run `npm run build` from `backend/` — must exit 0

**If ANY pre-flight check fails:**
- Set CR file header Status → `PRE-FLIGHT FAILED`
- Write failure details to `<!-- SECTION:summary -->`
- **STOP** — notify developer: "Pre-flight verification failed: [specific failure]. Fix before requesting review."
- Do NOT proceed to GATE 3 or any review agents

This gate prevents wasting review agent tokens on code that doesn't compile or pass tests.

### GATE 3: Automated Quality Gate

**ACTION**: Invoke `automated-quality-gate` agent

```
Task directory: [path]
cr_file_path: [CR_FILE_PATH]
changed_files: [CHANGED_FILES]
Run quality checks (format, lint, types, tests, build).
Write results to your section in the CR file between <!-- SECTION:quality-gate --> markers.
Return short summary only.
```

- **Read agent summary** → If status is `GATE_FAILED`:
  - Edit CR file header Status → `GATE_FAILED`
  - Edit `<!-- SECTION:summary -->` → "Review terminated at Quality Gate. [agent summary]"
  - **STOP** — notify developer with fixes list
- Agent has written its findings to the CR file

### GATE 4a: Spec Compliance Review (Sequential Gate)

**Skip if**: `QUICK_MODE = true`

**ACTION**: Invoke `spec-compliance-reviewer` agent

> **Purpose**: Verify the implementation matches what was specified — before checking architecture or code quality. This prevents wasting tokens reviewing code that doesn't implement the spec.

**Standard prompt:**

```
Task directory: [path]
cr_file_path: [CR_FILE_PATH]
changed_files: [CHANGED_FILES]
full_diff: [FULL_DIFF]
Verify each acceptance criterion from the task document is implemented in code.
Do NOT trust implementer's claims or task document checkboxes. Read actual code files.
FOCUS on changed files/lines. You MAY read unchanged files for context but do NOT flag pre-existing issues.
Write results to your section in the CR file between <!-- SECTION:spec-compliance --> markers.
Return short summary only.
```

**Incremental additions** (append when `INCREMENTAL_MODE = true`):

```
incremental_changed_files: [INCREMENTAL_CHANGED_FILES]
INCREMENTAL RE-REVIEW (Round [N]):
FOCUS on incremental changes (incremental_changed_files).
[If PREV_AGENTS_WITH_FINDINGS includes this agent:]
Previous findings to verify resolution:
[paste Critical/Major findings from previous CR-STATE]
Mark each as: RESOLVED / STILL OPEN. Also flag any NEW issues.
[Else:]
No previous findings. Check for any NEW issues in the incremental changes.
```

- **Read agent summary** → If status is `NON_COMPLIANT`:
  - Edit CR file header Status → `NEEDS_REWORK`
  - Edit `<!-- SECTION:summary -->` → "Review terminated at Spec Compliance. [agent summary]"
  - **STOP** — notify developer with missing/partial requirements
- If `COMPLIANT` → proceed to GATE 4b

### GATE 4b: Architecture & Approach Review (Sequential Gate)

**Skip if**: `QUICK_MODE = true`

**ACTION**: Invoke `senior-architecture-reviewer` agent

> **Sequential dependency**: GATE 4b runs only after GATE 4a (spec compliance) passes. Architecture review on non-compliant code is wasted effort.

**Standard prompt:**

```
Task directory: [path]
cr_file_path: [CR_FILE_PATH]
changed_files: [CHANGED_FILES]
full_diff: [FULL_DIFF]
Review architecture fit, TDD compliance, solution approach, and best practices.
Spec compliance has already been verified by a separate agent — focus on HOW the code is structured, not WHETHER it meets requirements.
FOCUS on changed files/lines. You MAY read unchanged files for context but do NOT flag pre-existing issues.
Write results to your section in the CR file between <!-- SECTION:approach-review --> markers.
Return short summary only.
```

**Incremental additions** (append when `INCREMENTAL_MODE = true`):

```
incremental_changed_files: [INCREMENTAL_CHANGED_FILES]
INCREMENTAL RE-REVIEW (Round [N]):
FOCUS on incremental changes (incremental_changed_files).
[If PREV_AGENTS_WITH_FINDINGS includes this agent:]
Previous findings to verify resolution:
[paste Critical/Major findings from previous CR-STATE]
Mark each as: RESOLVED / STILL OPEN. Also flag any NEW issues.
[Else:]
No previous findings. Check for any NEW issues in the incremental changes.
```

- **Read agent summary** → If status is `NEEDS_REWORK`:
  - Edit CR file header Status → `NEEDS_REWORK`
  - Edit `<!-- SECTION:summary -->` → "Review terminated at Architecture Review. [agent summary]"
  - **STOP** — notify developer with issues
- Agent has written its findings to the CR file

### GATE 5: Code Quality Review (runs ONLY after GATE 4a + 4b pass)

**ACTION**: Invoke review agents **IN PARALLEL** (single message, multiple Agent calls).

**Agent selection**:
- **Full review** (`QUICK_MODE = false`): All 5 agents below
- **Quick review** (`QUICK_MODE = true`): Only `security-code-reviewer` + `code-quality-reviewer`

**In both modes**: Run selected agents in parallel. In incremental mode, all agents review the incremental changes to prevent blind spots where fixing one issue introduces a new one in a different domain.

Each agent receives `cr_file_path`, `changed_files`, and `full_diff`, and writes directly to its section in the CR file using the Edit tool.

**Incremental additions** (append to each agent's standard prompt when `INCREMENTAL_MODE = true`):
- **Agents WITH previous findings**: `"INCREMENTAL RE-REVIEW (Round [N]): incremental_changed_files: [LIST]. FOCUS on incremental changes. Previous findings to verify: [findings list]. Mark each as RESOLVED/STILL OPEN. Also flag NEW issues."`
- **Agents WITHOUT previous findings**: `"INCREMENTAL RE-REVIEW (Round [N]): incremental_changed_files: [LIST]. FOCUS on incremental changes. Check for any NEW issues introduced since last review."`

**Agent failure handling**: If any agent fails to return or errors out, write to its section:
`*[Agent name] encountered an error and could not complete its review. Section not assessed.*`
Continue with consolidation using available results — do not block the entire review for one failed agent.

1. **`security-code-reviewer`**:
   ```
   Review security: OWASP, input validation, auth. Task: [path]
   cr_file_path: [CR_FILE_PATH]
   changed_files: [CHANGED_FILES]
   full_diff: [FULL_DIFF]
   FOCUS on changed files/lines. You MAY read unchanged files for context but do NOT flag pre-existing issues.
   Write findings to your section in the CR file between <!-- SECTION:security --> markers.
   Return short summary only.
   ```

2. **`code-quality-reviewer`**:
   ```
   Review quality: SOLID, DRY, patterns, DDD layers. Task: [path]
   cr_file_path: [CR_FILE_PATH]
   changed_files: [CHANGED_FILES]
   full_diff: [FULL_DIFF]
   FOCUS on changed files/lines. You MAY read unchanged files for context but do NOT flag pre-existing issues.
   Write findings to your section in the CR file between <!-- SECTION:code-quality --> markers.
   Return short summary only.
   ```

3. **`test-coverage-reviewer`** (skip in QUICK_MODE):
   ```
   Review tests: coverage gaps, edge cases, quality. Task: [path]
   cr_file_path: [CR_FILE_PATH]
   changed_files: [CHANGED_FILES]
   full_diff: [FULL_DIFF]
   FOCUS on test coverage for changed files. You MAY read unchanged files for context but do NOT flag pre-existing gaps.
   Write findings to your section in the CR file between <!-- SECTION:test-coverage --> markers.
   Return short summary only.
   ```

4. **`documentation-accuracy-reviewer`** (skip in QUICK_MODE):
   ```
   Review docs: accuracy, completeness. Task: [path]
   cr_file_path: [CR_FILE_PATH]
   changed_files: [CHANGED_FILES]
   full_diff: [FULL_DIFF]
   FOCUS on documentation for changed files. You MAY read unchanged docs for context but do NOT flag pre-existing gaps.
   Write findings to your section in the CR file between <!-- SECTION:documentation --> markers.
   Return short summary only.
   ```

5. **`performance-reviewer`** (skip in QUICK_MODE):
   ```
   Review performance: bottlenecks, N+1 queries, efficiency. Task: [path]
   cr_file_path: [CR_FILE_PATH]
   changed_files: [CHANGED_FILES]
   full_diff: [FULL_DIFF]
   FOCUS on changed files/lines. You MAY trace call chains into unchanged code but do NOT flag pre-existing issues.
   Write findings to your section in the CR file between <!-- SECTION:performance --> markers.
   Return short summary only.
   ```

**Quick mode skipped sections**: For agents not invoked in QUICK_MODE, edit their sections to:
`*Skipped — quick review mode (small PR). Only security and code quality assessed.*`

### GATE 6: Consolidation & Decision

All parallel agents have written their findings directly to the CR file. Read the CR file to verify all sections are populated, then proceed.

**Validation**: If any section still contains its placeholder text despite agent returning success, write:
`*Agent reported: [summary]. Detailed findings not written to section.*`

#### 6.1 Write Consolidated Issues

Edit `<!-- SECTION:consolidated -->` markers. Scan each agent section for severity-tagged items.

##### Full Review Mode:

```markdown
## Consolidated Issues

All issues from Pre-Review and Code Review agents, grouped by severity.

### Critical (Must Fix Before Merge)

- [ ] **[Source Agent]** Issue: Description → Solution → Files

### Major (Should Fix)

- [ ] **[Source Agent]** Issue: Description → Solution

### Minor (Nice to Fix)

- [ ] **[Source Agent]** Issue: Description → Suggestion

### Informational (Observations)

- **[Source Agent]** Observation: Description
```

De-duplicate issues flagged by multiple agents (note all sources).

##### Incremental Re-Review Mode:

```markdown
## Consolidated Issues (Round [N] Re-Review)

### Previous Issues Resolution

| # | Agent | Severity | Issue | Status |
|---|-------|----------|-------|--------|
| 1 | [agent] | [CRITICAL/MAJOR] | [description] | RESOLVED / STILL OPEN |

### New Issues Found

### Critical (Must Fix Before Merge)
- [ ] **[Source Agent]** [NEW] Issue: Description → Solution → Files

### Major (Should Fix)
- [ ] **[Source Agent]** [NEW] Issue: Description → Solution

### Minor (Nice to Fix)
- [ ] **[Source Agent]** Issue: Description → Suggestion

**Summary**: X of Y previous issues resolved. Z new issues found.
```

#### 6.2 Write Decision

Edit `<!-- SECTION:decision -->` markers. Apply decision matrix:

| Critical | Major | Decision |
|----------|-------|----------|
| 0 | 0-2 | APPROVED |
| 0 | 3+ | NEEDS FIXES |
| 1+ | any | NEEDS FIXES |

The 3+ Major threshold balances thoroughness with velocity — one or two Majors may be acceptable tech debt, but three signals systemic issues worth addressing before merge.

In incremental mode, count only STILL OPEN + NEW Critical/Major issues (RESOLVED issues do not count).

Include severity count table and actionable next steps.

#### Evidence Verification (before APPROVED decision)
Before writing an APPROVED decision, verify evidence exists:
- [ ] Quality Gate agent explicitly confirmed all 5 checks passed (not assumed from silence)
- [ ] At least one test file (`.spec.ts` or `.test.ts`) exists in `CHANGED_FILES`
- [ ] No review agent returned an error or failed to write its section
- [ ] If the task document claims N test cases, verify the actual test count is within range

If evidence is insufficient — e.g., no test files in changed files, or quality gate status is ambiguous — downgrade decision to `NEEDS FIXES` with reason: "Insufficient evidence of working implementation."

#### 6.3 Write Reviewer Note, Metadata & CR-STATE

- Edit `<!-- SECTION:summary -->` → Write a synthesized "Reviewer Note" (2-5 sentences) that reads like a senior human code reviewer's overall impression. Cover: what was implemented, implementation quality, notable strengths or concerns, and the bottom-line verdict. Synthesize findings into one cohesive perspective — do NOT list what each agent found.
  - In incremental mode, note which round this is and summarize resolution progress.
- Edit `<!-- SECTION:metadata -->` → Include:
  - `**Review Commit**: [REVIEW_COMMIT_SHA]`
  - `**Changed Files Count**: [N]`
  - Agent table: all agents invoked with their one-line summary + timestamp
- **Write CR-STATE block** — Append a hidden JSON state block to the CR file (after the metadata section, before the closing). This enables reliable incremental re-review detection in future runs:

```html
<!-- CR-STATE:
{
  "round": 1,
  "review_commit": "[REVIEW_COMMIT_SHA]",
  "decision": "[APPROVED/NEEDS FIXES/NEEDS_REWORK]",
  "agents_with_findings": {
    "senior-architecture-reviewer": { "critical": 0, "major": 1, "findings": ["[MAJOR] Issue description"] },
    "security-code-reviewer": { "critical": 0, "major": 0 },
    "code-quality-reviewer": { "critical": 0, "major": 2, "findings": ["[MAJOR] Issue 1", "[MAJOR] Issue 2"] },
    "test-coverage-reviewer": { "critical": 0, "major": 0 },
    "documentation-accuracy-reviewer": { "critical": 0, "major": 0 },
    "performance-reviewer": { "critical": 0, "major": 0 }
  }
}
-->
```

  Only include Critical and Major findings text in the `findings` arrays — Minor/Info are omitted to keep the block compact.

- Update header **Status** from PENDING to final decision

### GATE 7: Cross-AI Final Validation (Required If Overall APPROVED)

**CONDITION**: Only run if Decision = APPROVED (0 Critical, 0-2 Major) AND `QUICK_MODE = false`

**ACTION**: Always invoke skills to get info about how these CLIs work `/codex-cli`, `/gemini-cli`, and `/cursor-cli` skills in parallel for cross-AI validation.
Format output per `docs/product-docs/templates/cross-ai-protocol.md` (comparison table, validation, verdict).

- **FOCUS**: All acceptance criteria implemented, no regressions, production-ready, no missed security issues
- **FILE_REFS**: Task document path + `CHANGED_FILES` list
- **OUTPUT**: Write to `<!-- SECTION:cross-ai-validation -->` in CR file:
  1. Comparison table (what each AI found, agreements/disagreements)
  2. Validation table (each finding checked against actual code — VALID/INVALID/DISPUTED)
  3. Consolidated verdict with only VALID findings
- **If CRITICAL valid findings** → Change decision to NEEDS FIXES, update `<!-- SECTION:decision -->`
- **If no critical findings** → Keep APPROVED, note minor findings in `<!-- SECTION:consolidated -->`

**If skipped** (Decision != APPROVED, QUICK_MODE, or neither CLI available):
- Write to `<!-- SECTION:cross-ai-validation -->`: `**Status**: SKIPPED — [reason]`

### GATE 8: Linear & Completion

Linear integration is metadata — a failure here should never block or invalidate a completed review.

1. **Attempt Linear status update** (see `.claude/skills/cc-linear/SKILL.md`):
   ```bash
   .claude/scripts/linear-api.sh update-status WYT-XX "[Done | In Progress | In Review]"
   ```
   If this fails, warn: "Could not update Linear status ([reason]). Please update manually." Continue.

2. **Attempt results comment** (separate command):
   ```bash
   .claude/scripts/linear-api.sh add-comment WYT-XX "Code review: [APPROVED/NEEDS FIXES]. [issue counts]. Review doc: [path]"
   ```
   If this fails, warn similarly. Continue.

3. **Notify user** of outcome and next steps

## SEVERITY LEVELS

- `[CRITICAL]` — Must fix before merge (blocks approval)
- `[MAJOR]` — Should fix (3+ blocks approval)
- `[MINOR]` — Nice to fix (does not block)
- `[INFO]` — Observations (does not block)

## STATUS MAPPING

- APPROVED → "Done"
- NEEDS FIXES → "In Progress"
- NEEDS DISCUSSION → Keep "In Review"

## OUTPUT

Single `Code Review - [Task].md` in task directory. All agents write directly to their designated sections in the CR file. Orchestrator writes Reviewer Note, Consolidated Issues, Cross-AI Validation (or skipped status), Decision, and Metadata.

## Handoff — Next Steps

After review is complete, present to the user:

**If APPROVED:**
```
Code review APPROVED for [task-name]:
- Review: [CR file path]

Next steps:
→ Create PR: gh pr create
→ Update docs: /udoc
```

**If NEEDS FIXES:**
```
Code review: NEEDS FIXES for [task-name]:
- Review: [CR file path]
- Issues: [N critical, M major]

Next steps:
→ Fix issues, then re-review: /sr [task-path]
→ Address specific PR comments: /prc [PR-number]
```
