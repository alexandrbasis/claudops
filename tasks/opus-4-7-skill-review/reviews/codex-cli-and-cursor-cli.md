# Review: codex-cli and cursor-cli skills (Opus 4.7 audit)

**Scope:** Cross-AI bridge skills that shell out to external CLIs (`codex` and `agent`). Files audited:

- `.claude/skills/codex-cli/SKILL.md` (223 lines)
- `.claude/skills/codex-cli/reference.md` (264 lines)
- `.claude/skills/codex-cli/templates.md` (187 lines)
- `.claude/skills/cursor-cli/SKILL.md` (170 lines)
- `.claude/skills/cursor-cli/reference.md` (182 lines)
- `.claude/skills/cursor-cli/templates.md` (209 lines)

**Lens:** INSIGHTS.md §3 (anti-patterns) and §4 (positive patterns), with particular attention to tool-use over-nudging, literal-scope gaps in *when* to invoke the external CLI, and intensifier hygiene.

**Overall verdict:** Both skills are mostly well-tuned for Opus 4.7 on the *how-to-invoke* layer (clear flag tables, explicit "cold start" framing, good token-optimization pattern). The weaknesses cluster on the *when-to-invoke* layer: triggers in the frontmatter and early body could cause 4.7 to over-dispatch to the external CLI, and several intensifiers (`Always`, `Never`, `mandatory`, `Critical`) are used as emphasis rather than as load-bearing guards. No coverage/filter concerns because these skills don't themselves rank severity — they delegate to the external model via the user-provided prompt.

---

## codex-cli

### High priority

#### H1. Frontmatter description is trigger-heavy and risks over-dispatch (§3 tool-use over-nudging)

**File:** `.claude/skills/codex-cli/SKILL.md:2-7`

**Current:**

```yaml
description: >-
  Run OpenAI Codex CLI for cross-AI code review or validation. Use when asked for
  'second opinion', 'codex review', 'cross-AI check', 'ask codex', 'run codex',
  or when another workflow needs cross-AI verification.
  NOT for interactive conversations (codex is one-shot only).
```

The trigger `when another workflow needs cross-AI verification` is under-scoped — any reviewing workflow could plausibly "need" cross-AI verification, and 4.7 is more action-biased than 4.6. INSIGHTS.md §3 flags broad triggers like *"Default to using [tool]"* as a cause of tool over-use; this phrasing reads similarly.

**Proposed:**

```yaml
description: >-
  Run OpenAI Codex CLI for one-shot cross-AI code review or approach validation.
  Invoke ONLY when the user explicitly asks ('second opinion', 'codex review',
  'ask codex', 'run codex', 'cross-AI check'), or when another skill passes an
  explicit instruction to delegate to codex. Do not invoke proactively on general
  review requests — the primary review skills handle those.
  Not for interactive conversations (codex is one-shot only).
```

**Why:** §3 anti-pattern "Default to using [tool]" → replace with "use [tool] **when** it would enhance X". The new wording states scope literally (INSIGHTS.md §3 "More literal; will NOT silently generalize" — use that in our favor by being literal about *not* invoking).

---

#### H2. "Always update codex to latest before running any command" over-triggers a shell call (§3 tool-use over-nudging + intensifier hygiene)

**File:** `.claude/skills/codex-cli/SKILL.md:41-52`

**Current:**

```markdown
## Prerequisite: Update First

**Always update codex to latest before running any command.** Codex releases frequently and older versions may have bugs (e.g., v0.115-0.116 approval loop regression).

```bash
# Step 1: Update to latest
npm i -g @openai/codex@latest > /dev/null 2>&1

# Step 2: Verify
codex --version
```
```

Two problems compound:

1. `Always update codex to latest before running any command` is an intensifier that, on 4.7, will cause a global `npm i -g` on every invocation. For a skill that might be invoked multiple times per session, this adds real wall-clock cost and — more importantly — is a write-mode side effect on the user's global npm cache that they did not opt into.
2. The *why* is stated (regression bug) but the scope ("before **any** command") is wider than justified.

**Proposed:**

```markdown
## Prerequisite: Verify Installation

Before the first codex call in a session, verify the binary works:

```bash
codex --version
```

Update only if (a) a command fails with an unknown-flag error, (b) the version is older than v0.116.1, or (c) the user explicitly asks. The reason: v0.115-0.116 had an approval-loop regression; older versions work fine for most reviews.

```bash
# Run only when needed, not automatically
npm i -g @openai/codex@latest
```
```

