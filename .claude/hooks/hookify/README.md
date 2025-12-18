# Wythm Local Hookify

Self-managed copy of hookify engine, migrated from global plugin.

## Structure

```
.claude/hooks/hookify/
├── engine/           # Python modules (config_loader, rule_engine)
├── hooks/            # Hook scripts called by Claude Code
├── rules/            # Rule definitions (*.local.md)
└── docs/             # Documentation (hookify-guide.md)
```

## How It Works

1. Claude Code triggers hook events (PreToolUse, Stop, etc.)
2. Hook scripts in `hooks/` are executed
3. Scripts load rules from `rules/*.local.md`
4. Rules are evaluated against the current action
5. Matching rules return warnings or blocks to Claude Code

## Key Files

| File | Purpose |
|------|---------|
| `engine/config_loader.py` | Loads and parses rule files |
| `engine/rule_engine.py` | Evaluates rules against input |
| `hooks/pretooluse.py` | Runs before tool execution |
| `hooks/stop.py` | Runs when Claude wants to stop |

## Original Source

Migrated from: `~/.claude/plugins/cache/claude-code-plugins/hookify/0.1.0`

Migration date: 2025-12-18

## Documentation

See `docs/hookify-guide.md` for full documentation on:
- Rule syntax and examples
- Debugging tips
- Known limitations
