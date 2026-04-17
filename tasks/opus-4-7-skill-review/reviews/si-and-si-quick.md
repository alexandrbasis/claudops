# Review: `/si` and `/si-quick` Skills — Opus 4.7 Audit

**Files reviewed:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/si/SKILL.md` (151 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/si-quick/SKILL.md` (128 lines)

**Lens:** `tasks/opus-4-7-skill-review/INSIGHTS.md` (Opus 4.7 prompting deltas).

**Overall verdict.** Both skills are generally well-structured for Opus 4.7 — they use positive framing, embed rationale (e.g., "The task document is the source of truth. Do not endlessly explore the codebase."), keep intensifiers mostly off, and include action-biased permission gates that align well with 4.7's more literal behavior. The most important gaps are (a) `/si` lacks an explicit **context-compaction awareness** block despite being a long-running loop, and (b) both skills under-specify **parallel subagent spawning semantics** (a named 4.7 regression per INSIGHTS §1/§4). Several smaller issues around intensifier hygiene, over-engineering guardrails, and literal-scope gaps are called out below.

---

## `/si` — `.claude/skills/si/SKILL.md`

### High priority

#### H1. Missing context-compaction awareness for a long-running implementation loop
**Why:** INSIGHTS §4 ("Context-awareness for long skills") calls this out as a 4.7 positive pattern. `/si` drives multi-step TDD loops that routinely span many cycles and can hit compaction — without this prompt, 4.7 is prone to stopping early "to save tokens" or losing mid-loop state.
**Cross-ref:** INSIGHTS §4 (Context-awareness), §1 (Interactive coding — "Front-load full context in turn 1").
**Location:** file has no compaction block anywhere (verified across lines 1–151).
**Recommendation:** Add a short block after `## CONSTRAINTS` (around SKILL.md:19).

Before (nothing):
```
## CONSTRAINTS
- Follow the active tech-decomposition / task document as the source of truth
- Document lifecycle: `Technical Review` → `In Progress` → `Implementation Complete`
```
After:
```
## CONSTRAINTS
- Follow the active tech-decomposition / task document as the source of truth
- Document lifecycle: `Technical Review` → `In Progress` → `Implementation Complete`
- Context will be automatically compacted during long runs. Don't stop early due to token
  concerns — persist progress to the task document after each step so a fresh window can
  resume from the same state.
```

#### H2. Parallel subagent spawning is hinted but not *instructed* to fan out in one turn
**Why:** INSIGHTS §1 notes 4.7 "subagent spawning: more conservative by default — must explicitly tell it to fan out across files/items for parallelism." The current text just points to another skill:
> `.claude/skills/si/SKILL.md:37`: "If work can be done safely in parallel, use `.claude/skills/parallelization/SKILL.md`."
That's a soft pointer; 4.7 will often choose the sequential branch unless the prompt is explicit.
**Cross-ref:** INSIGHTS §3 (under-parallelization), §4 (Parallel subagent prompting).
**Recommendation:** In the `Parallelization (optional)` section (SKILL.md:33–47), explicitly tell 4.7 *when* to parallelize and *how to dispatch in one turn*.

Before (SKILL.md:33–37):
```
### Parallelization (optional)

If work can be done safely in parallel, use `.claude/skills/parallelization/SKILL.md`.
```
After:
```
### Parallelization

When two or more steps meet the "When to parallelize" criteria below, spawn all eligible
developer-agent workers in a single assistant message via the parallelization skill. Do not
default to sequential — if the task document has wave annotations or independent modules,
parallel is the expected path. Sequential is the fallback when independence is unclear.
```

#### H3. Over-engineering guard is absent for implementation phase
**Why:** INSIGHTS §4 flags "Minimize over-engineering" as a required positive pattern for implementation skills, because 4.6/4.7 still drift toward adding abstractions/cleanup beyond scope. `/si`'s `During Implementation (TDD)` block (SKILL.md:54–61) never tells the agent not to add scope, and line 58 even says "Update docs during code changes" without a scope cap.
**Cross-ref:** INSIGHTS §4 (Minimize over-engineering), §1 (Overeagerness/over-engineering).
**Recommendation:** Insert a bullet at the top of `During Implementation (TDD)` (SKILL.md:54).

