# Agent Review: task-splitter & comprehensive-researcher

Scope: audit two subagent definitions against Opus 4.7 best practices (`INSIGHTS.md` §1–§5).

Files under review:
- `.claude/agents/tasks-validators-agents/task-splitter.md`
- `.claude/agents/helpful-agents/comprehensive-researcher.md`

---

## Agent 1: task-splitter

Role classification: structural/decision agent. Single-shot analyzer that reads a `tech-decomposition*.md`, evaluates splitting safety, and emits either a NO-SPLIT recommendation or a `splitting-decision.md`. No fan-out, no tool orchestration.

Overall: the prompt is tight and rationale-forward. Contract-ordering rule and anti-patterns are well-motivated with explicit *why*. Most concerns are minor (intensifier hygiene and two literal-scope gaps). No critical issues found.

### Frontmatter

File: `.claude/agents/tasks-validators-agents/task-splitter.md:1-6`

```yaml
name: task-splitter
description: Use this agent when you need to decide whether a technical decomposition should stay as one implementation task or be split into functionally coherent, logically sequenced phases.
model: opus
color: yellow
```

Assessment: the `description:` is action-biased and clean — starts with "Use this agent when you need to…", names the decision surface (split vs. keep), and names the input artifact class ("technical decomposition"). For 4.7's dispatcher this is appropriate: it will not trigger on unrelated phrasing like "split this codebase" or "break apart this file". No change needed.

Minor suggestion (Low): the description does not state the negative scope ("does NOT create phase folders / tracker issues"), which the body establishes on L9. For a dispatcher this is fine — the body catches it — but if this agent gets confused with `task-decomposer` at call sites, a 6-word disambiguator at the end ("analysis only; does not materialize phases") could help. Optional.

### High Priority

None.

### Medium Priority

**M1. Literal-scope gap on "Step 1: Read Task Files" when files are missing**

File/lines: `task-splitter.md:96-102`

Current:
```
1. Glob for `tech-decomposition*.md` in the provided task directory
2. Read the tech-decomposition file (**required** — if not found, inform the user and stop)
3. Optionally read `PRD-*.md` from `docs/product-docs/PRD/` for business context
4. Optionally read `JTBD-*.md` from the task directory for user needs context

**If the tech-decomposition has an unexpected format** (for example, missing test plan or implementation steps), inform the user and do a best-effort analysis from the available content.
```

Issue (per §3 "literal-scope gaps" and §1 "instruction following — more literal"): 4.7 will read these in order, one by one, sequentially. Steps 1, 3, and 4 are independent file reads with no dependencies between them. Since the agent is explicitly dispatched per §4 ("Parallel tool-calling — when calls have no dependencies, batch them in one turn"), the absence of parallel guidance here means 4.7 will under-parallelize.

Suggested after:
```
Read the available inputs in a single parallel batch (Glob + Reads have no dependencies):
1. Glob for `tech-decomposition*.md` in the provided task directory
2. Read the tech-decomposition file (**required** — if not found, inform the user and stop before Step 2)
3. Optionally read `PRD-*.md` from `docs/product-docs/PRD/` for business context
4. Optionally read `JTBD-*.md` from the task directory for user needs context

Batch these reads in one turn. If the tech-decomposition is missing, stop. If it has an unexpected format (for example, missing test plan or implementation steps), inform the user and do a best-effort analysis from the available content.
```

Rationale: cites §4 pattern "When calls have no dependencies, batch them in one turn." This is a small perf/latency win, not a correctness issue — hence Medium.

**M2. "Deliver Decision" step has a branching instruction that assumes generalization**

File/lines: `task-splitter.md:137-149`

Current:
```
**If SPLIT RECOMMENDED**:
- Read the template at `.claude/docs/templates/splitting-decision-template.md`
- Fill it in with a functionally coherent, logically sequenced phase plan
- Create `splitting-decision.md` in the task directory
- This decision artifact is required
```

Issue (§3 "literal-scope gaps"; §1 "instruction following — more literal"): 4.7 might produce the file with *only* the template scaffolding unless explicitly told what must be concrete. Phrases like "Fill it in with a functionally coherent, logically sequenced phase plan" are high-level — 4.7 will be literal about "fill" but may leave placeholder-ish content if the template has optional sections.

