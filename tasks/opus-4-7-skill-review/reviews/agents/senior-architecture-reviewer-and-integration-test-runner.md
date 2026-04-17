# Review: senior-architecture-reviewer & integration-test-runner

**Scope:** Two subagent definition files under `.claude/agents/automation-agents/` audited against Opus 4.7 prompting best practices (INSIGHTS.md).
**Files reviewed:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/automation-agents/senior-architecture-reviewer.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/automation-agents/integration-test-runner.md`

Special considerations for 4.7 agent definitions:
- `description:` drives auto-dispatch — must be action-framed and specific (INSIGHTS §1, dispatcher is more action-biased on 4.7).
- `tools:` narrows the agent’s capability surface — must match actual job.
- Review-type agents need **coverage-then-filter** framing (INSIGHTS §1 code-review row, §4).
- Test-runner agents must **not** filter failures — every failure must surface (task directive + INSIGHTS §3 "only report high-severity" anti-pattern).

---

## Agent 1 — senior-architecture-reviewer.md

### Frontmatter

**Current** (lines 1–8):
```yaml
---
name: senior-architecture-reviewer
description: Senior developer reviewing implementation approach, solution quality, architectural consistency, and TDD compliance. Validates technical decisions and architecture fit before detailed code review. Spec compliance is handled separately by spec-compliance-reviewer.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
skills:
  - review-conventions
---
```

**Assessment:**
- `description:` is clear and delineated against sibling reviewers (explicit "spec compliance is handled separately" is good disambiguation for the 4.7 dispatcher).
- Missing a **trigger verb / action phrasing** up front. 4.7's dispatcher prefers action-biased leading clauses. Starting with "Senior developer reviewing…" reads as a *persona* rather than *when to invoke*.
- `tools:` includes `Write` and `Edit`, which are load-bearing because the agent writes into a CR file via markers (line 87). Correct — do **not** remove.
- `Glob` is listed but never referenced in the body. Harmless but worth noting.
- `model: opus` + `skills: [review-conventions]` is appropriate for deep architectural judgment.

### High Priority

#### H1. Frontmatter `description:` is persona-framed, not dispatch-framed

**Location:** line 3
**Why it matters:** INSIGHTS §1 ("Instruction following — more literal") + dispatcher is action-biased on 4.7. Agents whose `description:` reads like a job title dispatch less reliably than agents whose `description:` starts with the **trigger condition**.

**Before:**
```yaml
description: Senior developer reviewing implementation approach, solution quality, architectural consistency, and TDD compliance. Validates technical decisions and architecture fit before detailed code review. Spec compliance is handled separately by spec-compliance-reviewer.
```

**After:**
```yaml
description: Use after implementation is complete, before detailed code review, to validate solution approach, architecture fit, and TDD compliance on a task directory or diff. Complements spec-compliance-reviewer (requirements) and code-quality-reviewer (naming/complexity) — do not invoke in parallel with them on the same scope.
```

#### H2. Filter-leakage risk — severity buckets without coverage-first instruction

**Location:** lines 104–108 (Issues block) and "Decision Criteria" lines 115–126
**Why it matters:** INSIGHTS §1 code-review row and §3: "Only report high-severity / important issues" causes recall drop on 4.7. The current prompt never explicitly tells the agent to surface *every* issue including low/uncertain ones before filtering. Combined with the decision-matrix buckets (APPROVED / NEEDS_REWORK / MINOR_ADJUSTMENTS) and severity labels `[CRITICAL]/[MAJOR]/[MINOR]`, 4.7 will tend to self-filter at find time.

**Before (lines 104–108):**
```markdown
#### Issues

- [CRITICAL] **Issue**: Description → Location → Solution
- [MAJOR] **Issue**: Description → Location → Suggestion
- [MINOR] **Suggestion**: Description
```

**After:**
```markdown
#### Issues

Report every issue you noticed — including low-confidence and low-severity ones. Severity/confidence labels drive later triage, not whether to surface an issue.

