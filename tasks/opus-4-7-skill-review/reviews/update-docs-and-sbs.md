# Opus 4.7 Audit — `update-docs` and `sbs`

Reviewed against `tasks/opus-4-7-skill-review/INSIGHTS.md`. Line numbers cite the skill files as read on 2026-04-17.

Files audited:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/update-docs/SKILL.md` (95 lines, single file, no subdirectory assets)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/sbs/SKILL.md` (210 lines, single file, no subdirectory assets)

---

## Skill 1 — `update-docs` (`udoc`)

Short, orchestration-only skill: it resolves a task path, calls two subagents (`docs-updater`, `changelog-generator`) sequentially, then offers a commit. Overall well-scoped and mostly clean — but there are two concrete 4.7 issues to address and a couple of smaller polish items.

### High priority

#### H-1. Sequential subagent chain leaves parallelization unstated (INSIGHTS §1 "Subagent spawning", §4 "Parallel subagent prompting")

The two agent calls in STEP 2 and STEP 3 are described as strictly sequential:

`.claude/skills/update-docs/SKILL.md:34–51`
```
### STEP 2: Update Documentation (docs-updater agent)

Call **docs-updater** agent:
...
Capture the summary of documentation changes.

### STEP 3: Generate Changelog (changelog-generator agent)

Call **changelog-generator** agent:
Prompt: "Generate a changelog entry based on the task document at [TASK_DOCUMENT_PATH] and documentation updates: [DOCS_UPDATES_SUMMARY] ..."
```

STEP 3 only depends on STEP 2's output because the prompt inlines `[DOCS_UPDATES_SUMMARY]`. The changelog generator can read the same task document directly — the coupling is an artefact of the prompt, not a real dependency. On 4.7 (which defaults to conservative, serial subagent use per INSIGHTS §1), this guarantees two sequential turns where one parallel fan-out would suffice.

**Before** (lines 34–51): two sequential steps, changelog depends on captured summary.

**After** — either:
(a) decouple and parallelize, adding an explicit "spawn in the same turn" instruction:

```
### STEP 2: Update Docs + Generate Changelog (parallel subagents)

Spawn both subagents in the same turn — they operate on the same task
document and do not depend on each other's output:

- docs-updater — "Review [TASK_DOCUMENT_PATH] and update all relevant
  documentation files. Return a summary of what was updated."
- changelog-generator — "Generate a changelog entry from [TASK_DOCUMENT_PATH]
  covering the main feature implementation. The docs-updater runs in
  parallel; its updates will be included in the same commit."

Do not default to sequential. When calls have no dependencies, batch them
in one turn.
```

(b) If you want to keep them sequential for editorial reasons (changelog references what docs changed), say so explicitly — the current text gives 4.7 no rationale.

Priority: **High** because this is the exact pattern INSIGHTS §4 flags as the #1 parallel-fan-out miss on 4.7.

#### H-2. Commit path in STEP 4 misses `CHANGELOG` locations (literal-scope gap, INSIGHTS §3 "more literal; will NOT silently generalize")

`.claude/skills/update-docs/SKILL.md:60–68`
```
   ```bash
   git add docs/
   git commit -m "docs: update documentation and changelog
   ...
   ```
```

STEP 5 describes the changelog path as `docs/changelogs/YYYY-MM-DD/changelog.md` (line 78), so `git add docs/` happens to cover it — but the pattern is fragile: any updated doc outside `docs/` (e.g. top-level `README.md`, `CLAUDE.md`, product docs under `product-docs/` per the project CLAUDE.md, or `.claude/` memory files) will be silently dropped. On 4.7, the model will follow the literal `git add docs/` and not generalize.

**Before** (line 61): `git add docs/`

**After**:
```
# Stage exactly the files the two subagents reported touching.
# Do not use `git add -A` (may pull in secrets) and do not assume
# everything lives under docs/ — changelog-generator writes to
# docs/changelogs/, but docs-updater may touch README.md, product-docs/,
# or other locations.

git add <files listed in docs-updater summary> \
        docs/changelogs/YYYY-MM-DD/changelog.md
```

Priority: **High** — silent data loss risk on commits.

### Medium priority

#### M-1. Intensifier hygiene — one stray `NEVER`-like construction is actually fine, but the section header style is terse to the point of losing *why* (INSIGHTS §2.2 "Explain the why")

The skill currently has no `CRITICAL` / `MUST` / `ALWAYS` / `NEVER` intensifiers — that's good. But several steps state rules without rationale, which costs nothing to add and helps 4.7 calibrate:

`.claude/skills/update-docs/SKILL.md:29`
```
2. If not provided — **Ask**: "Which task to update docs for? ..."
```

`.claude/skills/update-docs/SKILL.md:58`
```
2. **Ask**: "Commit these documentation and changelog updates?"
```

