# Agent Review — documentation-accuracy-reviewer & spec-compliance-reviewer

**Audited against:** `tasks/opus-4-7-skill-review/INSIGHTS.md` (Opus 4.7 prompting best practices)
**Files under review:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/code-review-agents/documentation-accuracy-reviewer.md` (99 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/code-review-agents/spec-compliance-reviewer.md` (129 lines)

Both agents are compliance/accuracy reviewers dispatched by `/sr`. They share common failure modes on Opus 4.7: over-literal filter obedience that suppresses recall, and over-intensified `MUST/NEVER` directives. Below, findings are grouped by agent and ranked High/Medium/Low per INSIGHTS §6.

---

## 1. documentation-accuracy-reviewer.md

### Frontmatter

**Current (line 3):**
```
description: Verifies code documentation is accurate, complete, and up-to-date. Use after implementing features, modifying APIs, or preparing code for release.
```

**Assessment:** Well-formed for 4.7's action-biased dispatcher (INSIGHTS §1). It names the capability (`Verifies…accurate, complete, up-to-date`) and gives three concrete trigger contexts (`after implementing features, modifying APIs, preparing code for release`). No change needed.

**Tools line (line 4):** `Glob, Grep, Read, Edit, Write, BashOutput` — appropriate. `Edit`/`Write` are justified by the section-marker write protocol. No change needed.

---

### HIGH priority

#### H1. Confidence filter will drop recall on 4.7 (INSIGHTS §1 code-review row, §3, §4)

**Location:** `documentation-accuracy-reviewer.md:86`

**Offending text:**
> `- **Only report findings you are >80% confident about.** If you are unsure whether something is actually a problem, do not report it. False positives waste developer time and erode trust in the review process.`

**Why this fails on 4.7:** INSIGHTS §1 — *"Code-review harnesses: Obey severity/confidence filters more literally — recall may appear to drop"*. INSIGHTS §3 explicitly flags `Only report high-severity / important issues` as an anti-pattern. A hard >80% threshold on a model that now *obeys literally* means legitimate documentation drift (subtle JSDoc/param mismatches, borderline-accurate examples) will be silently dropped.

A documentation reviewer is especially affected because doc inaccuracies are inherently fuzzy: "this example *might* not match the current signature" is exactly the kind of uncertain finding that still deserves a flag with confidence noted.

**Before → After:**

Before:
```
- **Only report findings you are >80% confident about.** If you are unsure whether something is actually a problem, do not report it. False positives waste developer time and erode trust in the review process.
```

After:
```
- **Report every documentation discrepancy you find, including low-severity and uncertain ones.** Tag each finding with a confidence level (HIGH/MEDIUM/LOW) and severity. A separate verification step filters noise. Suppressing uncertain findings here causes doc drift to compound silently across releases.
```

This matches INSIGHTS §4 ("Coverage-then-filter split for review skills").

---

#### H2. "Do NOT edit anything outside your section markers" is correct but under-rationalized (INSIGHTS §2.2)

**Location:** `documentation-accuracy-reviewer.md:54`

**Offending text:**
> `4. **Do NOT** edit anything outside your section markers`

**Why this matters on 4.7:** 4.7 is more action-biased (INSIGHTS §1 *"4.7 is now more action-biased, this may over-trigger edits"*). When multiple review sub-agents write to the *same* CR file, a literal-but-rationale-free `Do NOT` plus Edit/Write tools invites boundary bleed. The *why* (concurrent writers clobber each other) is missing.

**Before → After:**

Before:
```
4. **Do NOT** edit anything outside your section markers
```

After:
```
4. Edit only the text between your section markers. Other review agents write to the same CR file in parallel — editing outside your markers corrupts their findings.
```

Pattern: INSIGHTS §2.2 — *"rationale > rules"*.

---

### MEDIUM priority

#### M1. Intensifier pile-up without load-bearing purpose (INSIGHTS §3)

**Location:** `documentation-accuracy-reviewer.md:11`, `documentation-accuracy-reviewer.md:54`, `documentation-accuracy-reviewer.md:76`

