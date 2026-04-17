# Opus 4.7 Audit — `developer-agent` and `automated-quality-gate`

**Reference:** `tasks/opus-4-7-skill-review/INSIGHTS.md` (§1 behavior deltas, §3 anti-patterns, §4 positive patterns, §5 audit checklist).

Files audited:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/automation-agents/developer-agent.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/automation-agents/automated-quality-gate.md`

Both agents are broadly well-structured. The issues below are real dispatch/behaviour risks on Opus 4.7, not stylistic nits. Findings are ranked by priority within each agent.

---

## Agent 1 — `developer-agent`

### Frontmatter dispatch description review

`developer-agent.md:3`:

```yaml
description: "Universal developer agent. Implements ONE scoped work item (usually one acceptance criterion) in isolation. Can be spawned by /si for parallel execution."
```

Assessment: **Mostly good, with one minor tightening opportunity (Medium).**

- Good: explicit scope signal ("ONE scoped work item"), explicit spawner (`/si`), isolation cue. This gives the 4.7 dispatcher a clear "when to use" shape and avoids the under-specified trap called out in INSIGHTS §1 (instruction following is more literal).
- "Universal developer agent" is the only weak phrase — on the new action-biased 4.7 dispatcher it can read as an open invitation for *any* code-writing request, not just `/si`-orchestrated parallel slices. This overlaps the over-invocation risk the prompt flags under *"over-broad description causes over-invocation"*.
- `tools:` field (`Read/Write/Edit/Bash/Grep/Glob`) is correctly scoped for an implementation agent — it needs write access. No change needed.

**Before → After (frontmatter, Medium):**

```yaml
# Before
description: "Universal developer agent. Implements ONE scoped work item (usually one acceptance criterion) in isolation. Can be spawned by /si for parallel execution."

# After
description: "Implementation agent spawned by /si (and /si-quick) to implement ONE scoped work item — typically one acceptance criterion from a tech-decomposition document — in an isolated forked context. Use when an orchestrator needs a single slice of work built with TDD and returned as a structured JSON result. Not for ad-hoc coding outside a task directory."
```

Why: narrows the dispatcher to the actual invocation contract (orchestrator-spawned, task-doc backed, JSON return) while still leaving the `/si` path open. Cross-ref: INSIGHTS §1 "more literal instruction following" and the dispatch-description guidance in the task brief.

---

### High priority

#### H1. Intensifier inflation in the execution protocol

`developer-agent.md:73` — step header:

> `### Step 1: Read Task Document (CRITICAL)`

`developer-agent.md:85`:

> `**Task Document = Source of Truth** for WHAT to build.`

`developer-agent.md:99`:

> `**Context Summary = Guide** for HOW to build.`

`developer-agent.md:33`:

> `- **Git writes are forbidden unless explicitly approved** in the orchestrator prompt (branch/commit/push/merge).`

The `(CRITICAL)` label is the classic 4.7 intensifier anti-pattern (INSIGHTS §3: *"CRITICAL:, You MUST, ALWAYS, NEVER used as intensifiers — dial back"*). The *content* of Step 1 is load-bearing; the word `CRITICAL` is not — every step is already mandatory by virtue of being in the protocol. Same applies to the other bolded declarations used as emphasis.

**Before:**

```markdown
### Step 1: Read Task Document (CRITICAL)
```

**After:**

```markdown
### Step 1: Read Task Document

The task document is the source of truth for *what* to build. Start here — don't skim project code first, because project patterns only tell you *how* to build, not *what*.
```

Cross-ref: INSIGHTS §3 (anti-pattern — intensifier inflation) and §2.2 ("explain the *why* — rationale > rules").

---

#### H2. Git-write gating is stated three times — reduce to one authoritative spot

`developer-agent.md:33`, `:88-94`, `:141-154` all restate the same rule ("don't git-write unless orchestrator approved"). On 4.7's more literal reading this is fine but wastes context; worse, two of the restatements are embedded inside code blocks presented as executable recipes, which a 4.7 model reasoning literally may still treat as the default path before it notices the guard.

