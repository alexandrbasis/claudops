# Opus 4.7 Skill Audit — `ct` and `rip`

Scope: `.claude/skills/ct/SKILL.md` (318 lines) and `.claude/skills/rip/SKILL.md` (131 lines). Each skill has a single `SKILL.md` file — no subdirectories. Both reviewed against `tasks/opus-4-7-skill-review/INSIGHTS.md` §3 anti-patterns and §4 positive patterns.

---

## Skill 1: `ct` (Create Task / Technical Decomposition)

Overall: **Well-tuned for 4.7 on the big-ticket items.** Explicit parallel subagent prompting at Gate 2 (INSIGHTS §4), strong scope-protection language (INSIGHTS §4 over-engineering mitigation), no filter leakage, no hard response-length caps, no prefill patterns. The remaining findings are dial-back items and a few missing rationales.

### High priority

#### H1. Add compaction-awareness for this long-running, multi-gate skill
**Finding:** The skill has 7 gates (Gate 0 through Gate 6) with subagent launches, user Q&A via `AskUserQuestion`, and output to a file — easily long enough to trigger auto-compaction. No context-awareness guidance is present.
**Location:** `.claude/skills/ct/SKILL.md:15-32` (PRIMARY OBJECTIVE + CORE PRINCIPLES) — appropriate place to add.
**Cross-ref:** INSIGHTS §4 "Context will be automatically compacted. Do not stop early due to token concerns. Save state to memory before refresh."
**Before:**
```markdown
## CORE PRINCIPLES
- **Test plan first** — define what proves the work is done before describing how to build it
...
- **Stay executable** — name files, commands, dependencies, and completion signals explicitly
```
**After:**
```markdown
## CORE PRINCIPLES
- **Test plan first** — define what proves the work is done before describing how to build it
...
- **Stay executable** — name files, commands, dependencies, and completion signals explicitly
- **Context is compacted automatically** — for long sessions, save the in-progress decomposition to disk as you go; do not stop early due to token concerns
```

