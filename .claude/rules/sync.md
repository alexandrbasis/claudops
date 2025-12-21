---
paths: backend/{CLAUDE.md,AGENTS.md}
---

# Backend Documentation Synchronization

## Sync Requirement
`backend/CLAUDE.md` and `backend/AGENTS.md` MUST stay 100% in sync.

## When to Sync
Any change to either file must be mirrored to the other:
- `backend/CLAUDE.md` - Primary file for Claude Code
- `backend/AGENTS.md` - Consumed by Cursor and other AI agents

## Why Both Files Exist
- Different AI tools look for different filenames
- Claude Code: prefers `CLAUDE.md`
- Cursor: prefers `AGENTS.md`
- Keeping both ensures consistent behavior across all tools
