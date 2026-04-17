# Opus 4.7 Review — `code-quality-reviewer` & `test-coverage-reviewer`

Scope: `.claude/agents/code-review-agents/code-quality-reviewer.md` + `.claude/agents/code-review-agents/test-coverage-reviewer.md`. Findings cite `INSIGHTS.md` §1 (behavior deltas), §3 (anti-patterns), §4 (positive patterns), and §5 (audit checklist). Both files are dispatched by the `/sr` orchestrator and both inherit the shared `review-conventions` skill (`.claude/skills/review-conventions/SKILL.md`). The `/sr` audit (`sr-and-prc.md:13`) already flagged the `>80% confidence` filter in that shared skill as the single largest recall risk on 4.7; this review does NOT re-prescribe the shared-skill fix (SR owns that) but DOES flag where these two agents *re-assert* or *compound* the filter in their own body.

Cross-reference: the three agents that re-assert the shared confidence threshold verbatim are `code-quality-reviewer.md`, `performance-reviewer.md`, and `documentation-accuracy-reviewer.md`. `test-coverage-reviewer.md` does NOT re-assert it and is already in the shape the SR audit recommends (inherits only).

---

## Agent 1 — `code-quality-reviewer.md`

### Frontmatter

```yaml
name: code-quality-reviewer
description: Reviews code for quality, maintainability, and adherence to best practices. Use after implementing features, refactoring, or before committing significant changes.
tools: Glob, Grep, Read, Edit, Write, BashOutput
model: opus
skills:
  - review-conventions
```

Two frontmatter issues for 4.7 auto-dispatch:

**F1. `description` is broad and action-dispatch-friendly (Medium priority).** The trigger phrase "Use after implementing features, refactoring, or before committing significant changes" reads as three independent triggers. On 4.7 — which is more action-biased in dispatch (INSIGHTS §1 "Overeagerness" row and §3 "Do not suggest, make the changes used too aggressively … 4.7 is now more action-biased, this may over-trigger") — this phrasing invites invocation after *any* refactor or *any* commit, not only the orchestrated `/sr` flow this agent is built for. The agent is designed to run as a dispatched subagent of `/sr` (note the `cr_file_path` file-mode protocol at line 51 and the section-marker contract at line 55) — it is not a standalone "run after every commit" tool.

Before (line 3):
```
description: Reviews code for quality, maintainability, and adherence to best practices. Use after implementing features, refactoring, or before committing significant changes.
```

After:
```
description: Dispatched by /sr to review code quality and maintainability of changed files. Not intended for direct invocation — use /sr for code review workflows.
```

This scopes the dispatcher to the intended orchestrator and prevents 4.7 from fanning it out on a bare "refactor this" request where the user wants the refactor, not a review. (INSIGHTS §1 row "Instruction following — more literal; will NOT silently generalize" — we want dispatch hints to be literal too.)

**F2. `tools` grants `Edit` and `Write` (High priority).** A code-quality reviewer should not write source code. The justification here is the file-mode protocol that writes findings into `cr_file_path` between section markers — that needs `Edit`, not `Write`. Granting `Write` in addition means 4.7 can legitimately create new files (e.g., a "helper abstraction" or a "fixed version of file X"), which is directly against INSIGHTS §4 "Minimize over-engineering" guidance for a review agent. `BashOutput` is also unneeded here (this agent does not run commands — `test-coverage-reviewer` does, legitimately).

Before (line 4):
```
tools: Glob, Grep, Read, Edit, Write, BashOutput
```

After:
```
tools: Glob, Grep, Read, Edit
```

Rationale cite: INSIGHTS §5 axis 10 ("Over-engineering mitigation — is the don't-add-beyond-what-was-asked guard present?"). Removing `Write` is a structural guard; the prompt text can't undo what a tool grant allows.

---

### Priority 1 — High

#### H1. Compounded filter leakage — re-asserts `>80% confidence` on top of the shared skill

