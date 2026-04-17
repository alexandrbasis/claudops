---
name: cursor-cli
description: >-
  Run Cursor CLI (Composer 2, a Kimi-K2.5 lineage) for one-shot cross-AI code
  review when a non-OpenAI/non-Anthropic perspective is specifically wanted.
  Invoke ONLY when the user explicitly asks ('cursor review', 'ask cursor',
  'run cursor'), or when another skill passes an explicit instruction to
  delegate to cursor. For generic 'cross-AI check' requests, the caller skill
  should pick the specific CLI; do not invoke both cursor and codex implicitly.
  Not for interactive conversations (cursor is one-shot only).
allowed-tools:
  - Bash
  - Read
---

# Cursor CLI Integration Skill

> **Announcement**: Begin with: "I'm using the **cursor-cli** skill for cross-AI validation with Cursor."

Invoke Cursor CLI (Composer 2 model) for one-shot code review, approach validation, and cross-AI verification.

## Self-Update: Official Documentation

When the skill feels outdated (wrong flags, unknown model, new features), consult these
official sources to update commands and reference files:

| Resource | URL |
|---|---|
| CLI Overview | https://cursor.com/docs/cli/overview |
| Headless Mode | https://cursor.com/docs/cli/headless |
| Output Format | https://cursor.com/docs/cli/reference/output-format |
| Composer 2 Model | https://cursor.com/docs/models/cursor-composer-2 |
| Install Script | https://cursor.com/install |

Use `WebFetch` or `mcp__exa__web_search_exa` to check for updates when:
- A cursor command fails with an unknown flag error
- The user mentions a cursor feature not covered here
- The user explicitly asks to verify the skill against upstream docs

> **Last verified**: v2026.03.20 (March 2026), pinned model `composer-2`

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

If agent is not installed at all:
```bash
curl https://cursor.com/install -fsS | bash
```

> **Critical**: The binary is `agent`, NOT `cursor`. The `cursor` binary is the GUI app launcher (Electron) — it does not work in headless mode.

## Core Patterns

### 1. Custom Prompt (most common)

```bash
agent -p "[prompt with explicit file paths]" \
  --model composer-2 --mode=ask --trust \
  --output-format text > /tmp/cursor-result.txt 2> /dev/null \
  && echo "Cursor completed"
```
Then read with **Read tool**: `/tmp/cursor-result.txt`

### 2. Code Review

```bash
agent -p "Review these files for bugs, security issues, and improvements:
- path/to/file1.ts
- path/to/file2.ts

Check against requirements in: tasks/task-doc/tech-decomposition.md
Focus on: correctness, edge cases, error handling" \
  --model composer-2 --mode=ask --trust \
  --output-format text > /tmp/cursor-review.txt 2> /dev/null \
  && echo "Review completed"
```
Then read with **Read tool**: `/tmp/cursor-review.txt`

### 3. Background Execution (for long tasks)

For complex tasks that take 2-10 minutes:

```bash
# Use Bash tool with run_in_background=true
agent -p "[complex prompt]" \
  --model composer-2 --mode=ask --trust \
  --output-format text > /tmp/cursor-result.txt 2> /dev/null \
  && echo "Cursor completed"
```

**Workflow**:
1. Run with `run_in_background: true` on the Bash tool
2. Continue working on other tasks while cursor runs
3. You'll be notified automatically when it completes
4. Read `/tmp/cursor-result.txt` with the Read tool
5. Summarize findings to the user

## Output capture

### Why it matters

Without redirection, Bash returns thousands of tokens of verbose output. With the redirect pattern, you get ~30 tokens. Use this pattern on every invocation.

**Pattern**: `--output-format text > /tmp/cursor-result.txt 2> /dev/null && echo "Cursor completed"`

Read with the **Read tool** (not `cat`) so the file is registered with the harness and counted once.

### Required flags for cross-AI review

| Flag | Why |
|---|---|
| `--model composer-2` | Pins to Cursor's Kimi-K2.5 lineage — the whole reason to use this skill instead of codex/gemini. Without it, you get a default that may duplicate another CLI. |
| `--mode=ask` | Read-only mode, enforced at the CLI level. A review must not modify files. |
| `--trust` | Bypasses the workspace-trust prompt, which would otherwise hang headless mode. |

Do not use `--force` or `--yolo` here — those authorize writes, which defeats the read-only guarantee above.

### Cursor Has No Context From This Conversation

Cursor starts with zero context. Always include in your prompt:
- **Task/requirement file paths** — so cursor knows what to check against
- **Implementation file paths** — so cursor knows what to review
- **Directory paths** — for broader context

File paths are referenced directly in the prompt text (no `@path` syntax like Gemini).

**Example**:
```bash
agent -p "Review the implementation in:
- {{SRC_DIR}}/application/sessions/use-cases/create-session.use-case.ts
- {{SRC_DIR}}/infrastructure/web/dto/sessions/create-session.dto.ts

Check against requirements in: tasks/task-2026-01-09-feature/tech-decomposition.md
Focus on: correctness, edge cases, error handling" \
  --model composer-2 --mode=ask --trust \
  --output-format text > /tmp/cursor-result.txt 2> /dev/null
```

### Parallel with sibling CLI skills

When the caller wants perspectives from multiple external CLIs (e.g. codex + cursor + gemini) on the same diff or question, issue the three Bash calls in the same turn rather than sequentially. The calls have no dependency on each other and the external CLIs take 1-10 minutes each — serializing them multiplies wall-clock time.

### One-Shot Only

Cursor runs non-interactively via `-p`. No follow-up questions, no conversation. Craft your prompt to be complete and self-contained.

### When NOT to Use

- Simple, quick tasks (overhead not worth the 1-10 min wait)
- Tasks requiring interactive conversation/refinement
- Trivial changes (typos, formatting)
- General "review this code" requests where no sibling-AI perspective was asked for — those belong to `/sr` or other primary-review skills; cursor-cli supplements, it does not replace.
- When the user is iterating live on code and wants fast feedback — primary Claude is lower-latency.

## Unique Strengths

Compared to codex-cli and gemini-cli, cursor-cli offers:

- **Composer 2 model**: Fine-tuned Kimi K2.5 — a non-OpenAI/non-Anthropic model lineage, providing a genuinely different perspective in cross-AI validation
- **Explicit read-only mode**: `--mode=ask` guarantees no file modifications (enforced at CLI level)
- **Cloud agent**: `-c` flag offloads heavy tasks to Cursor's cloud infrastructure for complex analysis

## Reference Files

Read these as needed — they are NOT loaded into context automatically:

| File | When to Read |
|---|---|
| `reference.md` | Need exact flag syntax, model list, config options, or error handling |
| `templates.md` | Need a structured prompt template for a specific review type |
