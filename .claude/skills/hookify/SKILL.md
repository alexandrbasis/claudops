---
name: hookify
description: Guide for creating hookify rules to prevent unwanted behaviors. Use when creating, editing, or understanding hookify rule files.
---

# Hookify Rule Writing Guide

This skill provides the complete reference for writing hookify rule files in the Wythm project.

## Rule File Location

All rules are stored in: `.claude/hooks/hookify/rules/{rule-name}.local.md`

**Naming convention:**
- Use kebab-case: `block-dangerous-rm`, `warn-console-log`
- Start with action verb: `block-`, `warn-`, `require-`, `prevent-`
- End with `.local.md` suffix

## Rule File Structure

```markdown
---
name: rule-name
enabled: true
event: bash|file|stop|prompt|all
conditions:
  - field: command|new_text|file_path|user_prompt
    operator: regex_match|contains|equals|starts_with|ends_with|not_contains
    pattern: 'your-pattern-here'
action: warn|block
---

**Your Warning Title**

Your warning message in Markdown format.
```

## YAML Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (kebab-case) |
| `enabled` | Yes | `true` or `false` |
| `event` | Yes | Event type (see below) |
| `conditions` | Yes | List of conditions (AND logic) |
| `action` | No | `block` (recommended) or `warn` |
| `tool_matcher` | No | Filter by tool (`Bash`, `Edit\|Write`) |

## Event Types

| Event | When Triggered | Available Fields |
|-------|----------------|------------------|
| `bash` | Before/after Bash command | `command` |
| `file` | Before/after Edit/Write | `file_path`, `new_text`, `old_text` |
| `prompt` | When user submits prompt | `user_prompt` |
| `stop` | When Claude wants to stop | `reason`, `transcript` |
| `all` | Always | Depends on event |

## Condition Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `regex_match` | Regex search | `'npm\s+run\s+test'` |
| `contains` | Contains substring | `'console.log'` |
| `equals` | Exact match | `'npm run test'` |
| `starts_with` | Starts with | `'rm '` |
| `ends_with` | Ends with | `'.env'` |
| `not_contains` | Does not contain | `':silent'` |

## Critical Syntax Rules

### 1. Use Single Quotes for Regex

```yaml
# CORRECT - single quotes:
pattern: 'npm\s+run\s+test'

# WRONG - double quotes require double escaping:
pattern: "npm\\s+run\\s+test"
```

### 2. Use Absolute Paths in file_path Patterns

Claude Code passes absolute paths. Include `/` at the start:

```yaml
# CORRECT - matches /Users/.../backend/src/file.ts:
pattern: '/backend/src/.*\.ts$'

# WRONG - won't find absolute path:
pattern: 'backend/src/.*\.ts$'
```

### 3. Use `block` Instead of `warn`

`warn` shows message but allows execution (Claude may ignore it).
`block` prevents execution and forces Claude to use the alternative.

**Use `warn` only for `prompt` events** where blocking isn't possible.

## Writing Directive Messages

Messages should be **directive** to save tokens:

1. **"BLOCKED:"** in title - Claude immediately understands what happened
2. **One command/action** - don't give choices, give solutions
3. **"Do NOT..."** at the end - explicit prohibition on extra actions
4. **No explanations "why"** - saves tokens and time

## Example Rules

### Block Dangerous rm Commands

```markdown
---
name: dangerous-rm
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'rm\s+(-rf|-fr|--recursive.*--force|--force.*--recursive)\s'
action: block
---

**BLOCKED: Dangerous rm command**

This rm command could delete critical files. Use specific file paths instead.

Do NOT use `rm -rf` on directories without explicit user confirmation.
```

### Block console.log in Backend

```markdown
---
name: no-console-log
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/backend/src/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: 'console\.(log|warn|error|info|debug)\('
action: block
---

**BLOCKED: Use NestJS Logger instead of console.log**

Replace with:
\`\`\`typescript
private readonly logger = new Logger(MyService.name);
this.logger.log('message');
\`\`\`

Do NOT use console.log/warn/error/info/debug in backend code.
```

### Block Silent Test Bypass

```markdown
---
name: use-silent-tests
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'npm\s+run\s+test(?!.*:silent)(?::unit|:integration|:e2e)?\s*$'
action: block
---

**BLOCKED: Use silent test command instead**

Replace your command with the `:silent` variant:
- `npm run test` -> `npm run test:silent`
- `npm run test:unit` -> `npm run test:unit:silent`

Do NOT search for scripts or check package.json. Just run the `:silent` version.
```

### Architecture Layer Protection

```markdown
---
name: architecture-violation
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/src/core/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: "from\\s+['\"]@?infrastructure"
action: block
---

**BLOCKED: Infrastructure import in Core layer**

Core layer cannot import from Infrastructure. Use port interface instead.

Do NOT import PrismaService, Controllers, or @infrastructure in core files.
```

### Pre-commit Quality Gate

```markdown
---
name: pre-commit-check
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'git\s+commit'
action: block
---

**BLOCKED: Run quality checks before commit**

Execute in backend/ directory:
\`\`\`bash
npm run format:check && npm run lint:check && npm run build && npm run test:silent
\`\`\`

Only commit after all checks pass.
```

## Multiple Conditions (AND Logic)

All conditions must match. For OR logic, create separate rules:

```markdown
---
name: protect-env-files
enabled: true
event: file
conditions:
  - field: file_path
    operator: ends_with
    pattern: '.env'
  - field: new_text
    operator: contains
    pattern: 'API_KEY'
action: block
---

**BLOCKED: Sensitive data in .env file**

Do not hardcode API keys. Use environment variable references.
```

## Testing Rules

### Test Rule Loading

```bash
cd .claude/hooks/hookify
python3 -c "
import sys
sys.path.insert(0, 'engine')
from config_loader import load_rules

rules = load_rules(event='bash', cwd='$(pwd)')
print(f'Found {len(rules)} bash rules')
for r in rules:
    print(f'  - {r.name}: enabled={r.enabled}')
"
```

### Test Rule Matching

```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "npm run test"}, "hook_event_name": "PreToolUse", "cwd": "'$(pwd)'"}' | \
  python3 .claude/hooks/hookify/hooks/pretooluse.py
```

## Quick Reference

| Want to... | Use event | Use field | Example pattern |
|------------|-----------|-----------|-----------------|
| Block bash command | `bash` | `command` | `'rm\s+-rf'` |
| Block code pattern | `file` | `new_text` | `'console\.log\('` |
| Block file type | `file` | `file_path` | `'\.env$'` |
| Check stop conditions | `stop` | `reason` | `'.*'` |
| Validate user input | `prompt` | `user_prompt` | `'password'` |

## Full Documentation

See `.claude/hooks/hookify/docs/hookify-guide.md` for complete reference.