**Cross-ref:** INSIGHTS.md §1 (Code-review harnesses row: "Obey severity/confidence filters more literally — recall may appear to drop"), §3 ("Only report high-severity / important issues in review skills — 4.7 obeys literally → recall drops"), §4 (coverage-then-filter split). Also `sr-and-prc.md:13` which already tagged this as the highest-recall risk in the stack.

The shared `review-conventions` skill already contains:
```
- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.
```

This agent then restates the same filter in even more restrictive language at lines 95–96:
```markdown
## Confidence & Consolidation

- **Only report findings you are >80% confident about.** If you are unsure whether something is actually a problem, do not report it. False positives waste developer time and erode trust in the review process.
- **Consolidate similar issues into a single finding with count.** For example, write "5 functions missing error handling" with a list of locations, not 5 separate findings. This keeps the review scannable.
```

Three compounding problems on 4.7:

1. The re-assertion uses stronger anchors than the shared skill ("Only report", "do not report it", "erode trust in the review process"). 4.7 reads this more literally than 4.6, so the effective threshold drifts above 80%.
2. The phrase "If you are unsure whether something is actually a problem" converts *any* uncertainty (not just confidence <80%) into a silent drop. This is the exact shape INSIGHTS §3 warns about.
3. Code quality findings (naming, DRY, complexity, over-engineering) are *inherently* subjective — most real findings sit in the 60–85% confidence band. A hard 80% cut disproportionately zeroes out this agent's output relative to, say, `security-code-reviewer` where findings are more verifiable.

The SR audit (`sr-and-prc.md:33`) recommends moving the filter to the orchestrator. This file should stop re-asserting it on top, even if the shared skill fix lands.

Before (lines 93–96):
```markdown
## Confidence & Consolidation

- **Only report findings you are >80% confident about.** If you are unsure whether something is actually a problem, do not report it. False positives waste developer time and erode trust in the review process.
- **Consolidate similar issues into a single finding with count.** For example, write "5 functions missing error handling" with a list of locations, not 5 separate findings. This keeps the review scannable.
```

After:
```markdown
## Coverage & Consolidation

- Report every code quality issue you find, including ones you are uncertain about. Tag each
  finding with `confidence: low | medium | high` alongside severity. The /sr orchestrator
  filters; your job is to cover. Low-confidence findings still help the reviewer — they are
  dropped or collapsed at the consolidation stage, not here.
- Consolidate structurally similar issues into a single finding with a location list. Example:
  "5 functions missing error handling" with 5 `file:line` entries, not 5 separate findings.
  This is compression, not filtering — every issue still appears.
```

This matches INSIGHTS §4's coverage-then-filter split and mirrors what the `/sr` audit prescribes for the shared skill.

---

#### H2. "Focus on teaching principles" overrides the compaction-aware, scope-bounded style

**Cross-ref:** INSIGHTS.md §1 (Response length row: "Calibrated to task complexity"), §3 ("Be thorough / exhaustive / comprehensive with no stopping condition"), §4 (Minimize over-engineering).

Closing Constraints block (lines 106–111):
```markdown
- Be precise and actionable: every finding needs severity, location, and suggestion
- Order findings by severity (CRITICAL → INFO)
- Be constructive — explain why issues matter, suggest concrete improvements
- Highlight positive aspects when code is well-written
- Focus on teaching principles, not just fixing current issues
```

"Focus on teaching principles, not just fixing current issues" is an implicit expansion prompt — it tells 4.7 to go beyond the diff and lecture. Combined with the adaptive-length default, this produces long "here's why clean code matters" paragraphs attached to each finding. On 4.7 this compounds because the model now calibrates length to perceived task complexity, and "teach principles" raises the perceived complexity of every finding.

Also note: this agent runs in dispatched file-mode (writing into a section of a shared CR file), where verbose teaching prose actively hurts readability. The `/sr` orchestrator consolidates findings into a key-findings section; teaching prose is wasted tokens there.

Before (line 111):
```
- Focus on teaching principles, not just fixing current issues
```