**Why:** §3 "`ALWAYS` used as intensifiers — dial back to normal voice". §4 "Don't add features… beyond what was asked" also applies — a silent global install is feature creep on the CLI-runner role.

---

#### H3. Heading `## Critical Rules` and sub-heading `### Token Optimization (mandatory)` stack intensifiers (§3)

**File:** `.claude/skills/codex-cli/SKILL.md:155-163`

**Current:**

```markdown
## Critical Rules

### Token Optimization (mandatory)

Without redirection, Bash returns ~4700+ tokens of verbose output. With `-o` + redirect, you get ~30 tokens.

**Pattern**: `-o /tmp/codex-result.md > /dev/null 2>&1 && echo "Codex completed"`

Always read the result with the **Read tool**, never `cat`.
```

The content is genuinely load-bearing (token cost is a real constraint), but three overlapping intensifiers in seven lines — `Critical`, `mandatory`, `Always`/`never` — is exactly the stacking §3 warns against. The rationale sentence ("~4700+ tokens → ~30 tokens") is already doing the persuasion work; the intensifiers are redundant.

**Proposed:**

```markdown
## Output capture

### Why it matters

Without redirection, Bash returns ~4700+ tokens of verbose output. With `-o` + redirect, you get ~30 tokens — a ~150× reduction. Use this pattern whenever you invoke codex.

**Pattern**: `-o /tmp/codex-result.md > /dev/null 2>&1 && echo "Codex completed"`

Read the result with the **Read tool** (not `cat`) so the file is registered with the harness and counted once.
```

**Why:** §2 rule 2 — "Explain the *why* — rationale > rules". The *why* (token math, harness registration) is stronger than "mandatory" and "Critical". §3 — drop the intensifier stack.

---

#### H4. "Critical: `codex review` vs `codex exec review`" can be demoted (§3 intensifier hygiene)

**File:** `.claude/skills/codex-cli/SKILL.md:54-67`

**Current heading:** `## Critical: `codex review` vs `codex exec review``

This section is *excellent* content-wise — the mutually-exclusive-flags table is exactly the kind of concrete, load-bearing information that belongs here. The intensifier `Critical:` in the heading is unnecessary because the table itself makes the stakes obvious.

**Proposed heading:** `## Command variants: `codex review` vs `codex exec review``

**Why:** §3 intensifier hygiene — reserve emphasis for cases where the prose alone wouldn't convey stakes. A comparison table comparing "NO / YES / works / empty" is already vivid.

---

### Medium priority

#### M1. Self-Update block encourages speculative WebFetch (§3 tool-use over-nudging)

**File:** `.claude/skills/codex-cli/SKILL.md:19-39`

**Current (excerpt):**

```markdown
Use `WebFetch` or `mcp__exa__web_search_exa` to check for updates when:
- A codex command fails with an unknown flag error
- The user mentions a codex feature not covered here
- It's been a while since the skill was last updated
```

The third bullet — `It's been a while since the skill was last updated` — is the over-nudge. It has no threshold, and 4.7's literal instruction-following will re-interpret "a while" every invocation. The first two bullets are sharp and should stay.

**Proposed:** Drop the third bullet, or make it concrete:

```markdown
Use `WebFetch` or `mcp__exa__web_search_exa` to check for updates when:
- A codex command fails with an unknown flag error
- The user mentions a codex feature not covered here
- The user explicitly asks to verify the skill against upstream docs
```

**Why:** §3 "`If in doubt, use [tool]` — causes tool over-use on 4.7" — vague temporal conditions behave the same as "if in doubt".

---

#### M2. "Codex Has No Context From This Conversation" block should include parallel-call guidance (§4 positive patterns)

**File:** `.claude/skills/codex-cli/SKILL.md:166-186`

The block is good at explaining the cold-start model. It omits one pattern that is very relevant for a cross-AI bridge: when a caller (e.g. `/sr`) asks for cross-AI verification against multiple sibling skills (codex, cursor, gemini), 4.7 under-parallelizes by default (§1 "Subagent spawning: more conservative").

**Proposed addition (new paragraph after line 186):**

