# Review: `blueprint` and `ph` (Opus 4.7 audit)

**Scope**: Two long-horizon / session-handoff skills. Both revolve around Opus 4.7's strength in long-horizon agentic coding (INSIGHTS.md §1 "Response length" + §4 "Context-awareness for long skills"). They are the primary vehicles the workflow uses to survive context compaction, so missing compaction-aware prompts or over-indexed intensifiers have outsized impact.

**Files reviewed**:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/blueprint/SKILL.md` (143 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/ph/SKILL.md` (174 lines)

**Overall verdict**: Both skills are *structurally* well-tuned for 4.7 — the cold-start-brief pattern in `blueprint` and the "Files to Read First" pattern in `ph` are exactly the investigate-before-answering / quote-ground discipline INSIGHTS §2 and §4 ask for. The gaps are concentrated in three areas: (1) neither skill explicitly tells 4.7 about context compaction even though that is the *entire reason they exist*, (2) both lean on `NOT` / `MUST` / `ALWAYS` / `critical` intensifiers in a few places where dialing back is cheap, (3) neither prompts for parallel tool calls during the git/test capture phase, which 4.7 under-parallelizes by default.

---

## 1. Skill: `blueprint`

### High priority

#### H1. Missing compaction-aware prompt in the skill that exists *because of* compaction
**Cross-reference**: INSIGHTS §4 "Context-awareness for long skills"; §1 "Interactive coding" (more post-turn reasoning → more tokens).

**Evidence**: The purpose section (`blueprint/SKILL.md:22-26`) states:

> "Large features can't be completed in a single Claude session. This skill decomposes a high-level objective into a sequenced plan where each step: 1. Has a **cold-start context brief** — everything a fresh agent needs to execute without reading prior session history"

The entire skill is a compaction-survival tool, but nowhere does it tell the executing agent *"context will be automatically compacted; save state before refresh; do not stop early due to token concerns."* When a blueprint plan grows to 6–8 steps in Phase 3, the model may truncate later step documents because it mis-estimates remaining context.

**Before** (`blueprint/SKILL.md:22-26`, Purpose section):
```
## Purpose

Large features can't be completed in a single Claude session. This skill decomposes a high-level objective into a sequenced plan where each step:
```

**After** (add a short paragraph at the end of Purpose or in a new "Context discipline" section before Pipeline):
```
## Purpose

Large features can't be completed in a single Claude session. This skill decomposes a high-level objective into a sequenced plan where each step:
...

### Context discipline while drafting

Context may be compacted mid-plan. If you sense the window tightening, write the plan to disk incrementally (one step at a time) rather than building the whole blueprint in memory. Do not stop early because of token concerns — produce every step. If you hit compaction, resume from the last written step.
```

**Why this matters for 4.7 specifically**: §1 notes 4.7 does more post-user-turn reasoning, which means it spends more tokens deliberating between writing each step. Without a compaction-aware nudge, a blueprint with 8 steps × ~60 lines each is exactly the length where 4.7 starts hedging.

---

#### H2. Step 4 "Review" uses negative, recall-lossy framing for 4.7's more literal reviewer
**Cross-reference**: INSIGHTS §1 "Code-review harnesses" (4.7 obeys severity filters literally); §4 "Coverage-then-filter split".

**Evidence** (`blueprint/SKILL.md:88-94`):

> "### Phase 4: Review (adversarial check)
> Before presenting the plan, self-review:
> 1. **Completeness**: Does executing all steps achieve the original objective?
> 2. **Independence**: Can each step truly be executed by a fresh agent with only its cold-start brief?
> 3. **Ordering**: Are dependencies correctly captured? No circular dependencies?
> 4. **Gaps**: Are there implicit steps (migrations, config changes, env setup) that should be explicit?
> 5. **Rollback**: If step N fails, does it break steps 1..N-1?"

These are good questions, but they're framed as a *filtered* checklist. 4.7 will literally answer "yes/no" per item and move on; it won't volunteer additional concerns it noticed. The skill should do a coverage pass ("list every risk/gap you can see") before the filter ("then categorize by severity").

**Before** (`blueprint/SKILL.md:88-94`):
```
### Phase 4: Review (adversarial check)
Before presenting the plan, self-review:
1. **Completeness**: Does executing all steps achieve the original objective?
2. **Independence**: ...
```

**After**:
```
### Phase 4: Review (adversarial check)

First, list every concern you noticed while drafting — missing migrations, implicit env setup, unclear step boundaries, weak acceptance criteria — including low-confidence ones. Then classify each into: Completeness / Independence / Ordering / Gaps / Rollback. Include the low-confidence items in the Risks table below with explicit "(low confidence)" tags; do not silently drop them.

After listing, verify against the checklist:
1. **Completeness**: ...
2. **Independence**: ...
3. **Ordering**: ...
4. **Gaps**: ...
5. **Rollback**: ...
```