Before (SKILL.md:54–61):
```
#### During Implementation (TDD)

1. **Follow the agreed Test Plan** from the task document
2. **RED before GREEN**: each new behavior starts with a failing test that fails for the right reason
3. **One behavior per cycle**: keep each RED → GREEN → REFACTOR loop narrow
4. **No retroactive tests**: ...
```
After (add bullet 1, renumber):
```
#### During Implementation (TDD)

1. **Stay in scope**: implement what the step asks for, nothing more. Don't add abstractions,
   refactor adjacent code, or insert defensive error handling for cases that can't occur.
   Surrounding cleanup belongs in STEP 4, not inside the TDD loop.
2. **Follow the agreed Test Plan** from the task document
3. **RED before GREEN**: ...
```

### Medium priority

#### M1. Intensifier hygiene — load-bearing `REQUIRED` on a bookkeeping task
**Why:** INSIGHTS §3: "`CRITICAL:`, `You MUST`, `ALWAYS`, `NEVER` used as intensifiers — dial back to normal voice. The model is already more responsive; these now cause over-triggering."
**Location:** `.claude/skills/si/SKILL.md:89`:
> `1. **Update task document** (REQUIRED):`
This is a standard housekeeping step; the `(REQUIRED)` is decorative on 4.7.
**Recommendation:** Drop `(REQUIRED)` — the numbered step and the checkbox bullets below already carry the obligation.

Before: `1. **Update task document** (REQUIRED):`
After: `1. **Update task document**:`

Same pattern appears lightly at SKILL.md:95 ("workers must not edit shared docs; orchestrator updates once after merge") — fine as-is because it's conveying genuine safety info, not emphasis.

#### M2. Literal-scope gap: "Self-Verification" applies per step but doesn't tell 4.7 to apply across all files touched in that step
**Why:** INSIGHTS §1/§4 — "More literal; will NOT silently generalize. State scope explicitly."
**Location:** `.claude/skills/si/SKILL.md:114–119`:
```
### Self-Verification (after each step)
Before marking a step complete, verify your claims:
1. All files listed in the step actually exist on disk (run `ls <file>`)
2. All tests mentioned can be found and pass (run them)
```
On 4.7 this risks checking only the first file/test mentioned in the step.
**Recommendation:** Add explicit "every" scoping.

After:
```
### Self-Verification (after each step)
Before marking a step complete, verify your claims across **every** file and test
touched in that step — not just the first one listed:
1. Every file listed in the step exists on disk (run `ls` on each)
2. Every test mentioned can be found and passes (run them)
```

#### M3. "Use repo-appropriate verification commands ... Prefer quiet commands ..." — negative framing
**Why:** INSIGHTS §2 "Positive framing beats negative" and §3 on response-length hard caps.
**Location:** `.claude/skills/si/SKILL.md:60`:
> "Use repo-appropriate verification commands from the task doc or package scripts. Prefer quiet commands for routine loops and full output only while debugging."
The instruction is fine, but it mixes routine guidance with a verbosity hint.
**Recommendation:** Minor rewording for positive framing.

After:
```
Use repo-appropriate verification commands from the task doc or package scripts. Run the
quiet variant for routine loops; switch to full output when actively debugging a failure.
```

#### M4. Parallel-mode doc-edit rule buried inside the post-step bullet
**Why:** INSIGHTS §1/§4 — state scope explicitly for 4.7. The rule that "workers must not edit shared docs; orchestrator updates once after merge" (SKILL.md:95) is critical for avoiding merge conflicts, but sits as the last sub-bullet of the post-step update instruction. In parallel runs 4.7 may miss it.
**Cross-ref:** INSIGHTS §1 (instruction-following literalism), §4 (Parallel subagent prompting).
**Recommendation:** Promote it to its own line at the top of the `### Parallelization` section (SKILL.md:33) so each spawned worker sees the rule independent of the post-step flow.

Suggested addition to Parallelization section:
```
**Worker doc-edit rule**: In parallel mode, worker subagents MUST NOT edit the task document
or other shared files. The orchestrator consolidates all document updates once after the
wave merges. Workers return their checkbox diffs in their final message.
```