**Before (`:88-94`):**

```markdown
### Step 3: Create Sub-Branch (only if git writes are explicitly approved)

```bash
# Create isolated branch for this work item
git checkout -b {branch_name}-crit-{criterion_number}
```

If the orchestrator did **not** explicitly say git writes are approved, **DO NOT** run the command above. Continue without creating branches and return your work as "uncommitted changes" in the JSON.
```

**After:**

```markdown
### Step 3: Create Sub-Branch (skip unless git writes were explicitly approved)

Default: do NOT create a branch. The orchestrator commits on your behalf from the returned JSON.

Only if the orchestrator's prompt explicitly says "git writes approved" (or equivalent):

```bash
git checkout -b {branch_name}-crit-{criterion_number}
```

Otherwise skip this step entirely and set `"branch": null` in the return JSON.
```

And remove the duplicated paragraph at `:33` (the `## Role / Safety` block) — or trim it to a single pointer: *"Git writes are gated by the orchestrator prompt — see Step 3/Step 7."*

Cross-ref: INSIGHTS §1 ("Prompts that previously nudged tool use may now be unnecessary or cause over-reasoning") and §5.6 (literal-scope gaps — one clear rule beats three partial restatements).

---

#### H3. The "Minimal Code" / "No over-engineering" guard is present but weak

`developer-agent.md:39`:

> `4. **Minimal Code** - only what's needed to pass the test`

`developer-agent.md:103` (Step 5):

> ```
> Write MINIMAL code to make test pass:
> 1. Follow patterns from Context Summary
> 2. Implement only what test requires
> 3. No over-engineering
> 4. Follow {{ARCHITECTURE}} layer separation
> ```

`developer-agent.md:222`:

> `- Over-engineering beyond requirements`

The current wording ("no over-engineering", "minimal") is exactly the negative framing INSIGHTS §3 flags. 4.7 has a known tendency to add defensive error-handling, extra abstractions, and unrequested refactors even when told not to (INSIGHTS §1 — *"4.5 and 4.6 both tend to over-engineer; 4.7 more literal but still drifts"*, and §4 positive pattern *"Minimize over-engineering"*). Because this agent **has Write/Edit tools** (see `allowed-tools:` at `:7-12`), it needs a stronger, positively-framed guard per the task brief's explicit call-out ("Implementation agents should carry the over-engineering guard (§4)").

**Before (`:100-107`):**

```markdown
### Step 5: Implement (GREEN)

Write MINIMAL code to make test pass:

1. Follow patterns from Context Summary
2. Implement only what test requires
3. No over-engineering
4. Follow {{ARCHITECTURE}} layer separation
```

**After:**

```markdown
### Step 5: Implement (GREEN)

Write the smallest change that makes the failing test pass. Stay inside the files the work item names; follow patterns from the Context Summary for style.

Scope discipline (explicit, because the model tends to drift here):

- Don't add features, abstractions, helpers, or config that the acceptance criterion didn't ask for.
- Don't add defensive error handling for scenarios the test doesn't exercise — if the code path can't happen, don't guard it.
- Don't refactor surrounding code, even if it looks better afterwards. Bug fixes don't need surrounding refactors.
- Follow {{ARCHITECTURE}} layer separation for new code you add; don't re-layer existing code.

If a pattern or utility *looks* missing, check whether one already exists before creating a new one.
```

Cross-ref: INSIGHTS §4 positive pattern (*"Minimize over-engineering"*) — this rewording is almost verbatim from the insights doc, which is the intended pattern.

---

### Medium priority

#### M1. TDD framing assumes a JS/TS test file — genericize for the template

`developer-agent.md:111-122` (Step 4 example) and surrounding:

```typescript
// path/to/[work-item].spec.ts
describe('[Feature] - Work Item {criterion_number}', () => { ... });
```

