---
name: sync
description: >-
  Sync CLAUDE.md and AGENTS.md files to stay in lockstep. Use whenever editing
  CLAUDE.md, AGENTS.md, backend/CLAUDE.md, or backend/AGENTS.md. Also trigger
  when asked to 'sync docs', 'update AGENTS.md', or 'mirror CLAUDE.md'.
---

# Documentation Synchronization

> **Announcement**: Begin with: "I'm using the **sync** skill for CLAUDE.md/AGENTS.md synchronization."

## Root Files
`CLAUDE.md` and `AGENTS.md` MUST stay 100% in sync.

## Backend Files
`backend/CLAUDE.md` and `backend/AGENTS.md` MUST stay 100% in sync.

## When to Sync
Any change to either file must be mirrored to the other:
- `CLAUDE.md` / `AGENTS.md` - Root project instructions
- `backend/CLAUDE.md` / `backend/AGENTS.md` - Backend-specific instructions

## Why Both Files Exist
- Different AI tools look for different filenames
- Claude Code: prefers `CLAUDE.md`
- Cursor: prefers `AGENTS.md`
- Keeping both ensures consistent behavior across all tools