- [CRITICAL] **Issue**: Description → Location → Solution
- [MAJOR] **Issue**: Description → Location → Suggestion
- [MINOR] **Suggestion**: Description
- [NIT / LOW-CONFIDENCE] **Observation**: Description → why you're uncertain
```

And add a "Coverage before filter" block at the top of *Review Focus Areas* (after line 18):

```markdown
## Coverage Before Filter

Surface every concern at find time — severity and confidence are metadata, not gatekeepers. A later verification step (or the orchestrator) decides what to escalate. If you are uncertain whether something is a real problem, record it as `[LOW-CONFIDENCE]` rather than dropping it.
```

#### H3. "Be thorough" with no stopping condition

**Location:** line 11 ("Be thorough but constructive") and line 13 ("Challenge assumptions with reasoning")
**Why it matters:** INSIGHTS §3: "Be thorough / exhaustive / comprehensive with no stopping condition — causes overthinking and scope creep." On 4.7, this tends to inflate review length.

**Before:**
```markdown
## Your Mindset

- Be thorough but constructive
- Challenge assumptions with reasoning
- Maintain high standards without being harsh
- Consider the code will run in production for years
- Accept trade-offs only with explicit justification
```

**After:**
```markdown
## Your Mindset

- Constructive and specific — vague feedback is useless
- Challenge assumptions by citing the file/line that contradicts them
- High standards; production code with multi-year lifespan
- Accept trade-offs only when justified in the task docs or a commit message
- Stop when you've covered the four Focus Areas below and checked TDD — do not re-audit the codebase at large
```

### Medium Priority

#### M1. Intensifier hygiene — `CRITICAL:` / `REQUIRED` / `DO NOT` scattered as emphasis

**Location:**
- line 52: `**REQUIRED** (always exist):`
- line 58: `**REFERENCE** (always exists, read once):`
- line 61: `**OPTIONAL** (check if exists, use if found):`
- line 66: `**DO NOT search for**`
- line 92: `4. **Do NOT** edit anything outside your section markers`

**Why it matters:** INSIGHTS §3: "CRITICAL / MUST / ALWAYS / NEVER used as intensifiers — dial back; 4.7 is already more responsive and these cause over-triggering."

The `**DO NOT search for**` list (lines 66–69) is genuinely load-bearing — it prevents the agent from reading files produced by sibling agents. That one should stay forceful, but re-framed positively.

**Before (lines 66–69):**
```markdown
**DO NOT search for** (created by other agents, not your input):
- `Pre-Flight Validation - [Task].md`
- `Quality Gate Report - [Task].md`
- `Code Review - [Task].md`
```

**After:**
```markdown
**Produced by other agents — skip, don't read:**
- `Pre-Flight Validation - [Task].md` (pre-flight-validator)
- `Quality Gate Report - [Task].md` (quality-gate-agent)
- `Code Review - [Task].md` (you write *into* this via section markers, but don't read the other agents' sections for your own review inputs)
```

For line 92, the `Do NOT edit anything outside your section markers` is genuinely load-bearing for shared-file coordination — keep it, but pair it with the *why*:

**Before:**
```markdown
4. **Do NOT** edit anything outside your section markers
```

**After:**
```markdown
4. Edit only between your section markers — the CR file is shared memory with other reviewer agents, and overwriting their sections corrupts their output
```

#### M2. TDD bash block lacks stopping condition on empty history

**Location:** lines 47–49
**Why it matters:** INSIGHTS §4 "Investigate-before-answering" + literal-scope gap. On a task branch with no commits yet (or on a squash-merged branch), these commands return empty — the agent needs explicit instruction to handle that.

**Before:**
```bash
git log --oneline main..HEAD
git log --oneline --name-only main..HEAD | grep -E "(test:|feat:)"
```

**After:**
```bash
git log --oneline main..HEAD
git log --oneline --name-only main..HEAD | grep -E "(test:|feat:)"
```

Add right below:
```markdown
If the range returns no commits (e.g., squash-merged, amended history, or branched from a non-`main` base), report **TDD compliance: UNVERIFIABLE** with the reason. Do not guess or fabricate commit hashes.
```

#### M3. Diff-Scoped Review uses "MAY" / "do NOT" — could be positive

**Location:** lines 73–81
**Why it matters:** INSIGHTS §2.6 "Positive framing beats negative."

**Before (line 75):**
```markdown
3. **Context reading**: You MAY read unchanged files referenced by changed code (e.g., imported interfaces, base classes) to understand the full picture, but do NOT flag issues in unchanged code unless they are DIRECTLY caused by the changes
```

**After:**
```markdown
3. **Context reading**: Read unchanged files referenced by changed code (imports, base classes, types) to understand the full picture. Flag only issues caused by this PR — pre-existing issues in unchanged code are out of scope for this review.
```

#### M4. "Be specific with criticism" rule without rationale

**Location:** lines 155–160 (Constraints)
**Why it matters:** INSIGHTS §2.2 "Explain the *why* — rationale > rules."

**Before:**
```markdown
- Read task document FIRST to understand requirements
- Check git log to verify TDD was followed
- Be specific with criticism — vague feedback is useless
- Every criticism should include a suggested fix
- Don't proceed to code review if NEEDS REWORK
- Verify {{ARCHITECTURE}} layer boundaries are respected
```

**After:**
```markdown
- Read the task document first — the rest of the review only makes sense once you know the intended scope
- Check git log to verify TDD was followed (test commits precede implementation)
- Every finding includes file, line, and suggested fix — downstream agents and the human reviewer cannot act on "the architecture feels wrong"
- If status is NEEDS_REWORK, the orchestrator skips detailed code review — don't soften the status to avoid that
- Verify {{ARCHITECTURE}} layer boundaries are respected per `{{DOCS_DIR}}/project-structure.md`
```

### Low Priority

#### L1. `Glob` tool listed but unused

**Location:** line 4
**Why it matters:** Minor — tool scope hygiene. If the agent never globs (it reads a known task directory and specific CR file), listing `Glob` just widens capability surface without benefit.

**Suggestion:** Either remove `Glob` from `tools:` or add a brief usage in the body (e.g., "Use `Glob` to discover task files when only the task directory is given"). No change if unsure.

#### L2. Output-mode "Return ONLY a short summary" fights adaptive length

**Location:** lines 109–112
**Why it matters:** INSIGHTS §3: "Hard-coded response-length caps that fight 4.7's adaptive length." The summary *is* short by nature, but the phrasing could invite the model to under-report when issues are complex.

**Before:**
```markdown
**Then return ONLY a short summary:**
`"APPROVED. 0 critical, 1 major, 0 minor. Approach sound, port JSDoc needs update."`
```

**After:**
```markdown
**Then return a one-line status summary (counts + one-clause rationale) — the full findings are already in the CR file:**
`"APPROVED. 0 critical, 1 major, 0 minor. Approach sound, port JSDoc needs update."`
```

#### L3. `{{PLACEHOLDER}}` density in section headers

**Location:** lines 25–31 (`{{ARCHITECTURE}}`, `{{LAYERS}}`, `{{LAYER_RULES}}`, `{{DOCS_DIR}}`, `{{FRAMEWORK}}`, `{{ORM}}`, `{{AUTH}}`)
**Why it matters:** Generalization is intentional (portability). Just flagging — if `/setup` has not been run on a repo, the agent will emit literal `{{ARCHITECTURE}}` in its output. Consider a one-line guard: "If a `{{PLACEHOLDER}}` is unresolved, treat it as 'project-specific architecture unknown' and flag in the report."

---

## Agent 2 — integration-test-runner.md

### Frontmatter

**Current** (lines 1–8):
```yaml
---
name: integration-test-runner
description: Runs integration and E2E tests after code review passes. Verifies the implementation works correctly with the full system before PR creation.
tools: Bash, Read, Write, Grep
model: sonnet
effort: low
color: purple
---
```

**Assessment:**
- `description:` is action-framed ("Runs… Verifies…") and places the agent cleanly in the pipeline ("after code review passes", "before PR creation") — this is **good** for the 4.7 dispatcher.
- `tools:` is tight (`Bash, Read, Write, Grep`) — correct. No `Edit` because the agent only produces a new report file.
- `model: sonnet` + `effort: low` is defensible for a mostly-shell-execution role, but see I1 below.

### High Priority

#### H1. Contradicts the task's "report every failing test" directive — current doc filters and summarizes

**Location:** lines 160–170 (Critical Issues / Warnings split), lines 224–226, and line 194–198 (Integration Issues Found)
**Why it matters:** The task brief explicitly says: *"Integration-test-runner should NOT filter failures; it should report every failing test."* INSIGHTS §3 also calls out "Only report important issues" as an anti-pattern. The current template buckets issues into "Critical (Block PR)" vs "Warnings (Should Address)" — which encourages filtering at report time and, worse, encourages summarizing test output rather than listing every failure.

**Specifically problematic passages:**
- Line 122 (E2E Tests block): `**Summary**: [X] tests, [Y] passed, [Z] failed` — summary without per-failure list
- Lines 161–173: two-bucket "Critical" / "Warnings" framing
- Line 226: `Skip tests that don't exist rather than failing` — correct, but easy for 4.7 to over-generalize into "skip tests that look flaky"

