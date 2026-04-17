# Agent Review — `plan-reviewer` and `task-decomposer`

**Files audited:**
- `.claude/agents/tasks-validators-agents/plan-reviewer.md` (133 lines)
- `.claude/agents/tasks-validators-agents/task-decomposer.md` (217 lines)

**Lens:** Opus 4.7 prompting best practices — see `tasks/opus-4-7-skill-review/INSIGHTS.md`.

Both agents are task-lifecycle subagents. `plan-reviewer` is review-like (coverage-then-filter applies; INSIGHTS §1 code-review row, §3 filter-leakage, §4). `task-decomposer` is a structural/formatting agent (literal-scope gaps and XML structure apply, §4).

---

## Agent 1: `plan-reviewer`

### Frontmatter

**Current:**
```yaml
name: plan-reviewer
description: Review a technical decomposition for implementation readiness before `/si`. Validate functional depth, step sequencing, codebase fit, testing strategy, and risks; write a canonical plan review document.
model: opus
color: yellow
```

**Assessment:** Description is well-scoped — it names the artifact (`technical decomposition`), a concrete trigger boundary (`before /si`), and the deliverable (`plan review document`). No over-broad verbs like "review any plan" or "check any design." Under 4.7's action-biased dispatcher behavior (§1), this avoids over-dispatch onto adjacent tasks such as architecture review, code review, or PRD review.

**Priority: None — already tight.** Leave as-is.

---

### High Priority

#### H1. Filter-leakage risk in the "Core Lens: Reality Check" section (INSIGHTS §3, §4)

**Location:** `plan-reviewer.md:21-29`

**Offending text:**
> "Be skeptical of shallow plans. **Reject** plans that mostly create:
> - mock screens
> - empty scaffolding
> - placeholder types or interfaces
> - speculative contracts with no real consumer
> - "looks like it works" steps without working behavior"

**Why it matters on 4.7:** 4.7 obeys severity/filter cues more literally (INSIGHTS §1, code-review row). The word "reject" combined with a fixed blacklist is a *filter-at-find-time* pattern. Legitimate plans that contain *some* scaffolding as a sub-step (e.g., a deliberate stub before a migration) may be flagged as shallow and rejected, or conversely, the reviewer may under-report other defects because the reality-check is the mental anchor. This is exactly the "coverage-then-filter" failure mode INSIGHTS §4 warns about.

**Before:**
> "Be skeptical of shallow plans. Reject plans that mostly create:
> - mock screens
> - empty scaffolding
> …"

**After:**
> "Be skeptical of shallow plans. **Surface every instance** of the following patterns you find, with location and severity — a separate verdict step will decide whether the plan is rejected:
> - mock screens with no real consumer
> - empty scaffolding that is not followed by wiring
> - placeholder types or interfaces that aren't implemented in a later step
> - speculative contracts with no real consumer
> - 'looks like it works' steps without working behavior
>
> A plan is only *rejected* if these patterns dominate the plan — isolated scaffolding steps are acceptable when they set up clearly-implemented follow-ups."

**Priority: High.**

---

#### H2. "Only report critical/major issues" risk in Severity Guidance (INSIGHTS §3, §4)

**Location:** `plan-reviewer.md:92-95`

**Offending text:**
> "- **Critical**: blocks implementation, would create incorrect or incomplete behavior, or leaves key contracts or flows undefined
> - **Major**: important gap or ambiguity that should be fixed before implementation, but does not invalidate the whole plan
> - **Minor**: quality improvement, hardening, or clarity upgrade that is valuable but not blocking"

**Why it matters on 4.7:** The three-tier definition is fine, but the agent is never told to **report all tiers**. INSIGHTS §1 (code-review row): "Obey severity/confidence filters more literally — recall may appear to drop." And §4: "Report every issue you find, including low-severity and uncertain ones. Include confidence + severity. A separate verification step will filter." Without that instruction, 4.7 may silently suppress Minor/uncertain findings to feel "focused."

**Before:**
> "## Severity Guidance
>
> - **Critical**: blocks implementation…
> - **Major**: important gap or ambiguity…
> - **Minor**: quality improvement, hardening, or clarity upgrade that is valuable but not blocking"