```markdown
### Parallel with sibling CLI skills

When the caller wants perspectives from multiple external CLIs (e.g. codex + cursor + gemini) on the same diff or question, issue the three Bash calls in the same turn rather than sequentially. The calls have no dependency on each other and the external CLIs take 1-10 minutes each — serializing them multiplies wall-clock time.
```

**Why:** §4 "Parallel tool-calling… When calls have no dependencies, batch them in one turn."

---

#### M3. Background Execution section lacks a "when to use background" rationale (§2 rationale > rules)

**File:** `.claude/skills/codex-cli/SKILL.md:143-153`

**Current:** The section shows *how* to background but the trigger — `For complex tasks that take 2-10 minutes` — is the only gating condition, followed immediately by "Run with `run_in_background: true`".

4.7 will read this literally and may background every invocation where it expects >2 minutes, which is wasteful for simple reviews where the next action depends on the result anyway.

**Proposed refinement:**

```markdown
### 3. Background Execution (for long tasks *with parallel work*)

Use `run_in_background: true` only when you have a concrete non-codex task queued for the same turn (reading files, editing, running another CLI). If the next step is "wait for codex to finish and summarize", run synchronously — the notification overhead isn't worth it.
```

**Why:** §2 — rationale. §1 Opus 4.7 is more literal, so spelling out the condition prevents needless async dispatch.

---

#### M4. Reference section advertises exhaustive flag coverage (§3 "Be thorough / exhaustive / comprehensive")

**File:** `.claude/skills/codex-cli/reference.md:140-158`

**Current:**

```markdown
## Global Flags (apply to all commands)

| Flag | Description |
|---|---|
| `-m, --model MODEL` | Override model |
...
```

The content is fine. The concern is that the header `Global Flags (apply to all commands)` implies exhaustiveness, which then tempts the model to enumerate flags the user didn't ask about. Not urgent — this is a reference file loaded on demand, so the risk is low — but worth a framing tweak.

**Proposed header:**

```markdown
## Common global flags

These propagate to subcommands (but see the `codex review` caveat above).
```

**Why:** §3 — avoid framing that invites exhaustive recitation.

---

### Low priority

#### L1. `templates.md` hard-codes `model_reasoning_effort=xhigh` without the 4.7 rationale (§2)

**File:** `.claude/skills/codex-cli/templates.md:22-186` (every template)

Every template passes `-c model_reasoning_effort=xhigh`. That's a good default per INSIGHTS.md §1 (*"`xhigh` is recommended default for coding/agentic"*), but the skill never explains **why** to the user/caller. A one-line note near the top of the file would lock in the intent and prevent future edits dropping to `high` silently.

**Proposed addition (after line 14):**

```markdown
> **Reasoning effort**: Templates pin `model_reasoning_effort=xhigh`. That is the current Opus-era recommendation for coding/agentic cross-AI review — `max` over-thinks, `medium` under-thinks. Only override if the caller has a specific reason.
```

**Why:** §2 rule 2 (rationale), §1 (xhigh default).

---

#### L2. Announcement line is fine but verbose (§3 soft note)

**File:** `.claude/skills/codex-cli/SKILL.md:13`

**Current:**

```markdown
> **Announcement**: Begin with: "I'm using the **codex-cli** skill for cross-AI validation with Codex."
```

Minor redundancy — "codex-cli … with Codex". Not an Opus 4.7 concern, but if trimming: "I'm using the **codex-cli** skill for cross-AI validation." Leave as-is if preserving symmetry with cursor-cli is important.

---

## cursor-cli

### High priority

#### H1. Frontmatter description has the same over-dispatch risk as codex-cli (§3)

**File:** `.claude/skills/cursor-cli/SKILL.md:2-8`

**Current:**

```yaml
description: >-
  Run Cursor CLI (Composer 2 model) for cross-AI code review or validation. Use when asked for
  'cursor review', 'ask cursor', 'cross-AI check', 'run cursor', or when another workflow
  needs cross-AI verification with a non-OpenAI/non-Anthropic perspective.
  NOT for interactive conversations (cursor is one-shot only).
```

Same issue as codex-cli H1 — `or when another workflow needs cross-AI verification` is broad. Additionally the trigger `cross-AI check` overlaps with codex-cli's identical trigger, meaning 4.7 may invoke either (or both) for that phrase.

**Proposed:**