Suggested after:
```
**If SPLIT RECOMMENDED**:
- Read the template at `.claude/docs/templates/splitting-decision-template.md`
- Fill every section with content specific to this decomposition — do not leave template placeholders, TBDs, or "see above" stubs
- For each proposed phase, include: phase goal, REQ items, test scope, file/module areas, contracts introduced, contracts consumed, and dependency direction relative to other phases
- Save as `splitting-decision.md` in the task directory
- This decision artifact is required
```

Rationale: makes the scope of "fill in" literal, per §3 pattern "State scope explicitly — 4.7 will NOT silently generalize."

**M3. Contract-ordering rule lacks `why` for one of its branches**

File/lines: `task-splitter.md:18-21`

Current:
```
The split must respect dependency direction:
- If Phase 2 consumes a contract, Phase 1 must introduce it first
- If the only way to split requires Phase 1 to assume a future contract, reorder the phases or do NOT split
- Prefer "contract-producing slice -> consumer slice" over "consumer first -> contract later"
```

Assessment: this is already quite good by §2.2 standards (most rules state *what* clearly). The bad/good example block immediately below (L23-31) provides the *why* by demonstration. The three bullets themselves omit the *why* but gain it from context. This is borderline acceptable.

Suggested (optional polish) — add one sentence of *why* at the top:
```
The split must respect dependency direction, because any forward-referenced contract forces earlier phases to guess shape and creates rework when the later phase finalizes it:
- If Phase 2 consumes a contract, Phase 1 must introduce it first
...
```

Rationale: §2.2 "Explain the why — rationale > rules." Low/Medium because the examples right after already illustrate the consequence.

### Low Priority

**L1. Intensifier hygiene — `MUST`, `IMPORTANT`, `required` density**

File/lines:
- `task-splitter.md:10` — "You **analyze and recommend** — you do NOT create phase folders…" (appropriate; load-bearing negative scope)
- `task-splitter.md:57` — "**MUST SPLIT** when:" (decision-rule label; acceptable — a defined term, not an intensifier)
- `task-splitter.md:71` — "Do NOT recommend these splitting patterns:" (appropriate; naming anti-patterns)
- `task-splitter.md:97` — "**required**" on tech-decomposition existence (appropriate; hard stop)
- `task-splitter.md:120` — "Before recommending a split, explicitly check:" (fine)
- `task-splitter.md:141` — "This decision artifact is required" (acceptable)
- `task-splitter.md:149` — "**IMPORTANT**: You only provide analysis and recommendations. The human decides next steps." (borderline — see below)

Per §3, the concerning pattern is intensifiers used *as emphasis* rather than as load-bearing scope markers. Here, most usages are legitimate because they define decision labels (`MUST SPLIT`, `SHOULD SPLIT`, `DO NOT SPLIT`) or name hard stops. Only L149's `**IMPORTANT**:` is a soft emphasis on a boundary already stated in L9-10 and in the description.

Current (L149):
```
**IMPORTANT**: You only provide analysis and recommendations. The human decides next steps.
```

Suggested after:
```
The human decides next steps after reading your recommendation.
```

Rationale: §3 "intensifiers used as emphasis — dial back to normal voice." The scope restriction is already stated in the frontmatter description and L9-10; repeating it with `**IMPORTANT**:` adds weight without new information. Low priority because it's one line and the model will follow either version.

**L2. "Bad split example" is clear; "Good split examples" lists two items without a separator**

File/lines: `task-splitter.md:27-31`

Current:
```
**Good split examples**:
- Phase 1: Domain + endpoint happy path defining and using the contract
- Phase 2: Secondary consumer (UI, CLI, additional workflow) built on that existing contract
- Phase 1: Shared migration/module introduced alongside its first real consumer
- Phase 2: Additional consumers and edge cases
```

Issue: these are two separate examples collapsed into a single list. 4.7's literal reading may treat these as one 4-phase plan. Minor clarity issue.