After:
```
- Suggestions should be concrete and fit the diff — one-sentence rationale, then the fix.
  Do not expand into general lectures on clean-code principles; the reviewer reading this
  already knows why DRY matters. The `why` belongs in the suggestion only when it is
  non-obvious for the specific change.
```

Rationale cites INSIGHTS §2.2 ("Explain the why — rationale > rules") balanced against §3 ("Be thorough / exhaustive / comprehensive with no stopping condition").

---

### Priority 2 — Medium

#### M1. Over-Engineering Detection section is well-aligned but bullets read as detection *triggers* not stopping conditions

Lines 41–45:
```markdown
**Over-Engineering Detection:**
- Features/refactoring beyond what was requested
- Helpers/abstractions for one-time operations
- Error handling for impossible scenarios
- Designing for hypothetical future requirements
```

This section is conceptually right (INSIGHTS §4 "Minimize over-engineering" — a positive pattern). The issue is shape: these are phrased as things to *find* in the diff, but on 4.7 a "Detection" bullet list doubles as behavioral self-instruction — the model tends to also apply the list to its own findings ("was my suggestion adding a helper for a one-time operation?"). That's actually *useful* here, but it's accidental. Make it explicit in both directions so the self-guard is deliberate.

Before (line 40):
```
**Over-Engineering Detection:**
```

After:
```
**Over-Engineering Detection (flag in code, and apply to your own suggestions):**
```

No other body changes needed — the bullets themselves are good.

---

#### M2. `{{LANGUAGE}}-Specific` and `Project-Specific` sections assume `/setup` ran and placeholders are replaced — no fallback

Lines 24–35 contain three `{{ORM}}`, two `{{LANGUAGE}}`, two `{{DOCS_DIR}}`, one `{{FRAMEWORK}}`, one `{{ARCHITECTURE}}`, one `{{AUTH}}` placeholder. If `/setup` was not run, the agent reads "`{{ORM}}` repository code quality" literally. 4.7's more-literal instruction following (INSIGHTS §1) makes this worse than on 4.6 — the model will look for a repository named `{{ORM}}` or try to interpret the placeholder as a variable.

The shared `review-conventions` has the same pattern but at least scopes it to a structured table. Here the placeholders are embedded in prose.

Recommendation: either (a) make the placeholder block conditional on `/setup` completion (hard — this is a markdown file), or (b) have the `/setup` skill fail loudly if these placeholders are unresolved when any review agent ships. Option (b) is an SR/setup concern, not an agent-file concern, so flag-and-defer.

No in-file change recommended; routed to the `setup` skill owner.

---

### Priority 3 — Low

#### L1. Output format block good, but the "short summary" return mixes severity labels with prose

Lines 85–88:
```markdown
**Then return ONLY a short summary:**
`"Clean. 0 critical, 0 major, 0 minor. Code is well-structured."`
or
`"Findings. 0 critical, 1 major, 2 minor. Port JSDoc contradicts implementation."`
```

4.7 hard caps on response length tend to fight adaptive length (INSIGHTS §3 "Hard-coded response-length caps"). The good news: this isn't a word cap, it's a format example. Kept as-is is fine. Minor note only: the example uses lowercase `critical / major / minor` while the finding format above uses `[CRITICAL] / [MAJOR] / [MINOR]`. Align casing to reduce ambiguity for 4.7's literal reading.

No urgent change.

---

## Agent 2 — `test-coverage-reviewer.md`

### Frontmatter

```yaml
name: test-coverage-reviewer
description: Reviews testing implementation and coverage. Use after writing features, refactoring code, or completing modules to verify test adequacy.
tools: Glob, Grep, Read, Edit, Write, BashOutput, KillBash
model: inherit
skills:
  - review-conventions
```

Two frontmatter notes:

**F1. `description` same over-broad pattern as Agent 1 (Medium priority).** "Use after writing features, refactoring code, or completing modules" is three triggers that invite 4.7 auto-dispatch outside the `/sr` orchestrator. Same fix shape as Agent 1's F1.

