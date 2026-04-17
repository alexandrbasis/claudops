# Opus 4.7 Skill Audit — `/nf` and `/product`

Scope: `.claude/skills/nf/SKILL.md` and `.claude/skills/product/SKILL.md`.
Lens: `tasks/opus-4-7-skill-review/INSIGHTS.md` (§1 behavior deltas, §3 anti-patterns, §4 positive patterns, §5 checklist).

Both skills are interactive-interview workflows with the same backbone: template-as-contract, design-exploration, optional research, deep-dive, grill-me, write, cross-AI validation. Findings below apply to each skill individually.

---

## Skill: `nf`

File: `.claude/skills/nf/SKILL.md` (212 lines)

### High priority

#### H1. Hard intensifiers used as emphasis (INSIGHTS §3 — intensifier hygiene; §5 checklist item 1)
`.claude/skills/nf/SKILL.md:25-26`
```
- **Use `AskUserQuestion` tool for ALL clarifications**
- **Never assume behavior**: if any behavior is unclear/ambiguous (UX flow, edge cases, error handling, states), ask the user to define expected behavior
```
Also `.claude/skills/nf/SKILL.md:171` (under Cross-AI Validation):
```
**Important:** Do not guess or improvise the underlying CLI commands. The skill initialization step is mandatory for each validator.
```
And `.claude/skills/nf/SKILL.md:179`:
```
**Only after all three skills are invoked**, launch the three validation runs in parallel. Do not wait for Codex to finish before starting Gemini...
```

`ALL` / `Never assume` / `mandatory` / `Do not wait` are emphasis-style intensifiers. INSIGHTS §3 warns that on 4.7 these now cause over-triggering (e.g., `AskUserQuestion` invoked for trivial items a user already stated, or refusal to proceed when a validator CLI silently succeeds). The rules themselves are load-bearing — it's the tone that needs to drop to normal voice and add *why*.

Before → after:
```
# before
- **Use `AskUserQuestion` tool for ALL clarifications**
- **Never assume behavior**: if any behavior is unclear/ambiguous ...

# after
- Use `AskUserQuestion` for any clarification that the user hasn't already answered — structured options reduce ambiguity and keep the interview auditable.
- If behavior is unclear (UX flow, edge cases, error handling, states), ask the user to define it rather than inferring. Downstream `/vp` and `/ct` trust this document as the source of truth, so silent assumptions compound.
```

And for line 179:
```
# before
**Only after all three skills are invoked**, launch the three validation runs in parallel. Do not wait for Codex to finish before starting Gemini, and do not wait for Gemini to finish before starting Cursor.

# after
Once all three skills are initialized, launch the three validation runs in the same turn (parallel tool calls). Running them sequentially adds ~2× latency with no quality benefit, since the reviews are independent.
```
Cross-ref: INSIGHTS §4 "Parallel tool-calling" positive pattern.

---

#### H2. Subagent fan-out is not explicitly parallel (INSIGHTS §1 "Subagent spawning"; §4 parallel subagent prompting)
`.claude/skills/nf/SKILL.md:173-179`
```
**Invoke skills sequentially first:**
1. Invoke `/codex-cli`
2. Invoke `/gemini-cli`
3. Invoke `/cursor-cli`

**Only after all three skills are invoked**, launch the three validation runs in parallel. Do not wait for Codex to finish before starting Gemini, and do not wait for Gemini to finish before starting Cursor. The `invoke` steps happen one-by-one; the review runs happen concurrently after initialization.
```

INSIGHTS §1 notes that 4.7 is "more conservative by default" about subagent spawning and must be *explicitly* told to fan out in the same turn. The current phrasing says "in parallel" but never says "in the same turn / one tool-call block" — which is the concrete thing 4.7 needs. Also, the sequential-skill-invocation-then-parallel-run is a non-obvious two-phase protocol; a skill that also trips `AskUserQuestion` checkpoints mid-turn can lose the thread.

Before → after:
```
# before
**Invoke skills sequentially first:**
1. Invoke `/codex-cli`
2. Invoke `/gemini-cli`
3. Invoke `/cursor-cli`

**Only after all three skills are invoked**, launch the three validation runs in parallel. Do not wait for Codex to finish before starting Gemini, and do not wait for Gemini to finish before starting Cursor.

# after
Two phases — initialization (sequential), then review (parallel):

Phase 1 — Initialization. Invoke `/codex-cli`, `/gemini-cli`, `/cursor-cli` one at a time to load each validator's CLI contract. The skills need to run in turn because they modify runtime state.

Phase 2 — Review. In a single assistant turn, dispatch all three validator runs as parallel tool calls (one turn, three tool invocations). Reviews are independent, so sequential execution only adds latency. If one validator is unavailable, dispatch the other two anyway.
```