### Low priority

#### L1. "Don't endlessly explore the codebase" is negative framing
**Why:** INSIGHTS §2/§7 — convert negative to positive.
**Location:** `.claude/skills/si/SKILL.md:62`:
> "The task document is the source of truth. Do not endlessly explore the codebase."
**Recommendation:**

After:
```
The task document is the source of truth — read the files it names, implement against its
acceptance criteria, and stop exploring once you have the context needed for the current step.
```

#### L2. "Think step by step" not used — already compliant
**Why:** INSIGHTS §3 warns against reflexive `Think step-by-step`. `/si` does not contain this phrase. Noted as a point of health.

#### L3. "Ask permission **before** git write operations" list — consider splitting the list into "requires approval" vs. "always ok"
**Why:** INSIGHTS §2 "rationale > rules". The current text at SKILL.md:97 does both but bundles them mid-paragraph.
**Location:** `.claude/skills/si/SKILL.md:97`:
> "Ask permission **before** git write operations (`commit`, branch creation / switch, stash apply / drop, `push`, `rebase`, `merge`). Read-only inspection such as `git status` or `git log` is fine."
**Recommendation:** Minor formatting split into a two-column feel — low impact, but clearer.

---

## `/si-quick` (file `name: quick`) — `.claude/skills/si-quick/SKILL.md`

**Overall tuning note:** This skill is tighter and more 4.7-friendly than `/si`. Positive framing is good, scope gates are clear, and the "When to Use / When NOT to Use" pair (SKILL.md:23–35) is an excellent example of the explicit-scope pattern INSIGHTS §1 asks for. A few smaller tweaks below.

### High priority

#### H1. Over-engineering guard is absent
**Why:** Same rationale as `/si` H3 — `/si-quick` is explicitly for "small untracked changes", which is where 4.7 is most tempted to add adjacent refactors since the scope feels "low risk".
**Cross-ref:** INSIGHTS §4 (Minimize over-engineering), §1 (Overeagerness).
**Location:** STEP 3: Implement block (SKILL.md:54–61) has no guard.
**Recommendation:** Add a one-line scope lock at the top of STEP 3.

Before (SKILL.md:54):
```
### STEP 3: Implement
- Make changes directly — no task document needed
```
After:
```
### STEP 3: Implement
- Stay inside the quick plan from STEP 2. Don't refactor adjacent code, rename unrelated
  symbols, or add defensive checks for cases the plan didn't identify. If you find
  something tempting, note it as a follow-up instead of doing it.
- Make changes directly — no task document needed
```

### Medium priority

#### M1. Literal-scope gap on multi-file bugfixes
**Why:** 4.7 literalism — "Make changes directly" doesn't say "in *every* file you listed in STEP 2". For a 3-file bugfix, 4.7 may fix the first file and think it's done.
**Cross-ref:** INSIGHTS §1, §4 ("State scope explicitly").
**Location:** `.claude/skills/si-quick/SKILL.md:55`:
> "- Make changes directly — no task document needed"
**Recommendation:** Promote the plan's file list to an explicit scope.

After:
```
- Apply the change to **every file listed** in the STEP 2 plan — not only the first.
  If implementation reveals a file that wasn't in the plan, confirm before expanding scope.
```

#### M2. Intensifier: `Evidence requirement: Do not claim the task is done ...`
**Why:** INSIGHTS §3 on intensifier hygiene + negative framing. This line is load-bearing (hooks may enforce it), so we keep the substance — but positive framing lands better on 4.7.
**Location:** `.claude/skills/si-quick/SKILL.md:84`:
> "**Evidence requirement**: Do not claim the task is done without running these checks and confirming they pass. Project hooks (for example `stop-guard.sh`) may enforce similar checks."
**Recommendation:**

After:
```
**Evidence requirement**: Before reporting completion, run the checks above and show their
passing output. Project hooks (for example `stop-guard.sh`) enforce the same contract, so
skipping them will block the run anyway.
```

