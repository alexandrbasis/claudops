---
name: gemini-cli
description: >-
  Run Google Gemini CLI for web-grounded research, cross-AI review, or validation.
  Use when asked for 'ask gemini', 'gemini review', 'gemini search', 'use gemini',
  or when you need Google Search grounding or a different AI perspective.
  NOT for interactive conversations (gemini is one-shot only).
allowed-tools:
  - Bash
  - Read
---

# Gemini CLI Integration Skill

> **Announcement**: Begin with: "I'm using the **gemini-cli** skill for cross-AI validation with Gemini."

Invoke Google Gemini CLI for one-shot code review, web-grounded research, and cross-AI verification.

## Self-Update: Official Documentation

When the skill feels outdated (wrong flags, unknown model, new features), consult these
official sources to update commands and reference files:

| Resource | URL |
|---|---|
| CLI cheatsheet (flags & options) | https://geminicli.com/docs/cli/cli-reference |
| Gemini 3 model page | https://geminicli.com/docs/get-started/gemini-3/ |
| Official docs home | https://geminicli.com/docs |
| Headless mode reference | https://geminicli.com/docs/cli/headless |
| GitHub repo (issues, releases) | https://github.com/google-gemini/gemini-cli |
| Available models & deprecations | https://ai.google.dev/gemini-api/docs/models |

Use `WebFetch` or `mcp__exa__web_search_exa` to check for updates when:
- A gemini command fails with an unknown flag error
- The user mentions a gemini feature not covered here
- It has been a while since the skill was last updated

> **Last verified**: 2026-03-16 (Gemini CLI v0.33.1, Auto (Gemini 3) routing, thinking level HIGH)

## Prerequisite Check

Before running any gemini command, verify installation:

```bash
command -v gemini >/dev/null || { echo "ERROR: gemini CLI not installed. Run: npm i -g @google/gemini-cli"; exit 1; }
```

## Core Patterns

### 1. Custom Prompt (most common)

The canonical pattern: run gemini, capture JSON, extract clean final answer with jq.

```bash
gemini \
  -p "Output ONLY the final answer.Task: [your prompt] @file/paths" \
  --approval-mode=yolo -o json \
  > /tmp/gemini.json 2> /dev/null \
  && jq -r '.response' /tmp/gemini.json > /tmp/gemini-result.txt \
  && echo "Gemini completed"
```
Then read with **Read tool**: `/tmp/gemini-result.txt`

**Why this works**: `-o json` captures structured output. `jq -r '.response'` extracts ONLY the final answer — no thinking tokens, no tool traces, no reasoning chain. `2> /dev/null` suppresses extension loading noise. This is functionally equivalent to codex-cli's `-o FILE` flag.

### 2. Code Review

```bash
gemini \
  -p "Respond with the final review only — concise, fact-forward.
Review these files for bugs, security issues, and improvements:
- @path/to/file.ts
- @path/to/other-file.ts
Check against requirements in: @tasks/task-doc/tech-decomposition.md
Focus on: correctness, edge cases, error handling" \
  --approval-mode=yolo -o json \
  > /tmp/gemini.json 2> /dev/null \
  && jq -r '.response' /tmp/gemini.json > /tmp/gemini-review.txt \
  && echo "Review completed"
```
Then read with **Read tool**: `/tmp/gemini-review.txt`

### 3. Web Research (Google Search Grounding)

Gemini's unique differentiator over other CLI tools: native Google Search grounding.

```bash
gemini \
  -p "Respond with the final answer only — concise, fact-forward.
Use Google Search to find: [topic]. Cite sources with URLs.
Format: markdown with bullet points." \
  --approval-mode=yolo -o json \
  > /tmp/gemini.json 2> /dev/null \
  && jq -r '.response' /tmp/gemini.json > /tmp/gemini-research.txt \
  && echo "Research completed"
```
Then read with **Read tool**: `/tmp/gemini-research.txt`

### 4. Background Execution (for long tasks)

For complex tasks that take 2-10 minutes. When you have multiple *independent* gemini queries (e.g. a security review and a perf review of the same diff), launch them in the same turn as separate background Bash calls — don't serialize.

