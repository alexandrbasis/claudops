# Git Workflow Rules

## Branch Naming
- Feature: `feature/wyt-[ID]-description`
- Bugfix: `fix/wyt-[ID]-description`
- Docs: `docs/wyt-[ID]-description`
- Refactor: `refactor/component-name`

## Commit Format
```
<type>(<optional-scope>): <summary>

- Body (optional): why + what changed
- Refs (recommended): `Refs: WYT-123`
```

### Allowed Types
- `feat` - new user-facing feature
- `fix` - bug fix
- `refactor` - code change that neither fixes a bug nor adds a feature
- `docs` - documentation only
- `test` - tests only
- `chore` - tooling/maintenance (no production behavior change)
- `ci` - CI-only changes

## Commit Rules (CRITICAL)
- **NEVER commit without user permission**
- Ask user before creating any commit
- Wait for explicit approval before git operations

## Pre-merge Checklist
- Format: `prettier --write .` (TS/JS)
- Types: `tsc --noEmit`
- Lint: `npm run lint`
- Tests: All passing