Suggested after:
```
**Good split examples**:

Example A (endpoint-first):
- Phase 1: Domain + endpoint happy path defining and using the contract
- Phase 2: Secondary consumer (UI, CLI, additional workflow) built on that existing contract

Example B (module-with-consumer-first):
- Phase 1: Shared migration/module introduced alongside its first real consumer
- Phase 2: Additional consumers and edge cases
```

Rationale: §2.3 "XML tags / structure" — here just visual separators, but same principle. Low because the content is correct; only the framing is ambiguous.

**L3. "Strong Signals" table has thresholds expressed as numbers — 4.7 may treat them literally**

File/lines: `task-splitter.md:43-51`

Current thresholds: "3+ cohesive REQ", "3+ test suites or ~15+ test cases", "4+ distinct module areas", "2+ bounded contexts".

Assessment: the section is prefaced with "Use these as heuristics, not hard laws:" (L44), which is exactly the §3 mitigation for literal-following. This is already well-handled. No change.

### Already-good patterns (don't change)

- Role assignment in L7 is tight and specific (§2.8).
- Contract ordering rule (L16-21) with bad/good examples (L23-31) uses §2.2 (*why*) via demonstration.
- Anti-patterns section (L71-77) names each anti-pattern with a motive — high-quality §2.2.
- Analysis Process (L93-131) has numbered steps with clear sub-checks; Step 4's validation checklist is a good §3 "coverage-then-filter" analog applied to splitting.
- The "If any candidate split fails the contract-ordering rule, reject it and either: propose a different sequence, or recommend NO SPLIT" (L127-129) is an explicit stopping condition — exactly the §3 counter to over-thoroughness.
- Delivery section (L133-149) has a clear branch on decision and correctly escopes file creation to only the SPLIT case.

---

## Agent 2: comprehensive-researcher

Role classification: research agent. Per the review brief, **HIGH RISK** for §3 over-thoroughness anti-patterns because (a) its NAME is "comprehensive-researcher" — which biases 4.7 toward exhaustive behavior, and (b) the prompt uses multiple thoroughness intensifiers without stopping criteria.

Overall: significant work needed. The prompt reads like pre-4.7 research boilerplate — thorough-by-default, source-ladder-heavy, with *no* budget guidance, *no* parallel-tool-calling guidance, and *no* stopping criteria. It also lacks XML structure for inputs and has multiple intensifier issues.

### Frontmatter

File: `.claude/agents/helpful-agents/comprehensive-researcher.md:1-5`

```yaml
name: comprehensive-researcher
description: Use this agent when you need to conduct in-depth research on any topic, requiring multiple sources, cross-verification, and a structured report with citations. This agent excels at breaking down complex topics into research questions, finding authoritative sources, and synthesizing information into well-organized reports. 
model: opus
```

Issues:

1. **Name bias** (High): the name "comprehensive-researcher" itself is an instruction to 4.7. 4.7 will read this as a standing commitment to comprehensiveness and over-resist any internal "good enough" stopping. Combined with the body's "comprehensive understanding" (L15) and "comprehensive investigations" (L7), the agent has no signal that it may stop early on narrow tasks.

2. **Description "in-depth… multiple sources… cross-verification"** (Medium): these phrases compound with the name bias and the body's "at least 3-5 credible sources" floor (L17) to produce a fixed-floor behavior regardless of task complexity.

3. **Trailing space** on the description line (L3, at end) — harmless but suggests the file was drafted without care; mention for cleanup.

4. **No `color` field** — not material; some other agents have it, others don't.

Suggested rewrite (keep the name since renaming is out of scope for this review, but rebalance the description):

```yaml
name: comprehensive-researcher
description: Use this agent when you need a structured, cited research report on a topic that requires synthesizing multiple sources. Scale source count to the question's breadth — a narrow factual question may need 2–3 sources; a contested policy question may need 8+. Stop when marginal sources stop changing the conclusion.
model: opus
```

Rationale: §3 "Be thorough / exhaustive / comprehensive with no stopping condition — causes overthinking and scope creep." The dispatcher is the right place to land the stopping rule because it's the first thing 4.7 reads when the agent is invoked.

### High Priority

**H1. No stopping criteria for "comprehensive" — primary §3 anti-pattern**

File/lines: `comprehensive-researcher.md:7, 9, 15, 17`

