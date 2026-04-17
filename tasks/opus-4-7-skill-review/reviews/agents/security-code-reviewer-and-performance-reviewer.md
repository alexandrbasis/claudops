# Agent Review — `security-code-reviewer` & `performance-reviewer`

Audited against `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/tasks/opus-4-7-skill-review/INSIGHTS.md` (Opus 4.7 prompting best practices).

Both files are specialist review subagents invoked by the orchestrator code-review pipeline. They share the `review-conventions` skill (`.claude/skills/review-conventions/SKILL.md`), which sets a **>80% confidence threshold** and severity taxonomy globally — this shared filter matters for every finding below.

Scope:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/code-review-agents/security-code-reviewer.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/code-review-agents/performance-reviewer.md`

---

## 1. `security-code-reviewer.md`

### Frontmatter

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:1-8`

```yaml
name: security-code-reviewer
description: Reviews code for security vulnerabilities, input validation issues, and authentication/authorization flaws. Use after implementing auth logic, user input handling, API endpoints, or third-party integrations.
tools: Glob, Grep, Read, Edit, Write, BashOutput
model: inherit
skills:
  - review-conventions
```

**Assessment**: The `description:` is scoped by concrete triggers (`auth logic, user input handling, API endpoints, third-party integrations`). That is appropriate — security review should run whenever any of those are present, which is most backend diffs. No change needed. Tool list is correct for the file-mode write flow.

One minor observation — because the orchestrator invokes this agent explicitly (not via dispatcher auto-match), over-invocation risk on 4.7 is lower than for user-facing skills. The frontmatter here is fine as-is. **No priority.**

---

### High priority

#### H1. Filter leakage via the shared `>80% confidence` rule combined with "err on side of caution" — contradictory under 4.7

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:109`
**Related**: `.claude/skills/review-conventions/SKILL.md:28` (`>80% confidence threshold`)

The agent ends with:

> `- When uncertain about a vulnerability, err on side of caution and flag it`

But `review-conventions` (preloaded via `skills:` frontmatter) says:

> `- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.`

Per INSIGHTS §1 (code-review row) and §3:
> *"Only report high-severity / important issues" in review skills — 4.7 obeys literally → recall drops.*

4.7 will resolve this contradiction by defaulting to the **more literal** rule (the `>80%` global one), silently dropping low-confidence security findings — exactly the failure mode the task brief calls out ("Security reviews shouldn't drop low-confidence findings silently"). A low-confidence SQL injection suspicion is strictly more valuable to report than a low-confidence perf nit.

**Fix** — add explicit coverage-then-filter override for security specifically, and resolve the contradiction in the agent's favor (INSIGHTS §4 "Coverage-then-filter split"):

Before (`:109`):
```
- When uncertain about a vulnerability, err on side of caution and flag it
```

After:
```
## Coverage over filter (overrides shared >80% confidence rule)

Report every potential vulnerability you find, including low-confidence and low-severity ones. Tag each with:
- Severity: CRITICAL / MAJOR / MINOR / INFO
- Confidence: HIGH / MEDIUM / LOW

Security is recall-sensitive: a missed injection, auth bypass, or secret leak costs far more than a noisy false positive. The orchestrator handles de-duplication and final filtering downstream — do not pre-filter on your side.

If you would have dropped a finding because you weren't sure, include it as [MINOR]/LOW-confidence with the specific uncertainty noted in the Remediation field.
```

**Priority**: High — this is the single most important change on this file and the central theme of the INSIGHTS doc for review agents.

---

#### H2. Intensifiers stacked on format instructions cause over-compliance and eat tokens

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:62, :89`

Offending lines (exact quotes):
- `:62` — `4. **Do NOT** edit anything outside your section markers`
- `:89` — `**Then return ONLY a short summary:**`
- `:58` — `When `changed_files` and `full_diff` are provided in the prompt:`  (fine)
- `:47` — `5. **Do NOT** scan the entire codebase with Glob/Grep — only use Glob/Grep to find specific files referenced by changed code`

