# Skill Review — `parallelization` and `dbg`

Reviewed against `tasks/opus-4-7-skill-review/INSIGHTS.md` (Opus 4.7 prompting best practices).

Files examined:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/parallelization/SKILL.md` (153 lines, single file)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/dbg/SKILL.md` (130 lines, single file)

Overall: both skills are relatively well-tuned already. `parallelization` gets the "spawn in a single message" nudge right (critical for 4.7 per INSIGHTS §1 + §4) but buries it under too much scaffolding and could state the *why* more prominently. `dbg` strongly embodies the investigate-before-answering pattern via its runtime-evidence posture, but has a few intensifier and tool-nudge hotspots to dial back.

---

## Skill 1: `parallelization`

### High priority

#### H-P1. Strengthen the "fan out in one turn" directive — it is the single load-bearing instruction for 4.7

File: `.claude/skills/parallelization/SKILL.md:65`

Current text (lines 63–65):
> "Spawn ALL workers in a **single assistant message** to maximize true concurrency:"

This is correct but under-emphasized: it appears once, after 40+ lines of scaffolding, as a lead-in to a code block. Per INSIGHTS §1 (subagent-spawning row: *"More conservative by default. Must **explicitly** tell it to fan out across files/items for parallelism."*) and §4 (parallel-subagent prompt template), 4.7 under-parallelizes by default and this skill's entire value proposition collapses if the model spawns workers sequentially.

Recommendation: promote the rule to the top of the "Workflow" section, repeat it inside the spawn example, and add the rationale.

Before (lines 63–65):
```
Spawn ALL workers in a **single assistant message** to maximize true concurrency:
```

After:
```
Spawn every worker in **the same assistant message** — do not default to
sequential Agent calls. True concurrency only happens when all Agent tool
calls are in one turn; splitting them across turns serializes the work and
defeats the purpose of this skill. When calls have no dependencies, batch
them; never spawn one, wait, then spawn the next.
```

Cross-ref: INSIGHTS §1 (subagent-spawning), §4 (parallel-subagent prompt), §4 (parallel-tool-call prompt).

---

#### H-P2. Add an explicit "no sequential fallback" guard to the spawn step

File: `.claude/skills/parallelization/SKILL.md:67–89` (the pseudo-code spawn block)

The example shows two Agent calls stacked, but does not tell the model what **not** to do. 4.7's literal-instruction bias (INSIGHTS §1 instruction-following row) means it will follow the letter of the example without inferring the negative. A developer agent reading this may still pattern-match to "spawn worker 1, observe, spawn worker 2" unless the skill calls it out.

Before (after line 89, end of the pseudo-code block):
```
Agent tool call 2 (same message):
  subagent_type: "developer-agent"
  isolation: "worktree"
  prompt: |
    (same structure, different criterion)
```

After: append one line immediately below the block:
```
Anti-pattern: do not call one Agent, wait for its result, then call the
next. All N spawn calls go in one assistant message, period. If you find
yourself about to issue a single Agent call when multiple items were
selected, stop and batch them.
```

Cross-ref: INSIGHTS §1 (instruction-following: "More literal; will NOT silently generalize"), §4 (parallel-subagent prompt).

---

### Medium priority

#### M-P1. Dial back `MUST` / `ONLY` intensifiers that are not load-bearing

File: `.claude/skills/parallelization/SKILL.md:77`, `:140–142`

Offending lines:
- `:77` — "Implement ONLY criterion [N]"
- `:79` — "Do NOT create git commits — just make the changes"
- `:80` — "Do NOT edit shared task documents"
- `:140` — "**Git writes require explicit user approval**"
- `:141` — "**Task docs are orchestrator-owned**"
- `:142` — "**No scope creep**"

Per INSIGHTS §3, `MUST` / `NEVER` / `ONLY` as intensifiers cause over-triggering on 4.7. Some of these (git commit gating, task-doc ownership) are genuinely load-bearing and should stay forceful. But "Implement ONLY criterion [N]" in a worker prompt risks the developer-agent refusing to make a needed supporting edit (e.g., importing the function it just defined) because it reads "ONLY" too literally.

Before (line 77):
```
- Implement ONLY criterion [N]
```

After:
```
- Scope: criterion [N]. Make the edits needed to satisfy it (including
  required supporting imports, types, fixtures). Do not expand scope into
  other criteria, unrelated refactors, or drive-by cleanups.
```

This preserves the guard but explains the *why* (INSIGHTS §2 rule 2) and removes the bare intensifier.

Cross-ref: INSIGHTS §3 (intensifier hygiene), §4 (minimize-over-engineering prompt).

---

#### M-P2. "Be thorough" pattern absent — but an implicit coverage/stopping issue in the decision matrix

File: `.claude/skills/parallelization/SKILL.md:27–40` (decision matrix)

The matrix tells the model when to parallelize but not how to decide on ambiguous cases. Per INSIGHTS §1 (instruction-following), 4.7 will not generalize: if a scenario isn't in the table, the model may freeze or default unpredictably.