Current text that compounds the issue:
- L7: "conducting comprehensive investigations on any topic"
- L9: "Your research process follows these steps:"
- L15: "designed to uncover comprehensive understanding"
- L17: "at least 3-5 credible sources" (per question, × 5–8 questions = 15–40 source ceiling with no ceiling)

Issue (§3 direct match): "Be thorough / exhaustive / comprehensive with no stopping condition — causes overthinking and scope creep." The prompt stacks four reinforcements of exhaustive behavior with no counterweight. 4.7 will read each literally.

Suggested after (add a new Stopping Criteria section after L9 "Your research process follows these steps:"):

```
## Stopping Criteria

Before you start, calibrate effort to the question:

- **Narrow factual question** (e.g., "what year did X ship?"): 1–3 sources, short answer, no decomposition needed.
- **Definitional / landscape question** (e.g., "what is approach X?"): 3–5 sources, short structured report.
- **Contested / policy / multi-stakeholder question**: full decomposition, 5–8 questions, 3–5 sources per question.

Stop research when any of the following are true:
- The next source is unlikely to change your conclusion.
- You have corroborated the key claim from ≥2 independent sources and the remaining sub-questions are lower-value.
- Further search returns the same claims rephrased.

Do not chase exhaustiveness for its own sake. If you stop early, say so in the report's "Limitations" section and name what you did not investigate.
```

Also soften the fixed floor on L17:

Current:
```
2. **Search Multiple Reliable Sources**: For each research question, you identify and search at least 3-5 credible sources. You prioritize:
```

Suggested after:
```
2. **Search Reliable Sources**: For each research question, identify and search enough credible sources to answer it with confidence — typically 2–5, more for contested claims, fewer for uncontested factual ones. Prioritize:
```

And replace L15:

Current:
```
1. **Generate Detailed Research Questions**: When given a topic, you first decompose it into 5-8 specific, answerable research questions that cover different aspects and perspectives. These questions should be precise and designed to uncover comprehensive understanding.
```

Suggested after:
```
1. **Generate Research Questions Scaled to the Topic**: Decompose the topic into 3–8 specific answerable questions — fewer for narrow topics, more for contested or multi-stakeholder ones. Skip this step entirely if the user's question is already atomic. Each question should be precise and individually answerable.
```

Rationale: §3 verbatim. This is the single biggest fix in the file.

**H2. No parallel-tool-calling guidance — required for research agents per §4**

File/lines: `comprehensive-researcher.md:11-23` (the entire "Search Multiple Reliable Sources" step)

Issue (§4 direct match, and the review brief flags this explicitly): "Research agents should have parallel-tool-call guidance (§4) since they dispatch many independent searches." Currently the prompt describes research questions and sources but never says "batch searches in one turn." 4.7 will under-parallelize by default (§1 "Subagent spawning — more conservative by default" and §1 "Tool use — reasons more before calling tools").

Suggested addition (after the research questions are formed, before Step 2 begins, or as a new bullet in Step 2):

```
**Dispatch searches in parallel.** When you have identified the research questions, issue all initial web searches / tool calls for independent questions in a single turn. Do not search one question at a time. Only sequence calls when a later search genuinely depends on what an earlier one returns (e.g., disambiguating a term before searching its details).
```

Rationale: §4 "Parallel tool-calling — when calls have no dependencies, batch them in one turn. Never use placeholders or guess missing parameters." This is the #1 efficiency fix for research agents on 4.7.

**H3. No mention of which tools to use — tool-guidance gap**

File/lines: `comprehensive-researcher.md:17-21`

Current:
```
For each research question, you identify and search at least 3-5 credible sources. You prioritize:
   - Academic papers and peer-reviewed journals
   - Government and institutional reports
   - Reputable news organizations and specialized publications
   - Expert opinions and industry analyses
   - Primary sources when available
```

