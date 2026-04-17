# Review: `deep-research` and `brainstorm` skills — Opus 4.7 Audit

**Scope:** Two research/ideation skills.
**Files audited:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/deep-research/SKILL.md` (176 lines — only file in directory)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/brainstorm/SKILL.md` (164 lines — only file in directory)

**Lens:** INSIGHTS.md §3 (anti-patterns) and §4 (positive patterns) — with a focus on over-thoroughness, literal-scope gaps, and tool-use over-nudging.

**Overall verdict:** Both skills are **relatively well-tuned for 4.7**. They avoid shouty intensifiers (`CRITICAL:` / `ALWAYS` / `NEVER`), use positive framing, and include table-based decision gates. The main issues are (1) tool-use nudges likely to over-trigger on 4.7, (2) missing explicit stopping criteria for research loops (over-thoroughness risk), and (3) a couple of literal-scope gaps where the model won't generalize without being told.

---

## Skill 1: `deep-research`

### High priority

#### H1. Over-thoroughness: no explicit stopping criteria on source gathering
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 76–81 (Cross-Verification block)
**Cross-ref:** INSIGHTS.md §3 — *"Be thorough / exhaustive / comprehensive with no stopping condition — causes overthinking and scope creep"*

**Offending text (quoted):**
> ```
> ## 4. Cross-Verification
>
> - Never rely on a single source — triangulate across at least 2-3
> - Verify claims against official docs
> - Check publication dates — prefer content from the last 12 months
> - Look for consensus; flag disagreements explicitly
> - Be skeptical of AI-generated content in search results
> ```

The bullet `Never rely on a single source` combined with `triangulate across at least 2-3` sets a **floor** (≥2 sources) but no **ceiling**. On 4.7 — which is more literal and more patient — this pairs badly with the Quick/Comparison/Deep table (lines 23–27) because the Quick row says "1-2 sources" while Cross-Verification mandates ≥2. The model will resolve that by upgrading every Quick query to at least Comparison.

**Before:**
```
- Never rely on a single source — triangulate across at least 2-3
- Verify claims against official docs
```

**After:**
```
- Match source count to depth: Quick = 1–2 sources (skip Cross-Verification entirely); Comparison = 2–3; Deep = 3–5.
- Stop gathering once the answer is stable across sources — additional confirmatory sources add little value. If the first 2 sources agree and are authoritative (official docs, primary repos), that's enough.
- Verify claims against official docs only when the claim is load-bearing for a recommendation.
```

The *why*: Cross-Verification currently reads as a global rule; on 4.7 it cascades into "always fetch 3+ sources." An explicit ceiling + a stopping heuristic ("stable across sources") prevents drift.

---

#### H2. Tool-use over-nudging in "Tool Priority" section
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 42–49
**Cross-ref:** INSIGHTS.md §3 — *"`Default to using [tool]` — too broad; replace with 'use [tool] **when** it would enhance X'"* and §1 Tool-use row — *"Prompts that previously nudged tool use may now be unnecessary or cause over-reasoning."*

**Offending text (quoted):**
> ```
> Research tools should be used in this order — Exa provides the fastest, most code-aware results:
>
> 1. **`get_code_context_exa`** — code-oriented queries (API usage, library examples, patterns)
> 2. **`web_search_exa`** — broader technical topics, comparisons, ecosystem info
> 3. **`ref_search_documentation`** — only when Exa results seem outdated or contradictory
> 4. **`ref_read_url`** — read primary docs when clarification is needed
> 5. **`WebSearch` / `WebFetch`** — fallback for anything Exa/Ref can't reach
> ```

A ranked list with "should be used in this order" is a directional default. On 4.7, that's interpreted as "call tool 1 first even if the question is purely conceptual / already answerable." Combined with the Parallel Search block right below (lines 51–55), it encourages the model to fan out tool calls without first deciding whether any are needed.

**Before:**
```
Research tools should be used in this order — Exa provides the fastest, most code-aware results:

1. **`get_code_context_exa`** — code-oriented queries (API usage, library examples, patterns)
2. **`web_search_exa`** — broader technical topics, comparisons, ecosystem info
3. **`ref_search_documentation`** — only when Exa results seem outdated or contradictory
4. **`ref_read_url`** — read primary docs when clarification is needed
5. **`WebSearch` / `WebFetch`** — fallback for anything Exa/Ref can't reach
```

