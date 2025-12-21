# Git Workflow Rules

## Branch Naming
- Feature: `feature/wyt-[ID]-description`
- Bugfix: `fix/wyt-[ID]-description`
- Docs: `docs/wyt-[ID]-description`
- Refactor: `refactor/component-name`

## Commit Format
```
Type: Brief summary (50 chars)

- Details if needed
- Reference: WYT-123

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Commit Rules (CRITICAL)
- **NEVER commit without user permission**
- Ask user before creating any commit
- Wait for explicit approval before git operations

## Pre-merge Checklist
- Format: `isort . && black .` (Python) | `prettier` (TS)
- Types: `mypy` | `tsc --noEmit`
- Lint: `make lint`
- Tests: All passing

## Task Documentation
- Structure: `tasks/task-YYYY-MM-DD-[kebab-case]/`
- Archive completed: `tasks/completed/`