The file uses `{{SRC_DIR}}` / `{{TEST_CMD}}` / `{{LINT_CMD}}` / `{{TYPECHECK_CMD}}` / `{{FRAMEWORK}}` placeholders elsewhere, but the TDD example is hard-coded TypeScript/Jest. On 4.7's more literal reading this subtly anchors the agent to Jest-style `describe/it` even when `/setup` has populated `{{FRAMEWORK}}` with Python/Go/Rust. INSIGHTS §3 warns against hard-coded patterns that fight adaptive output.

**Before:**

```markdown
```typescript
// path/to/[work-item].spec.ts
describe('[Feature] - Work Item {criterion_number}', () => {
  describe('[behavior from task doc]', () => {
    it('should [expected outcome]', async () => {
      // Arrange - setup based on task doc
      // Act - call the method/endpoint
      // Assert - verify expected behavior
    });
  });
});
```
```

**After:**

```markdown
Write a failing test in the project's test style (matched to {{TEST_FRAMEWORK}} / {{FRAMEWORK}}). Structure:

- Arrange — setup based on the task doc
- Act — call the method/endpoint
- Assert — verify the expected behaviour

Name the test after the work item and its expected outcome, following the naming pattern you observed in existing tests in {{TEST_DIR}}.
```

Cross-ref: INSIGHTS §5.6 (literal-scope gaps) and §1 (*"state scope explicitly"* — the style should come from the project, not from a hard-coded example).

---

#### M2. Parallelism awareness missing despite the frontmatter advertising parallel use

Frontmatter advertises *"Can be spawned by /si for parallel execution"* (`:3`), yet the body has nothing about parallel-aware behaviour (no mention of not touching shared files, no mention of batching tool calls within this slice, no mention of reading-before-speculating). 4.7 under-parallelizes by default (INSIGHTS §1 and §4 *"Parallel tool-calling — When calls have no dependencies, batch them in one turn"*).

**Add (near the "Working Style" block at `:43`):**

```markdown
## Parallel-Safe Behaviour

When spawned by an orchestrator running several developer-agents in parallel on sibling criteria:

- Assume other agents are editing sibling files in the same repo. Do not touch files outside your work item, even for "small fixes".
- Treat the task document as read-only unless the orchestrator explicitly hands you write access (see "Return Format" — edits go through the orchestrator).
- Within your own work item, batch independent tool calls in the same turn (e.g., read all files you need to inspect before editing). Don't serialise reads.
- Never speculate about code you haven't opened. If the context summary references a file you'll depend on, read it before implementing against it.
```

Cross-ref: INSIGHTS §4 (*"Parallel tool-calling"*, *"Investigate-before-answering"*).

---

#### M3. Response length / "be thorough" pressure in the return format

`developer-agent.md:156-192` describes a JSON return with many optional fields (`notes`, `commit_message`, `validation`, `files_changed`). Combined with `:50-55`:

> `- **After finishing the scoped item**:\n  - Prepare a short summary + file list + any key notes for the orchestrator.`

there is no explicit instruction on *how terse* "notes" and "summary" should be. 4.7's adaptive length will often pad this when the task feels important. Not a severe issue, but worth a one-line calibration.

**Before (`:156`):**

```markdown
## Return Format

Return JSON result to orchestrator:
```

**After:**

```markdown
## Return Format

Return the JSON result below. Keep `summary` to one line, `notes` to ≤3 short bullets (omit the key entirely if there's nothing worth saying), and don't repeat information already captured in the structured fields.
```

Cross-ref: INSIGHTS §1 (*"Response length — calibrated to task complexity"*) and §3 (anti-pattern — absent stopping condition).

---

### Low priority

#### L1. "Status Meanings" could be collapsed into the JSON schema

`developer-agent.md:194-209` restates what `status` values mean *after* already defining the JSON schema. On 4.7 this is low-harm; the list could simply become enum-style comments inline in the schema. Optional cleanup.

#### L2. `## Constraints` and `## Anti-Patterns` overlap

`developer-agent.md:211-226` has two near-duplicate lists ("Constraints" and "Anti-Patterns"), both repeating "ONE work item", "minimal implementation", "no cross-item changes". Trim to one list with rationale per bullet (INSIGHTS §2.2 — explain the *why*).