**After:**
```
Pick the smallest set of tools that answers the question. Many Quick-depth queries need zero tool calls. When you do search, choose by fit:

- **`get_code_context_exa`** when you need API/library code examples or usage patterns.
- **`web_search_exa`** when the question is conceptual, comparative, or ecosystem-wide.
- **`ref_search_documentation` / `ref_read_url`** when you need authoritative confirmation and Exa's summary is insufficient.
- **`WebSearch` / `WebFetch`** only as a fallback when the above can't reach the source.

Do not run a tool to confirm something you already know confidently from the docs or the codebase — cite the source instead.
```

---

### Medium priority

#### M1. Literal-scope gap: parallel search instruction needs explicit "same-turn" cue
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 51–55
**Cross-ref:** INSIGHTS.md §4 — *"Parallel tool-calling: When calls have no dependencies, batch them in one turn. Never use placeholders or guess missing parameters."*

**Offending text (quoted):**
> ```
> ### Parallel Search
>
> Since this runs in a fork, optimize for speed by launching parallel queries:
> - Fire Exa code context + Exa web search simultaneously for different facets of the question
> - While web results load, scan the local codebase (`Grep`, `Glob`) for relevant existing patterns
> - Use multiple small, focused queries rather than one broad query
> ```

"Fire … simultaneously" is ambiguous: 4.7 may interpret it as "fire them both eventually" rather than "emit both tool calls in a single assistant turn." The INSIGHTS.md §1 row on subagent/parallel-call behavior notes that 4.7 under-parallelizes by default and needs **explicit** same-turn framing.

**Before:**
```
- Fire Exa code context + Exa web search simultaneously for different facets of the question
- While web results load, scan the local codebase (`Grep`, `Glob`) for relevant existing patterns
```

**After:**
```
- When queries have no dependencies, emit all of them in the **same assistant turn** (one tool-use block per query). Do not wait for the first to return before issuing the next.
- Combine web searches with a local `Grep`/`Glob` pass in the same turn when codebase context is relevant.
```

---

#### M2. Intensifier hygiene — `Never rely on a single source` / `never speculate`
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 78 (`Never rely on a single source`) and 170–176 (Before Returning checklist uses a neutral voice already — fine)
**Cross-ref:** INSIGHTS.md §3 — *"`CRITICAL:` / `You MUST` / `ALWAYS` / `NEVER` used as intensifiers — dial back"*

Only one `Never` appears as a bullet-starting intensifier, and it conflates with the stopping-criteria issue in H1. Already addressed in the H1 rewrite. **Standalone verdict: Low priority on its own — folded into H1.**

---

#### M3. Missing "investigate-before-answering" guard for codebase-touching research
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 126–133 (Project Context section) and 59–68 (Source Types / Local codebase rows)
**Cross-ref:** INSIGHTS.md §4 — *"Investigate-before-answering: Never speculate about code you have not opened. If the user references a file, read it before answering."*

The skill tells the model to "reference existing patterns in the codebase when making recommendations" (line 131) but never says **read the file before citing it**. Because deep-research runs in a forked context and the user often asks "should we use X given our current setup?" — the model may hallucinate about code it didn't open.

**Before (line 131):**
```
- Reference existing patterns in the codebase when making recommendations
```

**After:**
```
- Reference existing patterns in the codebase when making recommendations. If you cite a file or function, open it with `Read` first — do not speculate about code you have not read.
```

---

### Low priority

#### L1. Output-format templates use code fences around markdown
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 88–124 (Output Format section — Quick / Comparison / Full Report blocks)
**Cross-ref:** INSIGHTS.md §2 #9 — *"Match prompt style to desired output."*

The Full Report template (lines 109–124) is itself wrapped in ```` ```markdown ```` fences, which is fine for showing the template, but the Quick/Comparison blocks (88–102) are wrapped in bare ``` fences. This is a cosmetic nit; 4.7 handles this without issue. **No change required** — noting for completeness.

---

#### L2. `Before Returning` checklist is healthy
**File:** `.claude/skills/deep-research/SKILL.md`
**Lines:** 170–176

Six checkbox items, positively framed, no intensifiers. Well-tuned. No change.

---

### `deep-research` summary
- 2 High priority fixes (stopping criteria, tool-use over-nudging)
- 2 Medium priority fixes (explicit same-turn parallelism, read-before-cite)
- Remainder is well-tuned for 4.7.

---

## Skill 2: `brainstorm`

### High priority

#### H1. Tool-use over-nudging in "Research (When Needed)" — both over-triggers and under-specifies parallelism
**File:** `.claude/skills/brainstorm/SKILL.md`
**Lines:** 98–120
**Cross-ref:** INSIGHTS.md §1 Tool-use row, §3 — *"`Default to using [tool]` — too broad"*, and §4 — *"Spawn multiple subagents in the same turn when fanning out across files or independent items."*