---

#### H3. Grill/completion loop has no stopping condition (INSIGHTS §3 — "be thorough/exhaustive/comprehensive")
`.claude/skills/nf/SKILL.md:132` and `.claude/skills/nf/SKILL.md:154-160`
```
Continue deep-dive until the user confirms the document is clear, scoped, and ready to stand on its own.
```
```
Before writing the final discovery document, confirm that a new reader can answer without extra verbal context:
- What is this feature?
- Why does it exist?
- How does it work?
- What is in scope?
- What is out of scope?
- What requirements or constraints materially shape it?

If any of those remain unclear, continue discovery instead of finalizing the document.
```

Paired with the "Grill" step at line 137 and "Revisit design" checkpoint at 151, this is an open-ended loop with no cap. On 4.7 this reads as "keep grilling until exhaustion" and the skill can ping-pong between `/grill-me` and interview rounds. INSIGHTS §3 explicitly flags "be thorough/exhaustive/comprehensive with no stopping condition" as a 4.7 anti-pattern.

Before → after:
```
# before
Continue deep-dive until the user confirms the document is clear, scoped, and ready to stand on its own.

# after
Stop the deep-dive when every template section has an answer the user has confirmed once — don't keep re-confirming. If a section would require speculation, ask once, accept "skip / TBD" as a valid answer, and note it in the draft as `[NEEDS CLARIFICATION: ...]`. The document does not have to be perfect before writing — the grill round catches real gaps.
```

And for the completion check:
```
# after
One-pass completion check (not a loop): verify the six questions below have at least a one-sentence answer in the draft. If two or fewer are weak, flag them inline and proceed to writing — `/grill-me` and cross-AI validation will catch real blockers. If more than two are missing, run a single additional round of questions, then proceed regardless.
```

---

### Medium priority

#### M1. Tool-use nudge on research is broad (INSIGHTS §3 — "Default to using [tool]")
`.claude/skills/nf/SKILL.md:76-80`
```
When you need current information, best practices, or technical research:

- **Quick lookups**: Use Exa MCP tools directly
- **In-depth research**: Spawn `comprehensive-researcher` only when the answer materially affects the chosen direction, scope boundaries, key requirements, or constraints.
```

The "in-depth" clause is actually well-scoped already (good — cross-ref §4). The "Quick lookups: Use Exa MCP tools directly" line is weaker: on 4.7, "Use Exa directly" reads as a default instruction and can over-trigger Exa calls for details that were already settled in discovery or design-exploration. Tighten by making it conditional on genuine information gap.

Before → after:
```
# before
- **Quick lookups**: Use Exa MCP tools directly

# after
- **Quick lookups**: Use Exa MCP tools when the user asserts a factual claim about an external product, spec, or standard that you can't verify from the codebase or prior turns. Skip Exa if the question is about internal codebase behavior (design-exploration covers that) or about subjective product preference.
```

---

#### M2. Literal-scope gap at "Post-Action & Cross-Surface Behavior" (INSIGHTS §1 "Instruction following — more literal" and §5 item 6)
`.claude/skills/nf/SKILL.md:121-130`
```
**Post-Action & Cross-Surface Behavior** (for any create/update/delete workflow):
- After this action succeeds, what exactly should the user see?
...
- For every backend validation rule, what's the corresponding UI affordance (error message, disabled option, hint, highlighted field)?
- If the user picks an invalid option, do they see the error before or after submission?
- Are there options that should be hidden or visually distinguished based on context?
```

These are great questions but the header says *"for any create/update/delete workflow"*. On 4.7 (more literal), a feature that is read-only *or* a modal selector with no server side effect will simply skip this whole block — even though two of the questions (validation affordances, hidden options based on context) apply to selector/filter features too. Split the applicability.

