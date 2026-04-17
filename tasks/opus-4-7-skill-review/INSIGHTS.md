# Opus 4.7 Prompting Insights — Skill Audit Reference

**Sources:**
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://claude.com/blog/best-practices-for-using-claude-opus-4-7-with-claude-code

These insights are the lens through which you must review the assigned skills. Every recommendation you make must cite one of the patterns below.

---

## 1. Behavior deltas: what changed in Opus 4.7 (vs 4.6)

| Area | 4.7 default | What it means for prompts |
|---|---|---|
| **Response length** | Calibrated to task complexity, not fixed verbosity | Terse on simple tasks, long on complex. Positive examples tune output better than negative ("don't…") instructions. |
| **Effort tiers** | New `xhigh` tier between `high` and `max`; `xhigh` is recommended default for coding/agentic | `max` risks overthinking; `low`/`medium` under-think on complex tasks. |
| **Thinking** | **Adaptive only** — `budget_tokens` deprecated | Control via `effort` + prompt nudges ("think carefully" to raise, "respond directly" to lower). |
| **Tool use** | Less frequent — reasons more before calling tools | Prompts that previously *nudged* tool use may now be unnecessary or cause over-reasoning. |
| **Subagent spawning** | More conservative by default | Must **explicitly** tell it to fan out across files/items for parallelism. |
| **Instruction following** | More literal; will NOT silently generalize | State scope explicitly ("apply to every section, not just the first"). |
| **Prefill (last assistant turn)** | Deprecated; errors on Mythos Preview | Migrate to Structured Outputs, XML output tags, or direct instructions. |
| **Frontend defaults** | Strong "cream/serif/terracotta" house style — persistent | Specify concrete alternative palettes; or ask it to propose 4 directions first. |
| **Sampling** | `temperature` removed | For variety, ask for N proposals. |
| **Overeagerness / over-engineering** | 4.5 and 4.6 both tend to over-engineer; 4.7 more literal but still drifts | Add explicit "minimize scope / no new abstractions" guidance where relevant. |
| **Code-review harnesses** | Obey severity/confidence filters **more literally** — recall may *appear* to drop | Prompt for **coverage** at find stage, **filter** in a separate stage. |
| **Interactive coding** | More post-user-turn reasoning → more tokens | Front-load full context in turn 1; minimize interactive back-and-forth. |
| **Design/frontend** | Distinctive out of the box; prior lengthy aesthetic prompts now cause overcorrection | Tight `<frontend_aesthetics>` block is enough. |

## 2. Foundational techniques still true

1. **Golden rule**: If a new colleague couldn't follow the prompt, Claude can't either.
2. **Explain the *why*** — rationale > rules. "Your response is read aloud by TTS" beats "never use ellipses".
3. **XML tags** for structure: `<instructions>`, `<context>`, `<input>`, `<document>`, `<example>`.
4. **Long context**: put documents **at the top**, query at the bottom — up to 30% quality lift.
5. **Examples**: 3–5, relevant + diverse + wrapped in `<example>` / `<examples>` tags.
6. **Positive framing** beats negative: "write flowing prose" > "no markdown".
7. **Quote-ground**: for long docs, ask Claude to extract relevant quotes first, then reason.
8. **Role assignment** in system prompt focuses behavior.
9. **Match prompt style to desired output** (e.g., no markdown in prompt → less markdown out).

## 3. Anti-patterns to grep for in skills

These are the specific phrases/patterns that *used* to help but now backfire on 4.7:

- `CRITICAL:`, `You MUST`, `ALWAYS`, `NEVER` used as intensifiers — dial back to normal voice. The model is already more responsive; these now cause **over-triggering**.
- `If in doubt, use [tool]` — causes tool over-use on 4.7.
- `Default to using [tool]` — too broad; replace with "use [tool] **when** it would enhance X".
- `Be thorough / exhaustive / comprehensive` with no stopping condition — causes overthinking and scope creep.
- `Do not suggest, make the changes` used too aggressively in contexts where user wants a plan first — 4.7 is now more action-biased, this may over-trigger edits.
- `Think step-by-step` as reflexive boilerplate — only helps when genuinely multi-step.
- `Only report high-severity / important issues` in review skills — 4.7 obeys literally → recall drops.
- Hard-coded response-length caps (e.g. "respond in 1 sentence") that fight 4.7's adaptive length.
- Pre-filled assistant turns / `<assistant>` prefills at the end — deprecated.
- Broad instructions like "don't use cream backgrounds" — these shift the model to *a different fixed default*, not variety.

## 4. Positive patterns to add / reinforce

- **Coverage-then-filter split** for review skills:
  > *"Report every issue you find, including low-severity and uncertain ones. Include confidence + severity. A separate verification step will filter."*
- **Context-awareness for long skills:**
  > *"Context will be automatically compacted. Do not stop early due to token concerns. Save state to memory before refresh."*
- **Parallel subagent prompting** (because 4.7 under-parallelizes):
  > *"Spawn multiple subagents in the same turn when fanning out across files or independent items. Do not default to sequential."*
- **Parallel tool-calling** (same reason):
  > *"When calls have no dependencies, batch them in one turn. Never use placeholders or guess missing parameters."*
- **Investigate-before-answering** (for code-reading skills):
  > *"Never speculate about code you have not opened. If the user references a file, read it before answering."*
- **Minimize over-engineering** (for implementation skills):
  > *"Don't add features, abstractions, or cleanup beyond what was asked. Bug fixes don't need surrounding refactors. No defensive error handling for scenarios that can't happen."*
- **State scope explicitly** when 4.7 needs to generalize:
  > *"Apply this to every file touched, not only the first."*
- **For design/variety:**
  > *"Before building, propose N distinct directions (each a one-line rationale). Ask the user to pick one."*

## 5. Audit checklist per skill

For each skill file, evaluate along these axes and cite concrete line numbers:

1. **Intensifier hygiene** — any `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` used as emphasis (not genuinely load-bearing)? Dial back.
2. **Tool-use over-nudging** — phrases that would cause 4.7 to over-use tools?
3. **Subagent / parallel calls** — does the skill spawn subagents? If so, does it explicitly tell 4.7 to parallelize when work is independent?
4. **Filter leakage in review skills** — does the skill ask for "only important" / "high severity"? Needs coverage-then-filter split.
5. **Response-length constraints** — any hard caps that fight adaptive length?
6. **Literal-scope gaps** — places where the prompt assumes the model will generalize (it won't in 4.7)?
7. **Verbosity-nudging instructions** — negative framing ("don't be verbose", "skip preamble") should become positive ("write direct, fact-forward responses").
8. **Prefill patterns** — any assistant-turn prefill that needs migration?
9. **Context-awareness** — for long-running skills, is the compaction-aware prompt present?
10. **Over-engineering mitigation** — for implementation skills, is the "don't add beyond what was asked" guard present?
11. **`why` vs `rule`** — are rules stated without rationale? Add the *why*.
12. **XML structure** — where prompts mix instructions + context + examples, are XML tags used?

## 6. Style of your output

- Cite specific file paths and line numbers (e.g. `.claude/skills/nf/SKILL.md:42`).
- Quote the offending text exactly when proposing a change.
- Provide **before → after** snippets, not just prose descriptions.
- Rank each recommendation **High / Medium / Low** priority.
- Do **not** modify any skill files. Only produce the review document.
- If a skill is already well-tuned, say so — don't invent issues.
