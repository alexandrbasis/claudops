# Opus 4.7 Audit — `sr` and `prc` skills

Scope: `.claude/skills/sr/SKILL.md` + `.claude/skills/prc/SKILL.md`. Findings cite `INSIGHTS.md` §3 (anti-patterns) and §4 (positive patterns). The SR orchestrator also owns the dispatch contract for the downstream review agents (`.claude/agents/code-review-agents/*.md`) and the shared `review-conventions` skill (line 28 of that skill), so filter-leakage that lives there is flagged here because SR is what ships it to 4.7.

---

## `sr` — Start Review (`.claude/skills/sr/SKILL.md`)

SR is the highest-impact skill in this audit for 4.7 because it is a multi-agent review orchestrator. Three issues materially hurt recall or parallelism on 4.7; the rest are polish.

### HIGH priority

#### H1. Filter leakage: ">80% confidence" threshold shipped to every review agent

**Cross-ref:** INSIGHTS.md §1 (Code-review harnesses row), §3 ("Only report high-severity/important issues … 4.7 obeys literally → recall drops"), §4 (coverage-then-filter split).

SR does not carry the filter itself, but it dispatches the six review agents that share the `review-conventions` skill. That shared skill contains the filter, and three agents re-assert it verbatim. On Opus 4.7, which obeys filter instructions *more* literally than 4.6, this is the single largest recall risk in this stack.

Offending text (shared skill — `.claude/skills/review-conventions/SKILL.md:28`):

```
- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.
```

Re-asserted at `code-quality-reviewer.md:102`, `documentation-accuracy-reviewer.md:91`, `performance-reviewer.md:93`:

```
- **Only report findings you are >80% confident about.** If you are unsure whether something
  is actually a problem, do not report it. False positives waste developer time and erode trust
  in the review process.
```

Because SR is the only caller of these agents and because SR's STEP 9 already performs a consolidation pass (`key-findings — consolidate actionable findings from all agents, ordered by severity`), the correct place to filter is the orchestrator, not the agent. This is exactly INSIGHTS §4's coverage-then-filter split.

**Recommended change (in `review-conventions` + the three re-asserting agents — not SR itself, but SR should adopt the orchestrator-side filter to compensate):**

Before:

```
- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.
```

After:

```
- **Coverage first**: report every issue you find in your scope, including low-severity and
  uncertain ones. Tag each finding with a `confidence: low | medium | high` field alongside
  severity. The orchestrator filters; your job is to find.
- **Consolidate duplicates** (e.g. "5 functions missing error handling" with a list) so the
  orchestrator sees one item, not five.
```

And in SR itself, STEP 9, teach the orchestrator to do the filtering that used to happen inside the agents:

Before (`.claude/skills/sr/SKILL.md:193`):

```
- `key-findings` — consolidate actionable findings from all agents, ordered by severity
```

After:

```
- `key-findings` — consolidate actionable findings from all agents. Include every
  CRITICAL and MAJOR regardless of confidence. For MINOR/INFO, include items marked
  `confidence: high`; drop or collapse `confidence: low` MINOR/INFO into a single
  "Other low-confidence notes" bullet. Order by severity, then confidence.
```

This keeps the final review just as terse as today but stops silently discarding real issues at the agent boundary.

---

#### H2. SR spawns many agents but never tells 4.7 to run them in parallel

**Cross-ref:** INSIGHTS.md §1 (Subagent spawning row: "must **explicitly** tell it to fan out"), §4 ("Parallel subagent prompting").

STEP 5 lists up to seven reviewers (spec, security, code-quality, senior-architecture, test-coverage, documentation-accuracy, performance) plus three conditional targeted reviewers. STEP 8 says only:

`.claude/skills/sr/SKILL.md:179`

```
## STEP 8: Dispatch Agents

Pass `cr_file_path` to every agent so they use **File Mode**.

Dispatch agents and let each agent **Read → Edit** its own `<!-- SECTION:xxx -->` markers in `cr_file_path`.
```

There is no instruction to dispatch in the same turn. On 4.7, "dispatch agents" defaults to *sequential* — recall from INSIGHTS §1 that 4.7 is more conservative about subagent spawning. A 6-agent sequential review costs several minutes of wall time and multiplies context pressure versus a one-turn fan-out.

Before (STEP 8, first two lines):

```
Pass `cr_file_path` to every agent so they use **File Mode**.

Dispatch agents and let each agent **Read → Edit** its own `<!-- SECTION:xxx -->` markers in `cr_file_path`.
```

After:

```
Pass `cr_file_path` to every agent so they use **File Mode**.

Dispatch **all agents selected in STEP 5 in a single turn** — issue every Agent tool call
in the same assistant message. The agents write to disjoint `<!-- SECTION:xxx -->` markers
in `cr_file_path`, so there are no ordering dependencies. Do not dispatch one, wait for it
to finish, then dispatch the next; that serializes a parallel workload.
```

