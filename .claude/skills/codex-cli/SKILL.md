---
name: codex-cli
description: >-
  Run OpenAI Codex CLI for one-shot cross-AI code review or approach validation.
  Invoke ONLY when the user explicitly asks ('second opinion', 'codex review',
  'ask codex', 'run codex', 'cross-AI check'), or when another skill passes an
  explicit instruction to delegate to codex. Do not invoke proactively on general
  review requests — the primary review skills handle those.
  Not for interactive conversations (codex is one-shot only).
allowed-tools:
  - Bash
  - Read
---

# Codex CLI Integration Skill

> **Announcement**: Begin with: "I'm using the **codex-cli** skill for cross-AI validation with Codex."

Invoke OpenAI Codex CLI for one-shot code review, approach validation, and cross-AI verification.

## Self-Update: Official Documentation

When the skill feels outdated (wrong flags, unknown model, new features), consult these
official sources to update commands and reference files:

| Resource | URL |
|---|---|
| CLI Overview | https://developers.openai.com/codex/cli/ |
| CLI Features | https://developers.openai.com/codex/cli/features/ |
| Command Reference | https://developers.openai.com/codex/cli/reference/ |
| Config Reference | https://developers.openai.com/codex/cli/config-reference/ |
| Changelog | https://developers.openai.com/codex/changelog/ |
| GitHub Repo | https://github.com/openai/codex |
| npm Package | https://www.npmjs.com/package/@openai/codex |

Use `WebFetch` or `mcp__exa__web_search_exa` to check for updates when:
- A codex command fails with an unknown flag error
- The user mentions a codex feature not covered here
- The user explicitly asks to verify the skill against upstream docs

> **Last verified**: v0.116.0 (March 2026), default model `gpt-5.4`

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

If codex is not installed at all:
```bash
npm i -g @openai/codex
```

## Command variants: `codex review` vs `codex exec review`

These are **NOT equivalent** — they have different flag sets:

| Command | Has `--full-auto`? | Has `-m`? | Has `-o` (working)? | Prompt + scope flags? |
|---|---|---|---|---|
| `codex review` (top-level) | NO | NO | NO | N/A |
| `codex exec review` | YES | YES | `-o` writes empty! | **Mutually exclusive** |
| `codex exec` | YES | YES | YES (works) | N/A |

**Use `codex exec review`** for scoped reviews (scope flags auto-select the diff).
**Use `codex exec`** when you need both a custom prompt AND full output capture via `-o`.

The top-level `codex review` only supports: `--uncommitted`, `--base`, `--commit`, `--title`, `-c`, `--enable`, `--disable`.

## Core Patterns

### 1. Custom Prompt (most common)

```bash
codex exec "[prompt with explicit file paths]" \
  -m gpt-5.4 --full-auto \
  -o /tmp/codex-result.md > /dev/null 2>&1 && echo "Codex completed"
```
Then read with **Read tool**: `/tmp/codex-result.md`

### 2. Code Review

**v0.116.0 constraints** (tested and verified):
- Scope flags (`--uncommitted`, `--base`, `--commit`) are **mutually exclusive** with `[PROMPT]`
- `-o` flag writes **empty** for review commands — review output goes to stderr
- Must capture stderr to file: `2> /tmp/codex-review.md`

#### Option A: Scoped review (no custom prompt — codex decides what to focus on)

```bash
# Against branch (auto-generated review)
codex exec review --base main \
  -m gpt-5.4 --full-auto \
  2> /tmp/codex-review.md && echo "Review completed"

# Uncommitted changes
codex exec review --uncommitted \
  -m gpt-5.4 --full-auto \
  2> /tmp/codex-review.md && echo "Review completed"

# Specific commit
codex exec review --commit [SHA] \
  -m gpt-5.4 --full-auto \
  2> /tmp/codex-review.md && echo "Review completed"
```

#### Option B: Custom prompt review (codex decides scope — PREFERRED)

Pass a detailed prompt WITHOUT scope flags. Codex will figure out the diff context.

```bash
codex exec review \
  -m gpt-5.4 --full-auto \
  "Review the uncommitted changes in this repo. Focus on:
1. Correctness and edge cases
2. Error handling
3. Security concerns

Key files: [list relevant files or modules]
Requirements: [link to task doc or brief description]" \
  2> /tmp/codex-review.md && echo "Review completed"
```

