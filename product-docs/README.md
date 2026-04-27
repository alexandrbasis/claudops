# product-docs

Long-lived product documentation that spans tasks. Source of truth for product framing — not for technical decomposition (those live in `tasks/`).

## Layout

```
product-docs/
├── UBIQUITOUS_LANGUAGE.md   # Domain glossary — managed by /ubiquitous-language
├── JTBD/
│   └── JTBD-[feature-name].md   # Jobs-to-be-Done — created by /product
└── PRD/
    └── PRD-[feature-name].md    # Product Requirements — created by /product
```

## Who writes what

| File | Owner skill | When |
|------|-------------|------|
| `UBIQUITOUS_LANGUAGE.md` | `/ubiquitous-language` | Auto-invoked from `/nf`, `/product`, `/ct` (load at Step 0; update after grill round before doc write) |
| `JTBD/JTBD-*.md` | `/product` | When user runs `/product jtbd [feature]` |
| `PRD/PRD-*.md` | `/product` | When user runs `/product prd [feature]` |

## Why this folder is at repo root, not under `.claude/`

`.claude/` is workflow scaffolding — skills, agents, hooks. `product-docs/` is project knowledge that survives independently of the workflow tooling. Anyone reading the repo (without Claude) should be able to find product framing here.

## Conventions

- **No file paths or implementation details.** These docs describe behaviors and contracts; they must survive radical refactors.
- **Use canonical domain terms** from `UBIQUITOUS_LANGUAGE.md`. If a term is missing, run `/ubiquitous-language` to add it.
- **One file per feature.** Don't combine multiple features into one PRD/JTBD.