#### H2. Parallelize Gate 1 discovery and Gate 1.5 read-through
**Finding:** Gate 1 lists many glob patterns (`**/discovery-*.md`, `**/JTBD-*.md`, `**/PRD*.md`, …) that are independent lookups; Gate 2 already batches exploration but Gate 1 implicitly runs sequentially. INSIGHTS §1 notes 4.7 "under-parallelizes by default" and §4 recommends "batch them in one turn" for independent calls.
**Location:** `.claude/skills/ct/SKILL.md:54-67` (Gate 1 "Look for" list).
**Cross-ref:** INSIGHTS §4 "Parallel tool-calling… When calls have no dependencies, batch them in one turn."
**Before:**
```markdown
**Look for:**
- Discovery docs: `**/discovery-*.md`
- Product docs: `**/JTBD-*.md`, `**/PRD*.md`, `**/*requirements*.md`
- Architecture notes: `**/ADR*.md`, `**/*architecture*.md`, `**/*decision*.md`
- Existing plans: `**/tech-decomposition-*.md`, `**/*implementation-plan*.md`
- Optional supporting artifacts: prototypes, flow diagrams, issue links, design notes
```
**After:**
```markdown
**Look for (run these Glob calls in a single turn — they are independent):**
- Discovery docs: `**/discovery-*.md`
- Product docs: `**/JTBD-*.md`, `**/PRD*.md`, `**/*requirements*.md`
- Architecture notes: `**/ADR*.md`, `**/*architecture*.md`, `**/*decision*.md`
- Existing plans: `**/tech-decomposition-*.md`, `**/*implementation-plan*.md`
- Optional supporting artifacts: prototypes, flow diagrams, issue links, design notes
```

### Medium priority

#### M1. Dial back absolute instructions into normal voice
**Finding:** Several instructions use hard imperatives without being genuinely load-bearing on 4.7. These now risk over-triggering per INSIGHTS §3 ("CRITICAL / MUST / ALWAYS / NEVER used as intensifiers — dial back").
**Locations:**
- `SKILL.md:252` — `Do not skip the required review path for the selected complexity level.`
- `SKILL.md:266` — `Always invoke the \`task-splitter\` agent on the finalized parent plan.`
- `SKILL.md:225` — `**Required sections:**` list followed by an implicit "all required"
- `SKILL.md:47` — `Exclude time estimates from the plan`
- `SKILL.md:233` — `Exclude time estimates`

**Cross-ref:** INSIGHTS §3 first bullet; §2 rule #2 ("rationale > rules").
**Before:**
```markdown
Do not skip the required review path for the selected complexity level.
```
**After:**
```markdown
Follow the review path for the complexity tier above — skipping it has historically produced plans that miss architecture risks and require re-decomposition.
```

**Before:**
```markdown
Always invoke the `task-splitter` agent on the finalized parent plan.
```
**After:**
```markdown
Invoke the `task-splitter` agent on the finalized parent plan so the splitting decision is made against the reviewed doc, not a draft.
```

#### M2. Add rationale for "Exclude time estimates"
**Finding:** Appears twice (`:47`, `:233`) as a bare rule. 4.7 prefers the *why* over the rule (INSIGHTS §2 rule #2: "Explain the why — rationale > rules").
**Cross-ref:** INSIGHTS §2.
**Before:**
```markdown
- Exclude time estimates
```
**After:**
```markdown
- Exclude time estimates — this doc is a technical contract, not a schedule; estimates expire fast and mislead consumers of the doc
```

#### M3. Strengthen Gate 2 parallel prompt to "same turn" wording
**Finding:** Gate 2 says `Launch **2-3 Explore agents in parallel**` (`SKILL.md:108`) which is a positive pattern per INSIGHTS §4, but the word "parallel" alone can still be read as "concurrently over the gate's duration." The INSIGHTS §4 exemplar wording is stronger: "Spawn multiple subagents **in the same turn**."
**Location:** `.claude/skills/ct/SKILL.md:108`.
**Cross-ref:** INSIGHTS §4 "Parallel subagent prompting."
**Before:**
```markdown
Launch **2-3 Explore agents in parallel**, each with a specific mandate:
```
**After:**
```markdown
Launch **2-3 Explore agents in a single turn** (fan out in the same tool-call batch — do not sequence them), each with a specific mandate:
```

#### M4. Gate 5 review-path selection could leak "only report important" literalism
**Finding:** The complexity matrix at `SKILL.md:242-247` decides *which* reviewers to run, not what they report. But if `plan-reviewer` or `senior-architecture-reviewer` agents are themselves prompted with "only important issues" patterns, this skill will inherit filter leakage (INSIGHTS §3). Not a change for this file — **recommend a cross-link note** telling auditors to verify the reviewer-agent prompts follow coverage-then-filter.
**Location:** `.claude/skills/ct/SKILL.md:242-247`.
**Cross-ref:** INSIGHTS §3 "Only report high-severity / important issues… recall drops"; §4 "Coverage-then-filter split."
**Before:**
```markdown
| Simple | 1-2 focused steps | `plan-reviewer` agent |
| Medium | 3-5 steps, multiple touchpoints | `plan-reviewer` agent + `senior-architecture-reviewer` agent |
| Complex | 6+ steps, architecture or cross-system risk | `plan-reviewer` agent + `senior-architecture-reviewer` agent + cross-AI validation |
```
**After:** (same table, plus a note beneath)
```markdown
> Reviewer agents should follow a coverage-then-filter pattern — surface every issue they find (with severity + confidence), and filter in a separate pass. Do not instruct them to report "only important" findings; 4.7 obeys that literally and recall drops.
```

### Low priority

#### L1. `GATE 0` phrasing "Complete BEFORE writing the plan"
**Finding:** "BEFORE" is in all caps across all six gate headers (`SKILL.md:34, 51, 86, 105, 152, 175, 241, 263`). Not an intensifier per INSIGHTS §3, but the visual shouting is unnecessary on 4.7 — the model already respects sequence when it is stated once.
**Cross-ref:** INSIGHTS §3 intensifier bullet (borderline case).
**Before:**
```markdown
**Complete BEFORE writing the plan:**
```
**After:**
```markdown
**Complete before writing the plan:**
```

#### L2. Positive framing for "do not invent" in Gate 4
**Finding:** `SKILL.md:232` — `Do not invent 'Issue ID', 'Branch / PR', 'Split status', or 'Completion Summary' values during /ct unless they already exist`. Negative framing. INSIGHTS §2 rule #6: "Positive framing beats negative."
**Before:**
```markdown
- Do not invent `Issue ID`, `Branch / PR`, `Split status`, or `Completion Summary` values during `/ct` unless they already exist from prior workflow steps
```
**After:**
```markdown
- Leave `Issue ID`, `Branch / PR`, `Split status`, and `Completion Summary` blank or omitted unless prior workflow steps produced real values — those fields are owned by later skills (`/si`, tracker integration) and must reflect reality
```

#### L3. Minor XML opportunity at Gate 4 "Required sections"
**Finding:** Gate 4 mixes instructions, a required-section list (`SKILL.md:183-193`), and code-fence templates. INSIGHTS §2 rule #3 suggests XML tags for structure when instructions + context + examples are interleaved. Low priority because the current markdown is already navigable.
**Cross-ref:** INSIGHTS §2 rule #3.
**Before:** (current flat markdown)
**After (optional):**
```markdown
<required_sections>
- Linked Inputs / Context
- Primary Objective
- Must Haves
...
</required_sections>
```

---

## Skill 2: `rip` (Review Implementation Plan)

Overall: **Short, clean, mostly well-tuned.** No subagent spawning (so §4 parallel-subagent note doesn't apply), strong "verify, don't assume" pattern, positive framing on most rules, no heavy intensifiers. Main issues: one filter-leakage risk on PRD flagging, a forced-interaction pattern that fights 4.7's calibrated response length, and a missing "read before answering" guard is partially present but could be stronger.

### High priority

#### H1. "Flag PRD mismatches only when present" risks filter leakage
**Finding:** The "Criticality" row instructs: `Flag PRD mismatches **only** when present` (`SKILL.md:98`). 4.7 obeys "only" literally. Combined with the soft wording "if any" appearing in multiple format blocks (`SKILL.md:45, 68`), the net effect is the model under-reports borderline/unsure mismatches — the exact recall-drop failure mode described in INSIGHTS §3 and §1 ("Obey severity/confidence filters more literally — recall may *appear* to drop").
**Location:** `.claude/skills/rip/SKILL.md:98`.
**Cross-ref:** INSIGHTS §3 "Only report high-severity / important issues"; §4 "Coverage-then-filter split."
**Before:**
```markdown
| Criticality | Flag PRD mismatches **only** when present |
```
**After:**
```markdown
| Criticality | Surface every potential PRD mismatch, including uncertain ones; mark each with confidence (high/medium/low). Present them all in the Warning block — let the user decide what is in scope. |
```
And tune the `**Warning** (if any)` placeholders at `:45` and `:68` to `**Warnings (include uncertain ones with confidence tag):**`.

#### H2. Phase 2 forced "wait for user before advancing to each step" fights 4.7's adaptive-length default and interactive-coding delta
**Finding:** `SKILL.md:57` — `Wait for user confirmation ("ready", "next") before advancing to each step.` This is an explicit back-and-forth interaction loop. INSIGHTS §1 (Interactive coding row): "More post-user-turn reasoning → more tokens. Front-load full context in turn 1; minimize interactive back-and-forth." Enforced per-step gating multiplies the token cost on 4.7 significantly.
**Location:** `.claude/skills/rip/SKILL.md:57`.
**Cross-ref:** INSIGHTS §1 "Interactive coding" row.
**Before:**
```markdown
Wait for user confirmation ("ready", "next") before advancing to each step. Verify PRD alignment per step — if mismatch found, flag it and request confirmation before continuing.
```
**After:**
```markdown
Default to a continuous walkthrough in one response (all steps, back-to-back) — 4.7 calibrates length well and one message is cheaper than N turns. Pause only when (a) the user asks you to pause, (b) you need to resolve a PRD mismatch before the next step makes sense, or (c) the plan has more than ~6 steps and a mid-review check-in improves comprehension.
```

### Medium priority

#### M1. Add explicit "read before answering" guard
**Finding:** Phase 1 opens with `1. Read the plan completely` and `2. Study related code (Grep, Read) — verify, don't assume` (`SKILL.md:22-23`). The intent is right, but INSIGHTS §4 recommends an explicit guard against speculation: "Never speculate about code you have not opened. If the user references a file, read it before answering." Worth stating directly because the skill can receive ambiguous plan-file paths.
**Location:** `.claude/skills/rip/SKILL.md:21-23`.
**Cross-ref:** INSIGHTS §4 "Investigate-before-answering."
**Before:**
```markdown
Before responding:
1. Read the plan completely
2. Study related code (Grep, Read) — verify, don't assume
```
**After:**
```markdown
Before responding:
1. Read the plan completely. If the argument is a directory or ambiguous path, Glob for plan-shaped files (`tech-decomposition-*.md`, `*implementation-plan*.md`) before giving up.
2. Study related code (Grep, Read) — verify, don't assume. Never comment on a file you have not opened; if the plan names a file, read it before evaluating the step that touches it.
```

#### M2. "Criticism = facts + question" — keep, but add rationale
**Finding:** `SKILL.md:25` — `Criticism = facts + question.` This is a good rule but stated without the *why*. INSIGHTS §2 rule #2: rationale > rules.
**Before:**
```markdown
Record mismatches (extra features, missed requirements, logic conflicts) for discussion. Criticism = facts + question.
```
**After:**
```markdown
Record mismatches (extra features, missed requirements, logic conflicts) for discussion. Frame each as **facts + question** rather than a verdict — the plan author knows the product context you don't, and a question invites a fix instead of a defense.
```

### Low priority

#### L1. Minor intensifier in Rules table
**Finding:** `SKILL.md:98` (same line as H1) uses `**only**` in bold. Even after H1's rewrite, remove residual bold-intensifier use elsewhere. `SKILL.md:17` uses `**business value**` and `**Focus:**` — this is acceptable because it's emphasizing *topic*, not forcing a constraint. No change needed there.
**Cross-ref:** INSIGHTS §3 intensifier bullet.
**Action:** None beyond H1.

#### L2. Example block at `SKILL.md:102-131` is solid
**Finding:** Good concrete example with filled-in format, per INSIGHTS §2 rule #5 ("3–5 relevant + diverse examples wrapped in `<example>` tags"). Only nit: a second, *contrasting* example would help 4.7 generalize — e.g., a plan with zero PRD mismatches showing what the terse case looks like. Not required.
**Cross-ref:** INSIGHTS §2 rule #5.
**Action:** Optional second example; current single example is acceptable.

#### L3. Response-length shape via template blocks
**Finding:** The Step/Overview/Summary templates (`SKILL.md:31-91`) impose a structural shape rather than a hard word/sentence cap, so they do **not** fight adaptive length (INSIGHTS §1). Keep as-is.
**Action:** None.

---

## Cross-skill summary

| Skill | High | Medium | Low | Overall |
|---|---|---|---|---|
| `ct` | 2 | 4 | 3 | Well-tuned; big wins already in place (parallel subagents, scope-guardrails). Needs compaction-awareness and a few rationale adds. |
| `rip` | 2 | 2 | 3 | Short and clean; main issue is filter-leakage on PRD mismatch reporting and the forced per-step wait pattern. |

Both skills avoid the worst 4.7 anti-patterns (no prefill, no "if in doubt use X", no hard word caps, no CRITICAL/MUST shouting), so the work is refinement, not rewrite.
