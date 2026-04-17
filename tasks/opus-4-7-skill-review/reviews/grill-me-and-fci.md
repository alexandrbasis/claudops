# Review: `grill-me` and `fci` skills against Opus 4.7 Best Practices

**Scope:** `.claude/skills/grill-me/SKILL.md` (44 lines) and `.claude/skills/fci/SKILL.md` (104 lines).
**Lens:** `tasks/opus-4-7-skill-review/INSIGHTS.md` §1–§5.

---

## Skill 1: `grill-me`

**File:** `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/grill-me/SKILL.md`

**Overall verdict:** This skill is short and largely well-tuned for Opus 4.7. It already uses positive framing ("Prefer exposing hidden assumptions over inventing extra scope"), has an explicit stop condition, and avoids most of the intensifier anti-patterns in INSIGHTS.md §3. It does, however, have two mild gaps worth fixing: a coverage-then-filter concern around "one focused question at a time", and a literal-scope gap when invoked on long discovery documents.

### High priority

#### H1. Coverage-then-filter gap — single-question funnel may drop hidden risks early (INSIGHTS.md §1 Code-review row + §4)

**File:** `.claude/skills/grill-me/SKILL.md:9–13` (Core Behavior) and `:15–23` (When Invoked From Discovery)

**Offending text (line 10):**

> `- Ask one focused question at a time`

**Offending text (lines 17–21):**

> ```
> Prioritize:
> - Unclear scope boundaries
> - Missing states, flows, or edge cases
> - Hidden assumptions
> - Ambiguous wording a new reader could misinterpret
> - Decision branches that materially change the feature shape
> ```

**Why this matters on 4.7:** INSIGHTS.md §1 Code-review row warns that 4.7 "Obey[s] severity/confidence filters **more literally** — recall may *appear* to drop." `grill-me` is a stress-testing skill in the same family as `/sr`. The current prompt tells Claude to pick one question at a time from a prioritized list, with no explicit "enumerate all candidate risks first, then pick what to ask." On 4.6 the model used to implicitly enumerate; on 4.7 the more literal instruction-following means it may jump straight to asking about the first "Unclear scope boundary" it notices and never surface the rest. INSIGHTS.md §4 prescribes a coverage-then-filter split.

**Before:**

```
## Core Behavior

- Ask one focused question at a time
- For each question, provide your recommended answer or default position
- If a question can be answered from the codebase or docs, explore there instead of asking the user
- Prefer exposing hidden assumptions over inventing extra scope
```

**After:**

```
## Core Behavior

- First, enumerate every candidate risk you can see across all categories
  below (scope, states/flows, assumptions, wording, decision branches) — keep
  this internal list so nothing drops silently. A later step filters to what
  is worth asking.
- Then surface one focused question at a time, ordered by what most changes
  the feature shape if answered wrong.
- For each question, provide your recommended answer or default position.
- If a question can be answered from the codebase or docs, explore there
  instead of asking the user.
- Prefer exposing hidden assumptions over inventing extra scope.
```

This keeps the user-facing "one question at a time" UX but makes the **find** stage exhaustive, matching INSIGHTS.md §4 coverage-then-filter.

### Medium priority

#### M1. Literal-scope gap — "Prioritize" list is not bound to *every* section of the document (INSIGHTS.md §3 literal-scope, §5 checklist item 6)

**File:** `.claude/skills/grill-me/SKILL.md:15–23`

**Offending text (line 15):**

> `## When Invoked From Discovery`

Followed by a `Prioritize:` list with no statement of scope over the input document.

**Why this matters on 4.7:** INSIGHTS.md §1 Instruction-following row: "More literal; will NOT silently generalize. State scope explicitly ('apply to every section, not just the first')." When `grill-me` is handed a multi-section discovery doc (e.g. from `/nf`), a 4.6-era prompt would implicitly scan every section; 4.7 may stress-test only the first. The "Prioritize" list tells Claude *what categories of risk* to look for but not *where in the input* to look.

**Before:**

```
## When Invoked From Discovery

Prioritize:
- Unclear scope boundaries
...
```

**After:**

