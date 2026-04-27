---
name: nf
description: >-
  Conduct in-depth feature discovery interview to explore, challenge, and document a new feature.
  Use when asked to 'detail a feature', 'explore a new feature', 'feature discovery',
  'interview about feature', 'spec out a feature', 'design a feature',
  'think through a feature', 'let's spec this out', 'deep dive on a feature',
  'what should we consider for [feature]', or 'discover [feature-name]'.
  NOT for quick brainstorming (use /brainstorm),
  NOT for PRD/JTBD docs (use /product), NOT for implementation tasks (use /ct).
argument-hint: [feature-description]
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion, Task, Skill
---

# New Feature Discovery

> **Announcement**: Begin with: "I'm using the **nf** skill for feature discovery."

## Objective
Conduct a discovery interview that turns a rough feature idea into a clear, easy-to-read discovery document. The output should serve as the entry point for anyone who later needs to visualize, plan, or implement the feature.

## Guidelines
- Use `AskUserQuestion` for any clarification that the user hasn't already answered — structured options reduce ambiguity and keep the interview auditable.
- If behavior is unclear (UX flow, edge cases, error handling, states), ask the user to define it rather than inferring. Downstream `/vp` and `/ct` trust this document as the source of truth, so silent assumptions compound.
- Ask non-obvious and thought-provoking questions
- Challenge assumptions actively. When the user's answer sounds confident but under-specified, name the gap ("You said X — does that cover case Y?") rather than accepting it at face value.
- Offer alternatives, shortcuts, and "go deeper" paths
- Continue until the feature is fully understood
- Work with the final discovery template in mind throughout the interview
- Gather exactly the information needed to fill the discovery document clearly

**Context management.** This workflow can run long (design-exploration + research + interview + grill + validators). If you notice a compaction event or context refresh:
- Re-read any already-created task files in the task directory before continuing.
- Re-open the discovery template to reconfirm output shape.
- Do not restart discovery from scratch — resume from the last unanswered template section.
Do not stop early due to token-budget worries — the parent harness handles compaction.

## Workflow

### Argument Validation

**If no `[feature-description]` argument is provided:**
1. Use `AskUserQuestion`: "What feature would you like to explore?"
   - Include a free-text "Describe a new feature" option
2. Derive the feature-name slug from the user's response

### Step 0: Load the Output Shape and Upstream Context

Before asking deep-dive questions, read `.claude/docs/templates/discovery-template.md` to understand the expected structure, level of clarity, and final shape of the discovery document.

Treat the template as the **output contract**:
- It defines what the final document should contain
- The discovery interview should gather exactly the information needed to fill it clearly
- Do not duplicate the template structure inside this skill; use the template itself as the source of truth for the final document shape

**Load upstream product docs** (if they exist):
- Check `product-docs/PRD/PRD-*[feature-name]*.md` for an existing PRD
- Check `product-docs/JTBD/JTBD-*[feature-name]*.md` for an existing JTBD
- If found, read them as input context — they define the product-level "what and why" that this discovery will explore in depth. Reference them in the discovery document.

**Load shared glossary**: If `product-docs/UBIQUITOUS_LANGUAGE.md` exists, read it and use its terms verbatim during the interview. Flag any conflict between user wording and the glossary immediately rather than silently drifting. If the glossary is missing or new domain terms come up, plan to invoke `/ubiquitous-language` after the grill round (Step 4 → Step 5 transition).

### Step 1: Context Gathering & Design Exploration

**Invoke the `design-exploration` skill** to ground discovery in the real codebase.

When invoking, ask it to return:
- Key codebase findings and current fit
- Viable design directions
- Constraints discovered in the existing system
- Risk flags or open decisions

For discovery work, prefer fit, options, constraints, and risks over implementation decomposition.

**Checkpoint:** Present findings summary and initial approach. `AskUserQuestion`: "Does this direction look right?" Options: "Continue with this approach" / "Explore a different direction" / "I have corrections"

### Step 2: External Research (If Needed)

When you need current information, best practices, or technical research:

- **Quick lookups**: Use Exa MCP tools when the user asserts a factual claim about an external product, spec, or standard that you can't verify from the codebase or prior turns. Skip Exa if the question is about internal codebase behavior (design-exploration covers that) or about subjective product preference.
- **In-depth research**: Spawn `comprehensive-researcher` only when the answer materially affects the chosen direction, scope boundaries, key requirements, or constraints.

When invoking `comprehensive-researcher`, ask for a **concise decision memo for discovery**, not a broad general report by default. The memo should return:
- Key findings
- Implications for feature shape or scope
- Risks or caveats
- Unresolved external unknowns

Topics to research:
- Industry best practices for the feature type
- Competitor implementations and patterns
- API/library capabilities and limitations
- Security considerations and compliance requirements

### Step 3: Deep-Dive Questions

Drive the conversation toward the sections of the discovery template. Ask additional **non-obvious** questions until the final document can be filled clearly and read as a standalone entry point.

**Feature Overview / Why This Exists:**
- What is the feature in plain language?
- What problem or opportunity does it address?
- Why does it matter now?
- What value should it create for the user or product?