Before (line 3):
```
description: Reviews testing implementation and coverage. Use after writing features, refactoring code, or completing modules to verify test adequacy.
```

After:
```
description: Dispatched by /sr to verify test coverage for changed files, including running project test suites. Not intended for direct invocation — use /sr for code review workflows.
```

**F2. `tools` list is appropriate *except* for `Write` (Medium priority).** This agent legitimately needs `Edit` (file-mode output into CR section markers), `Read` / `Grep` / `Glob` (exploration), `BashOutput` + `KillBash` (running `{{COVERAGE_CMD}}` and `{{TEST_CMD}}` — line 10 explicitly instructs: "Always execute the project's test suites"). `Write` is not needed and is worse here than in Agent 1 because 4.7 could decide to *write a missing test* on the reviewer's behalf — which is exactly the "4.7 is now more action-biased" risk from INSIGHTS §3.

Before (line 4):
```
tools: Glob, Grep, Read, Edit, Write, BashOutput, KillBash
```

After:
```
tools: Glob, Grep, Read, Edit, BashOutput, KillBash
```

Also note: this agent uses `model: inherit` while `code-quality-reviewer` uses `model: opus`. Not a bug (coverage review is more mechanical, inherit is fine), but worth a comment — if the top-level caller is on a weak model, `inherit` may under-think the missing-scenarios analysis. This is a calibration choice for the repo owner, not a 4.7-specific issue.

---

### Priority 1 — High

#### H1. "Always execute the project's test suites" is a good literal instruction, but paired with "never assume coverage from static analysis alone" creates a tool-use trap on 4.7

**Cross-ref:** INSIGHTS.md §1 (Tool use row: "Less frequent — reasons more before calling tools"), §3 ("Default to using [tool] — too broad … replace with use [tool] when it would enhance X").

Line 10:
```markdown
You are an expert QA engineer and testing specialist. Always execute the project's test suites (`{{COVERAGE_CMD}}`) and include real output — never assume coverage from static analysis alone.
```

On 4.6 this was appropriate — "Always … never assume" nudged a tool-shy model toward actually running `{{COVERAGE_CMD}}`. On 4.7 the picture is different:

- 4.7 reasons more before tool calls (INSIGHTS §1) — the nudge is less needed
- 4.7 is more literal — "Always execute" plus "never assume" now read as a hard precondition, meaning if `{{COVERAGE_CMD}}` fails or the placeholder is unresolved, the agent may either (a) refuse to review, or (b) invent output to satisfy the "include real output" demand. The latter is a hallucination risk created by the prompt.

The good instinct (actually run the tests) is preserved better by stating *why* and giving a fallback.

Before (line 10):
```
You are an expert QA engineer and testing specialist. Always execute the project's test suites (`{{COVERAGE_CMD}}`) and include real output — never assume coverage from static analysis alone.
```

After:
```
You are an expert QA engineer and testing specialist. Run the project's test suites
(`{{COVERAGE_CMD}}`, `{{TEST_CMD}}`) when reviewing — static analysis alone misses dead
test files, skipped tests, and flaky assertions. If the commands are unresolved placeholders
or fail to run in this environment, say so explicitly in your output (as an INFO finding)
and fall back to static coverage analysis — do not fabricate coverage numbers.
```

This is INSIGHTS §2.2 ("Explain the why — rationale > rules") plus a literal fallback path for the placeholder case. Preserves the tool-use behavior without the hallucination trap.

---

### Priority 2 — Medium

#### M1. No confidence-tagging guidance — inherits the shared `>80%` filter invisibly

**Cross-ref:** INSIGHTS.md §4 (coverage-then-filter), `sr-and-prc.md:13`.

Unlike `code-quality-reviewer`, this file does NOT re-assert the `>80% confidence` filter in its own body. Good — it's the cleanest of the three sister agents on this axis. But it also does not contain the positive `confidence: low|medium|high` tagging instruction that the SR audit recommends adding to complete the coverage-then-filter split.