Per INSIGHTS §3:
> `CRITICAL:`, `You MUST`, `ALWAYS`, `NEVER` used as intensifiers — dial back to normal voice. The model is already more responsive; these now cause over-triggering.

The `Do NOT` instructions at `:47` and `:62` are genuinely load-bearing (section markers are a contract with the orchestrator) — keep those. But `:89`'s `Then return ONLY a short summary` combined with the multi-line template that follows is redundant emphasis.

Before (`:89-94`):
```
**Then return ONLY a short summary:**
`"Clean. 0 critical, 0 major, 0 minor. No security issues found."`
or
`"Findings. 1 critical, 0 major, 1 minor. SQL injection in UserService.search()."`
```

After:
```
After writing to the CR file, return a one-line summary to the caller. Format:
- Clean: `"Clean. 0 critical, 0 major, 0 minor. No security issues found."`
- With findings: `"Findings. <n> critical, <n> major, <n> minor. <short top-finding headline>."`

The detailed findings live in the CR file; the summary is for the orchestrator's dashboard.
```

This adds the **why** (INSIGHTS §2.2) and drops the `ONLY` intensifier.

**Priority**: High — small change, but the explicit `why` prevents 4.7 from either padding the return or silently omitting the summary line.

---

### Medium priority

#### M1. Unbounded bullet lists under "Review Scope" invite exhaustive scanning

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:13-35`

The `Review Scope` section lists ~20 bullet items across 4 sub-headers ("OWASP Top 10", "Input Validation", "Auth/Authz", "Project-Specific") with no stopping condition.

INSIGHTS §3 flags:
> `Be thorough / exhaustive / comprehensive` with no stopping condition — causes overthinking and scope creep.

The Scope section does not literally say "be exhaustive," but presenting ~20 concerns as a checklist with no prioritization produces the same effect on 4.7, especially combined with `:109` "err on side of caution."

**Fix** — add a short framing sentence before the bullets stating diff-relevance trumps checklist completeness:

Before (`:11`):
```
## Review Scope
```

After:
```
## Review Scope

Use the categories below as a lens, not a checklist. For each changed file, identify which categories apply based on what the code actually does (e.g. no auth code → skip the auth section). Depth matters more than category coverage.
```

**Priority**: Medium — reduces tokens-per-review and focuses the model on relevant categories.

---

#### M2. Analysis Methodology is reflexive boilerplate

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:49-54`

```
## Analysis Methodology

1. Identify security context and attack surface
2. Map data flows from untrusted sources to sensitive operations
3. Examine each security-critical operation for proper controls
4. Evaluate defense-in-depth measures
```

INSIGHTS §3:
> `Think step-by-step` as reflexive boilerplate — only helps when genuinely multi-step.

This is effectively a "think step-by-step" prompt rebranded. For a single-file diff with no auth code, forcing a four-step attack-surface analysis adds latency without value. For larger diffs, 4.7 will do this anyway once given the Scope lens.

**Fix** — either delete the section, or gate it on diff complexity:

Before (`:49-54`): as above.

After (option A — delete; prefer this):
```
(section removed — diff-scoped review + Scope categories already imply the methodology)
```

After (option B — gate):
```
## Analysis Methodology

For diffs touching auth, input handling, or data access — trace untrusted → sensitive data flow before flagging individual findings. For small diffs in non-security-sensitive paths, apply the Scope lens directly.
```

**Priority**: Medium — removes 4 lines of reflexive structure that 4.7 will now follow literally.

---