**Usage Context** (only if it adds clarity):
- Who is the primary user or actor?
- When does this feature matter?
- What surrounding context, prior state, or constraints affect usage?

**Chosen Direction** (only if multiple viable approaches exist):
- What direction was selected?
- What alternatives were considered?
- Why is this direction preferred?

**How It Works:**
- Entry points
- Main happy path
- Key states (loading, empty, error, success, variants)
- Important edge cases that materially shape the feature

**Scope Boundaries:**
- What is explicitly in scope for this version?
- What is explicitly out of scope?
- Where could the scope accidentally expand?

**Key Requirements / Constraints:**
- Must-have behaviors
- Integration points and dependencies
- Security, accessibility, performance, privacy, or platform limitations that materially shape the feature
- Assumptions the downstream implementation must preserve

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

Stop the deep-dive when every template section has an answer the user has confirmed once — don't keep re-confirming. If a section would require speculation, ask once, accept "skip / TBD" as a valid answer, and note it in the draft as `[NEEDS CLARIFICATION: ...]`. The document does not have to be perfect before writing — the grill round catches real gaps.

### Step 4: "Grill Me" Challenge Round

Now that the draft shape is clear, **invoke the `/grill-me` skill** to pressure-test the feature design and the document's clarity.

**Before invoking**, summarize the current state for the grill session:
- Feature name and description
- Why this exists
- Chosen direction (if any)
- How it works
- In scope / out of scope boundaries
- Key requirements and constraints
- Any areas of uncertainty or risk already identified

**After the grill session completes:**
- Incorporate all findings and decisions back into the feature understanding
- Tighten unclear wording, scope boundaries, hidden assumptions, and missing states or edge cases

**Update shared glossary** (before writing the discovery doc): if the grill or interview surfaced new domain terms, synonym conflicts, or sharpened a fuzzy term, invoke `/ubiquitous-language` to update `product-docs/UBIQUITOUS_LANGUAGE.md`. The discovery doc then uses canonical terms, and downstream `/vp`, `/ct`, `/si` inherit the same vocabulary.

**Checkpoint:** `AskUserQuestion`: "How should we proceed?" Options: "Proceed to discovery document" / "Revisit design based on findings" / "Cut scope based on grill findings"

### Completion Check

One-pass completion check (not a loop): verify the six questions below have at least a one-sentence answer in the draft:
- What is this feature?
- Why does it exist?
- How does it work?
- What is in scope?
- What is out of scope?
- What requirements or constraints materially shape it?

If two or fewer are weak, flag them inline and proceed to writing — `/grill-me` and cross-AI validation will catch real blockers. If more than two are missing, run a single additional round of questions, then proceed regardless.

### Step 5: Discovery Document Writing

After interview completion:

1. Re-read `.claude/docs/templates/discovery-template.md` before writing. Long interviews drift from the template shape, and re-reading takes <5s while preventing section order/heading mismatches that downstream `/vp` and `/ct` parsers depend on.
2. **Create task directory**: `tasks/task-YYYY-MM-DD-[feature-name]/`
3. **Write discovery document** by filling the template with the decisions, flows, scope boundaries, requirements, and constraints resolved during discovery
   - Output file: `discovery-[feature-name].md`
4. **If any required section cannot be filled clearly**, continue discovery instead of finalizing the document
5. **Present summary** to user for confirmation


### Step 6: Cross-AI Validation

The skill initialization step loads each validator's CLI contract, so invent underlying CLI commands will produce unreliable results — run the skill initializer first for each.

Two phases — initialization (sequential), then review (parallel):

Phase 1 — Initialization. Invoke `/codex-cli`, `/gemini-cli`, `/cursor-cli` one at a time to load each validator's CLI contract. The skills need to run in turn because they modify runtime state.

Phase 2 — Review. In a single assistant turn, dispatch all three validator runs as parallel tool calls (one turn, three tool invocations). Reviews are independent, so sequential execution only adds latency. If one validator is unavailable, dispatch the other two anyway.

Format output per `.claude/docs/templates/cross-ai-protocol.md` (comparison table, validation, verdict).

- **FOCUS**: Discovery document review as senior product analyst — entry-point readability, completeness, consistency, flow clarity, scope boundaries, feasibility, and hidden ambiguities that would cause confusion in `/vp` or `/ct`
- **FILE_REFS**: `discovery-[feature-name].md` + relevant codebase paths
- **OUTPUT**: Append "Cross-AI Validation: PASSED/FAILED" with consolidated verdict

**If validation fails**: Present valid findings via `AskUserQuestion`: "Revise discovery doc" / "Override and proceed" / "Abandon feature".

**Skip conditions**: No CLI available, or user explicitly skips.

## Output
`tasks/task-YYYY-MM-DD-[feature-name]/discovery-[feature-name].md`

## Handoff — Next Steps

After discovery is complete, present to the user:
```
Discovery complete for [feature-name]:
- Document: tasks/task-YYYY-MM-DD-[feature-name]/discovery-[feature-name].md

Next steps:
→ Visualize the design: /vp [feature-name]
→ Skip to tech planning: /ct [feature-name]
``