Before (after line 40):
```
**Max concurrency**: Spawn at most **4 workers** simultaneously.
```

After: add one line below:
```
If a scenario is not covered by the matrix, default to sequential and state
your reasoning in one sentence before proceeding. Parallelization is an
optimization, not a requirement — when independence is uncertain,
sequential is the safe choice.
```

Cross-ref: INSIGHTS §3 (literal-scope gaps), §4 (state scope explicitly).

---

### Low priority

#### L-P1. Add compaction-awareness note for long multi-wave runs

File: `.claude/skills/parallelization/SKILL.md` (no line — add at end of "Workflow" section, after `:137`)

For tasks with multiple waves and 3–4 workers each, the orchestrator's context can fill quickly with worker-result summaries. INSIGHTS §4 includes a recommended compaction-awareness prompt for long-running skills.

Suggested addition (after "Update task document" section):
```
### Context note
Worker results accumulate in this conversation. Context may be
auto-compacted between waves. Before starting the next wave, re-read the
task document to reconstruct scope, and only persist between waves what
you will actually need (diffs applied, validation status). Do not stop a
multi-wave run because context feels full — compaction is handled for you.
```

Cross-ref: INSIGHTS §4 (context-awareness for long skills).

---

#### L-P2. Announcement line is fine; leave as-is

File: `.claude/skills/parallelization/SKILL.md:23`

> `> **Announcement**: Begin with: "I'm using the **parallelization** skill for parallel implementation orchestration."`

This is a harmless tag; no 4.7 anti-pattern triggers. No change.

---

## Skill 2: `dbg`

### High priority

#### H-D1. The "Forbidden" section collides with 4.7's intensifier aversion — reframe positively

File: `.claude/skills/dbg/SKILL.md:126–129`

Current text:
```
## Forbidden
- Fixing without runtime evidence
- Removing logs before verification
- Using sleeps/delays as a "fix"
```

Per INSIGHTS §2 rule 6 ("Positive framing beats negative") and §3 (negative-framing verbosity nudges should become positive), a "Forbidden" header with bare rules is the most aggressive negative framing in the skill. Reframe as positive statements tied to the skill's core posture (runtime evidence).

Before:
```
## Forbidden
- Fixing without runtime evidence
- Removing logs before verification
- Using sleeps/delays as a "fix"
```

After:
```
## Core principles
- Fix only after logs confirm the root cause — runtime evidence is the
  contract this skill offers the user.
- Keep instrumentation in place until the verification run proves the
  fix, then clean up in one pass.
- If a sleep or delay "fixes" the bug, it is masking a race condition;
  surface the race in the report instead of shipping the delay.
```

This preserves the same rules, explains the *why* (INSIGHTS §2 rule 2), and drops the negative framing that 4.7 tends to over-weight.

Cross-ref: INSIGHTS §2 (positive framing, explain the why), §3 (verbosity-nudging negative framing).

---

#### H-D2. "only then fix" and the Step 6 "**only**" intensifier are good — but pair them with investigate-before-answering rationale

File: `.claude/skills/dbg/SKILL.md:25–26`, `:107`

Lines 25–26:
> "Find root cause using **runtime evidence**, not guesses. Instrument code, collect logs, confirm hypotheses, and only then fix."

Line 107:
> "Implement a fix **only** when logs confirm the root cause."

These lines are the skill's strongest asset — they match INSIGHTS §4's investigate-before-answering prompt almost verbatim. The recommendation here is additive, not corrective: make the rationale explicit at the top so 4.7 (which is more action-biased per INSIGHTS §3 "Do not suggest, make the changes...") doesn't skip straight to editing on the first guess.

Before (line 25–26, Objective):
```
## Objective
Find root cause using **runtime evidence**, not guesses. Instrument code, collect logs, confirm hypotheses, and only then fix.
```

After:
```
## Objective
Find root cause using runtime evidence, not guesses. Never speculate
about code paths you have not opened or behavior you have not logged.
The investigate-then-fix ordering exists because guessed fixes mask
bugs that reappear in production; logged-and-verified fixes do not.
Instrument, reproduce, analyze, confirm, and only then edit.
```

Cross-ref: INSIGHTS §2 rule 2 (explain the why), §4 (investigate-before-answering prompt), §1 (4.7 more action-biased).

---

### Medium priority

#### M-D1. "Default to using [tool]" risk: the `AskUserQuestion` nudge is slightly too reflexive

File: `.claude/skills/dbg/SKILL.md:75–77`

Current text:
```
### Step 0: Clarify (if needed)
If the bug context is vague, ask clarifying questions first using `AskUserQuestion`.
Goal: reproducible steps, expected vs actual behavior, environment info, scope.
```

This is close to "Default to using [tool]" (INSIGHTS §3 anti-pattern) — 4.7 may over-trigger `AskUserQuestion` even when the user has already supplied a stack trace + repro steps. Narrow the trigger.