If the SR audit's prescribed fix lands in `review-conventions` (replace the `>80% confidence` line with "report everything, tag with confidence, orchestrator filters"), this file inherits it automatically and needs no edits. If that fix does not land, this file still needs the override that Agent 1 needs (see Agent 1 H1).

No proactive edit recommended here beyond tracking the shared-skill change.

---

#### M2. "Be thorough but practical" in closing constraints is a soft version of the INSIGHTS §3 anti-pattern

Line 93:
```markdown
- Be thorough but practical — focus on tests that catch real bugs
```

INSIGHTS §3 flags: "Be thorough / exhaustive / comprehensive with no stopping condition — causes overthinking and scope creep." "Be thorough but practical" is the same pattern with a softener. On 4.7 the "but practical" softener doesn't function as a stopping condition — it's too vague. "Focus on tests that catch real bugs" is the actual stopping condition; put it first and drop the intensifier.

Before (line 93):
```
- Be thorough but practical — focus on tests that catch real bugs
```

After:
```
- Prioritize tests that catch real bugs (error paths, boundaries, async/race cases) over
  tests that merely hit uncovered lines. If coverage is 100% but error paths are untested,
  report the gap.
```

Rationale cites INSIGHTS §2.6 ("Positive framing beats negative") and §3 (no-stopping-condition anti-pattern).

---

#### M3. "Consider the testing pyramid: balance unit, integration, e2e" is good but needs scope

Line 94:
```markdown
- Consider the testing pyramid: balance unit, integration, e2e
```

On 4.7, "Consider X" with no scope tends to produce meta-commentary ("I notice the project leans heavily on e2e tests, consider adding more unit tests") that is outside the diff-scoped review brief (lines 41–47). Since this agent is diff-scoped when `changed_files` is provided, the pyramid observation should only fire when the changes themselves shift the pyramid balance.

Before (line 94):
```
- Consider the testing pyramid: balance unit, integration, e2e
```

After:
```
- If the changes add tests at one layer only (e.g., new feature has unit tests but no
  integration test) and the feature's nature warrants cross-layer coverage (spans a service
  boundary, hits external I/O), flag the pyramid gap. Do not comment on the pyramid when
  the balance is untouched by this diff.
```

---

### Priority 3 — Low

#### L1. Test-file-identification heuristic (line 44) assumes co-location

Line 44:
```markdown
3. **Test file identification**: For each changed source file, check if a corresponding test file exists and was also changed. Flag as a potential coverage gap if a source file changed but its test file was not
```

This heuristic works for co-located test conventions (e.g., `src/foo.ts` + `src/foo.test.ts`) but breaks when the project uses a parallel `tests/` tree (e.g., `src/foo.ts` + `tests/unit/foo.spec.ts`). The shared `review-conventions` references `{{TEST_DIR}}` — this agent doesn't use it. On 4.7, the literal reading of "corresponding test file" will miss tests in a sibling tree and over-flag.

Before (line 44):
```
3. **Test file identification**: For each changed source file, check if a corresponding test file exists and was also changed. Flag as a potential coverage gap if a source file changed but its test file was not
```

After:
```
3. **Test file identification**: For each changed source file, locate its corresponding
   test file. Test files may be co-located (e.g., `src/foo.ts` + `src/foo.test.ts`) or live
   in a parallel tree (`{{TEST_DIR}}`). Use Grep to find tests that `import`/`require` the
   changed module. Flag as a potential coverage gap only if no test file references the
   changed module — do not flag solely on "no file with matching name".
```

---

#### L2. `{{COVERAGE_CMD}}` / `{{TEST_CMD}}` placeholder behavior

Same placeholder-fallback concern noted in Agent 1 M2 — applies here too and is partially addressed by the H1 fix above (explicit fallback for unresolved placeholders). No additional change needed if H1 lands.

---

## Summary Table