**Offending text:**
- Line 11: `You are an expert technical documentation reviewer. Always cross-check with task docs...`
- Line 54: `Do **NOT** edit anything outside your section markers`
- Line 76: `Then return ONLY a short summary`

**Why:** INSIGHTS §3 — dial back `ALWAYS` / `NEVER` / `ONLY` used as emphasis. `Always cross-check` is reasonable because it names the sources, but the pattern `Always … Always … Do NOT … ONLY` across a short file (99 lines) compounds into over-triggering.

**Before → After (line 11):**

Before:
```
You are an expert technical documentation reviewer. Always cross-check with task docs (`tasks/.../tech-decomposition*.md`), JTBD/PRD references in `{{DOCS_DIR}}/product-docs/`, and `{{DOCS_DIR}}/project-structure.md`.
```

After:
```
You are an expert technical documentation reviewer. Your source of truth is the task document (`tasks/.../tech-decomposition*.md`) and the project docs in `{{DOCS_DIR}}/product-docs/` and `{{DOCS_DIR}}/project-structure.md`. Cross-check every claim against those before flagging.
```

**Before → After (line 76):**

Before:
```
**Then return ONLY a short summary:**
```

After:
```
**Then return a short summary (one line):**
```

---

#### M2. "Do NOT audit all documentation" is literal-scope — good, but needs positive framing (INSIGHTS §4, §3)

**Location:** `documentation-accuracy-reviewer.md:40-41`

**Offending text:**
> `5. **Do NOT** audit all documentation in the project — only check docs related to changed functionality`

**Why:** INSIGHTS §3 flags negative framing. INSIGHTS §4 — state scope explicitly. The current sentence is half-right (literal scope is helpful on 4.7), but double-negative.

**Before → After:**

Before:
```
5. **Do NOT** audit all documentation in the project — only check docs related to changed functionality
```

After:
```
5. Scope your review to documentation tied to the changed functionality. Unrelated doc gaps in other areas are out of scope for this pass — auditing the full docset here slows the review without adding signal.
```

---

#### M3. Missing "investigate-before-answering" explicitly (INSIGHTS §4)

**Location:** Applies to the whole file; no such instruction exists.

**Why:** INSIGHTS §4 — *"Never speculate about code you have not opened. If the user references a file, read it before answering."* A documentation reviewer is exactly the agent that can be tempted to compare a summary against docs instead of the real code. 4.7's more conservative tool use (INSIGHTS §1 tool-use row) makes this more likely, not less.

**Before → After (new line, suggested to add after line 11):**

After (new):
```
Before flagging any doc as inaccurate, open and read the implementation it describes. Do not infer accuracy from commit messages, PR descriptions, or the implementer's summary — those are often the source of the drift you are looking for.
```

---

### LOW priority

#### L1. "Focus on genuine issues, not stylistic preferences" — add the *why* (INSIGHTS §2.2)

**Location:** `documentation-accuracy-reviewer.md:97`

**Offending text:**
> `- Focus on genuine documentation issues, not stylistic preferences`

**Before → After:**

Before:
```
- Focus on genuine documentation issues, not stylistic preferences
```

After:
```
- Flag documentation issues that would mislead a developer (wrong params, outdated examples, stale API shapes). Style preferences (wording, formatting, voice) are out of scope — a separate style pass handles those.
```

---

#### L2. Output examples use `[MAJOR]` / `[MINOR]` / `[INFO]` but the canonical severities elsewhere in the repo are `CRITICAL/MAJOR/MINOR` (consistency)

**Location:** `documentation-accuracy-reviewer.md:64-72`, compare with `spec-compliance-reviewer.md:105-108` (uses `CRITICAL/MAJOR/MINOR`).

**Why:** Not strictly an Opus 4.7 issue, but the agent is dispatched alongside `spec-compliance-reviewer` by `/sr` — divergent severity vocab makes the merged CR harder to skim. This is a consistency note, flagged as Low per §6.