```yaml
description: >-
  Run Cursor CLI (Composer 2, a Kimi-K2.5 lineage) for one-shot cross-AI code
  review when a non-OpenAI/non-Anthropic perspective is specifically wanted.
  Invoke ONLY when the user explicitly asks ('cursor review', 'ask cursor',
  'run cursor'), or when another skill passes an explicit instruction to
  delegate to cursor. For generic 'cross-AI check' requests, the caller skill
  should pick the specific CLI; do not invoke both cursor and codex implicitly.
  Not for interactive conversations (cursor is one-shot only).
```

**Why:** §3 — "Default to using [tool]" → narrow to explicit triggers. §1 — Opus 4.7 "more literal" gives us room to disambiguate between sibling skills by naming the overlap explicitly.

---

#### H2. "Always update cursor agent CLI to latest before running" — same issue as codex H2 (§3 intensifier + tool-use over-nudge)

**File:** `.claude/skills/cursor-cli/SKILL.md:41-52`

**Current:**

```markdown
## Prerequisite: Update First

**Always update cursor agent CLI to latest before running.** Releases are frequent.

```bash
# Step 1: Update to latest
curl https://cursor.com/install -fsS | bash > /dev/null 2>&1

# Step 2: Verify
agent --version
```
```

This is more concerning than codex H2 because `curl … | bash` is a root-privilege install script that downloads and executes remote code. Running it on every invocation is a security and correctness smell — a transient network blip or upstream hosting change could silently break the user's tooling, and the `> /dev/null 2>&1` redirect hides install errors.

**Proposed:**

```markdown
## Prerequisite: Verify Installation

Before the first cursor call in a session:

```bash
agent --version
```

Update only if (a) a flag fails with an unknown-flag error, (b) the user explicitly asks, or (c) the version is older than the one pinned at the top of this file. The install script is a `curl | bash` — run it interactively, not silently, so the user sees any installer output:

```bash
# Run only when needed
curl https://cursor.com/install -fsS | bash
```
```

**Why:** §3 "`ALWAYS` as intensifier" and §4 "Don't add features… beyond what was asked" (silent reinstall = feature creep). Also a user-safety concern that's orthogonal to 4.7 but worth flagging.

---

#### H3. "Always Use `--model composer-2`" and "Always Use `--mode=ask` and `--trust`" stack intensifiers (§3)

**File:** `.claude/skills/cursor-cli/SKILL.md:108-121`

**Current:**

```markdown
### Always Use `--model composer-2`

Composer 2 is Cursor's frontier in-house model (fine-tuned Kimi K2.5 with RL on long-horizon coding tasks). It provides a unique non-OpenAI/non-Anthropic perspective for cross-AI validation. Always pass `--model composer-2` explicitly.

### Always Use `--mode=ask` and `--trust`

- `--mode=ask` ensures read-only operation — Cursor will not modify any files during cross-AI validation.
- `--trust` bypasses the workspace trust prompt, which would otherwise block non-interactive execution.
- **Never** use `--force` or `--yolo` for cross-AI validation reviews.
```

Three `Always` plus a `Never` in 14 lines. The content is load-bearing (read-only mode for a review skill is genuinely important), but the stacked intensifiers will cause 4.7 to over-emphasize rather than internalize the reason.

**Proposed:**

```markdown
### Required flags for cross-AI review

| Flag | Why |
|---|---|
| `--model composer-2` | Pins to Cursor's Kimi-K2.5 lineage — the whole reason to use this skill instead of codex/gemini. Without it, you get a default that may duplicate another CLI. |
| `--mode=ask` | Read-only mode, enforced at the CLI level. A review must not modify files. |
| `--trust` | Bypasses the workspace-trust prompt, which would otherwise hang headless mode. |

Do not use `--force` or `--yolo` here — those authorize writes, which defeats the read-only guarantee above.
```

**Why:** §3 intensifier hygiene. §2 "Explain the *why*". §4 "Positive framing beats negative" — the table replaces three `Always`es with three `Why`s.

---

#### H4. `## Critical Rules` heading + `### Token Optimization (mandatory)` — same stacking as codex (§3)

**File:** `.claude/skills/cursor-cli/SKILL.md:95-107`

**Current:**

