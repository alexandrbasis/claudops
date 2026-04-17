# Opus 4.7 Audit — `coding-conventions` and `review-conventions`

Scope: the two shared reference skills preloaded into developer and reviewer agents via
`skills:` frontmatter. Because they propagate into many downstream agents, even small
miscalibrations amplify. Both files are short and mostly well-tuned; findings are
targeted.

Reviewed files:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/coding-conventions/SKILL.md` (52 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/review-conventions/SKILL.md` (68 lines)

---

## Skill 1 — `review-conventions/SKILL.md`

### Overall verdict
Structurally good (clear ownership table, diff-scope rules, severity taxonomy). One
**high-priority** finding: the confidence threshold + "only confident findings"
language is the exact pattern INSIGHTS.md §1 (code-review row) and §3 warns about —
4.7 will obey literally and drop recall. Needs a coverage-then-filter split.

### High priority

#### H1. Filter leakage: ">80% confidence" + "only report findings you're confident about"
**File**: `review-conventions/SKILL.md:32`
**INSIGHTS cross-ref**: §1 code-review row, §3 ("Only report high-severity / important issues"), §4 (coverage-then-filter split).

Offending text (exact):
```
- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.
```

Why it backfires on 4.7: The 4.7 row in §1 says reviewers "obey severity/confidence
filters more literally — recall may appear to drop." The `>80%` number and
"only report findings you're confident about" are a literal filter at the *find*
stage — Opus 4.7 will silently discard real issues it is 60–79% sure about.
§4 explicitly prescribes splitting coverage and filtering.

Before:
```markdown
## Review Quality Rules

- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.
- **Consolidate similar issues**: "5 functions missing error handling" with a list, not 5 separate findings
- **Severity order**: CRITICAL → MAJOR → MINOR → INFO
- **Actionable**: every finding needs severity + location (`file:line`) + concrete suggestion
- **Constructive tone**: explain why issues matter, highlight positive practices
```

After (coverage-then-filter split, keeping the user-facing trust goal):
```markdown
## Review Quality Rules

Reviews run in two stages so we get recall AND precision:

1. **Find stage (this skill)** — report every issue you notice, including low-severity
   and uncertain ones. For each finding, include:
   - `severity`: CRITICAL | MAJOR | MINOR | INFO
   - `confidence`: high | medium | low
   - `location`: `file:line`
   - `suggestion`: concrete fix or next step
   Do not self-censor based on severity or confidence — a later verification pass
   will filter before anything reaches the user.

2. **Presentation** — consolidate repeats ("5 functions missing error handling" with
   a list, not 5 separate findings). Explain why each issue matters. Highlight
   positive practices alongside problems.
```

Rationale included inline ("so we get recall AND precision") per INSIGHTS §2.2 —
explain the *why*. The filter is still enforced, just in a separate stage, which is
what 4.7 needs.

---

### Medium priority

#### M1. `do NOT` emphasis caps in diff-scope rules
**File**: `review-conventions/SKILL.md:42-43`
**INSIGHTS cross-ref**: §3 ("`NEVER` used as intensifiers — dial back to normal voice").

Offending text:
```
- MAY read unchanged files for context (interfaces, contracts) — do NOT flag issues in unchanged code
- Pre-existing issues: do NOT flag unless changes make them worse
```

The `do NOT` caps are used as emphasis. On 4.7 these over-trigger — models become
too defensive about *any* out-of-scope observation, even when flagging a pre-existing
issue would genuinely help the user.

Before:
```markdown
- MAY read unchanged files for context (interfaces, contracts) — do NOT flag issues in unchanged code
- Pre-existing issues: do NOT flag unless changes make them worse
```

After (normal voice, rationale added):
```markdown
- You may read unchanged files for context (interfaces, contracts), but don't raise
  findings against unchanged code — the author isn't touching it in this PR.
- Skip pre-existing issues unless the current changes make them worse (e.g., a bug
  that used to be in dead code is now reachable).
```

#### M2. Missing positive framing: what *to do* when you spot cross-owner issues
**File**: `review-conventions/SKILL.md:65`
**INSIGHTS cross-ref**: §3 (negative framing → positive), §2.6.

Offending text:
```
If you spot something outside your scope, note it briefly as INFO — do not deep-dive.
```

This is fine as-is but mixes positive + negative. Tighten to pure positive:

After:
```markdown
If you spot something outside your scope, note it as a one-line INFO finding with
the likely owner (e.g. "possible security concern — flag for `security-code-reviewer`")
and move on.
```