No before/after required — simply align severity ladder across the two agents (pick one: `[CRITICAL] [MAJOR] [MINOR] [INFO]` or keep `CRITICAL/MAJOR/MINOR`).

---

#### L3. Response-length constraint is soft but present (INSIGHTS §3, §5)

**Location:** `documentation-accuracy-reviewer.md:76`, `documentation-accuracy-reviewer.md:79`

**Offending text:**
> `**Then return ONLY a short summary:**`
> Example: `"Clean. 0 critical, 0 major, 0 minor. Documentation is accurate and complete."`

**Why:** This is a reasonable structured-output constraint, not a blanket "one sentence" cap, so it mostly survives 4.7's adaptive length. Flagging as Low because the `ONLY … short` phrasing drifts into the soft cap pattern INSIGHTS §3 warns about. The one-line example is excellent — keep that as the anchor, drop the ONLY.

**Before → After:** Covered in M1.

---

## 2. spec-compliance-reviewer.md

### Frontmatter

**Current (line 3):**
```
description: Verifies implementation matches spec requirements by reading actual code. Dispatched in /sr GATE 4a before architecture review. Do NOT trust implementer claims — read the code.
```

**Assessment:** This is a strong 4.7 description. It (a) states the job, (b) names the dispatch context (`/sr GATE 4a`), and (c) embeds the *one* principle this agent cannot compromise on — `Do NOT trust implementer claims — read the code`. Having the anti-trust principle in the frontmatter is exactly right for a dispatcher-read surface on 4.7 (INSIGHTS §1 dispatcher bias). The `Do NOT` here *is* load-bearing (not an emphasis intensifier) — keep it.

**Tools line (line 4):** `Read, Grep, Glob, Edit, Write, Bash` — appropriate. `Bash` is justified because compliance verification may require running tests to confirm an acceptance criterion. No change needed.

**Model line (line 5):** `model: opus` — correct; this agent needs Opus for multi-file reasoning. No change needed.

---

### HIGH priority

#### H1. "DO NOT trust the implementer's report" is clearly stated — reinforce with positive framing (INSIGHTS §2.6, §4)

**Location:** `spec-compliance-reviewer.md:13`

**Current text:**
> `**DO NOT trust the implementer's report, summary, or task document checkboxes.** Read the actual code files and verify each requirement independently. Implementers often claim coverage of edge cases that were not actually handled, or mark criteria as complete when the implementation is partial.`

**Assessment:** This section is actually **well-tuned** — it pairs the negative injunction with a positive directive (`Read the actual code files and verify each requirement independently`) AND gives the *why* (implementers over-claim). Per INSIGHTS §2.2 and §2.6, this is the right shape.

**One refinement:** INSIGHTS §4 ("Investigate-before-answering") — make the minimum evidence standard explicit. On 4.7's more conservative tool use (INSIGHTS §1), an agent told *"read the code"* may still get away with reading 1 file of 5 and generalizing. State the coverage rule literally.

**Before → After:**

Before:
```
**DO NOT trust the implementer's report, summary, or task document checkboxes.** Read the actual code files and verify each requirement independently. Implementers often claim coverage of edge cases that were not actually handled, or mark criteria as complete when the implementation is partial.
```

After:
```
**Do not trust the implementer's report, summary, or task document checkboxes.** Open every file the criterion touches and verify the behavior in code. One file read per criterion is the floor, not the ceiling — if a criterion spans a controller, a service, and a DTO, read all three before marking IMPLEMENTED. Implementers often claim coverage of edge cases that were not actually handled, or mark criteria complete when the implementation is partial.
```

This tightens §4 ("Investigate-before-answering") and states scope literally per INSIGHTS §1 ("4.7 will NOT silently generalize").

---

#### H2. No coverage-then-filter guidance — the agent may suppress PARTIAL findings (INSIGHTS §1, §4)

**Location:** Applies to the whole file; missing directive. Relevant site: after `spec-compliance-reviewer.md:25` (the `IMPLEMENTED / PARTIAL / MISSING / EXTRA` ladder).