---

### Medium priority

#### M1. "Cold-start briefs must be self-contained" intensifier + negation combined
**Cross-reference**: INSIGHTS §3 (negative framing + intensifiers); §2 #6 (positive framing beats negative).

**Evidence** (`blueprint/SKILL.md:138`):

> "- **Cold-start briefs must be self-contained** — a fresh agent should NOT need to read the full blueprint, only its step's brief"

Uses "must be" plus "NOT" negation. 4.7 is already literal; positive framing lands cleaner.

**Before** (`blueprint/SKILL.md:138`):
```
- **Cold-start briefs must be self-contained** — a fresh agent should NOT need to read the full blueprint, only its step's brief
```

**After**:
```
- **Cold-start briefs are self-contained** — a fresh agent reads only its step's brief and can begin work. If you find yourself about to reference "see Step 2", inline the information instead.
```

This also adds the *why* (INSIGHTS §2 #2: rationale > rules).

---

#### M2. "No implementation" as bare negation on an action-biased model
**Cross-reference**: INSIGHTS §3 ("Do not suggest, make the changes" — 4.7 is more action-biased, over-triggers on aggressive action framing); §4 (positive framing).

**Evidence** (`blueprint/SKILL.md:141`):

> "- **No implementation** — this skill produces a plan, not code. Use `/si` to execute steps."

This is fine in spirit, but 4.7 is slightly more action-biased on coding tasks (§1 "Instruction following" + `/setup` lineage note). When the user's objective contains verbs like "add" or "build", the model may still start editing. A positive reframe with the handoff target stated upfront is more robust.

**Before** (`blueprint/SKILL.md:141`):
```
- **No implementation** — this skill produces a plan, not code. Use `/si` to execute steps.
```

**After**:
```
- **Output is a plan document, not code edits.** The deliverable is the blueprint file; `/si` executes each step in a later session. If the user asks you to "also start on step 1", respond with the plan first and offer to hand off to `/si` afterward.
```

---

#### M3. "Don't over-plan" lacks a stopping condition
**Cross-reference**: INSIGHTS §3 ("Be thorough / exhaustive / comprehensive with no stopping condition"); §4 ("Minimize over-engineering").

**Evidence** (`blueprint/SKILL.md:140`):

> "- **Don't over-plan** — later steps can be intentionally vague; refine them as earlier steps complete"

The spirit is right, but "don't over-plan" is vague. 4.7 benefits from explicit stopping signals.

**Before** (`blueprint/SKILL.md:140`):
```
- **Don't over-plan** — later steps can be intentionally vague; refine them as earlier steps complete
```

**After**:
```
- **Plan to the level each step needs right now** — Steps 1–2 (starting soon) get full cold-start briefs. Steps 3+ get a one-paragraph objective and can be refined later. Stop adding detail once the next executor has enough to start.
```

---

### Low priority

#### L1. `Agent` tool in `allowed-tools` with no parallelization guidance
**Cross-reference**: INSIGHTS §1 ("Subagent spawning — more conservative by default"); §4 ("Parallel subagent prompting").

**Evidence** (`blueprint/SKILL.md:15`):

> "allowed-tools:
>   ...
>   - Agent"

The `Agent` tool is allowed but the skill body never invokes or even mentions subagents. If the original intent was to fan out research across codebase areas in Phase 1, 4.7 won't do that without being told explicitly. Either remove `Agent` from `allowed-tools` (it's unused) or add one line in Phase 1:

**Add to `blueprint/SKILL.md` around line 40 (Phase 1 Research)**:
```
When the objective spans multiple codebase areas (e.g., backend + mobile + infra), spawn one Agent subagent per area in the same turn rather than reading sequentially. Each subagent returns its findings; you synthesize.
```

---

#### L2. Emoji in dependency graph code fence may confuse downstream parsers
**Evidence** (`blueprint/SKILL.md:108-113`):

The ASCII `─` and `│` box-drawing chars are fine, but nesting a fenced code block inside another fenced code block (the outer `markdown` fence wrapping an inner unfenced graph) can cause markdown renderers to break. Not an Opus 4.7 issue — style nit only.

---

## 2. Skill: `ph`

### High priority

#### H1. Same compaction-blind spot, and `ph` is run *when compaction is imminent*
**Cross-reference**: INSIGHTS §4 "Context-awareness for long skills".

**Evidence** (`ph/SKILL.md:21`):

> "## PRIMARY OBJECTIVE
> Capture the current implementation state into a cold-start brief (`HANDOFF.md`) so a fresh Claude session can resume work without re-exploring the codebase. This is critical when context windows run long..."