Before → after:
```
# before
**Post-Action & Cross-Surface Behavior** (for any create/update/delete workflow):

# after
**Post-Action & Cross-Surface Behavior** — use the subset that applies:

*Any workflow with a submit / confirm action (create, update, delete, toggle, selection-apply):*
- After success, what exactly should the user see?
- Which screen is the canonical place to confirm the result?
- If the current screen doesn't show the result, what success feedback appears?

*Any feature that renders lists, search results, dashboards, or categorized views:*
- Where else does this entity appear? What metadata governs how it appears there?

*Any feature with user input or selection (including read-only filters):*
- For every validation rule, what's the UI affordance (error, disabled option, hint, highlighted field)?
- For invalid input, does feedback appear before or after submission?
- Are there options that should be hidden or visually distinguished based on context?
```
Cross-ref: INSIGHTS §4 "State scope explicitly".

---

#### M3. Announcement and "why" missing for template re-read (INSIGHTS §2 rule 2 — rationale > rules)
`.claude/skills/nf/SKILL.md:163-166`
```
1. **Re-read template if needed**: Review `.claude/docs/templates/discovery-template.md` to confirm the expected structure and clarity level
2. **Create task directory**: `tasks/task-YYYY-MM-DD-[feature-name]/`
3. **Write discovery document** by filling the template with the decisions, flows, scope boundaries, requirements, and constraints resolved during discovery
```

"If needed" is vague — 4.7 will probably skip it. The *why* is that the template may have evolved since Step 0 or the interview may have drifted from the structure. State that.

Before → after:
```
# before
1. **Re-read template if needed**: Review `.claude/docs/templates/discovery-template.md` to confirm the expected structure and clarity level

# after
1. Re-read `.claude/docs/templates/discovery-template.md` before writing. Long interviews drift from the template shape, and re-reading takes <5s while preventing section order/heading mismatches that downstream `/vp` and `/ct` parsers depend on.
```

---

#### M4. No compaction / context-awareness guard (INSIGHTS §4 "Context-awareness for long skills")
This skill runs design-exploration + optional comprehensive-researcher + multi-round interview + grill-me + cross-AI validation — easily 50k+ tokens on a real feature. There is no instruction to handle compaction.

Before → after (add a new section near the top of Guidelines or right before Step 5):
```
# after
**Context management.** This workflow can run long (design-exploration + research + interview + grill + validators). If you notice a compaction event or context refresh:
- Re-read any already-created task files in the task directory before continuing.
- Re-open the discovery template to reconfirm output shape.
- Do not restart discovery from scratch — resume from the last unanswered template section.
Do not stop early due to token-budget worries — the parent harness handles compaction.
```
Cross-ref: INSIGHTS §4 positive pattern, verbatim model.

---

### Low priority

#### L1. Positive framing for the "grill" instruction (INSIGHTS §2 rule 6)
`.claude/skills/nf/SKILL.md:28`
```
- Actively challenge assumptions; do not be a yes-boy. Grill.
```
Mix of positive ("Actively challenge assumptions") and negative ("do not be a yes-boy"). The negative frame is fine but the terse imperative "Grill." reads as intensity rather than direction. Not load-bearing.

Before → after:
```
# before
- Actively challenge assumptions; do not be a yes-boy. Grill.

# after
- Challenge assumptions actively. When the user's answer sounds confident but under-specified, name the gap ("You said X — does that cover case Y?") rather than accepting it at face value.
```

---

#### L2. Announcement line (INSIGHTS §1 "Response length")
`.claude/skills/nf/SKILL.md:17`
```
> **Announcement**: Begin with: "I'm using the **nf** skill for feature discovery."
```
Mandatory preamble that conflicts with 4.7's calibrated-length default. Not high-harm but it trains a small preamble habit. Consider keeping for UX reasons only — flag for the maintainer's call.

---

#### L3. Cross-AI validation FOCUS wording could leak "only important" (INSIGHTS §3 — filter leakage)
`.claude/skills/nf/SKILL.md:184`
```
- **FOCUS**: Discovery document review as senior product analyst — entry-point readability, completeness, consistency, flow clarity, scope boundaries, feasibility, and hidden ambiguities that would cause confusion in `/vp` or `/ct`
```
This is actually *coverage*-oriented (list of concerns, no severity filter) — which is good. No change needed; flagging only so the maintainer doesn't accidentally reword it later.

---

### Items already well-tuned in `nf`

