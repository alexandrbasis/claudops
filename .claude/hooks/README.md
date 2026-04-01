# Claude Code hooks

Scripts invoked by Claude Code for validation, linting, sync, and guardrails.

## Layout

```
.claude/hooks/
├── guards/          # Bash/file/stop guards
├── lint/            # Format/lint on write (e.g. Python)
├── metrics/         # Cost tracking
├── paralysis/       # Session helpers
├── sync/            # CLAUDE.md ↔ agents sync, public repo sync
├── typecheck/       # Typecheck on write (e.g. TS)
├── validation/      # Pre-commit and pre-tool checks
└── README.md
```

## Active hooks (representative)

| Area | Script | Role |
|------|--------|------|
| Validation | `validation/pre-commit-validation.py` | Checks before git commit |
| Lint | `lint/lint-on-write.py` | Format/lint after Write/Edit |
| Sync | `sync/claude-agents-sync.py` | Keep CLAUDE.md / AGENTS.md in sync |
| Sync | `sync/auto-sync-public-repo.py` | Optional public-repo sync on commit |
| Typecheck | `typecheck/ts-typecheck-on-write.py` | TS checks on write |
| Guards | `guards/*.sh` | Bash/file/stop guardrails |

Wire hooks in `.claude/settings.json` (and `settings.local.json` for machine-specific paths). Logs under `hooks/logs/` are typically gitignored.

## Adding hooks

1. Add a script under the appropriate subdirectory.
2. Register the command and matcher in `settings.json` / `settings.local.json`.
3. Test manually before relying on it in production.

## Naming

- Scripts: **kebab-case** (`pre-commit-validation.py`)
- Directories: **lowercase** (`validation/`, `sync/`)