The skill is literally invoked when context is running out, yet it has no instruction to save incrementally or to acknowledge compaction risk. If compaction fires mid-workflow (e.g., between STEP 3 and STEP 5), the HANDOFF.md may never be written.

**Before** (`ph/SKILL.md:21-24`):
```
## PRIMARY OBJECTIVE

Capture the current implementation state into a cold-start brief (`HANDOFF.md`) so a fresh Claude session can resume work without re-exploring the codebase. This is critical when context windows run long or when work spans multiple sessions.
```

**After** (add a sentence or short block):
```
## PRIMARY OBJECTIVE

Capture the current implementation state into a cold-start brief (`HANDOFF.md`) so a fresh Claude session can resume work without re-exploring the codebase. This is invoked when context windows run long or when work spans multiple sessions.

### Write-first discipline

Context may compact while this skill runs. Create `HANDOFF.md` with section headers immediately after STEP 1, then fill each section as you complete STEPS 2–5. A partially-written handoff is more useful than a fully-planned one that never gets saved. Do not stop early due to token concerns.
```

---

#### H2. Git/test capture phase is serialized — 4.7 under-parallelizes independent bash calls
**Cross-reference**: INSIGHTS §1 "Subagent spawning — more conservative"; §4 "Parallel tool-calling".

**Evidence** (`ph/SKILL.md:34-57`): STEP 2 and STEP 3 list several bash commands — `git branch --show-current`, `git log --oneline -5`, `git status --short`, `git diff --stat`, `git diff --cached --stat`, `git stash list`, `git diff --name-only $(git merge-base HEAD main)..HEAD`, `{{TEST_CMD}} 2>&1 | tail -20`. None of these depend on each other (except the last two, which can still run in parallel with all the git ones). 4.7 will issue them serially unless told to batch.

**Before** (`ph/SKILL.md:34-40` and `ph/SKILL.md:53-56`):
```
### STEP 2: Capture Git State

```bash
# Branch and last commit
git branch --show-current
git log --oneline -5
...
```

**After** (prepend a short parallelization note):
```
### STEP 2: Capture Git State

Run all of the following bash calls in the same turn — they are independent. Batch them into a single response with parallel tool calls. Do not issue them one at a time.

```bash
# Branch and last commit
git branch --show-current
git log --oneline -5
...
```

Apply the same note at STEP 3 step 3 (`git diff --name-only`) and step 4 (test command) — note that the test run can run in parallel with the git commands.

---

### Medium priority

#### M1. "Do not commit HANDOFF.md" + "Do not modify implementation code" — stacked negations
**Cross-reference**: INSIGHTS §2 #6 (positive framing); §3 (intensifiers).

**Evidence** (`ph/SKILL.md:168-172`):

> "## CONSTRAINTS
>
> - **Do not commit HANDOFF.md** — it's a transient artifact for the next session, not a permanent record
> - **Do not modify implementation code** — this skill only captures state, it doesn't fix things
> - **Be honest about state** — if tests are failing, say so. If a step is partially done, say so. The next session needs truth, not optimism."

The third bullet is positively framed and ideal. The first two are negations where positive works just as well. More importantly, "do not modify implementation code" on an action-biased 4.7 during a session where the user is likely *frustrated* about failing tests is a place 4.7 sometimes drifts — "just one quick fix before handoff" is a common failure mode. Reframe as a scope statement with rationale.

**Before** (`ph/SKILL.md:170-171`):
```
- **Do not commit HANDOFF.md** — it's a transient artifact for the next session, not a permanent record
- **Do not modify implementation code** — this skill only captures state, it doesn't fix things
```

**After**:
```
- **HANDOFF.md stays uncommitted** — it's a transient artifact consumed by the next session. Leave it in the working tree.
- **This skill only captures state** — If you notice a quick fix while reviewing, log it under "Next Actions" and let the next session decide. Fixing mid-handoff corrupts the snapshot.
```

The rationale ("corrupts the snapshot") is the *why* INSIGHTS §2 #2 recommends.

---

#### M2. "Be honest about state" is great — extend the pattern
**Cross-reference**: INSIGHTS §2 #2 (*why* > *rule*).

**Evidence** (`ph/SKILL.md:172`): already well-written, cite as the model for the rewrites above. No change needed here — this is the gold-standard phrasing in the file.

---