**After:**
> "## Severity Guidance
>
> Report **every** issue you find at all three tiers, including uncertain ones. Tag each with severity and a one-word confidence (high/medium/low). The verdict step at the end filters; the discovery step must prioritize coverage.
>
> - **Critical**: blocks implementation, would create incorrect or incomplete behavior, or leaves key contracts or flows undefined
> - **Major**: important gap or ambiguity that should be fixed before implementation, but does not invalidate the whole plan
> - **Minor**: quality improvement, hardening, or clarity upgrade that is valuable but not blocking
>
> Do not suppress Minor findings to keep the review short. If there are no findings at a tier, say so explicitly."

**Priority: High.**

---

### Medium Priority

#### M1. "Do not speculate" rationale could be strengthened (INSIGHTS §2.2, §4 investigate-before-answering)

**Location:** `plan-reviewer.md:59-65`

**Offending text:**
> "### Step 2: Validate Against the Codebase
> Before making recommendations, inspect relevant files, modules, or reference docs to verify:
> - existing patterns the plan should follow
> - likely integration points
> - whether proposed file or module boundaries make sense
> - whether dependencies or sequencing assumptions are realistic
>
> Do not speculate about code you have not inspected."

**Why it matters on 4.7:** The rule is correct but INSIGHTS §2.2 ("Explain the *why* — rationale > rules") and §4 note that 4.7 tends to underuse tools (§1, tool-use row). A short "why" anchors the behavior and keeps the agent from reasoning-its-way-around instead of reading.

**Before:**
> "Do not speculate about code you have not inspected."

**After:**
> "Do not speculate about code you have not inspected. Findings grounded in real files survive implementation; findings from guessed behavior waste the author's time and erode trust in the review. If a file is referenced in the plan but you haven't opened it, open it before commenting on it."

**Priority: Medium.**

---

#### M2. XML structure missing around the five review lenses (INSIGHTS §2.3)

**Location:** `plan-reviewer.md:67-85` (Step 3 block)

**Why it matters:** The five-lens block is a dense instruction bundle mixed with criteria. INSIGHTS §2.3 recommends XML tags for structured instruction blocks. Wrapping the lenses in `<review_lenses>` with per-lens `<lens name="…">` sub-tags would make 4.7 traverse each lens deterministically rather than merging them. Not essential, but it would help the agent produce a matrix-style review.

**Before:**
```markdown
### Step 3: Review Across Five Lenses
1. **Reality check**
   - …
2. **Step quality**
   - …
```

**After (sketch):**
```markdown
### Step 3: Review Across Five Lenses

Walk each lens independently. Do not merge findings across lenses at the discovery stage.

<review_lenses>
  <lens name="reality_check">
    - Does the plan produce real functionality, not scaffolding or placeholders?
    - …
  </lens>
  <lens name="step_quality">…</lens>
  <lens name="testing">…</lens>
  <lens name="risk_and_dependencies">…</lens>
  <lens name="codebase_fit">…</lens>
</review_lenses>
```

**Priority: Medium.**

---

#### M3. No explicit parallelization cue for Step 1 reads (INSIGHTS §4 parallel tool-calling)

**Location:** `plan-reviewer.md:51-57`

**Offending text:**
> "### Step 1: Read the Plan and Supporting Context
> 1. Read the required tech decomposition completely.
> 2. Read the canonical tech decomposition template to judge missing or malformed sections.
> 3. Read the canonical plan review template you will write into.
> 4. Read only the supporting docs that materially affect the review."

**Why it matters on 4.7:** Four independent file reads with no dependencies between them. 4.7 under-parallelizes by default (INSIGHTS §1 subagent row, §4 parallel tool-calling). The numbered list reads as sequential.

**Before:**
> "1. Read the required tech decomposition completely.
> 2. Read the canonical tech decomposition template…
> 3. Read the canonical plan review template…
> 4. Read only the supporting docs…"