- **Template-as-contract** framing (lines 45-51) is strong — it tells 4.7 *why* to re-read rather than prescribing a ritual.
- **Conditional section guards** ("only if it adds clarity", "only if multiple viable approaches exist", lines 102, 108) are the *positive* version of what §3 warns against.
- **`comprehensive-researcher` invocation is scoped** to "materially affects the chosen direction, scope boundaries, key requirements, or constraints" (line 74) — textbook §4 pattern for gating an in-depth tool.
- **Handoff section** at lines 196-212 explicitly lists next steps with command names — good for 4.7's more-literal instruction following.

---

## Skill: `product`

File: `.claude/skills/product/SKILL.md` (241 lines)

### High priority

#### H1. `MANDATORY` intensifier on research (INSIGHTS §3 — intensifier hygiene; §5 checklist item 1)
`.claude/skills/product/SKILL.md:28` and `.claude/skills/product/SKILL.md:64-66`
```
- Research is MANDATORY — product decisions without research are assumptions
```
```
### Step 2: Research (MANDATORY)

Research is not optional. Both JTBD and PRD templates have mandatory Research Findings sections that must be filled with cited sources.
```

Three uses of MANDATORY / "not optional" in close proximity. The rationale ("decisions without research are assumptions") is good — keep it — but drop the all-caps + triple repetition. On 4.7 this over-triggers: the skill will spawn `comprehensive-researcher` for product areas where the user already has prior art, or it will refuse to proceed when the codebase alone has enough signal. The rule is genuinely load-bearing; the *tone* is the issue.

Before → after:
```
# before
- Research is MANDATORY — product decisions without research are assumptions
...
### Step 2: Research (MANDATORY)

Research is not optional. Both JTBD and PRD templates have mandatory Research Findings sections that must be filled with cited sources.

# after
- Research is required for both JTBD and PRD. The template's "Research Findings" section must have cited sources because product decisions without evidence are assumptions, and downstream `/ct` and `/vp` inherit those assumptions silently.
...
### Step 2: Research

Fill the "Research Findings" section of the template with cited sources. The research doesn't have to be exhaustive — two or three high-quality references per claim is enough. Use quick lookups by default; only escalate to `comprehensive-researcher` when findings would materially change the job statement, scope, or requirements.
```
Cross-ref: INSIGHTS §2 rule 2 (rationale > rules), §3 (intensifier anti-pattern).

---

#### H2. Cross-AI validators not explicitly told to parallelize in one turn (INSIGHTS §1 subagent spawning; §4 parallel)
`.claude/skills/product/SKILL.md:217-222`
```
**Invoke skills sequentially first:**
1. Invoke `/codex-cli`
2. Invoke `/gemini-cli`
3. Invoke `/cursor-cli`

**Only after all three skills are invoked**, launch the three validation runs in parallel.
```
Same issue as `nf` H2 — "in parallel" is vague for 4.7, which under-parallelizes by default.

Before → after:
```
# before
**Invoke skills sequentially first:**
1. Invoke `/codex-cli`
2. Invoke `/gemini-cli`
3. Invoke `/cursor-cli`

**Only after all three skills are invoked**, launch the three validation runs in parallel.

# after
Two phases — initialization (sequential), then review (parallel):

Phase 1 — Initialization. Invoke `/codex-cli`, then `/gemini-cli`, then `/cursor-cli` in separate turns. Each skill loads its CLI contract into runtime state, so they must run serially.

Phase 2 — Review. In a single assistant turn, dispatch all three validator runs as parallel tool calls. The three reviews are independent — sequential execution only adds latency. If one validator is unavailable, dispatch the other two anyway.
```

---

#### H3. "Never assume" / "do not be a yes-agent" intensifiers (INSIGHTS §3)
`.claude/skills/product/SKILL.md:23-28`
```
- **Use `AskUserQuestion` tool for ALL clarifications** — never assume behavior, needs, or context
- Ask non-obvious and thought-provoking questions; actively challenge assumptions
- Focus on user progress and context, not features or demographics
- A job statement describes progress the user wants to make — not a feature request
- Work with the templates as output contracts throughout the interview
- Research is MANDATORY — product decisions without research are assumptions
- Do not include any time estimates
```
And `.claude/skills/product/SKILL.md:154`:
```
Continue until the template can be filled clearly. Use multiple-choice options in `AskUserQuestion` when there are clear alternatives. Challenge assumptions — do not be a yes-agent.
```

Same pattern as `nf` H1. `ALL` / "never assume" / "do not be a yes-agent" / `MANDATORY` stack up.

