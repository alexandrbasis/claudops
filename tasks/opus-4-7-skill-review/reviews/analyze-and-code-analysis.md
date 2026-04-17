# Review: `analyze` + `code-analysis` skills — Opus 4.7 audit

Scope: audit against INSIGHTS.md §3 (anti-patterns) and §4 (positive patterns). Both skills are analysis/audit skills that read-and-report; the high-risk axes are **investigate-before-answering** (§4), **over-thoroughness with no stopping condition** (§3), and **coverage-then-filter** separation for audit-style skills (§4).

Files reviewed:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/analyze/SKILL.md` (153 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md` (200 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/references/project-checks.md` (81 lines)

Overall: both skills are unusually well-behaved relative to the §3 anti-pattern list — no `CRITICAL:`/`MUST`/`ALWAYS`/`NEVER` intensifiers, no "if in doubt use tool", no reflexive "think step-by-step", no hard response-length caps, no prefill. The findings below are mostly calibration adjustments (medium/low). One high-priority issue applies to each skill.

---

## Skill 1: `analyze`

### High priority

#### H1. Filter-leakage risk in the gap-reporting rubric (§3 "Only report high-severity", §4 coverage-then-filter)

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/analyze/SKILL.md:93-101`

The severity table conflates "what to flag" with "what counts as a gap" in a single pass. Under 4.7's literal instruction-following, the model may silently skip findings it judges to be below Major when building the matrix, because the **Verdict rules** at `analyze/SKILL.md:128-130` gate on "0 Critical, 0 Major gaps" — i.e., Minor findings don't affect the verdict.

Offending text (`analyze/SKILL.md:93-101`):

```
| Tag | Meaning | Severity |
|-----|---------|----------|
| `[UNCOVERED]` | Requirement has no test case | Major |
| `[UNTESTED]` | Implementation step has no associated test | Minor |
| `[SCOPE CREEP]` | Implementation step maps to no requirement | Major |
| `[CONFLICT]` | Requirement contradicts a tech decision or another requirement | Critical |
| `[UNRESOLVED]` | `[NEEDS CLARIFICATION]` marker not yet resolved | Critical |
```

And at `analyze/SKILL.md:128-130`:

```
**Verdict rules**:
- **ALIGNED**: 0 Critical, 0 Major gaps
- **GAPS FOUND**: Any Critical or Major gaps exist
```

Together these tell a 4.7 model that Minor (`[UNTESTED]`) findings are non-blocking, which — combined with 4.7's more literal scope-reading — risks recall loss on the `[UNTESTED]` category entirely.

Before → after: split the prompt into a coverage pass and a filter pass.

Before:
```
## Step 6: Flag Gaps

Report findings using these tags:

| Tag | Meaning | Severity |
| ... Major/Minor/Critical table ... |
```

After:
```
## Step 6: Flag Gaps (coverage pass)

Report every gap you find, including low-signal ones. Do not suppress findings based on severity at this stage — a separate verification step will filter. Annotate each finding with a tag and a severity guess:

| Tag | Meaning | Default severity |
| ... same table ... |

## Step 6a: Verdict (filter pass)

Apply severity gating only when computing the final verdict, not when collecting findings.
```

Rationale: INSIGHTS.md §4 ("Report every issue you find, including low-severity and uncertain ones. Include confidence + severity. A separate verification step will filter."). Also INSIGHTS.md §3 — 4.7's literal obedience to "Only report high-severity" causes apparent recall drops.

### Medium priority

#### M1. Traceability semantics are under-scoped for 4.7's literalism (§3 "Literal-scope gaps")

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/analyze/SKILL.md:84-88`

Offending text:
```
For each implementation step, determine:
- Does it trace back to a requirement? (via `[REQ-XXX]` tag or semantic match)
- Does it have an associated test?
```

"Semantic match" is vague; 4.7 will not silently generalize. A step that fulfills *part* of a multi-part requirement may be counted as fully traced, missing partial-coverage cases.

Before → after:

Before:
```
- Does it trace back to a requirement? (via `[REQ-XXX]` tag or semantic match)
```

After:
```
- Does it trace back to a requirement, either by explicit `[REQ-XXX]` tag or by covering one or more sub-clauses of a requirement? If it only covers part of a requirement, flag the uncovered portion as a separate `[UNCOVERED]` finding for that sub-clause.
```

Rationale: INSIGHTS.md §3 — "State scope explicitly ('apply to every section, not just the first')."

#### M2. Requirement extraction section list is open-ended (§3 literal-scope)

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/analyze/SKILL.md:56-58`

Offending text:
```
- From **discovery docs**: `How It Works`, `In Scope`, `Out Of Scope`, `Key Requirements`, `Constraints`, and any equivalent older sections such as Functional Requirements, Non-Functional Requirements, UI/UX Specifications, and acceptance scenarios
```

Under 4.7 this is mostly fine, but "equivalent older sections" is not bounded. Add an explicit instruction to iterate every heading in the spec doc rather than matching only known names, so that renamed sections are not silently dropped.

Before → after:

Before:
```
- From **discovery docs**: `How It Works`, `In Scope`, `Out Of Scope`, `Key Requirements`, `Constraints`, and any equivalent older sections such as Functional Requirements, Non-Functional Requirements, UI/UX Specifications, and acceptance scenarios
```

After:
```
- From **discovery docs**: walk every top-level heading. Extract requirements from `How It Works`, `In Scope`, `Key Requirements`, `Constraints` (and their older equivalents: Functional/Non-Functional Requirements, UI/UX Specifications, acceptance scenarios). For any heading you are unsure about, include it in a `[UNCERTAIN-SOURCE]` note rather than skipping.
```

Rationale: INSIGHTS.md §3 literal-scope gap + §4 coverage-over-filter.

### Low priority

#### L1. Announcement preamble is negative framing (§3 preamble / §2 positive framing)

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/analyze/SKILL.md:19`

```
> **Announcement**: Begin with: "I'm using the **analyze** skill for cross-artifact consistency checking."
```

Not load-bearing; acceptable. No change needed unless you are trimming preamble globally.

#### L2. "This skill is read-only." — already positively framed

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/analyze/SKILL.md:25`

Already in the style INSIGHTS §2.6 recommends. Leave as-is.

### Already well-tuned (no change)

- No `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` intensifiers anywhere.
- No tool over-nudging (`If in doubt, use X`, `Default to using X`).
- `allowed-tools: Read, Grep, Glob, AskUserQuestion` is tight and read-only — matches INSIGHTS §3 "Do not suggest, make the changes" concern (correctly scoped read-only).
- The `AskUserQuestion` handoff for verdict (`analyze/SKILL.md:134-137`) follows INSIGHTS §1 "plan first" over action-bias.
- The `SKIPPED` verdict when inputs missing (`analyze/SKILL.md:40-42`) is a clean stopping condition — no risk of the model fabricating traceability against absent docs (INSIGHTS §4 "Never speculate about code you have not opened").

---

## Skill 2: `code-analysis`

### High priority

#### H2. "explore extensively" + "comprehensive" with no stopping condition (§3 "Be thorough / exhaustive / comprehensive")

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:34`

Offending text:
```
Perform comprehensive code analysis returning structured findings. Since this runs in a forked context, explore extensively — only the final report returns to the main conversation.
```

This is exactly the INSIGHTS.md §3 anti-pattern: `Be thorough / exhaustive / comprehensive` with no stopping condition causes overthinking and scope creep on 4.7. The presence of the depth matrix at `code-analysis/SKILL.md:44-54` partially mitigates this, but the top-level instruction is "comprehensive…extensively" with no cap, and the forked-context framing ("only the final report returns") actively removes the usual token-pressure signal that would cause the model to stop. In a forked context with `agent: Explore`, this is the worst combination for 4.7 over-reasoning.

Before → after:

Before:
```
Perform comprehensive code analysis returning structured findings. Since this runs in a forked context, explore extensively — only the final report returns to the main conversation.
```

After:
```
Perform code analysis scoped to the depth tier in Step 1 (Quick / Standard / Deep). Stop as soon as you have enough evidence to fill the output template for that tier — do not expand scope beyond it. Since this runs in a forked context, be decisive: a focused 10-finding report beats a 40-finding report with filler.
```

Rationale: INSIGHTS.md §3 "Be thorough / exhaustive / comprehensive with no stopping condition" + §1 "effort tiers — `max` risks overthinking." The revised wording sets a concrete stopping signal (the output template) and swaps the negative "comprehensive" framing for a positive "focused, decisive" framing (§2.6).

### Medium priority

#### M3. Filter-leakage in the concerns severity label (§3 "Only report high-severity")

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:180`

Offending text:
```
- [severity: CRITICAL/MAJOR/MINOR] [finding]
```

The template does not instruct the model to include minor findings — only that if it includes them, it should label them. In practice, combined with H2's "comprehensive" framing being pulled back, the Standard report may drop minor items entirely. Make the coverage-then-filter contract explicit.

Before → after:

Before:
```
### Concerns
- [severity: CRITICAL/MAJOR/MINOR] [finding]
```

After:
```
### Concerns
Include every concern you found, labeled with severity. Do not pre-filter to only CRITICAL/MAJOR — a small number of MINOR items in the report is expected and useful.
- [severity: CRITICAL/MAJOR/MINOR] [confidence: high/med/low] [finding]
```

Rationale: INSIGHTS.md §4 coverage-then-filter positive pattern. Confidence column matches the §4 recommended template.

#### M4. `Default to **Standard** if ambiguous` — OK but slightly under-scoped (§3 "Default to …")

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:54`

Offending text:
```
Default to **Standard** if ambiguous.
```

INSIGHTS.md §3 flags `Default to using [tool]` as too broad. Here it's applied to a mode selection, not a tool, so the anti-pattern is weak. But 4.7 is more literal about scope — a one-liner request like "what's the structure?" matches Quick, not Standard. Make the triage criterion positive.

Before → after:

Before:
```
Default to **Standard** if ambiguous.
```

After:
```
When the request is ambiguous, pick the mode whose "When" column best matches the user's phrasing. If still unclear, use Standard.
```

Rationale: INSIGHTS.md §2.6 positive framing; §3 literal-scope.

#### M5. Parallel-batching signal missing for multi-step shell discovery (§4 parallel tool-calling)

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:57-66, 94-105, 112-129`

The skill runs several bash discovery commands across Steps 2, 4, and 6 — e.g., the two `find` commands in Step 2 (`code-analysis/SKILL.md:57-66`), four discovery commands in Step 4 (`:94-105`), and four git commands in Step 6 (`:112-129`). None of these depend on each other within a step. 4.7 tends to under-parallelize by default (INSIGHTS.md §1 "subagent spawning" and §4 "parallel tool-calling").

Before → after: add a one-line directive near the top of Step 2.

Before (add after `code-analysis/SKILL.md:56`):
```
## 2. Scope Discovery

Understand what you're analyzing before diving in:
```

After:
```
## 2. Scope Discovery

Understand what you're analyzing before diving in. When multiple discovery commands in a step have no dependencies between them, batch them in one turn. Never use placeholders or guess missing parameters.
```

Rationale: INSIGHTS.md §4 parallel tool-calling positive pattern. Direct quote: "When calls have no dependencies, batch them in one turn."

#### M6. `{{VARIABLES}}` are not grounded — risks speculation (§4 investigate-before-answering)

Files: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:74, 109, 141` and `references/project-checks.md:10, 13, 16, 27, 31, 34, 41, 44, 51, 56, 59, 66, 76`

The skill embeds many `{{SRC_DIR}}`, `{{TEST_DIR}}`, `{{LANGUAGE}}`, `{{FRAMEWORK}}`, `{{SCHEMA_PATH}}`, `{{CONFIG_FILES}}`, `{{DOCS_DIR}}`, `{{PROJECT_SPECIFIC_CHECKS}}` placeholders. In projects where `/setup` has not fully populated these, 4.7 may either run commands verbatim (returning "no matches") or silently substitute guessed values. INSIGHTS.md §4: "Never speculate about code you have not opened. If the user references a file, read it before answering."

Before → after: add an explicit resolution step.

Before (current `code-analysis/SKILL.md:68-72`):
```
Read project context dynamically — don't assume the stack:
- `CLAUDE.md` at repo root for architecture overview
- `{{DOCS_DIR}}/AGENTS.md` for project-specific conventions
- `package.json` / `tsconfig.json` for actual dependencies and versions
```

After:
```
Read project context dynamically — don't assume the stack:
- `CLAUDE.md` at repo root for architecture overview
- `{{DOCS_DIR}}/AGENTS.md` for project-specific conventions
- `package.json` / `tsconfig.json` for actual dependencies and versions

If any `{{VARIABLE}}` placeholder in this skill or in `references/project-checks.md` is not populated (e.g. `{{SRC_DIR}}` is still literal), detect the real path by inspection (e.g. `ls` the repo root for `src/`, `lib/`, `app/`) before running any command. Do not run a command containing an unresolved `{{…}}` placeholder.
```

Rationale: INSIGHTS.md §4 investigate-before-answering + §3 literal-scope (4.7 won't silently generalize placeholders).

### Low priority

#### L3. `context: fork` / `agent: Explore` interaction with effort (§1 effort tiers)

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:14-15`

```
context: fork
agent: Explore
```

Not an anti-pattern, but note: INSIGHTS.md §1 says `max` effort risks overthinking, `xhigh` is the recommended default. If the `Explore` agent is configured with `effort: max` somewhere in agent config, it will compound H2 (over-thoroughness) on 4.7. Worth verifying agent config as a follow-up — out of scope for this review.

#### L4. `CRITICAL/MAJOR/MINOR` appears in the output template, not as an instruction intensifier

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/SKILL.md:180`

The token `CRITICAL` here is a finding-severity label in the output, not a prompt intensifier, so INSIGHTS.md §3 "`CRITICAL:` used as intensifier" does not apply. No change.

#### L5. `analyze/SKILL.md:94` — same: `Critical` is a severity, not an intensifier

Same disposition as L4. No change.

#### L6. Project-checks reference file is cleanly scoped

File: `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/code-analysis/references/project-checks.md`

No anti-pattern hits. Commands are scoped to directories via `{{SRC_DIR}}` and most include `2>/dev/null` + grep excludes to keep output bounded. Already well-tuned.

### Already well-tuned (no change)

- No `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` intensifiers outside the severity-label legend.
- The depth matrix at `code-analysis/SKILL.md:44-54` is a strong §1 "calibrated to task complexity" pattern — Quick vs Standard vs Deep with explicit step-ranges.
- Scope boundaries block (`code-analysis/SKILL.md:28-32`) cleanly routes to sibling skills — matches INSIGHTS.md's emphasis on explicit NOT-for clauses.
- `READS and REPORTS` contract (`code-analysis/SKILL.md:28`) is positive framing — matches §2.6.
- Output templates per depth tier (`:136-197`) give a concrete stopping condition, mitigating H2 if applied literally.

---

## Summary of recommendations by priority

High:
- **H1** (`analyze`): split flag-gaps into coverage pass + verdict filter pass (§3/§4).
- **H2** (`code-analysis`): remove "comprehensive…explore extensively" framing; anchor to depth-tier output templates as the stopping signal (§3).

Medium:
- **M1** (`analyze`): spell out partial-coverage semantics for traceability (§3).
- **M2** (`analyze`): iterate all headings when extracting requirements (§3/§4).
- **M3** (`code-analysis`): make coverage-then-filter explicit in the concerns template; add confidence column (§4).
- **M4** (`code-analysis`): positive triage rule for mode selection (§2/§3).
- **M5** (`code-analysis`): add parallel-batching directive for independent discovery commands (§4).
- **M6** (`code-analysis`): require placeholder resolution before running any `{{…}}` command (§4).

Low:
- **L1–L6**: Either optional trims or items already well-tuned — no change needed.
