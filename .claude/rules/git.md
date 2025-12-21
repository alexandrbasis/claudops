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
- Format: `prettier --write .` (TS/JS)
- Types: `tsc --noEmit`
- Lint: `npm run lint`
- Tests: All passing