Before → after (for the Guidelines block):
```
# after
- Use `AskUserQuestion` for clarifications — structured options reduce ambiguity and keep the interview auditable. Skip it only when the user has already unambiguously answered in prior turns.
- Ask non-obvious, thought-provoking questions. If the user's answer sounds confident but vague ("users want it faster"), name the gap ("faster than what, measured how?") rather than accepting it.
- Focus on user progress and context, not features or demographics. A job statement is about the progress a user wants to make, not a feature request.
- Use the templates as output contracts throughout the interview — the interview gathers exactly what the template needs.
- Fill the research section with cited sources. Skipping research means downstream docs inherit unstated assumptions.
- Do not include time estimates in any output.
```
Cross-ref: INSIGHTS §3.

---

### Medium priority

#### M1. Quick mode's `[NEEDS CLARIFICATION]` pattern is good — but scope is literal (INSIGHTS §1 "more literal")
`.claude/skills/product/SKILL.md:44`
```
**Quick mode**: When `quick` prefix is detected, skip directly to Step 5 (document writing). Read templates, fill from available context, mark unknowns with `[NEEDS CLARIFICATION: ...]`. Present output with note: "Quick mode used. For deeper product thinking, run the full `/product` flow."
```

"Skip directly to Step 5" is fine, but Step 6 (Cross-AI Validation) is not covered — 4.7 will read this literally and skip validation too. Clarify.

Before → after:
```
# before
**Quick mode**: When `quick` prefix is detected, skip directly to Step 5 (document writing). Read templates, fill from available context, mark unknowns with `[NEEDS CLARIFICATION: ...]`. Present output with note: "Quick mode used. For deeper product thinking, run the full `/product` flow."

# after
**Quick mode**: When `quick` prefix is detected, skip Steps 1–4 (skip design-exploration, research, interview, and grill). Go directly to Step 5 (document writing): read the template, fill from the user's prompt and any linked context, and mark each unknown inline as `[NEEDS CLARIFICATION: <question>]`. Then run Step 6 (Cross-AI Validation) as usual — validation catches gaps that the skipped interview would have caught. Present output with: "Quick mode used — N clarifications remain. For deeper product thinking, run the full `/product` flow."
```

---

#### M2. Deep-dive has no stopping condition (INSIGHTS §3)
`.claude/skills/product/SKILL.md:92`
```
Drive the conversation section-by-section toward filling the template. Ask 2-3 questions per round. After each round, summarize what was gathered and which template section it fills.
```
Later at line 154:
```
Continue until the template can be filled clearly.
```

"2-3 per round" is good (a cap). "Continue until the template can be filled clearly" has no bound. On 4.7, this can produce 10+ rounds on complex features. Add a soft cap plus an escape valve.

Before → after:
```
# before
Continue until the template can be filled clearly. Use multiple-choice options in `AskUserQuestion` when there are clear alternatives. Challenge assumptions — do not be a yes-agent.

# after
Aim for 3–5 rounds total per document. After round 5, present what's still unclear and ask the user: "continue interviewing" / "mark unknowns and proceed to grill". Use `AskUserQuestion` with multiple-choice options when there are clear alternatives — it's faster than free-text for both sides.
```
Cross-ref: INSIGHTS §3 (no stopping condition).

---

#### M3. "Ask 2-3 questions per round" as hard-ish cap vs adaptive length (INSIGHTS §1 "Response length"; §5 item 5)
`.claude/skills/product/SKILL.md:92`
```
Ask 2-3 questions per round.
```

This is borderline. A hard count fights adaptive length. In practice the maintainer probably wants "batched, not one-by-one, not a firehose" — state the intent.

Before → after:
```
# before
Ask 2-3 questions per round.

# after
Batch questions per round — typically 2–4, matched to how much the user can reasonably answer at once. One-by-one drags; a ten-question firehose loses signal. When in doubt, 3.
```

---

#### M4. No compaction / context-awareness guard (INSIGHTS §4)
Same as `nf` M4. This skill is even longer — design-exploration + research + 3-5 interview rounds + grill + cross-AI + optional auto-JTBD write during PRD (line 180).

Before → after (new block near Guidelines):
```
# after
**Context management.** This workflow runs long (design-exploration + research + interview + grill + write + validators). If compaction happens mid-flow:
- Re-open the template you're writing against.
- Re-open any existing JTBD or previously-written product doc in `product-docs/`.
- Resume from the last unanswered template section; do not restart.
Do not stop early due to token-budget worries — the parent harness handles compaction.
```
Cross-ref: INSIGHTS §4 positive pattern.