```
## When Invoked From Discovery

Scan every section of the discovery document (scope, flows, states,
constraints, out-of-scope, open questions, risks) — not only the first
section or headline. Then prioritize:

- Unclear scope boundaries
- Missing states, flows, or edge cases
- Hidden assumptions
- Ambiguous wording a new reader could misinterpret
- Decision branches that materially change the feature shape
```

#### M2. Rationale missing for two rules (INSIGHTS.md §2 "Explain the *why*", §5 checklist item 11)

**File:** `.claude/skills/grill-me/SKILL.md:10` and `:13`

**Offending text:**

> `- Ask one focused question at a time`
> `- Prefer exposing hidden assumptions over inventing extra scope`

**Why this matters on 4.7:** INSIGHTS.md §2 point 2: "Explain the *why* — rationale > rules. 'Your response is read aloud by TTS' beats 'never use ellipses'." Opus 4.7 responds better to reasoned constraints than to flat rules. Both of these rules are load-bearing for this skill — worth a one-line *why*.

**Before:**

```
- Ask one focused question at a time
...
- Prefer exposing hidden assumptions over inventing extra scope
```

**After:**

```
- Ask one focused question at a time — the user must be able to answer
  without re-reading the whole thread; batched questions get half-answered
  or ignored.
...
- Prefer exposing hidden assumptions over inventing extra scope — the goal
  is to sharpen an existing plan, not to bolt on new features under the
  guise of stress-testing.
```

### Low priority

#### L1. `Return To Caller` section is passive — no explicit instruction to actually return (INSIGHTS.md §3 positive framing, §2 point 6)

**File:** `.claude/skills/grill-me/SKILL.md:33–40`

**Offending text (line 33):**

> `## Return To Caller`

The heading is declarative, not imperative. 4.7 is more literal; an imperative framing reduces the chance Claude ends with a generic summary instead of the requested compact summary.

**Before:**

```
## Return To Caller

Return a compact summary:
- Clarifications made
...
```

**After:**

```
## Return To Caller

When the stop condition is met, finish by returning this compact summary
(so the caller — typically `/nf` or `/ct` — can paste it into the doc
without editing):

- Clarifications made
- Scope cuts or out-of-scope decisions
- Hidden assumptions uncovered
- Wording fixes or ambiguity reductions
- Remaining risks or blockers
```

### Things `grill-me` already gets right (do not change)

- No `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` intensifiers anywhere — clean per INSIGHTS.md §3.
- Explicit stop condition at lines 25–30 — matches INSIGHTS.md §3 anti-pattern "Be thorough/exhaustive with no stopping condition."
- Positive framing throughout ("Prefer exposing…", "Avoid…") — matches INSIGHTS.md §2 point 6.
- "If a question can be answered from the codebase or docs, explore there instead of asking the user" (line 12) — aligns with INSIGHTS.md §4 "Investigate-before-answering" pattern.
- Short and scannable — no response-length caps that would fight 4.7 adaptive length (INSIGHTS.md §3).

---

## Skill 2: `fci`

**File:** `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/fci/SKILL.md`

**Overall verdict:** This skill has **multiple** Opus 4.7 anti-patterns per INSIGHTS.md §3 — intensifier overuse (`NEVER`, `ALL`), an announcement prefill, literal-scope gaps around parallel command execution, and missing over-engineering guard for a skill that edits code. The core logic is sound but the prompting style is still 4.5/4.6-era.

### High priority

#### H1. Intensifier overuse — `NEVER` and `ALL` used as emphasis (INSIGHTS.md §3, §5 checklist item 1)

**File:** `.claude/skills/fci/SKILL.md:23` and `:79`

**Offending text (line 23):**

> `- **NEVER** use `any` type, `@ts-ignore`, `// eslint-disable`, or architectural shortcuts to make CI pass`

**Offending text (line 79):**

> `Before completion, execute ALL checks and confirm passing:`

**Why this matters on 4.7:** INSIGHTS.md §3: "`CRITICAL:`, `You MUST`, `ALWAYS`, `NEVER` used as intensifiers — dial back to normal voice. The model is already more responsive; these now cause **over-triggering**." Line 23's `NEVER` in particular is load-bearing (users really do not want `any`/`@ts-ignore`) but the intensifier style causes 4.7 to over-trigger — e.g. refusing to use `any` even in a `.d.ts` shim where it's appropriate. The rationale ("to make CI pass") is already present — strengthen the *why*, drop the shouting.