#### M3. TDD section mixes positive spec with negative "tests after is not TDD" trailer
**Why:** INSIGHTS §2/§7 — positive framing, rationale over rebuke.
**Location:** `.claude/skills/si-quick/SKILL.md:56–61`:
```
- **Follow TDD for any logic changes** (same bright-line rules as /si):
  - Write a FAILING test first that specifies the expected behavior
  - If you wrote production code before a failing test: delete it and restart with RED
  - Implement the minimal fix to make the test pass (GREEN)
  - Verify test passes: `{{TEST_CMD}}`
  - "Tests after" is not TDD — it produces confirmation tests, not specification tests
```
The "FAILING" (all-caps) is an intensifier; the last bullet is negative-framed polemic.
**Recommendation:** Dial back caps and turn the last bullet into a positive "why".

After:
```
- **Follow TDD for any logic changes** (same bright-line rules as /si):
  - Write the test first, and confirm it fails for the right reason before writing code
  - If production code landed before the failing test, revert it and restart from the test
  - Implement the minimum change that turns the test green
  - Verify: `{{TEST_CMD}}`
  - The test-first order matters because it lets the test specify the behavior, not just
    confirm the implementation the model already wrote.
```

### Low priority

#### L1. "What /quick Does NOT Do" block — negative framing, but defensible
**Why:** INSIGHTS §2 prefers positive framing, but a *scope non-goals* list is a valid use of negation because it's the cleanest way to communicate "these adjacent skills handle these concerns". The current list at SKILL.md:103–108 is short and clear. No change needed — flagging for completeness.

#### L2. No explicit "parallel tool calls when independent" instruction
**Why:** INSIGHTS §4 (Parallel tool-calling). `/si-quick` is small enough that tool-call parallelism is rarely needed, but when it lists files, runs `git diff --name-only`, and checks hook status, those could batch. Low priority because the skill is intentionally small-surface.
**Recommendation (optional):** One-line note in STEP 4/4.5 if the skill is ever extended with more checks.

#### L3. `Skill tool → skill: "simplify"` — syntax note for operators
**Location:** `.claude/skills/si-quick/SKILL.md:89`:
> "Run `/simplify` skill (`Skill tool → skill: "simplify"`) — ..."
This is fine for 4.7 (explicit tool hint). Noted as a positive pattern worth keeping.

---

## Summary of recommendations

### `/si`
| # | Priority | Area | INSIGHTS ref |
|---|---|---|---|
| H1 | High | Add compaction-awareness block | §4 context-awareness |
| H2 | High | Tell 4.7 to fan out subagents in one turn, not default to sequential | §1, §4 parallelism |
| H3 | High | Add "stay in scope / no over-engineering" guard to TDD loop | §4 over-engineering |
| M1 | Med | Drop `(REQUIRED)` intensifier on bookkeeping step | §3 |
| M2 | Med | Scope Self-Verification explicitly to every file/test in the step | §1 literalism |
| M3 | Med | Positive-frame the verification-command guidance | §2, §7 |
| M4 | Med | Promote worker-doc-edit rule to the parallelization preamble | §1, §4 |
| L1 | Low | Positive-frame "Do not endlessly explore" | §2, §7 |
| L2 | Low | `Think step by step` absent — healthy | §3 |
| L3 | Low | Split git permission matrix for readability | §2 |

### `/si-quick`
| # | Priority | Area | INSIGHTS ref |
|---|---|---|---|
| H1 | High | Add "stay in scope" guard to STEP 3 | §4 over-engineering |
| M1 | Med | Make file-scope explicit in STEP 3 ("every file listed") | §1, §4 literalism |
| M2 | Med | Positive-frame "Evidence requirement" | §2, §3, §7 |
| M3 | Med | Dial back `FAILING` caps + positive-frame TDD trailer | §2, §3, §7 |
| L1 | Low | Non-goals list is fine (negative framing defensible) | §2 (exception) |
| L2 | Low | Optional parallel-tool-call note | §4 |
| L3 | Low | `Skill tool → skill: "simplify"` hint is healthy | positive pattern |

No "invented" issues: items not flagged (e.g., XML structure absence) are genuinely fine for these skills because they have minimal mixed instructions/examples that would benefit from XML tagging. Role assignment is light but appropriate — `/si` is a procedure, not a persona.