Before:
```
### Step 0: Clarify (if needed)
If the bug context is vague, ask clarifying questions first using `AskUserQuestion`.
Goal: reproducible steps, expected vs actual behavior, environment info, scope.
```

After:
```
### Step 0: Clarify (only if critical info is missing)
Skip this step if the user supplied a reproducible trigger, a stack
trace, or an error message — proceed to Step 1. Use `AskUserQuestion`
only when you cannot name a concrete first hypothesis without more
input. The missing pieces worth asking about are: exact repro steps,
expected vs actual, and environment (not general "tell me more").
```

Cross-ref: INSIGHTS §3 ("Default to using [tool]" anti-pattern, tool-use over-nudging).

---

#### M-D2. "Be thorough" shape around hypothesis count — has a stopping condition but instrumentation count may over-trigger on small bugs

File: `.claude/skills/dbg/SKILL.md:63–65`, `:86–87`

Line 63–65 (Rules block):
```
- Insert **3–8** log points total
- Cover: entry, exit, before/after critical ops, branches, edge values, state changes
```

Line 86–87:
```
Generate **3–5 precise hypotheses** about the bug cause. Be specific — each hypothesis should point to a different subsystem or failure mode.
```

Both have ranges (good — INSIGHTS §3 flags "be thorough with no stopping condition"), but for a trivial bug (missing import, typo) the 3–5 / 3–8 floors force over-investigation. The skill's own Step 1 ("This often narrows the search space dramatically or reveals trivial causes that don't need full instrumentation") acknowledges this but doesn't update the floors.

Before (line 63):
```
- Insert **3–8** log points total
```

After:
```
- Insert **3–8** log points for non-trivial bugs. For bugs where Step 1
  triage already identified a likely cause (typo, missing import, obvious
  config mismatch), 1–2 confirming log points are enough — do not pad.
```

And (line 86):
```
Generate **3–5 precise hypotheses** about the bug cause.
```

After:
```
Generate **2–5 precise hypotheses**, scaled to bug complexity. For a
trivial bug with a clear suspect from Step 1, two hypotheses (the suspect
and one alternative) are enough. For a cross-service race condition, use
the full 5.
```

Cross-ref: INSIGHTS §3 ("Be thorough" with no stopping condition), §1 (response length calibrated to task complexity).

---

### Low priority

#### L-D1. `No secrets or PII` reads as a bare negative — small positive reframe

File: `.claude/skills/dbg/SKILL.md:66`

Current:
```
- **No secrets or PII** in log data
```

After:
```
- Log shapes and non-sensitive values only: booleans, counts, enum
  states, sanitized IDs. If a field could contain a secret or PII,
  log its presence and type (`{ token: "<redacted:string:len=42>" }`),
  not the value.
```

Cross-ref: INSIGHTS §2 rule 6 (positive framing), §2 rule 2 (explain the why).

---

#### L-D2. Announcement + Configuration section are clean — no change

File: `.claude/skills/dbg/SKILL.md:23`, `:29–36`

The announcement tag and the Log Path / Log Payload configuration are concise, concrete, and positively framed. No 4.7 anti-pattern triggers. Leave as-is.

---

## Summary of recommended changes

| Skill | Priority | Recommendation | INSIGHTS ref |
|---|---|---|---|
| parallelization | High | Promote & repeat "spawn all workers in one message" with rationale | §1 subagent, §4 parallel-subagent |
| parallelization | High | Add explicit anti-pattern: "don't issue one Agent call then wait" | §1 instruction-following, §4 parallel-subagent |
| parallelization | Medium | Reframe `ONLY criterion [N]` with scope guidance + why | §3 intensifiers, §4 minimize-over-engineering |
| parallelization | Medium | Add fallback rule for scenarios not in decision matrix | §3 literal-scope gaps, §4 state scope explicitly |
| parallelization | Low | Add compaction-awareness note for multi-wave runs | §4 context-awareness |
| dbg | High | Reframe "Forbidden" section as "Core principles" (positive) | §2 positive framing, §3 negative framing |
| dbg | High | Add explicit investigate-before-answering rationale to Objective | §2 why, §4 investigate-before-answering |
| dbg | Medium | Narrow Step 0 `AskUserQuestion` trigger (avoid over-nudge) | §3 tool-use over-nudging |
| dbg | Medium | Scale hypothesis + log-point counts to bug complexity | §3 stopping condition, §1 adaptive length |
| dbg | Low | Positive reframe of "No secrets or PII" rule | §2 positive framing, §2 why |

What's already well-tuned (do not change):
- `parallelization`: the decision matrix itself (§3 structured examples), the "why worktrees" rationale paragraph at `:91` (§2 rule 2), the Safety Rules ownership model (genuinely load-bearing intensifiers).
- `dbg`: the Step 1 Quick Triage section (embodies investigate-before-answering), the NDJSON schema (positive/concrete), the scope-boundaries cross-references to `/code-analysis` and `/fci` (clear routing, no over-triggering).