---

#### M5. PRD auto-writes JTBD with a literal-scope gap (INSIGHTS §1 "more literal")
`.claude/skills/product/SKILL.md:180-181`
```
4. **For PRD without prior JTBD**: If the interview gathered sufficient JTBD data (which it should from the shared questions), also write the JTBD document for traceability
```

"If the interview gathered sufficient JTBD data (which it should...)" is hedged in a way 4.7 may read as optional. State the threshold concretely.

Before → after:
```
# before
4. **For PRD without prior JTBD**: If the interview gathered sufficient JTBD data (which it should from the shared questions), also write the JTBD document for traceability

# after
4. **For PRD without prior JTBD**: Write a companion `JTBD-[feature-name].md` whenever the interview produced a clear job statement, at least one answer per Four Force (push/pull/anxiety/habit), and a named primary user. If any of those are missing, note it in the PRD's "Related JTBD" section and skip the JTBD write — don't stub a thin JTBD.
```

---

### Low priority

#### L1. Announcement line (INSIGHTS §1 "Response length")
`.claude/skills/product/SKILL.md:17`
```
> **Announcement**: Begin with: "I'm using the **product** skill for product documentation creation."
```
Same comment as `nf` L2 — preamble that fights adaptive-length default. Maintainer's UX call.

---

#### L2. "Do not be a yes-agent" phrasing (INSIGHTS §2 rule 6 — positive framing)
`.claude/skills/product/SKILL.md:154`
```
Challenge assumptions — do not be a yes-agent.
```
Same as `nf` L1. Reframe positively.

Before → after:
```
# before
Challenge assumptions — do not be a yes-agent.

# after
Challenge assumptions. When an answer is confident but under-specified, name the gap ("You said X — how would that work for case Y?") instead of accepting at face value.
```

---

#### L3. Cross-AI "FOCUS" phrasing is coverage-oriented — good (INSIGHTS §3 filter leakage check)
`.claude/skills/product/SKILL.md:227-228`
```
**JTBD focus:** Job statement clarity, four-forces coherence, success criteria measurability, absence of solution bias in job framing
**PRD focus:** Requirements completeness for `/ct`, acceptance criteria testability, scope boundaries, metrics measurability, consistency with JTBD reference
```
No "only important" / "only high severity" filter leakage. Well-tuned.

---

### Items already well-tuned in `product`

- **Templates-as-contract** framing (lines 20, 48-52) is strong — consistent with `nf`.
- **`comprehensive-researcher` gating** at lines 70-74 ("Only when findings materially affect the job statement, scope boundaries, or requirements") is textbook §4.
- **Checkpoint options** use `AskUserQuestion` with 2-3 clear alternatives throughout (lines 60, 89, 168) — aligns with 4.7's preference for structured choice.
- **`Do not include any time estimates`** at line 29 is genuinely load-bearing for this workflow (product docs historically get padded with shipping dates) — keep as-is.
- **Handoff section** at lines 236-249 is comprehensive, lists command names, and covers the multi-path branching from a PRD. Good for 4.7's literal instruction following.

---

## Cross-skill themes (apply to both)

1. **Two-phase cross-AI validation protocol** (H2 in both) — both skills share the identical Step 6, so fix once in a shared include if the repo supports it (`.claude/docs/templates/cross-ai-protocol.md` is referenced). If that template owns the "how" of the protocol, move the parallel-tool-call guidance *there* and let both skills stay terse. Otherwise, duplicate the fix.
2. **Intensifier hygiene** (H1/H3 in both) — both skills use `ALL` / `MANDATORY` / `Never` / "do not be a yes-X" in the same voice. A project-wide voice pass would help more than per-skill edits.
3. **Compaction-awareness** (M4 in both) — these are long-running interview skills. Adding the `.claude/docs/templates/` a shared "long-skill context management" snippet and linking both would be cheaper than duplicating.
4. **Neither skill has an over-engineering guard** — but neither writes code, so this is not applicable here (INSIGHTS §4 over-engineering guard is scoped to implementation skills).
5. **Neither skill has a prefill pattern or temperature reference** — no migration needed (INSIGHTS §1 deprecations clean).