Also update the shared `full_diff` / `changed_files` contract note so batch dispatch is obviously safe: each agent already receives the same diff context (STEP 3 computes it "once and share[s] it with all reviewers"), so the tool calls are independent.

---

#### H3. "Always run" / "Never" / "Do NOT" intensifiers stacked without the *why*

**Cross-ref:** INSIGHTS.md §3 (`ALWAYS` / `NEVER` used as intensifiers → over-triggering on 4.7), §2.2 (explain the *why*).

SR is unusually intensifier-heavy. Some are genuinely load-bearing (e.g. "Never return APPROVED for an uncommitted working-tree draft" — that's a real gate). Others read as emphasis and are the exact pattern §3 flags:

- `.claude/skills/sr/SKILL.md:94` — `Do NOT force main...HEAD onto every review mode.`
- `.claude/skills/sr/SKILL.md:153` — `After **any** reviewer flags a major or critical finding, grep the codebase for the same anti-pattern in related files`
- `.claude/skills/sr/SKILL.md:167` — `Verification is evidence, not a prerequisite for starting review.`
- `.claude/skills/sr/SKILL.md:183` — `Each agent writes only within its own markers — no agent touches another agent's section.`
- `.claude/skills/sr/SKILL.md:187` — `After **all** agents finish, proceed to STEP 9.`

The problem isn't the content — it's that SR piles rule-without-rationale atop rule-without-rationale, which is the shape 4.7 over-triggers on.

Example before (line 153):

```
After **any** reviewer flags a major or critical finding, grep the codebase for the same
anti-pattern in related files before finalizing the review. Document sibling occurrences
in the `key-findings` section even if those files are outside the current diff.
```

After (adds *why*, drops emphasis):

```
When a reviewer flags a major or critical finding, scan the codebase for the same
anti-pattern in related files before finalizing. Sibling occurrences are often where
the real bug lives — the flagged file is frequently just the first place it was spotted.
Record siblings in `key-findings` even if they are outside the current diff.
```

Apply the same treatment to the "Common Mistakes" list at `sr/SKILL.md:222-231`: it is a pure negative-framing block ("Creating multiple CR files…", "Blocking review because the branch is dirty…"). On 4.6 that was helpful reinforcement; on 4.7 it crowds the prompt. Fold the genuinely load-bearing ones into positive rules at the relevant step and delete the rest.

---

### MEDIUM priority

#### M1. `Always run` vs. `Run … when` — literal-scope gap

**Cross-ref:** INSIGHTS.md §3 (literal scope, will not silently generalize), §1 (Instruction-following row).

STEP 5.2 says:

```
Always run:
- `security-code-reviewer`
- `code-quality-reviewer`
```

Then STEP 5.3 uses `In full scope, also run: …`. That's fine. But STEP 5.4 ("Targeted Reviewers") describes *what to inspect* in prose paragraphs rather than naming agent invocations:

`.claude/skills/sr/SKILL.md:129-149`

```
**Error path reviewer** — when the diff contains async call chains:
- For each async call chain: what happens if it throws? …
```

No corresponding agent file exists in `.claude/agents/code-review-agents/` (I checked — the six files there do not include an "error path reviewer"). So on 4.7 one of two things happens: the orchestrator silently skips these because there's no agent to Task-dispatch, or it does the checks itself inline. Either is literal — but the prompt is ambiguous. Make the intent explicit.

Before:

```
### 5.4 Targeted Reviewers

Run conditionally based on diff content:

**Error path reviewer** — when the diff contains async call chains:
- For each async call chain: what happens if it throws? …
```

After (pick one intent):

```
### 5.4 Targeted Review Passes (orchestrator-owned, not subagents)

When the diff matches these triggers, the orchestrator runs the check inline and
adds findings to `key-findings`. These are not separate agents.

**Error-path pass** — trigger: diff contains `async` / `await` / `.then(` / `Promise`.
  - For each async call chain: what happens if it throws? …
```

This removes the ambiguity *and* aligns with INSIGHTS §1's note that 4.7 is more literal — it won't invent an agent that doesn't exist, nor will it silently promote the prose to an action.

---

#### M2. "Be thorough"-shaped instruction without a stopping condition

**Cross-ref:** INSIGHTS.md §3 ("Be thorough / exhaustive / comprehensive with no stopping condition").

`.claude/skills/sr/SKILL.md:151-155`:

```
### 5.5 Pattern Propagation

After **any** reviewer flags a major or critical finding, grep the codebase for the same
anti-pattern in related files before finalizing the review. Document sibling occurrences
in the `key-findings` section even if those files are outside the current diff.
```

"grep the codebase" has no bound. On a large repo with a noisy regex, 4.7 can burn a lot of tokens chasing pattern matches. Add a stopping condition.

After:

```
### 5.5 Pattern Propagation

When a reviewer flags a major or critical finding, spend up to ~5 minutes scanning
sibling files for the same anti-pattern. Stop at 5 sibling occurrences, or when
coverage of plausible locations (same module, same layer, same call site shape) is
exhausted — whichever comes first. Record what you found in `key-findings`; record
"scanned N files, no sibling occurrences" if clean.
```

---

#### M3. QA recommendation is conditional — state the scope explicitly

**Cross-ref:** INSIGHTS.md §3 (literal scope).

STEP 10 today:

```
After the verdict is written, check if the diff includes UI/frontend files
(e.g., `.svelte`, `.tsx`, `.jsx`, `.vue`, `.html`, component files). If it does,
append a **QA recommendation** to the review file:
```

The list is examplar (`e.g.`). 4.7 reads `e.g.` more literally than 4.6 and may skip files the list didn't name (e.g. `.astro`, `.mdx`, CSS-only changes, Storybook). Either commit to a concrete regex, or state the intent and let it generalize from examples:

After:

```
After the verdict is written, check whether the diff affects user-facing rendering
— any file that produces DOM output, styling, or routing state. Use this list as a
seed, not a limit: `.svelte`, `.tsx`, `.jsx`, `.vue`, `.html`, `.astro`, `.mdx`,
CSS/SCSS, component stories, route files. When in doubt, treat it as UI.
```

---

### LOW priority

#### L1. `STEP 4` scope rule — positive framing

**Cross-ref:** INSIGHTS.md §2.6 (positive framing), §3 (hard numeric caps that fight 4.7's adaptive behavior).

`sr/SKILL.md:80-84`:

```
Use `quick` only when ALL are true:
- `<= 3` changed files
- `<= 50` diff lines
- no auth, migrations, infra, build-system, or shared framework changes

Otherwise use `full`.
```

This is well-tuned for a gate, but the "otherwise use `full`" fallback is the tell: 4.7 is biased to `full` anyway, so the "ALL are true" framing is belt-and-suspenders. Not worth changing unless you want to trim. Fine as-is.

#### L2. `Announcement` line

`sr/SKILL.md:24`:

```
> **Announcement**: Begin with: "I'm using the **sr** skill for universal code review."
```

This is prefill-shaped. Per INSIGHTS §1, prefill is deprecated and §3 flags "Pre-filled assistant turns". It's a short leading sentence rather than a full prefill, so the risk is low. If you ever see 4.7 output it twice or mangle it, migrate to: "Start your reply by naming the skill you're using, e.g. *the sr skill for code review.*"

#### L3. `review-context` uses positive framing already — keep

SR's STEP 9 field list is exemplar. `verdict`, `key-findings`, `coverage`, `verification` are all positive, action-oriented. No change needed.

---

## `prc` — PR Review Comments Handler (`.claude/skills/prc/SKILL.md`)

PRC is a short, linear skill with clear gates. It is mostly well-tuned for 4.7 — there is no subagent fan-out and no severity filter. Three small findings.

### MEDIUM priority

#### M1. Classification can silently drop reviewer feedback

**Cross-ref:** INSIGHTS.md §3 ("Only report high-severity / important" → 4.7 obeys literally → recall drops), §4 (coverage-then-filter split).

`.claude/skills/prc/SKILL.md:56-65`:

```
### Step 1: Categorize Comments

For each review comment, evaluate:
- Is the feedback valid and technically correct?
- Is it applicable to the current code?
- Does it align with project conventions and architecture?
- Is it a blocker or a nice-to-have suggestion?

Classify each comment into one of:
- **Address** — Valid feedback, will fix
- **Skip** — Not applicable or already handled (provide reason)
- **Discuss** — Ambiguous or disagreed, needs user input
```

The issue: this is an implicit filter. On 4.6 the model would usually present questionable comments as "Discuss". On 4.7, which is more literal about filtering instructions, there is a real risk that a comment the reviewer cares about lands in "Skip" with a plausible-sounding reason — and the user only sees the three categories in the plan table, never the raw comments. The user approves the table, and the skipped comment is gone.

Make coverage explicit:

Before:

```
### Step 1: Categorize Comments

For each review comment, evaluate:
…
Classify each comment into one of:
- **Address** — Valid feedback, will fix
- **Skip** — Not applicable or already handled (provide reason)
- **Discuss** — Ambiguous or disagreed, needs user input
```

After:

```
### Step 1: Categorize Comments

List **every** comment fetched in Gate 1 — do not drop any. Reviewer noise, nits,
and resolved threads all appear in the plan so the user sees what was received.

For each comment, propose one of:
- **Address** — Valid feedback, will fix.
- **Skip** — Not applicable, already handled, or nit you recommend ignoring.
  Always include a one-line reason so the user can override.
- **Discuss** — Ambiguous, contested, or would change scope — escalate to user.

When in doubt between Address and Skip, pick Discuss. The user decides in Gate 2
whether to drop it.
```

This is the coverage-then-filter split applied to PR comments: gather everything in Gate 1, classify in Gate 2, let the user be the final filter.

---

#### M2. "**STOP**" + "Do not proceed until user approves" — intensifier pileup

**Cross-ref:** INSIGHTS.md §3 (`CRITICAL` / `MUST` / hard stops as intensifiers).

`.claude/skills/prc/SKILL.md:76`:

```
**STOP** — Use AskUserQuestion to confirm the plan. Ask user to approve, modify,
or flag any items they disagree with. Do not proceed until user approves.
```

This pattern appears three more times (Gate 3 "Do not proceed to GATE 4" at line 100; Gate 4 "**Ask user permission** before committing" at line 113). It's load-bearing the first time and noise by the fourth. Collapse:

After (Gate 2):

```
Before implementing anything, confirm the plan with AskUserQuestion. Ask the user
to approve, edit, or flag items they disagree with — including items you marked
Skip. Implementation starts only after approval.
```

And drop the redundant "Do not proceed to GATE 4" in Gate 3 — the gate structure itself already enforces the sequence.

---

### LOW priority

#### L1. `git add` guidance — stay positive

`.claude/skills/prc/SKILL.md:111`:

```
1. Stage changed files with `git add` (specific files only)
```

This is positively framed and correct. (Compare with the project CLAUDE.md rule about avoiding `git add -A`.) No change.

#### L2. Test/lint verification block is fine

Gate 3 runs `npm test` / `{{LINT_CMD}}` / `tsc --noEmit`. These are concrete, not generic "be thorough". No change needed.

#### L3. `argument-hint: [pr-number]` vs. "If `$ARGUMENTS` contains a PR number"

The skill handles both "with arg" and "without arg" cases cleanly. 4.7's more literal following actually helps here. No change.

---

## What is already well-tuned (don't touch)

- **SR STEP 3** — explicit, ordered base-resolution list with a `Do NOT force main...HEAD` guard. The guard is load-bearing (not emphasis) because `main...HEAD` would silently corrupt working-tree reviews. Keep.
- **SR STEP 7** — one-CR-file-per-target contract with explicit sanitization and legacy-migration rules. Exactly the kind of literal scope 4.7 rewards.
- **SR STEP 9 verdicts** — four crisp verdicts with guard `Never return APPROVED for an uncommitted working-tree draft`. Load-bearing, not emphasis. Keep.
- **PRC Gate structure** — four ordered gates (Identify → Analyze → Implement → Commit) with an `AskUserQuestion` checkpoint. This is the positive pattern for 4.7's more action-biased behavior (INSIGHTS §3 flags over-aggressive "do not suggest, make changes"; PRC instead gates on user approval). Keep.
- **PRC error branches** — each gate has a concrete "Error — X" block with a Stop action. Positive, specific, no intensifier stack. Keep.

---

## Priority summary

| # | Skill | Priority | Finding | INSIGHTS ref |
|---|---|---|---|---|
| H1 | sr (via review-conventions + 3 agents) | High | `>80% confidence` filter drops recall on 4.7 — move filter to orchestrator | §3 (filter leakage), §4 (coverage-then-filter) |
| H2 | sr | High | Multi-agent dispatch not marked parallel — 4.7 serializes | §1 (subagent row), §4 (parallel subagents) |
| H3 | sr | High | Intensifier pileup without *why* across STEPs 3, 5, 6, 8 + "Common Mistakes" | §3 (intensifiers), §2.2 (why > rule) |
| M1 | sr | Medium | STEP 5.4 "Targeted Reviewers" names agents that don't exist — literal-scope ambiguity | §3 (literal scope) |
| M2 | sr | Medium | "grep the codebase" has no stopping condition | §3 (thorough without bound) |
| M3 | sr | Medium | STEP 10 UI-file list uses `e.g.` — 4.7 treats as closed list | §3 (literal scope) |
| L1-L3 | sr | Low | STEP 4 caps, announcement prefill, existing positive fields — mostly fine | §2.6, §3 (prefill) |
| M1 | prc | Medium | Gate 2 "Skip" category can silently drop reviewer comments | §3, §4 (coverage-then-filter) |
| M2 | prc | Medium | `STOP` / `Do not proceed` stacked across gates | §3 (intensifiers) |
| L1-L3 | prc | Low | `git add`, verification commands, argument handling — fine | n/a |