**After** (add *why* inline):

```
2. If not provided — Ask: "Which task to update docs for? ..."
   (Don't guess — picking the wrong task would generate a misleading
   changelog that may end up in the repo history.)
...
2. Ask: "Commit these documentation and changelog updates?"
   (This skill may run before a PR is opened; the user may want to
   squash docs into the feature commit rather than create a separate
   docs commit.)
```

Priority: **Medium**.

#### M-2. "Optional" in a step header invites 4.7 to skip unilaterally (literal-scope)

`.claude/skills/update-docs/SKILL.md:53`
```
### STEP 4: Commit (Optional)
```

"Optional" in a step title reads to 4.7 as "skip this unless asked". But the body of STEP 4 does the right thing: it asks the user. The title undermines the body.

**After**:
```
### STEP 4: Offer Commit (user-gated)
```

Priority: **Medium**.

### Low priority

#### L-1. SUCCESS CRITERIA checklist doesn't cover "changelog is in the *correct* task's dated dir"

`.claude/skills/update-docs/SKILL.md:88–94`
```
## SUCCESS CRITERIA
- [ ] Task document found and analyzed
- [ ] Documentation updated for affected files
- [ ] Changelog entry created in correct date directory
...
```

"Correct date directory" is ambiguous: the date of task completion, task creation, or today? Spell it out. Priority: **Low**.

#### L-2. Announcement line could explain *why* it's there

`.claude/skills/update-docs/SKILL.md:13`
```
> **Announcement**: Begin with: "I'm using the **udoc** skill for documentation update and changelog."
```

Fine as-is; just note that user-facing announcements are usually "why = the user asked us to work across multiple files, we're using a skill to keep it structured". One-line rationale would make this survive future edits. Priority: **Low**.

### Summary for `update-docs`

Two real issues worth fixing: (H-1) parallelize the two subagent calls or state the sequential dependency, and (H-2) stop hard-coding `git add docs/` since docs-updater can touch other paths. Everything else is polish. The skill avoids all the "intensifier inflation" pitfalls that INSIGHTS §3 warns about.

---

## Skill 2 — `sbs` (step-by-step teaching)

Longer skill (210 lines). Interactive teaching is output-style-sensitive, so small prompting defaults have outsized impact. Overall this is a thoughtfully-structured skill — most of the findings below are small dial-backs rather than structural rewrites.

### High priority

#### H-1. Hard stops on proceeding — `never proceed without explicit confirmation` is stated two different ways, risking 4.7 over-literalness on in-flow questions (INSIGHTS §1 "Instruction following — more literal")

`.claude/skills/sbs/SKILL.md:107`
```
- **Confirm Understanding:** Wait for explicit user confirmation before proceeding
```

`.claude/skills/sbs/SKILL.md:143`
```
3. **Pacing:** Use AskUserQuestion after each step — NEVER proceed without explicit confirmation
```

Two problems:
1. Line 143 uses `NEVER` as an intensifier. Per INSIGHTS §3, these now cause over-triggering on 4.7 — the model may refuse to batch adjacent micro-steps that clearly belong together (e.g. "run this command and read its output") because each sub-action "needs confirmation".
2. Lines 107 and 143 say the same thing in two voices, which fragments the rule. 4.7 may follow the stronger one literally and treat clarifying sub-questions ("What's the error?") as violations.

**Before** (line 143):
```
3. **Pacing:** Use AskUserQuestion after each step — NEVER proceed without explicit confirmation
```

**After**:
```
3. Pacing: Ask the user to confirm at each numbered step before moving to
   the next step. Reason: without a pause, the user can't execute the
   action themselves, which defeats the "learn by doing" goal.
   Mid-step clarifying questions (asking what error they saw, which option
   they picked) are fine and don't count as "proceeding".
```

Priority: **High** — teaching skills are where over-strict pacing is most visible to the user.

#### H-2. Teaching skills need positive framing of length defaults; `1-2 sentences` caps in the step template fight 4.7's adaptive length (INSIGHTS §1 "Response length", §3 "Hard-coded response-length caps")

`.claude/skills/sbs/SKILL.md:113–121` (Guided Execution step template)
```
**What we're doing:** [1-2 sentences on purpose]
**Why this matters:** [How this fits the bigger picture]
**Technical concept:** [Simple explanation of new concepts — skip if no new concept]
**Your action:** [Specific instruction with code blocks]
**What to expect:** [Expected outcome after completion]
```