**Before (lines 119–127, E2E block):**
```markdown
### E2E Tests
**Status**: ✅/❌/⏭️ (skipped)
```
[Test output]
```
**Summary**: [X] tests, [Y] passed, [Z] failed
```

**After:**
```markdown
### E2E Tests
**Status**: ✅ / ❌ / ⏭️ (skipped — no E2E test command configured)

**Totals**: [X] total, [Y] passed, [Z] failed, [W] skipped

**Every failing test — list all, do not truncate or group:**

| Test file | Test name | Failure message (first 3 lines) | Exit / status |
|-----------|-----------|---------------------------------|---------------|
| `test/e2e/foo.spec.ts` | `POST /resource should create item` | `Status 500: Database connection failed` | failed |

If the test runner produces more than 50 failures, list the first 50 in the table above and include the full raw output in an appendix section — do not summarize or drop failures.
```

**Before (lines 161–173):**
```markdown
## Integration Issues Found

### Critical Issues (Block PR)
1. **[Issue]**: [Description]
   - Impact: [What breaks]
   - Files: [Affected files]
   - Suggested Fix: [How to fix]

### Warnings (Should Address)
1. **[Warning]**: [Description]
   - Risk: [Potential impact]
   - Recommendation: [What to do]
```

**After:**
```markdown
## Integration Issues Found

Report every failure and every warning — do not pre-filter based on perceived severity. The PR / orchestrator decides which failures block. Your job is to surface, not gatekeep.

### Failures (every failing test or check)
1. **[Failure]**: [Description]
   - Source: [test file / check name]
   - Observed: [actual output]
   - Suggested fix (if obvious): [how to fix]

### Warnings (non-failing but noteworthy)
1. **[Warning]**: [Description]
   - Observed: [actual output]
   - Why it matters: [risk]
```