**Offending text (quoted):**
> ```
> ### Step 4: Research (When Needed)
>
> Launch research proactively when the conversation reveals knowledge gaps — no permission needed. Inform the user what's being researched and continue brainstorming while agents work in the background.
>
> **Quick lookups:**
> - `get_code_context_exa` — for code-related context, APIs, libraries
> - `web_search_exa` — for trends, market data, best practices
>
> **In-depth research:**
> - Spawn `comprehensive-researcher` agent via Agent tool for topics requiring multiple sources and cross-verification
> - Launch multiple researcher agents simultaneously for different sub-topics
>
> **Code context (project-related):**
> - Use Explore agents (Sonnet) to scan relevant modules, patterns, and prior art
>
> **Trigger research when:**
> - Topic requires current or up-to-date information
> - Market trends, competitor analysis, or industry standards are relevant
> - Technical decisions benefit from external validation
> - Knowledge gaps are identified during exploration
> ```

Two issues compound:

1. `Launch research proactively when the conversation reveals knowledge gaps — no permission needed` pairs with the four-item `Trigger research when` list that is quite broad (`Topic requires current or up-to-date information` covers almost any topic). On 4.7, this over-triggers research in conversations that were supposed to stay light ("Quick decision" depth from Step 1).
2. `Launch multiple researcher agents simultaneously` — same "simultaneously" ambiguity as deep-research M1. 4.7 under-parallelizes by default; it needs explicit same-turn framing.

**Before:**
```
Launch research proactively when the conversation reveals knowledge gaps — no permission needed. Inform the user what's being researched and continue brainstorming while agents work in the background.

…

**In-depth research:**
- Spawn `comprehensive-researcher` agent via Agent tool for topics requiring multiple sources and cross-verification
- Launch multiple researcher agents simultaneously for different sub-topics

…

**Trigger research when:**
- Topic requires current or up-to-date information
- Market trends, competitor analysis, or industry standards are relevant
- Technical decisions benefit from external validation
- Knowledge gaps are identified during exploration
```

**After:**
```
Research is a branch, not the trunk. Most brainstorms need none — the model's own knowledge plus user input is usually enough, especially for Quick Decision depth. Run research only when the answer genuinely depends on information you don't have.

…

**In-depth research:**
- Spawn `comprehensive-researcher` agents when the decision hinges on external evidence the user will ask about.
- When fanning out across independent sub-topics, spawn all subagents **in the same assistant turn** — do not default to sequential. Inform the user what's being researched.

…

**Trigger research only when** the brainstorm cannot move forward without it — e.g., the user explicitly asks for market data, a claim requires external verification to be actionable, or an unfamiliar technology is central to the decision. Do not research to pad Deep Dive depth.
```

The *why*: the current phrasing treats research as the default response to any topic complexity. That fights the adaptive-depth calibration in Step 1 — a Quick Decision brainstorm suddenly becomes a research task.

---

### Medium priority

#### M1. Literal-scope gap: "Context gathering is not a gate" may cause the model to skip it entirely
**File:** `.claude/skills/brainstorm/SKILL.md`
**Lines:** 70–81 (Step 2: Context Gathering (Adaptive))
**Cross-ref:** INSIGHTS.md §3 — *"literal-scope gaps"*, §1 row on instruction following

**Offending text (quoted):**
> ```
> ### Step 2: Context Gathering (Adaptive)
>
> Context gathering is not a gate — it happens organically as the brainstorm progresses. Start with what's immediately relevant and pull in more context as needed.
>
> **For project-related topics:**
> - If the topic clearly touches existing code, invoke the `design-exploration` skill to scan the codebase
> - If the scope is unclear, start with the brainstorm conversation and invoke design-exploration later when specific areas of the codebase become relevant
> ```

On 4.7's more literal reading, "not a gate … happens organically" can translate to "skip it unless I can't proceed." For project-related topics, this leads to brainstorming about code without ever opening it — the model generates plausible but unanchored options.

**Before:**
```
Context gathering is not a gate — it happens organically as the brainstorm progresses. Start with what's immediately relevant and pull in more context as needed.
```

**After:**
```
Context gathering is not a blocking gate, but for project-related topics you must ground the conversation in real code before proposing options. At minimum, read `CLAUDE.md` and skim the 1–2 files most directly named in the topic before Step 3. Pull in more context as specific areas become relevant. For general (non-project) topics, skip this step entirely.
```

---

#### M2. Hard-coded response-length caps in Exploration templates
**File:** `.claude/skills/brainstorm/SKILL.md`
**Line:** 92
**Cross-ref:** INSIGHTS.md §3 — *"Hard-coded response-length caps … that fight 4.7's adaptive length."*