```bash
# Use Bash tool with run_in_background=true
gemini \
  -p "[complex prompt with @file references]" \
  --approval-mode=yolo -o json \
  > /tmp/gemini.json 2> /dev/null \
  && jq -r '.response' /tmp/gemini.json > /tmp/gemini-result.txt \
  && echo "Gemini completed"
```

**Workflow**:
1. Run with `run_in_background: true` on the Bash tool
2. If there are other independent gemini calls, fire them in the same turn (different output files: `/tmp/gemini-sec.txt`, `/tmp/gemini-perf.txt`)
3. Continue working on other tasks while gemini runs
4. You will be notified automatically when each completes
5. Read each result with the Read tool
6. Summarize findings to the user

### 5. Capacity & Timeout Notes

Auto routing handles capacity via a fallback chain: Gemini 3.1 Pro → Gemini 2.5 Pro → Gemini 2.5 Flash. The CLI auto-retries with exponential backoff on 429 errors.

**Timeout protection**: Always set a `timeout` on the Bash tool call (default 120s is too short for complex reviews). Recommended values:

| Task Type | Bash timeout |
|---|---|
| Simple query | `60000` (60s) |
| Code review (small) | `180000` (3min) |
| Code review (large) / directory analysis | `300000` (5min) |
| Web research | `120000` (2min) |

### 6. @path Safety

Verify every `@path` reference points to a real file or directory before invoking — Gemini CLI can hang indefinitely on a missing path (upstream bug [#6440](https://github.com/google-gemini/gemini-cli/issues/6440)), and a hung background job will silently eat your timeout budget. A quick `ls` or `[ -f path ]` guard is enough.

## Critical Rules

### Auto Routing (Default — Do Not Pass `-m`)

Rely on **Auto** routing (omit `-m`, set `previewFeatures: true` in `~/.gemini/settings.json`); Auto handles the Gemini-3 fallback chain for you.

**How Auto routing actually works** (verified via test output and official docs):
1. A lightweight **classifier** (`gemini-2.5-flash-lite`) analyzes the prompt complexity
2. **Simple tasks** → `gemini-3-flash-preview` (or `gemini-2.5-flash` — routing is inconsistent, see [#22381](https://github.com/google-gemini/gemini-cli/issues/22381))
3. **Complex tasks** → `gemini-3.1-pro-preview` (if available) or `gemini-2.5-pro`

**Fallback chain** (when limits/capacity are hit): Gemini 3 Pro → Gemini 2.5 Pro → Gemini 2.5 Flash. The CLI auto-retries with exponential backoff on 429 errors.

> **Note**: The 2.5-flash-lite classifier is internal and expected — it doesn't affect answer quality. Only the **main** model response matters.

### Use `-p` for One-Shot

Claude Code can only drive Gemini non-interactively. Without `-p`, the CLI may drop into an interactive REPL in a TTY and hang the Bash call.

### Final Answer Only

Use `-o json` + `jq -r '.response'` to extract only the final answer.

### Token Optimization

Without redirection, Bash returns thousands of tokens of verbose gemini output; the redirect + `jq` pattern below collapses that to ~30 tokens, which is why every template uses it.

**Pattern**: `> /tmp/gemini.json 2> /dev/null && jq -r '.response' /tmp/gemini.json > /tmp/gemini-result.txt && echo "Gemini completed"`

Read the result file with the **Read tool** — `cat` will dump the full payload back into the conversation and defeat the token-optimization pipeline above.

### Gemini Has No Context From This Conversation

Gemini starts with zero context — it cannot see this conversation, open files, or prior turns. For any useful answer, the prompt itself has to carry what it needs:
- Task/requirement file paths via `@path`
- Implementation file paths for review targets
- Directory paths (`@src/`) when broader context matters

### One-Shot Only

Gemini runs non-interactively via `-p`. No follow-up questions, no conversation. Craft your prompt to be complete and self-contained.

### When NOT to Use

- Simple, quick tasks (overhead not worth the 1-10 min wait)
- Tasks requiring interactive conversation/refinement
- Trivial changes (typos, formatting)
- Simple web search (use Exa tools or /deep-research instead)

## Reference Files

Read these as needed — they are NOT loaded into context automatically:

| File | When to Read |
|---|---|
| `reference.md` | Need exact flag syntax, model list, config options, or error handling |
| `templates.md` | Need a structured prompt template for a specific review or research type |