#### L3. Skills preloading is fine

`skills: [coding-conventions]` at `:13-14` is the correct pattern for preloading project conventions into an implementation agent (the CLAUDE.md project rules explicitly endorse this). No change needed.

---

## Agent 2 — `automated-quality-gate`

### Frontmatter dispatch description review

`automated-quality-gate.md:3`:

```yaml
description: Runs automated quality checks (tests, lint, types, coverage) after implementation. Acts as a gate before human-like code review to catch obvious issues early.
```

Assessment: **Good — tight and accurate (High-confidence positive).**

- Clearly signals trigger ("after implementation", "before code review"), scope (tests, lint, types, coverage), and role ("gate"). This is the shape the 4.7 dispatcher needs.
- Minor: "coverage" appears in the description but the body (`:26`) says coverage is **optional and only on explicit request**. This mismatch could cause the dispatcher to over-invoke when a user casually asks about coverage. Low-priority tightening below.
- `tools:` field (`:4`) is `Bash, Read, Write, Edit, Grep` — Write/Edit are needed for the file-mode output that edits the CR document between section markers (`:112-120`). Correct.
- `model: sonnet` and `effort: low` (`:5-6`) are intentional for a gate running deterministic commands. This matches INSIGHTS §1 (*"`low`/`medium` under-think on complex tasks"* — but a gate isn't complex, it runs shell commands and tabulates). Good fit.

**Before → After (frontmatter, Low):**

```yaml
# Before
description: Runs automated quality checks (tests, lint, types, coverage) after implementation. Acts as a gate before human-like code review to catch obvious issues early.

# After
description: Runs automated pre-review gates (format, lint, types, tests, build) after an implementation task and reports PASS/FAIL for each. Use immediately before a human-like code-review agent, so reviewers don't waste effort on code that fails basic automated checks. Coverage runs are optional and only when explicitly requested.
```

Why: removes the "coverage" dispatch hook (it's opt-in), adds build (which is actually in the gate list), and makes the "before code review" ordering explicit for the dispatcher. Cross-ref: INSIGHTS §1 (more literal dispatch) and the task brief's "over-broad description causes over-invocation" warning.

---

### High priority

#### H1. Coverage-then-filter split is missing — this is the exact gap called out in the task brief

The task brief explicitly says:

> *"Automation gates (like quality-gate) should carry the coverage-then-filter split (§1 code-review row, §3, §4)."*

Current `automated-quality-gate.md` operates on **binary** PASS/FAIL per gate (`:51-91`, `:139-149`), with no notion of reporting every detected issue regardless of severity, and letting a downstream filter decide what's actionable. On Opus 4.7 this collides with the behaviour delta from INSIGHTS §1:

> *"Code-review harnesses — Obey severity/confidence filters more literally — recall may appear to drop. Prompt for coverage at find stage, filter in a separate stage."*

In practice: a gate that silently dedupes/thresholds lint warnings (the agent explicitly says *"warnings acceptable"* at `:58`) will under-report on 4.7, and the CR reviewer downstream has no visibility into what was suppressed.

**Before (`:55-60`):**

```markdown
### 2. Linting
```bash
{{LINT_CMD}}
```
- **Pass**: No lint errors
- **Fail**: Any lint error (warnings acceptable)
```

**After:**

```markdown
### 2. Linting
```bash
{{LINT_CMD}}
```
- **Coverage (always report)**: Total error count, total warning count, and a file:line list of every finding — including warnings and "style-only" rules. Do not filter at this stage.
- **Gate verdict**: FAIL if any error; PASS if only warnings. (Warnings don't fail the gate, but they must still appear in the report so the reviewer can decide.)
```

Apply the same pattern to `### 3. Type Checking`, `### 4. Test Suite`, `### 5. Build Verification`. Then in the output table (`:111-120`), add a `Findings` column that lists the raw file:line evidence regardless of severity.

Also update the closing return format. Current:

> `automated-quality-gate.md:124-127`:
> ```
> "GATE_PASSED. 0 critical, 0 major, 0 minor. All 5 gates passed — format, lint, types, tests, build clean."
> or
> "GATE_FAILED. 1 critical, 0 major, 0 minor. TypeCheck failed: 3 type errors in auth module."
> ```

To:

```markdown
"GATE_PASSED (warnings: 4 — see table). All 5 gates passed. Lint: 0 errors, 4 warnings (unused-imports ×3, prefer-const ×1). Format/types/tests/build clean."

"GATE_FAILED. TypeCheck: 3 errors (src/auth.ts:42, src/auth.ts:55, src/session.ts:17). Lint: 0 errors, 7 warnings. Tests: 2 failures (auth.spec.ts:81, session.spec.ts:22). Build: skipped — failed earlier gate."
```

Cross-ref: INSIGHTS §1 (code-review row), §3 (anti-pattern — *"Only report high-severity / important issues"*), §4 (*"Report every issue you find, including low-severity and uncertain ones"*).

---

#### H2. "Do not stop on first failure" is asserted but partially contradicted by the flow diagram

`automated-quality-gate.md:97`:

> `2. **Run all gates sequentially and collect results** (do not stop on first failure)`

vs. `automated-quality-gate.md:103-110` flow diagram:

```
Format → Lint → TypeCheck → Test Suite → Build
     ↓
If ANY fails → GATE_FAILED (return to implementation)
     ↓
All pass → GATE_PASSED (proceed to review)
```

The diagram reads as "short-circuit on first failure", which on 4.7's more literal reading will dominate the prose above it. Also note the `"Build: skipped — failed earlier gate"` phrasing I suggested in H1 — that's not actually the current contract; under the prose contract, build should *always* run.

**Before (`:103-110`):**

```markdown
## Gate Execution Order

```
Format → Lint → TypeCheck → Test Suite → Build
     ↓
If ANY fails → GATE_FAILED (return to implementation)
     ↓
All pass → GATE_PASSED (proceed to review)
```
```

**After:**

```markdown
## Gate Execution Order

Run all five gates in this order, **always running every gate** even if an earlier one fails — the point is to collect every issue in one pass so the developer can fix all of them at once.

```
Format → Lint → TypeCheck → Test Suite → Build   (all run, no short-circuit)
                        ↓
      Any gate failed?  → GATE_FAILED (return to implementation)
                        ↓
      All five passed?  → GATE_PASSED (proceed to review)
```
```

Cross-ref: INSIGHTS §1 (literal instruction following) and §3 (*"State scope explicitly — apply to every item, not just the first"*).

---

### Medium priority

#### M1. Tool-use over-nudging: "Truncate very long outputs" has no criterion

`automated-quality-gate.md:161`:

> `- Truncate very long outputs but keep essential info`

On 4.7 this is a classic unbounded instruction — INSIGHTS §3 (*"Be thorough / exhaustive / comprehensive with no stopping condition"*). The agent doesn't know what "essential" means for e.g. a 5000-line test failure dump vs. a 50-line build failure.

**Before:**

```markdown
- Truncate very long outputs but keep essential info
```

**After:**

```markdown
- For each failing gate, include: the exact failing command, up to 20 lines of the most-relevant output (usually the first error + stack frame pointing at project code), and the file:line of each distinct failure. If you truncate, say so explicitly: `[... truncated 340 lines ...]`. Never summarise errors into prose — paste the raw lines so the developer can grep.
```

Cross-ref: INSIGHTS §2.2 (*"explain the why"*) and §3.

---

#### M2. Intensifier hygiene: ALL-CAPS gates

`automated-quality-gate.md:140`:

> `### GATE_PASSED`
>
> `### GATE_FAILED`

`automated-quality-gate.md:148`:

> `- Do NOT approve if ANY gate fails`

`automated-quality-gate.md:158-160`:

> ```
> - Run ALL gates even if one fails (collect all issues)
> - Provide specific file paths and line numbers for failures
> - Do NOT approve if ANY gate fails
> ```

INSIGHTS §3 calls out `ALL` / `ANY` / `NOT` used as emphasis. `GATE_PASSED` / `GATE_FAILED` are fine — they're status tokens, which is load-bearing. The repeated "Do NOT approve if ANY gate fails" is emphasis noise; the rule is already stated once in the gate-execution section.

**Before:**

```markdown
## Constraints

- Run ALL gates even if one fails (collect all issues)
- Provide specific file paths and line numbers for failures
- Do NOT approve if ANY gate fails
- Only run coverage when explicitly requested
- Truncate very long outputs but keep essential info
```

**After:**

```markdown
## Constraints

- Run every gate in a single pass — the value is collecting all failures so the developer fixes them together.
- For every failure, include file path, line number, and the raw error output (don't paraphrase).
- Coverage runs only when the invoker explicitly asks for them (it's slow and usually duplicates unit-test signal).
- [replace the "truncate" line with the M1 version above]
```

Cross-ref: INSIGHTS §3 (intensifiers) and §2.2 (rationale over rules).

---

#### M3. Edit-tool write scope should be explicitly narrowed to the section markers

`automated-quality-gate.md:112-120`:

> ```
> 1. **Read** the CR file at the provided `cr_file_path`
> 2. **Locate** your section markers: `<!-- SECTION:quality-gate -->` ... `<!-- /SECTION:quality-gate -->`
> 3. **Use the Edit tool** to replace the placeholder text between markers with your findings
> 4. **Do NOT** edit anything outside your section markers
> ```

Good that the markers are explicit. On 4.7's more literal reading, the risk is different: the agent will succeed at the happy path but may still attempt an edit if the markers are *missing* (e.g., CR file wasn't pre-scaffolded). Add a positive error path.

**Add after `:120`:**

```markdown
5. If the section markers are missing or only one of the pair is present, do NOT create them and do NOT write outside them. Return inline mode output instead and flag the missing markers in your summary (e.g., `"cr_file_path provided but section markers missing — returning inline"`).
```

Cross-ref: INSIGHTS §5.6 (literal-scope gaps) and §4 (positive framing of error paths).

---

### Low priority

#### L1. "What this agent covers" section is helpful

`automated-quality-gate.md:28-38` — the explicit "Does NOT cover" list is a positive pattern on 4.7 (literal-scope handling). No change needed; this is already a good example of INSIGHTS §4.

#### L2. Shared-memory protocol block is truncated

`automated-quality-gate.md:40-47`:

```markdown
tasks/task-YYYY-MM-DD-[feature]/
├── tech-decomposition-[feature].md    ← READ: Requirements
├── IMPLEMENTATION_LOG.md              ← READ (optional): What was implemented
```

The agent is told it reads these, but the execution process (`:95-101`) only mentions `IMPLEMENTATION_LOG.md`. Either drop `tech-decomposition-*.md` from the memory protocol (the gate doesn't need requirements — it runs commands) or add an explicit line explaining why it's read. Purely hygienic.

#### L3. `model: sonnet` + `effort: low` is intentional and correct

Don't change. A gate runs deterministic commands and tabulates — complexity is low, so `effort: low` avoids the "overthinking" risk flagged by INSIGHTS §1 (*"`max` risks overthinking"*, and by extension so does any over-specified effort for trivial orchestration). This is a deliberate, well-tuned choice and should be preserved.

---

## Cross-agent summary

| Agent | Frontmatter | High | Medium | Low |
|---|---|---|---|---|
| `developer-agent` | Medium tightening | 3 | 3 | 3 |
| `automated-quality-gate` | Low tightening | 2 | 3 | 3 |

Both agents are in good shape overall. The single biggest gap is the **coverage-then-filter split missing from `automated-quality-gate` (H1)** — that's the one finding most likely to cause real behaviour degradation on 4.7. The second biggest is the **over-engineering guard wording in `developer-agent` (H3)**, because that agent holds Write/Edit tools and 4.7's literal-but-still-drifting behaviour around scope is well documented.

No invented issues: where the agents are already well-tuned (skills preloading, explicit "does not cover" list, `effort: low` on the gate, named spawner in the dispatch description) the review calls it out as such.