```markdown
## Critical Rules

### Token Optimization (mandatory)

Without redirection, Bash returns thousands of tokens of verbose output. With the redirect pattern, you get ~30 tokens.

**Pattern**: `--output-format text > /tmp/cursor-result.txt 2> /dev/null && echo "Cursor completed"`

Always read the result with the **Read tool**, never `cat`.
```

Identical issue to codex-cli H3. Same fix.

**Proposed:**

```markdown
## Output capture

### Why it matters

Without redirection, Bash returns thousands of tokens of verbose output. With the redirect pattern, you get ~30 tokens. Use this pattern on every invocation.

**Pattern**: `--output-format text > /tmp/cursor-result.txt 2> /dev/null && echo "Cursor completed"`

Read with the **Read tool** (not `cat`) so the file is registered with the harness and counted once.
```

---

### Medium priority

#### M1. Self-Update block has the same vague "been a while" trigger (§3)

**File:** `.claude/skills/cursor-cli/SKILL.md:28-35`

Mirrors codex-cli M1. Drop the "It's been a while since the skill was last updated" bullet or tie it to an explicit user request.

---

#### M2. No parallel-CLI guidance (§4 positive patterns)

**File:** `.claude/skills/cursor-cli/SKILL.md:130-143`

Same gap as codex M2 — the "Cursor Has No Context From This Conversation" section is good but omits the hint that when a caller requests multiple CLI perspectives (cursor + codex + gemini), those calls should be batched into one turn. Add the same paragraph as proposed in codex M2, with "sibling CLI skills" framing.

---

#### M3. "When NOT to Use" list is underspecified for a bridge skill (§1 literal-scope)

**File:** `.claude/skills/cursor-cli/SKILL.md:151-155`

**Current:**

```markdown
### When NOT to Use

- Simple, quick tasks (overhead not worth the 1-10 min wait)
- Tasks requiring interactive conversation/refinement
- Trivial changes (typos, formatting)
```

Good list, but missing the most common failure mode for a *cross-AI* bridge: "The user wants a code review, full stop" — that's what primary review skills (`/sr`, `/prc`) are for. Without this bullet, 4.7 may invoke cursor-cli *in place of* the primary reviewer rather than *in addition to* it.

**Proposed addition:**

```markdown
- General "review this code" requests where no sibling-AI perspective was asked for — those belong to `/sr` or other primary-review skills; cursor-cli supplements, it does not replace.
- When the user is iterating live on code and wants fast feedback — primary Claude is lower-latency.
```

**Why:** §1 "more literal; will not silently generalize" — we must state the negative scope that used to be implicit.

---

#### M4. Templates.md encourages multi-model loop (§3 tool over-use)

**File:** `.claude/skills/cursor-cli/templates.md:180-195`

**Current:**

```markdown
### Multi-Model Comparison

Run the same prompt with different models to get diverse perspectives:

```bash
# Composer 2 (default — Kimi K2.5 fine-tune)
agent -p "[review prompt]" --model composer-2 # ...pipeline

# GPT-5.4 (for OpenAI perspective)
agent -p "[review prompt]" --model gpt-5.4-medium # ...pipeline

# Gemini 3.1 Pro (for Google perspective)
agent -p "[review prompt]" --model gemini-3.1-pro # ...pipeline
```
```

The template is useful but silent on *when* to fan out. On 4.7, an action-biased read of "Run the same prompt with different models" will fire three 1-10-minute CLI calls as the default.

**Proposed addition (before the code block):**

```markdown
Use this only when the caller explicitly asks for multi-model fan-out, or when a high-stakes decision justifies ~10 minutes of extra CLI time. Default to a single `composer-2` run. When you do fan out, batch the three calls into one turn (they have no dependency on each other).
```

**Why:** §3 "Default to using [tool]" anti-pattern + §4 "Parallel tool-calling… batch them in one turn".

---

### Low priority

#### L1. "Cursor starts with zero context" — same as codex, already good (§2)

**File:** `.claude/skills/cursor-cli/SKILL.md:130-146`

The section is tight, states the *why* (no conversation carryover), and gives a concrete `{{SRC_DIR}}` example. No change needed — call this out as a positive anchor for how other sections should read.

---

#### L2. Reference file's "Always use `--model composer-2`" duplicates SKILL.md intensifier (§3)

**File:** `.claude/skills/cursor-cli/reference.md:68-72`

**Current:**