**After:**
> "Read these in a single batched turn — they have no dependencies on each other:
> - the required tech decomposition completely
> - the canonical tech decomposition template (`.claude/docs/templates/technical-decomposition-template.md`)
> - the canonical plan review template (`.claude/docs/templates/plan-review-template.md`)
> - any supporting docs that materially affect the review (skip ones that don't)"

**Priority: Medium.**

---

### Low Priority

#### L1. Two stray `NOT` / `NOT` intensifiers (INSIGHTS §3 intensifier hygiene)

**Locations:** `plan-reviewer.md:12` ("You do **NOT**:") and `plan-reviewer.md:88` ("Do **NOT** invent a second custom plan review format.")

**Assessment:** Both uses are load-bearing (scope fencing and template enforcement), so keep them — this is not intensifier abuse, it's explicit scope. Flag as **No change needed.** INSIGHTS §3 targets reflexive `CRITICAL:`/`MUST`/`ALWAYS`, which this agent avoids almost entirely. Leaving this note so the audit is complete.

**Priority: Low (informational).**

---

#### L2. Positive framing opportunity in "Quality Standards"

**Location:** `plan-reviewer.md:104-109`

**Offending text:**
> "- Prioritize actionable feedback over generic advice
> - Prefer concrete examples and affected sections or steps
> - Call out superficial or placeholder planning explicitly
> - If no issues are found, say so clearly
> - Keep the review focused on implementation readiness"

**Why it matters:** The list is already mostly positive, which is good (INSIGHTS §2.6). One small tightening: "Keep the review focused on implementation readiness" is mildly negative-shaped ("don't drift"). Pairing it with an affirmative frame helps 4.7's adaptive length calibration (INSIGHTS §1 response-length row).

**Before:**
> "Keep the review focused on implementation readiness"

**After:**
> "Scope every finding to implementation readiness — if a finding is about long-term strategy or pure aesthetics, drop it from the review and log it as a future note instead."

**Priority: Low.**

---

## Agent 2: `task-decomposer`

### Frontmatter

**Current:**
```yaml
name: task-decomposer
description: Execute an approved split by creating phase folders and phase-specific tech-decomposition documents aligned to the canonical template. Invoked after task-splitter recommends split and the user approves.
model: opus
color: blue
```

**Assessment:** Excellent — the description names both the prerequisite (`task-splitter recommends split`) and the gate (`user approves`), which is exactly the scope-fencing 4.7 rewards. It cannot be over-dispatched onto "decompose this idea" or "split this task" requests because the trigger explicitly requires a prior `splitting-decision.md` artifact.

**Priority: None — already tight.** Leave as-is.

---

### High Priority

#### H1. "Do NOT invent new content" is good, but over-engineering guard is missing for phase-doc generation (INSIGHTS §3, §4 over-engineering)

**Location:** `task-decomposer.md:202-207` (Important Notes)

**Offending text:**
> "1. **Do NOT invent new content** - only extract, reorganize, and clarify from the approved documents
> 2. **Preserve traceability** - keep original `REQ-XXX` and test references wherever possible
> 3. **Use the canonical template** - phase docs should look like normal tech-decompositions, not a second bespoke format"

**Why it matters on 4.7:** Rules are correct but rationale-free (INSIGHTS §2.2). More importantly, 4.7 is more literal but still drifts toward over-engineering (INSIGHTS §1 overeagerness row; §4 minimize over-engineering pattern). During phase-doc generation, the agent is tempted to "clarify" by adding new contract details or "improve" test plans — which silently introduces content that was not in the parent. The phrase "clarify from the approved documents" actively invites this.

**Before:**
> "1. **Do NOT invent new content** - only extract, reorganize, and clarify from the approved documents"

**After:**
> "1. **Do not invent new content** — extract and reorganize from the approved parent and `splitting-decision.md` only. 'Clarifying' is allowed only when it means rewording a sentence for the phase context; it is never an excuse to add new REQs, new tests, new decisions, new steps, or new contract shapes. If a phase feels under-specified, stop and ask the user — do not fill the gap yourself.
> *Rationale: the parent document is the source of truth for traceability. Any new content introduced here bypasses review and breaks the audit trail back to the PRD.*"

**Priority: High.**

---

#### H2. Literal-scope gap on "each phase" in Fill Rules (INSIGHTS §1 instruction-following, §3, §4)

**Location:** `task-decomposer.md:97-140` (Fill Rules For Each Phase Document)

**Offending text:**
> "### Fill Rules For Each Phase Document
>
> Populate each section as follows:
>
> - **Title / Status**:
>   - Title becomes `Technical Decomposition: Phase N - [Phase Name]`
>   …"

**Why it matters on 4.7:** INSIGHTS §1 (instruction-following row): "More literal; will NOT silently generalize. State scope explicitly ('apply to every section, not just the first')." The header says "For Each Phase Document" once, but the 8-subsection fill rules are written as a single list without restating scope. 4.7 may apply them fully to phase 1 and shortcut phase 2 and 3 ("same as phase 1").

**Before:**
> "### Fill Rules For Each Phase Document
>
> Populate each section as follows:"

**After:**
> "### Fill Rules For Each Phase Document
>
> Apply every rule below to **every** phase document you generate — not only the first. Each phase must be a self-contained, canonical tech-decomposition on its own, even if that means repeating structure across phases."

**Priority: High.**

---

### Medium Priority

#### M1. No parallelization cue for reading and generating phase documents (INSIGHTS §1 subagent row, §4 parallel subagent prompting, parallel tool-calling)

**Location:** `task-decomposer.md:29-45` (Step 1 reads), `task-decomposer.md:79-90` (Step 4 phase-doc generation)

**Why it matters on 4.7:** Two clear parallelism opportunities:
1. Step 1 reads four independent files (`splitting-decision.md`, `tech-decomposition-*.md`, the canonical template, optional supporting docs) — these have no dependencies.
2. Step 4 generates N phase documents that are independent of each other once Step 2 validation passes — this is a classic fan-out.

4.7 under-parallelizes by default (INSIGHTS §1 subagent row).

**Before (Step 1):**
> "1. Read `splitting-decision.md` to understand…
> 2. Read `tech-decomposition-[feature].md` to extract…
> 3. Read the canonical template at…"

**After (Step 1):**
> "Read these three documents in a single batched turn — they have no dependencies on each other:
> - `splitting-decision.md` (phase names, goals, sequence, dependencies, contracts)
> - `tech-decomposition-[feature].md` (Must Haves, Test Plan, Technical Requirements, Implementation Decisions, Implementation Steps, Dependencies / Risks / Blockers)
> - `.claude/docs/templates/technical-decomposition-template.md` (canonical structure)"

**Before (Step 4):**
> "For each phase, create:
>
> ```text
> phase-N-[phase-name-kebab-case]/tech-decomposition-phase-N-[phase-name-kebab-case].md
> ```"

**After (Step 4):**
> "Once Step 2 validation passes, the N phase documents are independent of one another. Generate them in a single batched turn — do not serialize phase 1 → phase 2 → phase 3 unless you need content from one phase's draft to inform another (which should not happen given the validated split).
>
> For each phase, create:
>
> ```text
> phase-N-[phase-name-kebab-case]/tech-decomposition-phase-N-[phase-name-kebab-case].md
> ```"

**Priority: Medium.**

---

#### M2. XML structure would help the dense Step 3–4 fill-rule block (INSIGHTS §2.3)

**Location:** `task-decomposer.md:69-140`

**Why it matters:** The Step 4 "Fill Rules" bundle is 8 nested bullet-list rules that apply to 8 template sections. INSIGHTS §2.3: "XML tags for structure: `<instructions>`, `<context>`, `<input>`, `<document>`, `<example>`." Wrapping each section's fill rule in `<section name="…">` would let 4.7 iterate deterministically over the template sections rather than merging rules.

**Before:**
```markdown
### Fill Rules For Each Phase Document
- **Title / Status**: …
- **Linked Inputs / Context**: …
- **Primary Objective**: …
```

**After (sketch):**
```markdown
### Fill Rules For Each Phase Document

Apply every rule to every phase doc.

<fill_rules>
  <section name="title_status">
    Title becomes `Technical Decomposition: Phase N - [Phase Name]`.
    Status reflects readiness for implementation.
  </section>
  <section name="linked_inputs_context">
    Reference the parent tech-decomposition, `splitting-decision.md`, and relevant supporting docs.
  </section>
  <section name="primary_objective">…</section>
  <section name="must_haves">…</section>
  <section name="test_plan">…</section>
  <section name="technical_requirements">…</section>
  <section name="implementation_decisions">…</section>
  <section name="implementation_steps">…</section>
  <section name="dependencies_risks_blockers">…</section>
  <section name="tracking_notes">…</section>
</fill_rules>
```

**Priority: Medium.**

---

#### M3. Example Invocation is light and untagged (INSIGHTS §2.5)

**Location:** `task-decomposer.md:188-194`

**Offending text:**
> "## Example Invocation
>
> ```text
> Execute the approved splitting decision.
>
> Task directory: /Users/.../tasks/task-2026-01-06-smart-word-selection/
>
> Create phase folders and phase tech-decomposition documents aligned to the canonical template.
> ```"

**Why it matters:** INSIGHTS §2.5 recommends "3–5, relevant + diverse + wrapped in `<example>` / `<examples>` tags." One example in a plain code block is below the recommendation and doesn't show the happy path vs. the clarification-needed path.

**Before:**
> (as above — single unexampled block)

**After (sketch):**
```markdown
## Example Invocations

<examples>
  <example label="happy_path_three_phases">
    User: Execute the approved splitting decision.
    Task directory: /Users/.../tasks/task-2026-01-06-smart-word-selection/

    Expected: 3 phase folders created, 3 phase tech-decompositions, splitting-decision.md updated with Decomposition Complete section, parent doc untouched.
  </example>
  <example label="stop_on_forward_contract">
    User: Execute the approved splitting decision.
    Task directory: /Users/.../tasks/task-2026-02-10-auth-refresh/

    Finding: splitting-decision.md places the token-rotation endpoint shape in Phase 2, but Phase 1 already calls it.
    Expected: stop, report the forward-contract violation, ask the user to revise the split. No folders or files created.
  </example>
  <example label="stop_on_ambiguous_split">
    User: Execute the approved splitting decision.
    Task directory: /Users/.../tasks/task-2026-03-04-profile-redesign/

    Finding: splitting-decision.md has three phases but does not assign REQ-014 or test SUITE-profile-avatar to any phase.
    Expected: stop, list the unassigned items, ask the user to clarify. No folders or files created.
  </example>
</examples>
```

**Priority: Medium.**

---

### Low Priority

#### L1. Intensifier count is reasonable; flag `ONLY` and `NEVER` once for context (INSIGHTS §3)

**Locations:**
- `task-decomposer.md:12` ("You do **NOT** create tracker issues…")
- `task-decomposer.md:17` ("You are invoked **ONLY** when:")
- `task-decomposer.md:58` ("Do **NOT** silently repair or reinterpret it.")
- `task-decomposer.md:87` ("Do NOT invent a second custom tech-decomposition format.")
- `task-decomposer.md:166` ("Do NOT rename, archive, or delete the parent tech-decomposition.")
- `task-decomposer.md:202-206` (the four "Do NOT…" bullets in Important Notes)

**Assessment:** Every one of these is load-bearing scope fencing — they define what this agent does *not* do, preventing it from expanding into task-splitter's or tracker-sync's territory. Per INSIGHTS §3, the anti-pattern is intensifiers used as *emphasis*, not as scope. These are fine. **No change needed**, but worth noting there are ~8 NOT/ONLY uses; if any are deleted later, make sure they're the non-scoping ones.

**Priority: Low (informational).**

---

#### L2. No compaction-awareness note (INSIGHTS §4)

**Location:** Whole file (not currently present)

**Why it matters:** INSIGHTS §4 recommends a compaction-aware prompt for long-running skills. This agent generates 2–N phase documents plus updates — plausibly 2,000–5,000 tokens of output. It's medium-length, not long-running in the multi-turn sense, so compaction risk is low. A one-line nudge would be defensive, not essential.

**Proposed addition (optional, after "## Important Notes"):**
> "If this decomposition spans many phases (5+) and you approach a context refresh, finish the current phase document, then save phase-list + completed-phase names to the task directory before producing the next one."

**Priority: Low (defensive only — skip if scope is always 2–4 phases).**

---

#### L3. "Do not guess" could use rationale (INSIGHTS §2.2)

**Location:** `task-decomposer.md:44` and `task-decomposer.md:58`

**Offending text:**
> "If any of this is unclear, stop and ask the user to clarify the split. Do not guess."

**After:**
> "If any of this is unclear, stop and ask the user to clarify the split. Do not guess.
> *Rationale: guessed phase boundaries silently corrupt traceability — the implementer in `/si` has no way to tell invented content from approved content.*"

**Priority: Low.**

---

## Summary

| Agent | Frontmatter | High | Medium | Low |
|---|---|---|---|---|
| `plan-reviewer` | Tight, no change | 2 (filter-leakage, coverage-then-filter) | 3 (rationale, XML, parallel reads) | 2 (informational) |
| `task-decomposer` | Tight, no change | 2 (over-engineering guard, literal-scope) | 3 (parallelization, XML, examples) | 3 (informational + optional) |

**Top fixes to prioritize** if only two changes per agent are made:

- `plan-reviewer`: H1 (reality-check filter-leakage) and H2 (coverage-then-filter on severity).
- `task-decomposer`: H1 (strengthen the "do not invent" guard with rationale) and H2 (state literal scope on fill rules for every phase).

Both agents are already well-structured and scope-disciplined. The frontmatter descriptions are model examples of action-biased dispatchers that resist over-dispatch. The recommendations above are targeted tunings for 4.7's literal-obedience and under-parallelization defaults, not structural rewrites.