**Before:**

```
- **NEVER** use `any` type, `@ts-ignore`, `// eslint-disable`, or architectural shortcuts to make CI pass
```

**After:**

```
- Do not silence CI with `any`, `@ts-ignore`, `// eslint-disable`, or
  architectural shortcuts — the goal is a real fix, not a green checkmark.
  If a suppression is genuinely correct (e.g. a `.d.ts` shim), flag it
  explicitly so the reviewer can confirm.
```

**Before:**

```
Before completion, execute ALL checks and confirm passing:
```

**After:**

```
Before completion, run the full CI validation suite locally and confirm
every command exits zero:
```

#### H2. Announcement prefill — `> **Announcement**: Begin with: "..."` is a disguised prefill (INSIGHTS.md §3 prefill pattern, §5 checklist item 8)

**File:** `.claude/skills/fci/SKILL.md:11`

**Offending text:**

> `> **Announcement**: Begin with: "I'm using the **fci** skill for CI failure resolution."`

**Why this matters on 4.7:** INSIGHTS.md §1 Prefill row: "Deprecated; errors on Mythos Preview." INSIGHTS.md §3: "Pre-filled assistant turns / `<assistant>` prefills at the end — deprecated." While this isn't a literal `<assistant>` prefill, it forces a fixed opening string, which is the same antipattern and also fights adaptive response length (§3 hard-coded response-length caps). If skill-announcement is a house convention across this repo, keep it — but make it a soft positive instruction, not a literal string to prefill. Alternatively, rely on the existing "I'm using the [skill] skill" convention other skills seem to follow without the forced quote.

**Before:**

```
> **Announcement**: Begin with: "I'm using the **fci** skill for CI failure resolution."
```

**After (option A, drop entirely if the harness already announces skills):**

```
(remove this line)
```

**After (option B, if announcement is project-mandatory):**

```
Briefly tell the user you are using the fci skill before starting work,
so they know which workflow is running.
```

#### H3. Literal-scope gap on parallel tool calls + missing parallelization guidance (INSIGHTS.md §1 Tool-use row, §4 Parallel tool-calling, §5 checklist item 3)

**File:** `.claude/skills/fci/SKILL.md:40–46` (Execute Diagnostic Checks) and `:80–85` (Verification)

**Offending text (lines 41–46):**

> ```
> 2. **Execute Diagnostic Checks:**
>    - Ensure dependencies are installed (run project install command)
>    - Lint check: `{{LINT_CMD}}`
>    - Type check: `{{TYPECHECK_CMD}}`
>    - Test suite: `{{TEST_CMD}}`
>    - Build: `{{BUILD_CMD}}`
> ```

**Offending text (lines 80–85):**

> ```bash
> # Run full CI validation suite
> {{LINT_CMD}} && \
> {{TYPECHECK_CMD}} && \
> {{TEST_CMD}} && \
> {{BUILD_CMD}}
> ```

**Why this matters on 4.7:** INSIGHTS.md §1 Tool-use row: "Less frequent — reasons more before calling tools." INSIGHTS.md §4: "When calls have no dependencies, batch them in one turn. Never use placeholders or guess missing parameters." Lint, typecheck, and tests are independent — they can and should run in parallel tool calls for the *diagnostic* phase. The final `&&`-chained verification is correctly sequential (it's a pass/fail gate, short-circuit is desirable), but nothing tells 4.7 to parallelize the *investigation*. On 4.7 the default is sequential; you must spell it out.

**Before:**

```
2. **Execute Diagnostic Checks:**
   - Ensure dependencies are installed (run project install command)
   - Lint check: `{{LINT_CMD}}`
   - Type check: `{{TYPECHECK_CMD}}`
   - Test suite: `{{TEST_CMD}}`
   - Build: `{{BUILD_CMD}}`
