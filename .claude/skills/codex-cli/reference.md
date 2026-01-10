# Codex CLI Reference

Complete command reference for Codex CLI v0.80.0.

## Core Commands

### `codex exec`

Run Codex non-interactively (one-shot).

```bash
codex exec [OPTIONS] [PROMPT]
```

**Arguments:**
- `PROMPT` - Instructions for the agent. Use `-` to read from stdin.

**Key Options:**
| Flag | Description |
|------|-------------|
| `-m, --model MODEL` | Model to use (e.g., `gpt-5.2-codex`) |
| `--full-auto` | Low-friction automation (workspace-write sandbox, auto-approval) |
| `-o, --output-last-message FILE` | Write final response to file |
| `-C, --cd DIR` | Set working directory |
| `-s, --sandbox MODE` | Sandbox policy: `read-only`, `workspace-write`, `danger-full-access` |
| `--json` | Output events as JSONL |
| `-i, --image FILE` | Attach image(s) to prompt |

### `codex exec review`

Run automated code review.

```bash
codex exec review [OPTIONS] [PROMPT]
```

**Review Options:**
| Flag | Description |
|------|-------------|
| `--uncommitted` | Review staged, unstaged, and untracked changes |
| `--base BRANCH` | Review changes against base branch |
| `--commit SHA` | Review specific commit |
| `--title TITLE` | Optional title for review summary |

**Examples:**
```bash
# Review uncommitted changes
codex exec review --uncommitted -m gpt-5.2-codex --full-auto

# Review against main branch
codex exec review --base main -m gpt-5.2-codex --full-auto

# Review specific commit
codex exec review --commit abc123 -m gpt-5.2-codex --full-auto

# Custom review instructions
codex exec review --uncommitted "Focus on security issues" -m gpt-5.2-codex --full-auto
```

## Configuration

### Model Selection

```bash
# Explicit model
codex exec "prompt" -m gpt-5.2-codex

# Override reasoning effort
codex exec "prompt" -m gpt-5.2-codex -c model_reasoning_effort=high
```

### Sandbox Modes

| Mode | Description |
|------|-------------|
| `read-only` | Can read files but not modify |
| `workspace-write` | Can write to working directory (default with `--full-auto`) |
| `danger-full-access` | Full system access (dangerous) |

### Output Options

```bash
# Save final response to file (only works with `codex exec`, NOT with `codex exec review`)
codex exec "prompt" -m gpt-5.2-codex --full-auto -o /tmp/result.txt

# Get JSON events
codex exec "prompt" -m gpt-5.2-codex --full-auto --json
```

**Note:** The `-o` flag is NOT supported by `codex exec review`. For reviews, capture output via shell redirection:
```bash
codex exec review --uncommitted -m gpt-5.2-codex --full-auto 2>&1 | tee /tmp/review.txt
```

## Common Patterns

### Standard Command Pattern
```bash
codex exec "[prompt]" -m gpt-5.2-codex --full-auto
```

### With Output File
```bash
codex exec "[prompt]" -m gpt-5.2-codex --full-auto -o /tmp/codex-output.txt
```

### With Custom Working Directory
```bash
codex exec "[prompt]" -m gpt-5.2-codex --full-auto -C /path/to/project
```

### With Image Input
```bash
codex exec "Explain this diagram" -m gpt-5.2-codex --full-auto -i diagram.png
```

## Session Management

### Resume Previous Session
```bash
# Resume most recent
codex exec resume --last "[follow-up prompt]"

# Resume specific session
codex exec resume SESSION_ID "[follow-up prompt]"
```

## Configuration File

Location: `~/.codex/config.toml`

Relevant settings:
```toml
model = "gpt-5.2-codex"
model_reasoning_effort = "high"

[features]
web_search_request = true
```

## Timeout Expectations

| Task Type | Expected Duration |
|-----------|-------------------|
| Simple query | 30-60 seconds |
| Code review (small) | 1-3 minutes |
| Code review (large) | 3-7 minutes |
| Complex analysis | 5-10 minutes |

## Error Handling

### MCP Server Errors
If you see MCP startup errors (like `etna-trader-remote failed`), they don't affect core Codex functionality. These are optional integrations.

### Rate Limits
Codex handles rate limits automatically with backoff. If you hit limits frequently, space out requests.

### Command Not Found
If `codex` command fails:
```bash
# Check installation
command -v codex

# Check version
codex --version
```
