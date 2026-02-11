# Gemini CLI Command Reference

Self-contained reference for using Gemini CLI effectively in this workspace.

## Installation

```bash
npm install -g @google/gemini-cli
# Or without installing (one-off):
npx @google/gemini-cli
```

## Authentication

```bash
# Option 1: API Key
export GEMINI_API_KEY=your_key

# Option 2: OAuth (interactive)
gemini  # First run prompts for auth
```

## Core Modes

### Interactive (REPL)

```bash
gemini
```

### One-shot (recommended for scripts/automation)

```bash
gemini --model gemini-3-pro-preview "What is fine tuning?"
echo "Explain this code" | gemini
```

## Key Flags

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--model` | `-m` | Model to use (pinned in this workspace) | `gemini --model gemini-3-pro-preview "q"` |
| `--output-format` | `-o` | `text` (default), `json`, `stream-json` | `gemini "q" --output-format json` |
| `--debug` | `-d` | Enable debug output | `gemini "q" --debug` |
| `--include-directories` | | Add extra workspace dirs | `--include-directories src,docs` |
| `--yolo` | `-y` | Auto-approve all actions | `gemini "q" --yolo` |
| `--approval-mode` | | Set approval mode | `--approval-mode auto_edit` |

Note: `--prompt/-p` exists but is **deprecated** in the current CLI. Prefer the positional prompt: `gemini "..."`.

For the full current flag list, run:

```bash
gemini --help
```

## Output Formats

### Text (default)

```bash
gemini --model gemini-3-pro-preview "prompt"
```

### JSON

```bash
gemini --model gemini-3-pro-preview "prompt" --output-format json > /tmp/gemini.json
jq -r '.response' /tmp/gemini.json
```

### Stream JSON

```bash
gemini --output-format stream-json "Analyze this code" > /tmp/events.jsonl
```

## Interactive Command Prefixes

Gemini CLI supports commands prefixed with:
- **`/`**: meta commands (help, settings, memory, etc.)
- **`@`**: inject file/directory contents into your prompt (git-aware filtering)
- **`!`**: shell mode / execute shell commands from within the CLI

## Configuration Files

### Settings Location
Common locations referenced in the docs:
- `~/.gemini/settings.json` (user)
- `.gemini/settings.json` (project)

### Project Context (GEMINI.md)

Create `.gemini/GEMINI.md` in project root:
```markdown
# Project Context

Project description and guidelines.

## Coding Standards
- Standards Gemini should follow

## When Making Changes
- Guidelines for modifications
```

### Ignore Files (.geminiignore)

Like `.gitignore`, excludes files from context:
```
node_modules/
dist/
*.log
.env
```

## Rate Limits

### Rate Limit Behavior
- CLI auto-retries with exponential backoff
- Message: `"quota will reset after Xs"`

### Mitigation
1. Batch operations into single prompts
2. Run long tasks in background

## Piping & Scripting

### Pipe Input
```bash
echo "What is 2+2?" | gemini
```

### File Reference Syntax
In prompts, reference files with `@`:
```bash
gemini --model gemini-3-pro-preview "Review @./src/main.js for bugs" --output-format text
```

### Shell Command Execution
In interactive mode, prefix with `!`:
```
> !git status
```

## Keyboard Shortcuts (Interactive)

| Shortcut | Function |
|----------|----------|
| `Ctrl+L` | Clear screen |
| `Ctrl+V` | Paste from clipboard |
| `Ctrl+Y` | Toggle YOLO mode |
| `Ctrl+X` | Open in external editor |

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "API key not found" | Set `GEMINI_API_KEY` env var |
| "Rate limit exceeded" | Wait for auto-retry or use Flash |
| "Context too large" | Use `.geminiignore` or be specific |
| "Tool call failed" | Use `--output-format json` and inspect `.stats` / `.error` |

### Debug Mode
```bash
gemini --model gemini-3-pro-preview "prompt" --debug --output-format text
```

### Error Reports
Full error reports saved to:
```
/var/folders/.../gemini-client-error-*.json
```