#### Option C: Use `codex exec` instead of `codex exec review` (full control)

When you need both scope control AND a custom prompt, use plain `codex exec`:

```bash
codex exec "Review the git diff between main and HEAD. Focus on:
1. [Focus area 1]
2. [Focus area 2]

Context: [what this branch implements]
Check against: [task-file-path]" \
  -m gpt-5.4 --full-auto \
  -o /tmp/codex-review.md > /dev/null 2>&1 && echo "Review completed"
```
Then read with **Read tool**: `/tmp/codex-review.md`

> **Note on stderr capture**: Review output in stderr includes verbose logs (diffs, commands).
> The actual review findings are at the **end** of the file. When reading, scan for lines
> starting with `- [P` (priority findings) or `Review comment:` markers.

### 3. Background Execution (for long tasks *with parallel work*)

Use `run_in_background: true` only when you have a concrete non-codex task queued for the same turn (reading files, editing, running another CLI). If the next step is "wait for codex to finish and summarize", run synchronously — the notification overhead isn't worth it.

```bash
# Use Bash tool with run_in_background=true
codex exec "[complex prompt]" -m gpt-5.4 --full-auto \
  -o /tmp/codex-result.md > /dev/null 2>&1 && echo "Codex completed"
```

**Workflow**:
1. Run with `run_in_background: true` on the Bash tool
2. Continue working on other tasks while codex runs
3. You'll be notified automatically when it completes
4. Read `/tmp/codex-result.md` with the Read tool
5. Summarize findings to the user

## Output capture

### Why it matters

Without redirection, Bash returns ~4700+ tokens of verbose output. With `-o` + redirect, you get ~30 tokens — a ~150× reduction. Use this pattern whenever you invoke codex.

**Pattern**: `-o /tmp/codex-result.md > /dev/null 2>&1 && echo "Codex completed"`

Read the result with the **Read tool** (not `cat`) so the file is registered with the harness and counted once.

### Codex Has No Context From This Conversation

Codex starts with zero context. **Every invocation is a cold start.** Always include in your prompt:
- **Task/requirement file paths** — so codex knows what to check against
- **Implementation file paths** — so codex knows what to review
- **Directory paths** — for broader context
- **What to focus on** — specific concerns, not generic "review this"
- **Brief context** — what the feature/change does (1-2 sentences)

This applies to ALL commands including `codex exec review` — the `--uncommitted`/`--base` flags
only tell codex WHICH diff to look at, not HOW to review it. The prompt provides the HOW.

**Example**:
```bash
codex exec "Review the implementation in:
- {{SRC_DIR}}/application/sessions/use-cases/create-session.use-case.ts
- {{SRC_DIR}}/infrastructure/web/dto/sessions/create-session.dto.ts

Check against requirements in: tasks/task-2026-01-09-feature/tech-decomposition.md
Focus on: correctness, edge cases, error handling" \
  -m gpt-5.4 --full-auto -o /tmp/codex-result.md > /dev/null 2>&1
```

### Parallel with sibling CLI skills

When the caller wants perspectives from multiple external CLIs (e.g. codex + cursor + gemini) on the same diff or question, issue the three Bash calls in the same turn rather than sequentially. The calls have no dependency on each other and the external CLIs take 1-10 minutes each — serializing them multiplies wall-clock time.

### One-Shot Only

Codex runs non-interactively. No follow-up questions, no conversation. Craft your prompt to be complete and self-contained.

### Web Search

Codex has built-in web search (cached by default). Add `--search` for live results:

```bash
codex exec "Research best practices for [topic]" \
  -m gpt-5.4 --full-auto --search -o /tmp/codex-result.md > /dev/null 2>&1
```

### When NOT to Use

- Simple, quick tasks (overhead not worth the 1-10 min wait)
- Tasks requiring interactive conversation/refinement
- Trivial changes (typos, formatting)

## Reference Files

Read these as needed — they are NOT loaded into context automatically:

| File | When to Read |
|---|---|
| `reference.md` | Need exact flag syntax, sandbox modes, config options, or error handling |
| `templates.md` | Need a structured prompt template for a specific review type |