#### H2. `effort: low` is likely too weak for debugging test failures

**Location:** line 6
**Why it matters:** INSIGHTS §1 "Effort tiers — `xhigh` is recommended default for coding/agentic". `low` on a test-running agent is fine for the *run-the-tests* happy path but under-thinks when failures need diagnosis (line 210–247 "Failure Handling" expects real root-cause suggestions). Root-causing a migration failure or startup failure is not `low`-effort work.

**Before:**
```yaml
model: sonnet
effort: low
```

**After:**
```yaml
model: sonnet
effort: medium
```

With an accompanying prompt nudge added after line 11 ("You are an Integration Test Runner Agent…"):
> "Running tests is fast; diagnosing failures is not. When tests pass, keep the report terse. When tests fail, think carefully about root cause before suggesting fixes."

This leverages INSIGHTS §1 ("think carefully" to raise thinking) without hard-coding effort too high.

#### H3. "Skip tests that don't exist rather than failing" is too broad on 4.7

**Location:** line 226
**Why it matters:** INSIGHTS §1 "Instruction following — more literal". On 4.7 a broadly-worded skip instruction risks the agent skipping tests that *exist but fail to start* (e.g., Docker not running, DB unreachable). The intent is "no configured E2E command = skipped, not failed" — but the current wording generalizes.