**Why:** The agent has a clean IMPLEMENTED/PARTIAL/MISSING ladder — good. But there's no instruction to *prefer marking PARTIAL over IMPLEMENTED when uncertain*. On 4.7's literal-obedience profile (INSIGHTS §1), an agent told to "verify each criterion" will tend toward binary IMPLEMENTED vs MISSING and skip the fuzzy middle, which is exactly where compliance drift hides.

**Before → After (add after line 25):**

After (new line):
```
When evidence is mixed or incomplete, mark PARTIAL and note what is missing — never round up to IMPLEMENTED. Under-reporting PARTIAL findings here hides drift from the downstream architecture and QA gates. Confidence lives in the Notes column; absence of confidence does not mean absence of a finding.
```

Maps to INSIGHTS §4 (coverage-then-filter).

---

### MEDIUM priority

#### M1. "you MUST" / "ONLY" intensifier pile-up (INSIGHTS §3)

**Locations:**
- `spec-compliance-reviewer.md:11` — `Your SOLE job is to verify that the implementation matches what was specified — nothing more, nothing less.`
- `spec-compliance-reviewer.md:44` — `**Primary focus**: Only review files listed in `changed_files``
- `spec-compliance-reviewer.md:46` — `**Context reading**: You MAY read unchanged files to understand interfaces or contracts, but do NOT flag issues in unchanged code`
- `spec-compliance-reviewer.md:67` — `**Do NOT** edit anything outside your section markers`
- `spec-compliance-reviewer.md:99` — `**Then return ONLY a short summary:**`
- `spec-compliance-reviewer.md:121` — `Your ONLY concern: **does the code do what the spec says it should do?**`

**Why:** INSIGHTS §3 — `SOLE`, `ONLY`, `MUST`, `do NOT` used as emphasis dial back. Several of these are load-bearing (line 46 is enforcing scope boundary — keep that one) but `SOLE`, two uses of `ONLY`, and the capitalized `Do NOT` stack up.

**Before → After (line 11):**

Before:
```
You are a spec compliance reviewer. Your SOLE job is to verify that the implementation matches what was specified — nothing more, nothing less.
```

After:
```
You are a spec compliance reviewer. Your job is to verify the implementation matches the specification — no more, no less. Quality, security, architecture, and performance are out of scope (other agents own those).
```

**Before → After (line 121):**

Before:
```
Your ONLY concern: **does the code do what the spec says it should do?**
```

After:
```
Your concern is one question: does the code do what the spec says it should do?
```

**Before → After (line 99):** See pattern from doc-accuracy M1.

---

#### M2. "What You Do NOT Review" is good content, weak framing (INSIGHTS §3)

**Location:** `spec-compliance-reviewer.md:113-120`

**Offending text:**
```
## What You Do NOT Review

These are owned by other agents — skip entirely:
- Code quality, naming, DRY → `code-quality-reviewer`
- Security vulnerabilities → `security-code-reviewer`
- Architecture fit, DDD layers → `senior-architecture-reviewer`
- Performance → `performance-reviewer`
- Test quality/coverage → `test-coverage-reviewer`
```

**Why:** INSIGHTS §2.6 (positive framing). The *table* is excellent (names the receiving agent, which is why the scope ownership is clear) but the section header is a double-negative.

**Before → After:**

Before:
```
## What You Do NOT Review

These are owned by other agents — skip entirely:
```

After:
```
## Scope Boundaries (owned by sibling agents)

These concerns are handled by other reviewers in the same `/sr` pipeline — defer to them:
```

---

#### M3. "Read the task document FIRST" — good, but add investigate-before-answer reinforcement (INSIGHTS §4)

**Location:** `spec-compliance-reviewer.md:125`

**Offending text:**
> `- Read the task document FIRST — you cannot verify compliance without knowing the spec`

**Why:** The instruction is correct and has the *why*. On 4.7, the `FIRST` intensifier is fine here because it's genuinely load-bearing (sequence-critical). One gap: when the task document is missing or the `cr_file_path`/`changed_files` are absent, the agent has no fallback. Current text assumes perfect input.

**Before → After:**

