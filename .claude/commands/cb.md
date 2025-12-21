---
description: Create git branch for Linear task with proper naming
---

## Claude Command — Teams: Create Branch

**Command trigger**: `create branch <task-number>`

Creates a new git branch for a Linear task following repository branch naming rules, after syncing with `main`.

### What it does
- **Reads Linear issue** via MCP (by task number, e.g. `WYT-123` or just `123`).
- **Determines branch prefix** based on labels/type:
  - `fix/` if labeled “Bug”
  - `docs/` if labeled “Docs” or title starts with `Docs:`
  - `refactor/` if labeled “Refactor”
  - otherwise `feature/`
- **Builds branch name**: `<prefix>/wyt-<number>-<kebab-title>`
  - Example: `feature/wyt-29-internal-user-creating`
- **Git workflow** (no commits):
  1) `git fetch origin`
  2) `git checkout main`
  3) `git pull --rebase origin main`
  4) `git checkout -b <branch-name>`

### Usage
- Chat: `create branch 29`
  - Interprets as Linear issue `WYT-29`
- Chat: `create branch WYT-29`

### Safety and constraints
- No commits, PRs, or merges are performed.
- Requires a clean working tree or the operation will exit.
- Requires git write permission when executed by the agent.

### Implementation details (Agent behavior)
1) Resolve Linear issue by number using `cg-linear` skill:
   ```bash
   cg --mcp-config .claude/mcp/linear.json -p "Get issue WYT-[number] details. Return: title, labels (as comma-separated list)"
   ```
   **Reference**: See `.claude/skills/cg-linear/SKILL.md` for self-contained prompt patterns
2) Compute prefix by label mapping (case-insensitive).
3) Slugify title to kebab-case, ASCII-only, trim to reasonable length.
4) Construct branch: `<prefix>/wyt-<number>-<slug>`.
5) Run git steps (fetch → checkout main → pull --rebase → create branch).
6) Switch to the new branch.

### Local helper script
This repo includes a helper script used by the agent for the git operations:

```bash
bash scripts/git-create-branch.sh <branch-name> [--main main]
```

- Default main branch is `main`.
- Exits with non-zero status on errors.

### Examples
- Linear: `WYT-29` — “Internal user creating” → `feature/wyt-29-internal-user-creating`
- Linear: `WYT-456` labeled “Bug” — “Fix crash on save” → `fix/wyt-456-fix-crash-on-save`

### Branch naming rules (from repository standards)
- `feature/wyt-123-description` — New features
- `fix/wyt-456-description` — Bug fixes
- `docs/wyt-789-description` — Docs work
- `refactor/...` — Refactors

If the label mapping is ambiguous, default to `feature/`.