This keeps the spirit (don't deep-dive) without the negative clause.

---

### Low priority

#### L1. `Severity order` line is fine — no change needed
**File**: `review-conventions/SKILL.md:34`

`CRITICAL → MAJOR → MINOR → INFO` is a taxonomy, not an intensifier. Keep as-is.

#### L2. Ownership table is well-tuned
**File**: `review-conventions/SKILL.md:49-59`

The concern/owner table is the exact positive-framing pattern INSIGHTS §2 calls for:
explicit scope per agent, no "be comprehensive" language. No change.

---

## Skill 2 — `coding-conventions/SKILL.md`

### Overall verdict
Short, mostly positive framing, and already carries the key §4 pattern ("No
over-engineering or speculative abstractions", "Minimal code — only what tests
require"). Two **medium** findings around emphasis caps and missing rationale, and
one **low** opportunity to make the over-engineering guard more concrete per INSIGHTS
§4.

### High priority
None. This skill is already well-calibrated for 4.7 on the load-bearing axes
(over-engineering mitigation, scope discipline).

### Medium priority

#### M3. `FIRST` caps as intensifier
**File**: `coding-conventions/SKILL.md:46`
**INSIGHTS cross-ref**: §3 (`CRITICAL:` / `ALWAYS` caps as intensifiers).

Offending text:
```
- Read task document FIRST — it's the source of truth for WHAT to build
```

Both `FIRST` and `WHAT` are emphasis caps. On 4.7 this can over-trigger — e.g.,
re-reading the task document even when it's already been loaded earlier in the
thread.

Before:
```markdown
- Read task document FIRST — it's the source of truth for WHAT to build
```

After:
```markdown
- Start by reading the task document — it's the source of truth for what to build,
  and implementation choices should flow from it rather than from prior assumptions.
```

Rationale now stated (why it matters), caps removed.

#### M4. Rules stated without *why* — INSIGHTS §2.2 violation
**File**: `coding-conventions/SKILL.md:28-34`
**INSIGHTS cross-ref**: §2.2 ("Explain the *why* — rationale > rules").

Offending text (Code Style block):
```
## Code Style

- Prefer project-established type/interface conventions
- No `any` — use proper types
- No unnecessary `_` prefixes for unused vars
- Secrets via config providers only — never hardcoded, never logged
- DTOs match API schemas and tech-decomposition acceptance criteria
- Database queries use parameter binding — no dynamic SQL or string interpolation
```

The secrets and parameter-binding rules have obvious rationale (security) but it's
unstated. The `any`/underscore rules read as arbitrary. 4.7 is more literal — rules
without rationale get followed robotically or dropped when they conflict with other
instructions.

After (rationale added; same rules; converted some negatives to positive framing):
```markdown
## Code Style

- Match the project's existing type/interface conventions — new code should look
  like it was written by the same person as the surrounding code.
- Use proper types instead of `any`. `any` hides type errors that only surface at
  runtime, which is the failure mode our type system exists to prevent.
- Drop the `_` prefix on unused vars unless the project's lint config requires it.
- Route secrets through config providers only — never hardcoded, never logged
  (logs ship to observability tools; hardcoded secrets leak via git history).
- Keep DTOs aligned with API schemas and the tech-decomposition's acceptance
  criteria — these are the contract downstream consumers rely on.
- Use parameter binding for database queries (not string interpolation) to prevent
  SQL injection.
```

### Low priority

#### L3. Over-engineering guard is present but could be more concrete
**File**: `coding-conventions/SKILL.md:48-51`
**INSIGHTS cross-ref**: §4 ("Minimize over-engineering").

Current text:
```
- Minimal code — only what tests require
- No scope creep — implement exactly the assigned work item
- No over-engineering or speculative abstractions
- Follow existing codebase patterns — new code should look like it belongs
```

This already covers the §4 intent. The §4 suggestion goes further with concrete
examples of the failure mode ("Bug fixes don't need surrounding refactors. No
defensive error handling for scenarios that can't happen."). Adding those makes the
guard harder for the model to overlook.

After:
```markdown
- Write the minimum code that makes the tests pass and the acceptance criteria
  hold. Don't add features, abstractions, or cleanup that weren't asked for.
- Bug fixes don't need surrounding refactors — fix the bug, leave the rest.
- Skip defensive error handling for scenarios that can't actually happen in this
  codebase's flow.
- Match existing codebase patterns — new code should look like it belongs.
```

#### L4. TDD rule is fine but lacks the *why*
**File**: `coding-conventions/SKILL.md:38`

```
- **TDD**: RED → GREEN → REFACTOR
```

Fine for a reference skill — the phrase is industry-standard shorthand. No change
needed unless new hires (or new agents) hit it without context; in that case, one
line of rationale ("write the failing test first so the test proves the fix, not
the fix-adjusted test").

#### L5. Template placeholders look healthy
**File**: both files, `{{FRAMEWORK}}` etc.

The Mustache-style placeholders are filled in by the `/setup` flow per the repo's
`CLAUDE.md`. They are not prompt-engineering concerns. No change.

---

## Summary table

| # | Skill | Priority | Issue | INSIGHTS ref |
|---|---|---|---|---|
| H1 | review-conventions | High | ">80% confidence" filter at find stage → recall drop | §1 code-review row, §3, §4 |
| M1 | review-conventions | Medium | `do NOT` caps as emphasis | §3 |
| M2 | review-conventions | Medium | Cross-scope finding guidance mixes positive + negative | §3, §2.6 |
| M3 | coding-conventions | Medium | `FIRST` / `WHAT` caps as intensifiers | §3 |
| M4 | coding-conventions | Medium | Rules without rationale | §2.2 |
| L3 | coding-conventions | Low | Over-engineering guard could name concrete failure modes | §4 |
| L4 | coding-conventions | Low | TDD abbreviation has no rationale (optional fix) | §2.2 |

## Things already well-tuned (do not change)

- `review-conventions` ownership table (L49-59) — exact positive-framing pattern.
- `review-conventions` severity taxonomy (L34) — taxonomy, not intensifier.
- `coding-conventions` over-engineering mitigation (L48-50) — already present;
  L3 is an enhancement, not a fix.
- `coding-conventions` template-var placeholders — infrastructure, not prompt.
- Both skills' `description:` frontmatter clearly marks them "Internal reference
  skill … Not user-invocable" — good scope discipline.