```

**After:**

```
2. **Execute Diagnostic Checks (run in parallel):**
   - These commands are independent — batch them in one turn as parallel
     Bash tool calls, do not chain sequentially.
   - Ensure dependencies are installed first (sequential prerequisite).
   - Then in parallel: `{{LINT_CMD}}`, `{{TYPECHECK_CMD}}`, `{{TEST_CMD}}`,
     `{{BUILD_CMD}}`.
   - Collect all failure logs before choosing where to start fixing —
     don't stop at the first red check.
```

#### H4. Missing over-engineering guard for a code-editing skill (INSIGHTS.md §3, §4 "Minimize over-engineering", §5 checklist item 10)

**File:** `.claude/skills/fci/SKILL.md:48–71` (Resolution Process)

**Why this matters on 4.7:** INSIGHTS.md §1: "4.5 and 4.6 both tend to over-engineer; 4.7 more literal but still drifts. Add explicit 'minimize scope / no new abstractions' guidance where relevant." `fci` edits code to make CI pass — exactly the context where 4.7 can easily pull in surrounding refactors ("while I'm here, let me extract this function"). There is no guard. The closest thing is line 23's `NEVER use any` rule which is about suppressions, not scope creep.

**Before:**

```
## RESOLUTION PROCESS
1. **Fix Formatting Issues First:**
...
```

**After (insert scope guard at the top of the section):**

```
## RESOLUTION PROCESS

Scope discipline: fix only what the failing CI checks require. Do not
refactor nearby code, rename symbols for consistency, tighten unrelated
types, or add defensive error handling that wasn't failing. If you spot
adjacent problems, note them in the handoff summary — don't fix them in
this PR.

1. **Fix Formatting Issues First:**
...
```

### Medium priority

#### M1. `DO NOT simplify tests` uses intensifier; rationale is the real lever (INSIGHTS.md §3, §2 point 2)

**File:** `.claude/skills/fci/SKILL.md:55`

**Offending text:**

> `   - DO NOT simplify tests or reduce assertions`

**Why this matters on 4.7:** Same intensifier-overuse pattern as H1. The *why* here is critical — "tests are a specification, weakening them to pass CI hides real bugs" — and it's missing. Moving from shouted rule to reasoned constraint fits INSIGHTS.md §2 point 2.

**Before:**

```
3. **Resolve Test Failures:**
   - Fix failing tests by correcting implementation bugs
   - DO NOT simplify tests or reduce assertions
   - Maintain or improve test coverage (>=80% target)
```

**After:**

```
3. **Resolve Test Failures:**
   - Fix failing tests by correcting the implementation bug the test is
     catching — the test is a spec, so weakening assertions to turn the
     check green hides the real defect.
   - Maintain or improve test coverage (>=80% target). If a test is
     genuinely wrong (e.g. asserts outdated behavior), update it and
     explicitly flag the change in the handoff summary.
```

#### M2. Literal-scope gap on "Fix Formatting Issues First" ordering (INSIGHTS.md §1 Instruction-following, §5 checklist item 6)

**File:** `.claude/skills/fci/SKILL.md:49–53`

**Offending text:**

> ```
> 1. **Fix Formatting Issues First:**
>    - Run `{{FORMAT_CMD}}` if style violations are reported
>    - Re-run lint check afterwards to confirm clean output
> ```

**Why this matters on 4.7:** 4.7 obeys ordering literally. "Fix formatting first" written as step 1 means the model may run `{{FORMAT_CMD}}` even when formatting isn't failing, just because it's step 1. The condition ("if style violations are reported") is there but buried.

**Before:**

```
1. **Fix Formatting Issues First:**
   - Run `{{FORMAT_CMD}}` if style violations are reported
   - Re-run lint check afterwards to confirm clean output
```

**After:**

```
1. **Formatting (only if lint reported style violations):**
   - Skip this step entirely if formatting is clean.
   - Otherwise run `{{FORMAT_CMD}}`, then re-run lint to confirm the
     formatter didn't introduce new issues.