**Offending text (quoted):**
> ```
> Present ideas in 200-300 word sections and validate understanding after each section before continuing.
> ```

A fixed 200–300 word cap is the exact anti-pattern INSIGHTS.md §3 calls out. For a Quick Decision brainstorm, 200 words per section is too much; for Deep Dive, sometimes too little.

**Before:**
```
Present ideas in 200-300 word sections and validate understanding after each section before continuing. Be ready to pivot if direction changes.
```

**After:**
```
Present ideas in tight, self-contained sections sized to the calibration from Step 1 — shorter for Quick Decision, longer for Deep Dive. Pause to validate understanding between sections. Be ready to pivot if direction changes.
```

---

### Low priority

#### L1. Minor intensifier — `ALL clarifications`
**File:** `.claude/skills/brainstorm/SKILL.md`
**Line:** 19
**Cross-ref:** INSIGHTS.md §3 — *"`ALWAYS` used as intensifiers — dial back"*

**Offending text (quoted):**
> ```
> - **Use `AskUserQuestion` tool for ALL clarifications** — provides interactive options for user to choose from
> ```

`ALL` in caps is a mild emphasis marker. The rationale (`provides interactive options`) is already correctly attached, so only the emphasis is excessive.

**Before:**
```
- **Use `AskUserQuestion` tool for ALL clarifications** — provides interactive options for user to choose from
```

**After:**
```
- Use `AskUserQuestion` for clarifications — it renders as interactive options the user can pick from, which is friendlier than free-text for most choices.
```

---

#### L2. Completion signals are well-framed
**File:** `.claude/skills/brainstorm/SKILL.md`
**Lines:** 94–97

**Quoted:**
> ```
> **Completion signals** — the brainstorm is "done" when:
> - For Quick Decision: user has enough info to decide
> - For Exploration: all major angles have been discussed and user confirms
> - For Deep Dive: all question categories explored, user has no more "what about..." questions
> ```

This is good prompting — it gives the model explicit stopping criteria per depth tier, which is exactly what INSIGHTS.md §3 recommends to prevent over-thoroughness. No change.

---

#### L3. Step 5/6 handoff structure is well-tuned
**File:** `.claude/skills/brainstorm/SKILL.md`
**Lines:** 122–155

Depth-adaptive capture (skip for Quick Decision, full template for Deep Dive) + explicit handoff to other skills. Positive framing, no intensifiers. No change.

---

### `brainstorm` summary
- 1 High priority fix (research trigger / parallelism)
- 2 Medium priority fixes (context-gathering literalism, hard-coded word cap)
- Remainder is well-tuned for 4.7.

---

## Cross-cutting observations

1. **Both skills share the "simultaneously" ambiguity.** Neither explicitly says "in the same assistant turn." 4.7's under-parallelization (INSIGHTS.md §1) means both skills will serialize research calls unless the framing is made explicit. This is the highest-leverage single change across both files.

2. **Neither skill has a compaction-awareness block** (INSIGHTS.md §4). This is **acceptable** — these are short-running skills (brainstorm is bounded by user dialogue, deep-research runs in a fork that discards its context). Low priority to add; not worth flagging as a finding.

3. **Both skills already do several things right for 4.7:** depth calibration with stopping signals (Quick/Comparison/Deep in deep-research, Quick Decision/Exploration/Deep Dive in brainstorm), positive framing, rationale attached to most rules, XML-ish structure via markdown headers. These are the patterns INSIGHTS.md §2 rewards.

4. **No prefill patterns found** — good. Both skills predate or cleanly avoid the deprecated assistant-turn prefill.

5. **No `CRITICAL:` / `You MUST` / `NEVER` intensifier spam found** — both files use neutral voice. Only two mild cases (deep-research `Never rely on a single source`, brainstorm `ALL clarifications`) and both are low-impact.

---

## Priority-ranked action list

| # | Skill | Finding | Priority |
|---|---|---|---|
| 1 | deep-research | Add stopping criteria to Cross-Verification | High |
| 2 | deep-research | Replace "use in this order" tool-priority list with fit-based guidance | High |
| 3 | brainstorm | Narrow "Launch research proactively" trigger + explicit same-turn parallelism | High |
| 4 | deep-research | Make parallel search explicitly same-turn | Medium |
| 5 | deep-research | Add read-before-cite guard to Project Context | Medium |
| 6 | brainstorm | Tighten Context Gathering for project topics (min: read CLAUDE.md + named files) | Medium |
| 7 | brainstorm | Remove hard-coded 200-300 word cap | Medium |
| 8 | brainstorm | Soften `ALL clarifications` emphasis | Low |
| 9 | deep-research | Fold standalone `Never` into H1 rewrite | Low (absorbed) |
