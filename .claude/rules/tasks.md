# Task Documentation

## Structure
`tasks/task-YYYY-MM-DD-[kebab-case]/`

## Modern Workflow (JTBD-based)
- `JTBD-[feature-name].md` - User needs, outcomes, success metrics
- `technical-decomposition.md` - Optional implementation details
- `splitting-decision.md` - Optional if task-splitter recommends split

## Legacy Workflow (read-only — for existing tasks before JTBD migration, do not use for new tasks)
- `business-requirements.md` - WHAT & WHY
- `technical-decomposition.md` - HOW

## Naming
Examples: `task-2025-10-16-user-authentication`, `task-2025-11-11-training-sessions`

## Archive
Move to `tasks/completed/` after PR merge

## PRD Integration
Reference relevant PRDs from `docs/product-docs/PRD/` in task documentation