```

#### M3. `allowed-tools` list missing parallel-friendly tools that the skill implicitly uses (consistency check, not a 4.7-specific issue, but worth noting)

**File:** `.claude/skills/fci/SKILL.md:8`

**Offending text:**

> `allowed-tools: Bash, Read, Edit, Write, Grep, Glob`

Analysis-only observation: the skill's analysis phase uses `gh workflow list` / `gh run list` / `gh run view` — all Bash, so this is fine. No change required, just flagging that if H3 leads to parallel Bash calls, the current `allowed-tools` line already supports it. Keep as-is.

### Low priority

#### L1. `Definition of Done` has a hard 80% coverage number without context (INSIGHTS.md §2 point 2, §3 hard-coded caps)

**File:** `.claude/skills/fci/SKILL.md:92`

**Offending text:**

> `- [ ] Test coverage maintained at >=80%`

**Why this matters on 4.7:** The number is already in the skill twice (line 56 and line 92). It's a hard threshold with no rationale. Not a major issue — just flag in the DOD that it's a *minimum maintained* bar, not a *target to fight for*, to keep 4.7 from churning to push coverage from 82% → 85% when CI doesn't require it.

**Before:**

```
- [ ] Test coverage maintained at >=80%
```

**After:**

```
- [ ] Test coverage did not drop below the pre-fix baseline (>=80% floor).
```

#### L2. `Be thorough`-adjacent phrasing missing stopping condition (INSIGHTS.md §3 anti-pattern row 4)

**File:** `.claude/skills/fci/SKILL.md:34–38`

**Offending text:**

> ```
> 1. **Identify CI Failures:**
>    - Run `gh workflow list` if you are unsure of the workflow name
>    - Run `gh run list --limit=3` to check recent CI status
>    - Review failure logs (`gh run view <run-id> --log`) to identify specific issues
>    - Categorize failures by type (linting, tests, types, build, other)
> ```

Minor: 4.7 may keep pulling logs across multiple runs. `--limit=3` is a good guardrail, but "Review failure logs" with no stop condition can cause the model to fetch logs for every recent run. Add "Focus on the most recent failing run only."

**Before:**

```
   - Run `gh run list --limit=3` to check recent CI status
   - Review failure logs (`gh run view <run-id> --log`) to identify specific issues
```

**After:**

```
   - Run `gh run list --limit=3` to check recent CI status.
   - Pick the most recent failing run and review its logs with
     `gh run view <run-id> --log`. Don't fetch logs for older runs unless
     the recent-run failures are ambiguous.
```

### Things `fci` already gets right (do not change)

- `disable-model-invocation: true` + `argument-hint: [workflow-name or run-id]` — the skill is explicitly user-invoked, no over-nudging of tool use (INSIGHTS.md §3).
- `## RELATED SKILLS` block at lines 26–29 cross-links `/dbg`, `/sr`, `/prc` — positive framing of scope boundaries without `NEVER use this for...` shouting.
- `## TROUBLESHOOTING` at lines 88–92 provides concrete rationale-first recovery actions (e.g. "Docker not running: Run `docker info`") — matches INSIGHTS.md §2 point 2.
- `{{...}}` command placeholders rather than hardcoded tool names — portable, no intensifiers embedded.

---

## Summary of priorities

### `grill-me`

| Priority | Count | Items |
|---|---|---|
| High | 1 | H1 coverage-then-filter |
| Medium | 2 | M1 literal-scope, M2 missing rationale |
| Low | 1 | L1 imperative return framing |

### `fci`

| Priority | Count | Items |
|---|---|---|
| High | 4 | H1 intensifiers, H2 announcement prefill, H3 parallel tool calls, H4 over-engineering guard |
| Medium | 3 | M1 `DO NOT` rationale, M2 conditional formatting step, M3 tools list (no-op) |
| Low | 2 | L1 coverage context, L2 log-fetch stop condition |

### Cross-cutting observation

Both skills are in the same "stress-test / CI gate" family but have different levels of 4.7 adaptation: `grill-me` is ~80% there and needs only targeted coverage-then-filter tuning; `fci` is still written in 4.5/4.6 style (shouted intensifiers, announcement prefill, implicit sequential tool use) and needs a broader refresh. If only one skill is updated in the first pass, `fci`'s H3 (parallel diagnostic checks) is the single highest-ROI change — it directly addresses INSIGHTS.md §1 Subagent-spawning + Tool-use rows, which are the two biggest behavioral deltas in 4.7.