#### M3. Cross-references block is good — but add the "what to do if you see it" rule from `review-conventions`

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:31-33`

```
**Cross-references:**
- {{ORM}} structural encapsulation ({{ARCHITECTURE}} check) → See `senior-architecture-reviewer`
- {{ORM}} query performance → See `performance-reviewer`
```

This is good (establishes ownership boundaries), but `review-conventions:67` already says:
> `If you spot something outside your scope, note it briefly as INFO — do not deep-dive.`

The agent does not re-state this, so when security-reviewer notices a perf issue adjacent to an injection finding, behavior is under-specified. 4.7 will either deep-dive (token cost) or silently skip (coverage loss).

**Fix** — add one line after the cross-references list:

Before (`:33`):
```
- {{ORM}} query performance → See `performance-reviewer`
```

After:
```
- {{ORM}} query performance → See `performance-reviewer`

If you notice a non-security issue while tracing data flows, log it as `[INFO]` with a one-line pointer to the owning agent — do not analyze further.
```

**Priority**: Medium — operationalizes an existing convention.

---

### Low priority

#### L1. `full_diff` / `changed_files` are referenced but not wrapped in XML

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:37-47`

INSIGHTS §2.3:
> **XML tags** for structure: `<instructions>`, `<context>`, `<input>`, `<document>`, `<example>`.

The agent references `changed_files` and `full_diff` as prompt variables but does not tell the model what structural form they arrive in. If the orchestrator wraps them in XML tags (e.g. `<changed_files>…</changed_files>`), documenting that here would let 4.7 parse them faster.

**Fix** — if the orchestrator does pass them as XML, add a one-line protocol note:

Before (`:37`):
```
## Diff-Scoped Review

When `changed_files` and `full_diff` are provided in the prompt:
```

After:
```
## Diff-Scoped Review

Orchestrator-provided inputs arrive as `<changed_files>` (newline-separated paths) and `<full_diff>` (unified diff). When both are present:
```