Two things to unpack:
- `[1-2 sentences on purpose]` is a hard length cap. On a Deep Mastery session, 1-2 sentences on "what we're doing" is often wrong — the user chose "I want to be able to teach this to someone else". On Quick Walkthrough it's overkill. This cap fights the depth matrix at lines 124–132.
- The rest of the fields have no length guidance at all, which is fine for 4.7's adaptive length — but then the inconsistency makes it look like only `What we're doing` is capped, which reads as a bug.

**Before** (line 114):
```
**What we're doing:** [1-2 sentences on purpose]
```

**After**:
```
**What we're doing:** Purpose, calibrated to session depth
(Quick: one sentence. Full: 2–3 sentences with a bit of context.
Deep: include what this replaces or competes with.)
```

Priority: **High** — this is the hottest path in the skill (every step uses this template) and the only place 4.7 will see a length cap.

#### H-3. Socratic-mode "Full answer" gating is load-bearing but under-specified (INSIGHTS §1 "Instruction following — more literal", §3 "Literal-scope gaps")

`.claude/skills/sbs/SKILL.md:135–143`
```
### Step Structure — Socratic Mode
...
**Full answer:** [Reveal only after user attempts — use AskUserQuestion to gate this]
```

"After user attempts" is a judgement call; 4.7's more literal bias means it will either (a) reveal on the first user message that isn't silence, or (b) gate behind an extra question even when the user said "I don't know, just tell me". Spell out what counts as "an attempt".

**After**:
```
**Full answer:** Reveal only after the user has either (a) proposed an
answer (right or wrong), (b) explicitly asked for the answer ("just tell
me", "I give up"), or (c) answered a clarifying hint. Do not reveal after
a pure clarification question ("what do you mean by X?") — respond to
the clarification first.
```

Priority: **High** for Socratic-mode users (the whole mode falls apart if gating is wrong).

### Medium priority

#### M-1. Intensifier hygiene — several capped words that no longer help on 4.7 (INSIGHTS §3)

Beyond the `NEVER` covered in H-1, the skill has other intensifier inflation:

`.claude/skills/sbs/SKILL.md:104`
```
- **One Step at a Time:** Present ONLY the current step, never jump ahead
```

`.claude/skills/sbs/SKILL.md:105`
```
- **Explain Before Action:** Always explain WHY before showing HOW — understanding motivation makes the steps stick
```

`.claude/skills/sbs/SKILL.md:108`
```
- **Ground in Reality:** Use real project code and files whenever possible
```

The `ONLY`, `never`, `Always`, `WHY`, `HOW` capitalisations are style, not semantics. 4.7 is already responsive. Dial them down, especially because line 105's combination of `Always` + `WHY` + `HOW` reads as three overlapping emphasis marks for one rule.

**Before** (lines 104–108):
```
- **One Step at a Time:** Present ONLY the current step, never jump ahead
- **Explain Before Action:** Always explain WHY before showing HOW — understanding motivation makes the steps stick
- **Confirm Understanding:** Wait for explicit user confirmation before proceeding
- **Learn by Doing:** User executes each action themselves with your guidance
- **Ground in Reality:** Use real project code and files whenever possible
```

**After**:
```
- One step at a time. Present the current step only — jumping ahead hides
  the action the user is meant to execute themselves.
- Explain before action. The rationale makes the mechanics stick; a
  recipe without the why doesn't transfer.
- Confirm understanding. Ask at the end of each step before moving on.
- Learn by doing. The user runs each action — you guide, not execute.
- Ground in reality. Prefer real code from this project to contrived
  examples; the user will recognise it again later.
```

Priority: **Medium** — mostly a tone-calibration fix; doesn't change behaviour but removes the "shouting" noise 4.7 is now prone to over-weight.

#### M-2. Negative framing on the scope description (INSIGHTS §2.6 "Positive framing beats negative")

`.claude/skills/sbs/SKILL.md:19–20`
```
- **Use for:** Teaching any task interactively — "teach me", "walk me through", ...
- **NOT for:** Open brainstorming (use `/brainstorm`), task documentation (use `/ct`), debugging (use `/dbg`), quick one-off questions (just answer directly)
```

And the frontmatter description lines 10–12:
```
  brainstorming (use /brainstorm), NOT for quick one-off explanations (just
  answer directly), NOT for debugging (use /dbg).
```

The `NOT for:` list is genuinely useful (it disambiguates from sibling skills) — keep it. But three `NOT for` items in a row read as negative-framing stacking to the router. A positive reformulation helps the router decide to route *in* rather than *not out*.

**Before** (line 20):
```
- **NOT for:** Open brainstorming (use `/brainstorm`), task documentation (use `/ct`), debugging (use `/dbg`), quick one-off questions (just answer directly)
```

**After**:
```
- Route elsewhere when:
  - The user wants to explore possibilities without a concrete topic → `/brainstorm`
  - The user wants a task doc produced, not learning → `/ct`
  - The user has a failing thing to fix, not a concept to learn → `/dbg`
  - The question is one-off and factual → answer directly, don't start a session
```

Priority: **Medium**.

#### M-3. "Never stop early" / context-compaction awareness is absent on a long interactive skill (INSIGHTS §4 "Context-awareness for long skills")

`sbs` sessions are explicitly long — Deep Mastery sessions run 30+ min (line 47), span many turns, and accumulate step context. INSIGHTS §4 recommends the compaction-aware prompt for long-running skills.

There is currently no compaction-safe instruction anywhere in the file. On a long Deep Mastery session, 4.7 may truncate or "wrap up" prematurely after compaction.

**After** (add near `PROGRESSION TRACKING`, lines 149–160):
```
### Context continuity
Long sessions (Full Tutorial, Deep Mastery) can span many turns. If
context is compacted mid-session, do not wrap the session up early —
the learning plan from SESSION SETUP is the source of truth. Before
any summarisation pass, save current step number, chosen depth, and
pending bonus-learning notes into the resume file under docs/learning/
so the session can pick up from the correct step.
```

Priority: **Medium** — risk materialises only on longest sessions, but those are exactly the "teach it to someone else" users.

#### M-4. Research step over-nudges tool use (INSIGHTS §3 "Default to using [tool]")

`.claude/skills/sbs/SKILL.md:80–88`
```
## RESEARCH (When Needed)

If the topic involves a library, API, or pattern that needs verification:
- Use `get_code_context_exa` for code-specific context (API docs, library usage)
- Use `web_search_exa` for current best practices and patterns
- Cite sources when sharing external knowledge — accuracy matters in teaching

This ensures the teaching is current and correct. Confidently-stated wrong information is worse than saying "let me look that up."
```

The framing already says "When Needed" — good. But "Use `get_code_context_exa`" / "Use `web_search_exa`" reads as the "Default to using [tool]" anti-pattern from INSIGHTS §3. The model on 4.7 will call these more aggressively than needed for, say, a Quick Walkthrough on a well-known pattern.

**Before** (lines 83–85):
```
- Use `get_code_context_exa` for code-specific context (API docs, library usage)
- Use `web_search_exa` for current best practices and patterns
```

**After**:
```
- Reach for `get_code_context_exa` when you are about to cite a specific
  API shape or library behaviour that you can't verify from the
  codebase. Skip it for concepts the user already knows.
- Reach for `web_search_exa` when current practice may have shifted
  (post-2024 library guidance, framework defaults). Skip it for
  stable, well-documented topics.
```

Priority: **Medium**.

### Low priority

#### L-1. "Always include" in the depth matrix fights adaptive length

`.claude/skills/sbs/SKILL.md:127` (depth matrix row for "Technical concept"):
```
| Technical concept | Skip if obvious | Always include | Include trade-offs |
```

`Always include` is benign here because it's inside a depth column, but consider softening to `Include when a new concept appears` to stay consistent with the dial-back in M-1. Priority: **Low**.

#### L-2. `TodoWrite` usage is stated once without rationale

`.claude/skills/sbs/SKILL.md:152`
```
- Use TodoWrite to track steps — gives the user a visual progress indicator
```

Already has a *why* — this is good. Keep as-is; noting it as an example of the right pattern.

#### L-3. "Argument validation" branch doesn't handle ambiguous input

`.claude/skills/sbs/SKILL.md:28–33`
```
## ARGUMENT VALIDATION

**If no `[topic]` argument provided:**
1. Use `AskUserQuestion`: "What would you like to learn about?"
```

What if the argument is provided but vague ("teach me stuff")? The branch is `no argument` vs `argument present`; the in-between case of "ambiguous argument" is a literal-scope gap (INSIGHTS §3). Low priority because `AskUserQuestion` in SESSION SETUP will surface the mismatch anyway.

### Summary for `sbs`

The skill is mostly well-tuned and already uses several of the positive patterns INSIGHTS §4 recommends (XML-like step templates, role calibration via experience-level question, rationale-with-rule in many places). The notable fixes:

- H-1 (relax `NEVER proceed` so clarifying sub-questions don't trigger refusals)
- H-2 (drop the `1-2 sentences` cap that fights adaptive length)
- H-3 (spell out Socratic gating so 4.7 doesn't under- or over-gate the reveal)
- M-3 (add compaction-aware instruction for Deep Mastery sessions)

Everything else is intensifier dial-back and framing polish.

---

## Cross-skill observations

- Neither skill has prefill/assistant-turn issues (INSIGHTS §3 "Pre-filled assistant turns") — good.
- Neither skill uses `CRITICAL:` or `You MUST` — the worst intensifier patterns are absent.
- `update-docs` is the more mechanical skill and has the sharper parallelization miss.
- `sbs` is the output-style-sensitive skill, and its issues cluster in step-template length caps plus `NEVER`-style pacing.
- Both skills would benefit from a single "context will be compacted; save state before stopping" sentence — currently missing in both, but load-bearing only in `sbs` (Deep Mastery sessions).