| ID | Agent | Priority | Issue | INSIGHTS cite |
|---|---|---|---|---|
| F1 (cq) | code-quality-reviewer | Medium | `description` over-broad → 4.7 auto-dispatch outside /sr | §1 (dispatch literal-ness), §3 (action-biased) |
| F2 (cq) | code-quality-reviewer | **High** | `tools` grants `Write` — reviewer can create files | §4 (no over-engineering) |
| H1 (cq) | code-quality-reviewer | **High** | Re-asserts `>80% confidence` on top of shared skill — recall drops on 4.7 | §1 (code-review harnesses), §3 (filter leakage), §4 (coverage-then-filter) |
| H2 (cq) | code-quality-reviewer | **High** | "Focus on teaching principles" expands output, fights adaptive-length calibration | §1 (response length), §3 (no stopping condition) |
| M1 (cq) | code-quality-reviewer | Medium | Over-engineering detection list should explicitly also apply to own suggestions | §4 (minimize over-engineering) |
| M2 (cq) | code-quality-reviewer | Medium | Unresolved `{{…}}` placeholders in prose break literal reading on 4.7 | §1 (more literal) |
| L1 (cq) | code-quality-reviewer | Low | Severity casing inconsistent between finding format and summary example | §1 (literal) |
| F1 (tc) | test-coverage-reviewer | Medium | Same over-broad `description` pattern | §1, §3 |
| F2 (tc) | test-coverage-reviewer | Medium | `tools` grants `Write` — reviewer could write tests on user's behalf | §3 (action-biased), §4 |
| H1 (tc) | test-coverage-reviewer | **High** | "Always execute / never assume" paired → hallucination risk when placeholders unresolved | §1 (tool use less frequent), §3 (default-to anti-pattern) |
| M1 (tc) | test-coverage-reviewer | Medium | No confidence-tagging — inherits shared `>80%` filter invisibly (tracks SR audit fix) | §4 (coverage-then-filter) |
| M2 (tc) | test-coverage-reviewer | Medium | "Be thorough but practical" — soft intensifier with no stopping condition | §3 (thorough/exhaustive anti-pattern) |
| M3 (tc) | test-coverage-reviewer | Medium | "Consider the testing pyramid" — unscoped, produces meta-commentary on 4.7 | §1 (literal), §3 |
| L1 (tc) | test-coverage-reviewer | Low | Test-file-identification heuristic assumes co-location, misses parallel trees | §1 (literal) |
| L2 (tc) | test-coverage-reviewer | Low | Placeholder fallback — subsumed by H1 fix | §1 |

---

## Cross-Agent Observations

1. **Filter-leakage split:** `code-quality-reviewer` re-asserts the shared `>80% confidence` filter in its own body (lines 95–96), making it the worst-case recall risk of the two. `test-coverage-reviewer` does not re-assert and only inherits. The SR audit (`sr-and-prc.md:13`) prescribes the shared-skill fix; this review prescribes *removing* the re-assertion in `code-quality-reviewer` regardless of whether the shared-skill fix lands — belt-and-suspenders on the most subjective review type.

2. **`tools: Write` is the highest-priority non-prose change for both agents.** Prompt text cannot undo a tool grant. A reviewer that can write files will, on 4.7, occasionally write them — because 4.7 is more action-biased (INSIGHTS §3) than 4.6. The fix is one-line-each and removes a structural footgun that no amount of prompt tuning closes.

3. **`description` auto-dispatch hygiene** is a pattern likely shared across all six review agents in this directory. A repo-level pass that rewrites each `description` to scope invocation to `/sr` would prevent 4.7 from dispatching these outside the orchestrator. This is a directory-wide edit, not per-file.

4. **Neither agent is badly broken.** Both are structurally sound, both correctly inherit `review-conventions`, both have the diff-scoped section, both have clear file-mode vs inline-mode output contracts, and `test-coverage-reviewer` is notably cleaner than its peers on the filter-leakage axis. The recommendations above are calibration for 4.7's more-literal, more-action-biased profile, not a structural rewrite.