(Verify the orchestrator's actual format before making this change — if it uses another convention, match that.)

**Priority**: Low — depends on orchestrator protocol. Skip if XML is not used.

---

#### L2. Positive framing for the no-issue path

**File**: `.claude/agents/code-review-agents/security-code-reviewer.md:71`

```
*No security issues found.* — OR severity-tagged findings:
```

INSIGHTS §2.6:
> **Positive framing** beats negative.

Minor polish — the italicized phrase is fine, but combining it with the coverage-over-filter change from H1 means the agent should almost never produce this literal string once low-confidence findings are included.

**Fix** — reword to make the no-issue path explicit about confidence:

Before (`:71`):
```
*No security issues found.* — OR severity-tagged findings:
```

After:
```
If after full coverage no issue meets even LOW confidence, write: *Reviewed; no security concerns surfaced.* Otherwise list severity-tagged findings below.
```

**Priority**: Low — cosmetic but aligns the clean-case output with the H1 coverage directive.

---

## 2. `performance-reviewer.md`

### Frontmatter

**File**: `.claude/agents/code-review-agents/performance-reviewer.md:1-8`

```yaml
name: performance-reviewer
description: Analyzes code for performance issues, bottlenecks, and resource efficiency. Use after implementing DB queries, API calls, data processing, or memory-intensive operations.
tools: Glob, Grep, Read, Edit, Write, BashOutput
model: inherit
skills:
  - review-conventions
```

**Assessment**: The task brief flags a specific risk:
> *"Performance reviews should only fire when relevant (narrow `description:` trigger)."*

The current description triggers on `DB queries, API calls, data processing, or memory-intensive operations` — which is reasonable, but `data processing` is **broad enough to match almost any business-logic diff** under 4.7's more action-biased dispatcher. A trivial `.map()` transformation counts as "data processing."

**Priority**: High frontmatter fix (tracked as H3 below).

---

### High priority

#### H3. `description:` over-triggers due to the phrase "data processing"

**File**: `.claude/agents/code-review-agents/performance-reviewer.md:3`

```yaml
description: Analyzes code for performance issues, bottlenecks, and resource efficiency. Use after implementing DB queries, API calls, data processing, or memory-intensive operations.
```

The orchestrator pipeline may invoke this agent explicitly (not via auto-dispatch), in which case the risk is lower. But per the task brief, 4.7's action-biased dispatcher amplifies over-broad triggers. `data processing` has no clear bound.

**Fix** — narrow to concretely performance-relevant patterns:

Before:
```yaml
description: Analyzes code for performance issues, bottlenecks, and resource efficiency. Use after implementing DB queries, API calls, data processing, or memory-intensive operations.
```

After:
```yaml
description: Reviews diffs that touch database queries, external API calls, loops over user-scaled collections, caching layers, or explicit concurrency primitives. Skip for pure UI, config, or small business-logic changes with no I/O and no unbounded iteration.
```

The added "Skip for…" clause gives the dispatcher a negative boundary — INSIGHTS §1 notes 4.7 follows instructions more literally, so an explicit skip condition is honored.

**Priority**: High — directly addresses the task brief's specialist-reviewer concern.

---

#### H4. "Only report findings you are >80% confident about" contradicts security-reviewer's coverage need AND is restated *twice*

**File**: `.claude/agents/code-review-agents/performance-reviewer.md:84`

```
- **Only report findings you are >80% confident about.** If you are unsure whether something is actually a problem, do not report it. False positives waste developer time and erode trust in the review process.
```

The shared `review-conventions` skill (`:28`) already states this rule. Restating it here with intensifiers (**Only**, **erode trust**) + a **second** paragraph of justification doubles down on filtering.

For performance this is *more* appropriate than for security — a noisy perf flag on every `.map()` is worse than missing one — but the current wording is still too strong for 4.7. Per INSIGHTS §1, review harnesses "obey severity/confidence filters more literally → recall may appear to drop." The model may now drop MEDIUM-confidence N+1 suspicions that are worth investigating.

**Fix** — soften wording, shift to coverage+confidence-tag model, and avoid duplicating the shared skill:

Before (`:82-85`):
```
## Confidence & Consolidation

- **Only report findings you are >80% confident about.** If you are unsure whether something is actually a problem, do not report it. False positives waste developer time and erode trust in the review process.
- **Consolidate similar issues into a single finding with count.** For example, write "3 unbounded findMany queries" with a list of locations, not 3 separate findings. This keeps the review scannable.
```

After:
```
## Confidence & Consolidation

- Tag every finding with a confidence level (HIGH / MEDIUM / LOW). Report HIGH- and MEDIUM-confidence findings. Drop LOW-confidence ones unless the potential impact is CRITICAL (e.g. unbounded query on a large table) — at that severity, reporting with a LOW tag is preferable to silence.
- Consolidate repeated patterns: write "3 unbounded findMany queries" with a location list, not 3 separate findings. This keeps the review scannable.
```

Rationale: the severity-conditional carve-out mirrors H1's coverage-over-filter for the narrow cases where perf issues are genuinely dangerous, while keeping the signal-to-noise bar high for routine perf nits.

**Priority**: High — the asymmetry between security (coverage) and performance (filter) is exactly what the task brief called out.

---

### Medium priority

#### M4. Intensifier on "Do NOT scan the entire codebase" could be softened with rationale

**File**: `.claude/agents/code-review-agents/performance-reviewer.md:47`

```
4. **Do NOT** scan the entire codebase with Glob/Grep for performance patterns — focus on the diff
```

This `Do NOT` *is* load-bearing (prevents cross-codebase scanning), so keep the prohibition. But INSIGHTS §2.2 ("Explain the *why*") says rationale beats rules. 4.7 will honor this either way, but adding the why prevents future drift.

Before:
```
4. **Do NOT** scan the entire codebase with Glob/Grep for performance patterns — focus on the diff
```

After:
```
4. Keep Glob/Grep scoped to files referenced by the diff. Codebase-wide pattern scans produce stale findings (pre-existing issues, not caused by this change) and inflate token cost — the orchestrator's full-codebase review pipeline handles that separately.
```

**Priority**: Medium — small polish, makes the rule stick.

---

#### M5. Empty "Analysis Methodology" absence — add a diff-complexity gate like security's M2

**File**: `.claude/agents/code-review-agents/performance-reviewer.md:49` (between Diff-Scoped Review and Output Mode)

Unlike `security-code-reviewer.md`, this file has no Analysis Methodology section. That is actually *fine* (INSIGHTS §3 flags boilerplate methodology sections as over-prompting). Noting it here to confirm — no change needed, and security-reviewer should match by removing M2 rather than performance adding one.

**Priority**: Medium — symmetry argument, dependent on M2's outcome. No action needed on this file.

---

### Low priority

#### L3. Missing explicit "non-issue" phrasing consistency

**File**: `.claude/agents/code-review-agents/performance-reviewer.md:62`

```
*No performance issues found.* — OR severity-tagged findings:
```

Same cosmetic concern as L2. Consider:

Before:
```
*No performance issues found.* — OR severity-tagged findings:
```

After:
```
If the diff shows no HIGH/MEDIUM-confidence performance concerns, write: *Reviewed; no performance concerns at current scale.* Otherwise list severity-tagged findings below.
```

The "at current scale" hedge matches the Confidence section's scale-aware philosophy (the file already says `Consider runtime environment and scale requirements`).

**Priority**: Low — alignment with H4.

---

#### L4. Missing INFO-pointer rule for cross-scope findings

**File**: `.claude/agents/code-review-agents/performance-reviewer.md`

Unlike security-reviewer, this file has **no** cross-references block pointing to other review agents. If perf-reviewer notices a security issue (e.g. an unbounded query that is also an IDOR), there is no explicit guidance to drop an `[INFO]` pointer. The shared `review-conventions:67` covers it, but the agent does not reinforce it.

**Fix** — add a short block after Review Scope:

Before (`:31`, end of Project-Specific block):
```
- Long-running tasks: no blocking awaits in request handlers
```

After:
```
- Long-running tasks: no blocking awaits in request handlers

**Cross-references** (drop a one-line `[INFO]` pointer, do not deep-dive):
- Query parameter binding / injection risk → `security-code-reviewer`
- Architectural layer violations (e.g. controller calling ORM directly) → `senior-architecture-reviewer`
```

**Priority**: Low — parity with security-reviewer and explicit reinforcement of the shared ownership convention.

---

## 3. Cross-file summary

| # | File | Priority | Category |
|---|---|---|---|
| H1 | security | High | Coverage-over-filter override (INSIGHTS §1, §4) |
| H2 | security | High | Intensifier hygiene on return-summary block |
| H3 | performance | High | Over-broad `description:` (task brief focus) |
| H4 | performance | High | Confidence-tag + severity-conditional carve-out |
| M1 | security | Medium | Scope framing (depth over checklist) |
| M2 | security | Medium | Remove reflexive methodology section |
| M3 | security | Medium | Add INFO-pointer rule for cross-scope findings |
| M4 | performance | Medium | Add rationale to `Do NOT` rule |
| M5 | performance | Medium | Symmetry note (no action) |
| L1 | security | Low | XML input-wrapping (orchestrator-dependent) |
| L2 | security | Low | Clean-case positive framing |
| L3 | performance | Low | Clean-case positive framing |
| L4 | performance | Low | Add cross-references block |

**Key asymmetry to preserve**: security favors **coverage** (H1), performance favors **filter** (H4). Both are consistent with INSIGHTS §1: review harnesses under 4.7 obey filters more literally, but the right filter threshold depends on the cost of a false negative — which is much higher for security than for performance.

**Items the files already get right** (don't change):
- Both use file-mode section-marker protocol cleanly — good separation of concerns with the orchestrator.
- Diff-Scoped Review sections are well-structured and cite `changed_files` / `full_diff` correctly.
- `tools:` lists are minimal and appropriate (no unnecessary tool access).
- Both correctly inherit the shared `review-conventions` skill and project-specific `{{…}}` tokens.
- Neither uses prefill/`<assistant>` turns (INSIGHTS §3 deprecation — not an issue here).
- Neither imposes hard response-length caps (INSIGHTS §3 — not an issue).