Before:
```
- Read the task document FIRST — you cannot verify compliance without knowing the spec
```

After:
```
- Read the task document before touching the code — you cannot verify compliance without the spec. If the task document is missing or acceptance criteria are unwritten, stop and return `NEEDS_CLARIFICATION` with a one-line reason. Do not invent criteria from commit messages or PR titles.
```

---

### LOW priority

#### L1. Input specification uses `**REQUIRED**:` but no handling for missing inputs (INSIGHTS §4 literal-scope)

**Location:** `spec-compliance-reviewer.md:54-57`

**Offending text:**
```
### Input

**REQUIRED**:
- Task document (tech-decomposition) — source of acceptance criteria
- `changed_files` — files to review
- `full_diff` — exact changes made
```

**Why:** 4.7 is more literal — absent explicit fallback, the agent will proceed anyway on partial input. Covered partially by M3; this is a structural note. Consider adding an explicit "if any REQUIRED input is missing, stop and request it" clause.

**Before → After:**

After (new line added after line 57):
```
If any REQUIRED input is missing, return a short diagnostic noting which input is missing and stop. Do not attempt partial review — compliance is a binary gate and incomplete evidence produces misleading PASS verdicts.
```

---

#### L2. Missing XML tag structure for multi-section output (INSIGHTS §2.3)

**Location:** Applies across `spec-compliance-reviewer.md:60-108` (Output section).

**Why:** INSIGHTS §2.3 — `XML tags for structure`. The output is a rich structured table with sub-sections (Requirements Verification, Extra Work, Issues). Currently delimited by markdown headers only. Not a blocker — markdown renders fine — but §2.3 notes quality lift when prompts instruct the model in XML.

Flagged Low because the current markdown-in-code-fence approach works and changing it could break the `/sr` CR merge flow.

---

#### L3. "Use the Edit tool" protocol duplicated across agents (consistency)

**Location:** `spec-compliance-reviewer.md:63-66` vs `documentation-accuracy-reviewer.md:51-54`

**Why:** The 4-step Edit protocol is copy-pasted between the two agents (and presumably others in the `/sr` family). Not a 4.7 issue — a maintainability note. If the shared `review-conventions` skill already contains this protocol (referenced via `skills:` frontmatter on both agents), the duplicated block could be replaced with a one-line pointer. Did not verify the skill file — flagging only.

---

## 3. Summary Scorecard

| Agent | Frontmatter | Coverage-then-filter | Investigate-before-answer | Intensifier hygiene | Overall |
|---|---|---|---|---|---|
| documentation-accuracy-reviewer | Good | **Missing** (H1) | Missing (M3) | Several pile-ups | Needs High fix + medium tune |
| spec-compliance-reviewer | Strong | Partial — ladder exists, preference missing (H2) | Strong core, scope gap (H1) | Moderate pile-ups | One tightening pass recommended |

**Top three edits across both files (by impact on 4.7 behavior):**
1. `documentation-accuracy-reviewer.md:86` — replace `>80% confident` filter with coverage-then-filter + confidence tags (High, H1).
2. `spec-compliance-reviewer.md:13` — add "one file per criterion is the floor" to defeat partial-read generalization (High, H1).
3. `spec-compliance-reviewer.md` (after line 25) — add explicit "prefer PARTIAL over rounding up to IMPLEMENTED" directive (High, H2).

**What's already well-tuned (don't change):**
- `spec-compliance-reviewer.md:3` frontmatter — embeds the load-bearing anti-trust principle where a 4.7 dispatcher will see it.
- `spec-compliance-reviewer.md:11-14` Core Principle — pairs negative with positive and rationale per INSIGHTS §2.2.
- `spec-compliance-reviewer.md:113-120` scope-ownership table — names the receiving agent, resolving 4.7 literal-scope questions cleanly (header framing aside, see M2).
- `documentation-accuracy-reviewer.md:34-42` Diff-Scoped Review — numbered, explicit, literal per INSIGHTS §1 row 7.
- Both agents' output formats (severity-tagged findings + one-line summary) match 4.7's adaptive length without hard caps.