**Before:**
```markdown
- Skip tests that don't exist rather than failing
```

**After:**
```markdown
- If a test category is **not configured** in the project (no command in package.json / Makefile / config), mark that category as `⏭️ skipped` and move on — this is not a failure.
- If a test category **is configured but errors at startup** (missing env var, DB unreachable, Docker not running), that is a **failure**, not a skip. Report the startup error verbatim and mark the category `❌`.
```

### Medium Priority

#### M1. Bash blocks hide command output behind `2>/dev/null || echo "…"` — loses failure signal

**Location:** lines 37 (E2E), 45 (schema)
**Why it matters:** INSIGHTS §2.1 "Golden rule — if a new colleague couldn't follow the prompt, Claude can't either." `{{TEST_CMD}} --passWithNoTests 2>/dev/null` swallows real errors, leaving the agent with "No E2E test command configured" even when the command existed and crashed.

**Before (line 37):**
```bash
{{TEST_CMD}} --passWithNoTests 2>/dev/null || echo "No E2E test command configured"
```

**After:**
```bash
# Run E2E tests if configured. Capture both stdout and stderr so diagnostics survive.
if command -v {{TEST_CMD%% *}} >/dev/null 2>&1 || grep -q '"test:e2e"' package.json 2>/dev/null; then
  {{TEST_CMD}} --passWithNoTests 2>&1
else
  echo "SKIPPED: no E2E test command configured in package.json / Makefile"
fi
```

Note: the exact guard depends on project type — the point is to **distinguish "no command" from "command failed"**.

#### M2. Return Format JSON schema has no per-failure detail

**Location:** lines 176–193 (Return Format block)
**Why it matters:** The JSON only carries `{status, total, passed}` per category plus a flat `critical_issues: ["list"]`. The orchestrator downstream cannot see individual failing tests unless they read the markdown report. If machine-consumption is the goal, per-test detail should be in the JSON too.

**Before (line 181):**
```json
"e2e": {"status": "passed|failed|skipped", "total": 10, "passed": 10},
```

**After:**
```json
"e2e": {
  "status": "passed|failed|skipped",
  "total": 10,
  "passed": 8,
  "failed": 2,
  "failures": [
    {"file": "test/e2e/foo.spec.ts", "name": "POST /resource", "message": "Status 500"},
    {"file": "test/e2e/bar.spec.ts", "name": "GET /health", "message": "timeout"}
  ]
},
```

Rationale: the task directive ("report every failing test") is more robustly enforced when the schema itself requires per-failure entries.

#### M3. `Integration Test Categories` hard-codes 5 categories without a "unknown category" escape

**Location:** lines 27–77
**Why it matters:** INSIGHTS §6 "Literal-scope gaps — places where the prompt assumes the model will generalize (it won't in 4.7)." A project may have performance tests, smoke tests, or consumer-driven contract tests (Pact). The current prompt enumerates 5 categories and the "Execution Process" (lines 79–86) has no explicit instruction for "if you find a test type not in this list, run it and report it under a new heading."

**Before (end of line 86):**
```markdown
6. **Generate report**
```

**After:**
```markdown
6. **Generate report**

If you detect a configured test category not listed above (e.g., Pact/CDC tests, smoke tests, load tests, visual regression), run it and add a matching section to the report under `### [Category Name]` — do not skip tests just because they're not in the default category list.
```

#### M4. "Cross-Module Integration" instructs a dependency-graph analysis with no tooling guidance

**Location:** lines 72–77
**Why it matters:** Asking the agent to verify "no circular dependencies" via bash/read only is a tall order. With no concrete detection command, 4.7 will likely skip it silently or fabricate a result.

**Before:**
```markdown
### 5. Cross-Module Integration
Based on IMPLEMENTATION_LOG.md, verify:
- New services are properly registered/injected
- Module dependencies are correct
- No circular dependencies
```

**After:**
```markdown
### 5. Cross-Module Integration