```markdown
### Default Model: `composer-2`

Always use `--model composer-2` for cross-AI validation. Composer 2 is Cursor's frontier in-house model — fine-tuned Kimi K2.5 with reinforcement learning on long-horizon coding tasks.
```

If H3 is adopted, align this to "Required model: …" and drop the `Always`. Otherwise leave — reference files are lower-risk because they're loaded on demand.

---

## Cross-skill observations

1. **Shared symmetry is good.** Both skills follow the same structure (frontmatter → announcement → self-update → prerequisite → core patterns → critical rules → reference files). Keep that — it helps the caller skill (`/sr`, etc.) swap between them.

2. **Both skills lack a "choosing between sibling CLIs" note.** Neither SKILL.md tells the invoking agent *which* CLI to pick when the caller just says "cross-AI check". Add a short 2-line cross-reference block (e.g. "See also: codex-cli (GPT-5.4 perspective), gemini-cli (Google web-grounded perspective). This skill = Kimi-K2.5 via Composer 2.") to help 4.7's more-literal scope selection.

3. **No prefill / pre-compact-guard concerns.** Neither skill uses deprecated assistant-turn prefill patterns. Neither is long-running enough to need `§4` compaction-aware prompting.

4. **No coverage/filter issue.** These skills delegate severity ranking to the external model via the caller's prompt — they don't themselves filter results, so INSIGHTS.md §3 "Only report high-severity" anti-pattern does not apply.

5. **Token-optimization patterns are well-engineered.** The `-o /tmp/*.md > /dev/null 2>&1 && echo "…"` pattern is genuinely load-bearing and should stay. The only change is removing the intensifier framing around it.

---

## Summary of priorities

| # | Skill | Finding | Priority | INSIGHTS ref |
|---|---|---|---|---|
| codex H1 | codex-cli | Frontmatter trigger too broad | High | §3 tool over-use |
| codex H2 | codex-cli | "Always update" → silent global npm install | High | §3 intensifier + §4 scope |
| codex H3 | codex-cli | "Critical Rules / mandatory / Always" stack | High | §3 intensifier |
| codex H4 | codex-cli | `## Critical:` heading redundant | High | §3 intensifier |
| codex M1 | codex-cli | "Been a while" self-update trigger | Medium | §3 "if in doubt" |
| codex M2 | codex-cli | No parallel-with-sibling-CLI guidance | Medium | §4 parallel calls |
| codex M3 | codex-cli | Background-execution trigger underspecified | Medium | §2 rationale |
| codex M4 | codex-cli | "Global flags" header implies exhaustiveness | Medium | §3 "exhaustive" |
| codex L1 | codex-cli | `xhigh` rationale missing from templates | Low | §2 rationale |
| codex L2 | codex-cli | Announcement line minor verbosity | Low | — |
| cursor H1 | cursor-cli | Frontmatter trigger + overlap with codex | High | §3 tool over-use |
| cursor H2 | cursor-cli | Silent `curl \| bash` install | High | §3 intensifier + safety |
| cursor H3 | cursor-cli | Three `Always` + one `Never` stack | High | §3 intensifier |
| cursor H4 | cursor-cli | "Critical Rules / mandatory" same as codex | High | §3 intensifier |
| cursor M1 | cursor-cli | "Been a while" self-update trigger | Medium | §3 "if in doubt" |
| cursor M2 | cursor-cli | No parallel-with-sibling-CLI guidance | Medium | §4 parallel calls |
| cursor M3 | cursor-cli | "When NOT to Use" missing "use instead of /sr" anti-case | Medium | §1 literal scope |
| cursor M4 | cursor-cli | Multi-Model Comparison invites fan-out by default | Medium | §3 tool over-use |
| cursor L1 | cursor-cli | "Zero context" section — positive anchor, no change | Low | — |
| cursor L2 | cursor-cli | reference.md duplicates `Always use composer-2` | Low | §3 intensifier |

**Net assessment:** Both skills are structurally sound and factually accurate (flag tables, model names, command variants all check out against the reference files). The consistent issue is emphasis-stacking — `Always`/`Critical`/`mandatory`/`Never` appearing together where the underlying rationale already carries the weight. Fixing the four High-priority items per skill would align the tone with Opus 4.7's adaptive, more-literal disposition without changing any of the load-bearing behavior.