#### M3. STEP 3 reconciliation lacks an "untracked work" prompt for 4.7's literal mode
**Cross-reference**: INSIGHTS §1 "Instruction following" (4.7 won't silently generalize); §3 (literal-scope gaps).

**Evidence** (`ph/SKILL.md:61-66`):

> "2. **Reconcile with reality**: Compare task doc claims against actual code:
>    - Do files mentioned in checked steps exist?
>    - Do tests for checked steps pass?
>    - Are there files modified but not mentioned in any step?"

Good, but 4.7 will literally check those three things and stop. Session handoffs often involve work that doesn't map cleanly to any step — exploratory refactors, debug scaffolding, a `console.log` left in. State the generalization explicitly.

**Before** (`ph/SKILL.md:61-66`):
```
2. **Reconcile with reality**: Compare task doc claims against actual code:
   - Do files mentioned in checked steps exist?
   - Do tests for checked steps pass?
   - Are there files modified but not mentioned in any step?
```

**After**:
```
2. **Reconcile with reality**: Compare task doc claims against actual code. Check every file in the diff, not only the files named in steps:
   - Do files mentioned in checked steps exist?
   - Do tests for checked steps pass?
   - Are there files modified but not mentioned in any step? (exploratory changes, debug code, temp scaffolding — all go under "Gotchas")
   - Is there uncommitted work that belongs to no step at all? Document it.
```

---

### Low priority

#### L1. Rename ritual at the end is one-sentence — fine, but reword the imperative
**Evidence** (`ph/SKILL.md:162-163`):

> "After `/si` Continue mode successfully resumes:
> - Rename `HANDOFF.md` to `HANDOFF-[date].md` (archive, don't delete — useful for debugging session boundaries)"

This is informational (it describes `/si`'s behavior), not a command to the `ph`-running agent. Slight reword for clarity would help; not a 4.7 issue.

---

#### L2. `HOW /si CONTINUE MODE USES HANDOFF.md` section is informational and could move to the end or be fenced as context
**Cross-reference**: INSIGHTS §2 #3 (XML tags for structure).

**Evidence** (`ph/SKILL.md:152-163`): This section describes *another* skill's behavior — it's context for the writer, not instructions for the executing agent. Wrapping it in `<context>...</context>` or moving under a "## Integration" header (like `blueprint` does at line 132) would match the pattern and reduce the chance 4.7 treats it as an action item.

---

## 3. What both skills do well (do not change)

- **Cold-start brief pattern** (`blueprint/SKILL.md:52-66`, `ph/SKILL.md:94-102`): Exactly the investigate-before-answering discipline INSIGHTS §4 calls for. The "Files to Read First" section with *why* annotations is a textbook example of §2 #2 (rationale > rules).
- **Explicit scope / out-of-scope fields** (`blueprint/SKILL.md:69-71`): Matches §4 "State scope explicitly" recommendation.
- **Positive framing in `ph/SKILL.md:172`** ("Be honest about state — if tests are failing, say so") — exemplary phrasing, should be the template for the other bullets.
- **`blueprint` Phase 1-4 structure**: Research → Design → Draft → Review is the coverage-first, filter-later pattern INSIGHTS §4 recommends; only Phase 4's internal framing needs a tweak (H2 above).
- **`ph` STEP 1 disambiguation** (`ph/SKILL.md:30-32`): Resolves task directory from `$ARGUMENTS`, branch, or user question — good literal-scope discipline.
- **Neither skill uses** `CRITICAL:` / `ALWAYS` / `NEVER` in caps, hard response-length caps, tool-use over-nudges, or prefill patterns. On the five highest-risk anti-patterns from INSIGHTS §3, both skills score clean.

---

## 4. Summary table

| Skill | ID | Priority | Issue | Fix locus |
|---|---|---|---|---|
| blueprint | H1 | High | Missing compaction-aware prompt | Add "Context discipline" block after Purpose (line ~26) |
| blueprint | H2 | High | Phase 4 review is filter-first, risks recall loss on 4.7 | Prepend coverage pass (lines 88–94) |
| blueprint | M1 | Medium | "must NOT" double negation in cold-start-brief constraint | Rewrite line 138 positively |
| blueprint | M2 | Medium | "No implementation" bare negation on action-biased 4.7 | Rewrite line 141 with handoff framing |
| blueprint | M3 | Medium | "Don't over-plan" lacks stopping condition | Rewrite line 140 with concrete cutoff |
| blueprint | L1 | Low | `Agent` in `allowed-tools` but no parallel-subagent instruction | Add one line at Phase 1 (or drop Agent) |
| blueprint | L2 | Low | Nested fenced code blocks in dependency-graph example | Use indented code block instead |
| ph | H1 | High | Same compaction blindness in a skill invoked *because of* compaction | Add write-first block at line 21 |
| ph | H2 | High | Serial bash calls in STEP 2/3 | Add parallelization note before the bash block (line ~34) |
| ph | M1 | Medium | Stacked "Do not …" negations in CONSTRAINTS | Rewrite lines 170–171 positively with rationale |
| ph | M3 | Medium | Reconciliation step risks literal interpretation | Add "check every file in diff" generalization (lines 61–66) |

Total: 2 skills, 11 findings (4 High, 5 Medium, 2 Low). Both skills are fundamentally well-aligned with 4.7 best practices; the fixes are editorial tightening, not structural rewrites.