Based on `IMPLEMENTATION_LOG.md`, verify:
- **Services registered/injected**: grep for the new service name in module files / DI container config
- **Module dependencies correct**: the service's imports resolve and match the architecture docs
- **No circular dependencies**: if the project has `madge`, `dpdm`, or a framework-native check (e.g., `nest build`), run it. If no tool is configured, mark this check `⏭️ skipped — no circular-dep tool configured` rather than guessing.
```

### Low Priority

#### L1. Emoji status indicators (`✅ ❌ ⏭️`) in output template

**Location:** lines 90, 122, 131, 139, 148, 155, and throughout
**Why it matters:** The project's global CLAUDE.md (`For clear communication with the user the assistant MUST avoid using emojis`) conflicts with the template's heavy emoji use. Downstream renderings may strip them; agents in other projects may render them inconsistently.

**Suggestion:** Replace `✅ / ❌ / ⏭️` with `PASS / FAIL / SKIPPED` throughout the template. Non-blocking, stylistic.

#### L2. "Don't run destructive tests against production data" lacks a concrete guard

**Location:** line 228
**Why it matters:** INSIGHTS §2.2 "Explain the *why*" — the rule is correct but the agent has no concrete check. If the project's test DB URL *is* prod, the agent won't know.

**Before:**
```markdown
- Don't run destructive tests against production data
```

**After:**
```markdown
- Before running destructive integration tests, verify the DB URL points at a test/dev database (check `DATABASE_URL`, `.env.test`, `docker-compose.test.yml`). If you can't confirm it's non-production, mark the category `⏭️ skipped — could not verify non-prod target` and flag it as a Warning.
```

#### L3. Persona sentence ("You are an Integration Test Runner Agent") is redundant with frontmatter

**Location:** line 11
**Why it matters:** Minor — INSIGHTS §2.8 role assignment is valuable, but restating the agent name adds no behavioral signal. Keep the role, drop the redundancy.

**Before:**
```markdown
You are an Integration Test Runner Agent responsible for verifying that implemented features work correctly with the full system. Your job is to catch integration issues that unit tests miss, ensuring the code works in a production-like environment.
```

**After:**
```markdown
Your job: run integration and E2E tests against a production-like environment to catch issues unit tests miss. You execute tests, observe outputs, and write a structured report — you do not modify implementation code.
```

---

## Cross-agent observations

1. **Both agents follow the shared-memory pattern well** — task directory as I/O boundary, explicit list of files they read vs. write vs. ignore. No change needed.
2. **Both agents miss compaction-awareness guidance** (INSIGHTS §4 "Context will be automatically compacted…"). For these two specifically the risk is low because neither runs for an extended conversation — they execute once and return. Safe to skip unless runtimes grow.
3. **Neither agent uses XML tags** for structuring instructions vs. context vs. output-format (INSIGHTS §2.3, §5.12). The markdown-heading structure is readable and follows the project's other agents — acceptable, but if you ever see dispatcher confusion between input schema and output schema, wrapping the Output Format block in `<output_format>` tags would help.
4. **Parallel-subagent prompting** (INSIGHTS §4) is not applicable — both are leaf agents invoked by an orchestrator, not fan-out agents.

---

## Summary of Priorities

### senior-architecture-reviewer
- **High:** H1 (dispatch-frame description), H2 (coverage-before-filter), H3 (stopping condition for "thorough")
- **Medium:** M1 (intensifier hygiene), M2 (TDD unverifiable case), M3 (positive framing for diff-scope), M4 (why-over-rule)
- **Low:** L1 (Glob unused), L2 (summary length cap), L3 (placeholder guard)

### integration-test-runner
- **High:** H1 (remove filter buckets, list every failure), H2 (effort low → medium + think-on-failure nudge), H3 (narrow the "skip" scope)
- **Medium:** M1 (stop swallowing stderr), M2 (per-failure JSON schema), M3 (unknown-category escape), M4 (concrete circular-dep guidance)
- **Low:** L1 (emoji vs project policy), L2 (concrete prod-DB guard), L3 (drop redundant persona sentence)