Issue: the prompt lists *source types* but never the *tools*. This repo (per `~/.claude/rules/research.md` — the user's global rules) has a tool hierarchy:

1. `mcp__exa__get_code_context_exa` — code/API questions
2. `mcp__exa__web_search_exa` — general search
3. `mcp__exa__deep_search_exa` — complex, multi-angle
4. `mcp__ref__ref_search_documentation` / `mcp__ref__ref_read_url` — official docs fallback
5. Extras: `web_search_advanced_exa`, `crawling_exa`, `company_research_exa`, `people_search_exa`

Without this, 4.7 will either (a) default to whatever generic web search is convenient, or (b) reason for too long about which tool to use (§1 "Tool use — reasons more before calling tools"). This is a significant quality gap.

Suggested addition (new subsection between current Step 1 and Step 2, or folded into Step 2):

```
## Tool Selection

Select the right search tool for each question before dispatching:

- Code / API / library questions → `mcp__exa__get_code_context_exa`
- General web / news / landscape → `mcp__exa__web_search_exa` (fast) or `mcp__exa__web_search_advanced_exa` (with filters)
- Multi-angle research questions where you want a synthesized answer → `mcp__exa__deep_search_exa`
- Full page extraction by URL → `mcp__exa__crawling_exa`
- Company background → `mcp__exa__company_research_exa`; people → `mcp__exa__people_search_exa`
- Official docs verification → `mcp__ref__ref_search_documentation`, then `mcp__ref__ref_read_url` for the exact page

Prefer Exa first; use Ref as an authoritative fallback for documentation claims.
```

Rationale: §2.1 "Golden rule: if a new colleague couldn't follow the prompt, Claude can't either" — the prompt currently omits the repo's canonical tool stack. Also per the user's global `research.md`.

**H4. No XML structure for inputs — prompt will be ambiguous when invoked**

File/lines: entire file

Issue (§2.3, §5.12): the prompt has no `<instructions>`, `<input>`, `<context>`, or `<examples>` tags. When invoked by a parent, the user's topic + any accompanying context arrives as free text and 4.7 has no structural anchor. For an agent that may be invoked with complex multi-part briefs, this is a real quality gap.

Suggested: wrap the operational body in XML and add an `<input_handling>` note. Minimal version:

```
<instructions>
You are a researcher conducting grounded investigations. Scale depth to the task (see Stopping Criteria below). Your output is a structured, cited report.
</instructions>

<input_handling>
The invoking agent will provide the research topic, and may provide additional context (audience, prior findings, specific angles to prioritize). Treat provided context as authoritative and scope-limiting — do not research beyond what was asked.
</input_handling>

<process>
... [the numbered steps] ...
</process>

<output_format>
... [the report structure] ...
</output_format>
```

Rationale: §2.3 and the §1 row on "Instruction following — more literal; will NOT silently generalize." XML tags give 4.7 concrete scope anchors.

### Medium Priority

**M1. Intensifier hygiene — "comprehensive" density**

File/lines: the word `comprehensive` / `comprehensively` / `comprehensiveness` appears at L7, L15, L49 (and in the agent name). Usage:
- L7: "conducting comprehensive investigations on any topic"
- L15: "uncover comprehensive understanding"
- L49: "a comprehensive, balanced, and well-sourced understanding"

Per §3, this is exactly the phrase pattern flagged ("Be thorough / exhaustive / comprehensive with no stopping condition"). Even with H1 added, these three residual mentions will still bias 4.7 toward exhaustive output on every invocation.

Suggested: replace "comprehensive" with scale-appropriate language in at least two of the three spots. Examples:
- L7: "conducting grounded investigations on any topic" or "conducting cited investigations on any topic"
- L15: remove the whole second sentence, or "designed to uncover the claim, its evidence, and meaningful dissent"
- L49: "a grounded, balanced, and well-sourced understanding, scaled to the task"

Rationale: §3 "dial back intensifiers used as emphasis." Keep the name "comprehensive-researcher" because renaming touches callers, but strip the reinforcements in the body.

**M2. `CRITICAL` / `MUST` / `strict` intensifier scan**

File/lines:
- L41: "You avoid jargon unless necessary (and define it when used). You maintain **strict objectivity**…"
- L46: "you explicitly state this limitation rather than speculating"

Assessment: "strict objectivity" is a soft intensifier; "explicitly state" is load-bearing (tells the model not to silently omit). No `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` in this file.

Current L41:
```
Your writing style is clear, professional, and accessible. You avoid jargon unless necessary (and define it when used). You maintain strict objectivity, presenting information without personal bias while acknowledging the complexity and nuance of most topics.
```

Suggested after (dials back "strict" per §3, keeps the behavior via §2.6 positive framing):
```
Your writing style is clear, professional, and accessible. You avoid jargon unless necessary (and define it when used). Write with the detachment of a journalist who has no stake in the outcome: present evidence, attribute claims, and acknowledge complexity rather than resolving it artificially.
```

Rationale: §2.6 "Positive framing beats negative" + §2.2 "Explain the *why*."

**M3. Negative framing around jargon and speculation**

File/lines: L41, L45-46

Current L45-46:
```
If you cannot find sufficient reliable information on any aspect, you explicitly state this limitation rather than speculating. You suggest alternative research directions or related topics that might provide relevant insights.
```

Assessment: this is fine — it is positive-framed already ("explicitly state this limitation… suggest alternative research directions"). No change needed. The "rather than speculating" clause gives the *why*.

### Low Priority

**L1. Rationale missing for the 5-step process**

File/lines: L11 "Your research process follows these steps:"

The 5 steps are listed, but the *why* of the process as a whole is implicit. A single sentence of rationale would help 4.7 adapt when a step doesn't fit (e.g., a narrow factual question may skip decomposition).

Current:
```
Your research process follows these steps:
```

Suggested after:
```
Your research process follows these five steps. Apply them to the extent they fit the question — narrow factual questions may collapse steps 1 and 2, while contested multi-stakeholder questions need all five.
```

Rationale: §2.2 "Explain the *why* — rationale > rules" and §3 "literal-scope gaps."

**L2. Citation format is prescribed inline; could be an XML example**

File/lines: L28-34

Current:
```
4. **Compile a Structured Report**: You organize your findings into a clear report with:
   - Executive summary (key findings in 3-5 bullet points)
   - Introduction stating the research scope
   - Main body organized by research questions or themes
   - Each claim supported by inline citations [Source Name, Year]
   - Conclusion highlighting key insights and implications
   - Full bibliography in a consistent format
```

Assessment: this is adequate. Per §2.5 "Examples: 3–5, relevant + diverse + wrapped in `<example>` tags" — one short example of the expected report shape would help, but the current structure list is sufficient for a capable model. Only worth doing if this agent's output quality is inconsistent.

**L3. Trailing whitespace / cleanliness**

File/lines: L3 has a trailing space at end; L4 is blank; L5 closes frontmatter. Not material.

### Already-good patterns (keep)

- Step 3 "Analyze and Summarize Findings" (L24-27) correctly names evaluation criteria (credibility, recency, methodology, consensus vs. conflicting viewpoints). Good §2.1 detail.
- Step 5 "Cross-Check for Objectivity and Accuracy" (L37-42) is a solid §3 "coverage-then-filter" analog (gather → verify → flag conflicts).
- "When you encounter conflicting information, you present all credible viewpoints" (L43) plus the evidence-strength phrases ("strong evidence suggests", "preliminary findings indicate", "experts disagree on…") — good calibration language, aligned with §2.6 positive framing.
- The limitation-disclosure instruction (L45-46) is correct and well-framed.

---

## Summary of rankings

| Agent | Priority | Count | Themes |
|---|---|---|---|
| task-splitter | High | 0 | — |
| task-splitter | Medium | 3 | Parallel reads in Step 1; literal-scope on "Fill in" instruction; optional *why* on contract rule |
| task-splitter | Low | 3 | One intensifier (`**IMPORTANT**:`), ambiguous list separator, table thresholds (already mitigated) |
| comprehensive-researcher | High | 4 | Name/description bias without stopping criteria (§3); no parallel tool-call guidance (§4); no tool selection (§2.1); no XML structure (§2.3) |
| comprehensive-researcher | Medium | 3 | "comprehensive" density in body; "strict" intensifier; process-rationale framing |
| comprehensive-researcher | Low | 3 | Rationale wrapper on the 5 steps; report-shape example; whitespace |

task-splitter is close to production-ready for 4.7 with three small polish edits. comprehensive-researcher needs meaningful rework on stopping criteria, parallelism guidance, tool selection, and structure before it can be trusted to avoid 4.7's over-thoroughness failure mode.
