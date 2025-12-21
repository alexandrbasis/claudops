---
description: Claude Commands Directory
---

# Claude Commands

Quick reference for Wythm development workflow commands.

## Commands

| Command | Purpose |
|---------|---------|
| **/cjtbd** | Create Jobs-to-be-Done analysis |
| **/cprd** | Create Product Requirements Document |
| **ct** | Create technical decomposition (TDD) |
| **si** | Start TDD implementation |
| **ph** | Prepare handover documentation |
| **sr** | Start code review |
| **asr** | Advanced multi-agent review (5 specialists) |
| **mp** | Merge PR with docs/changelog updates |
| **fci** | Fix CI pipeline failures |

## Workflow Patterns

**Standard**: `ct` -> `si` -> `sr` -> `mp`

**Full Product**: `/cjtbd` -> `/cprd` -> `ct` -> `si` -> `sr` -> `mp`

**With Handoff**: `ct` -> `si` -> `ph` -> `si` -> `sr` -> `mp`

## Task Structure

```
tasks/task-YYYY-MM-DD-[feature-name]/
├── JTBD-[feature-name].md (optional)
└── tech-decomposition-[feature-name].md (required)
```

## Full Documentation

See `docs/dev-workflow/commands-reference.md` for complete command details, sub-agent flows, and integration patterns.
