# Claude Code Hooks

This directory contains hooks for Claude Code that automate validation, linting, and synchronization tasks.

## Directory Structure

```
.claude/hooks/
├── hookify/       # Rule-based hook engine (declarative policies)
│   ├── engine/    # Python modules for rule evaluation
│   ├── hooks/     # Hook scripts called by Claude Code
│   ├── rules/     # Policy definitions (*.local.md)
│   └── docs/      # Hookify documentation
├── validation/    # Pre-action validation hooks
├── sync/          # File synchronization hooks
├── lint/          # Linting and formatting hooks
├── logs/          # Runtime logs (gitignored)
└── docs/          # Documentation (you are here)
```

## Active Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `validation/pre-commit-validation.py` | PreToolUse (Bash) | Quick checks before git commit (syntax, conflicts, debug code) |
| `hookify/hooks/pretooluse.py` | PreToolUse | Rule-based validation from `rules/*.local.md` |
| `hookify/hooks/userpromptsubmit.py` | UserPromptSubmit | User input validation |
| `hookify/hooks/stop.py` | Stop | Cleanup on session stop |
| `lint/lint-on-write.py` | PostToolUse (Write/Edit) | Auto-format Python files (black, isort, flake8, mypy) |
| `sync/claude-agents-sync.py` | PostToolUse (Write/Edit) | Sync CLAUDE.md <-> AGENTS.md |
| `sync/auto-sync-public-repo.py` | PostToolUse (Bash) | Sync to public repo on git commit |

## Hookify Rules

Hookify provides declarative policy enforcement via Markdown files in `hookify/rules/`:

| Rule | Action | Description |
|------|--------|-------------|
| `dangerous-rm.local.md` | BLOCK | Prevents dangerous `rm -rf` commands |
| `schema-change.local.md` | BLOCK | Requires migration workflow for schema.prisma |
| `arch-violation.local.md` | BLOCK | Prevents infrastructure imports in core layer |
| `no-console.local.md` | BLOCK | Prevents console.log in backend code |
| `test-silent.local.md` | BLOCK | Requires `:silent` test variants |
| `pre-commit.local.md` | WARN | Reminds about quality checks before commit |
| `db-danger.local.md` | BLOCK | Prevents dangerous Prisma commands |
| `interface-naming.local.md` | BLOCK | Enforces I- prefix for interfaces |

## Logs

- Logs are stored in `logs/` directory
- Log rotation is handled automatically (1MB max size)
- Logs are gitignored

## Adding New Hooks

1. Create script in appropriate directory (`validation/`, `sync/`, `lint/`)
2. Update `settings.local.json` with hook configuration
3. Test hook manually before committing

## Naming Convention

- Scripts: **kebab-case** (`pre-commit-validation.py`)
- Directories: **lowercase** (`validation/`, `sync/`)
- Rules: **kebab-case.local.md** (`no-console.local.md`)
