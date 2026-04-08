---
name: review-conventions
description: "Internal reference skill — shared conventions for all code review agents. Not user-invocable."
---

# Review Conventions

Shared knowledge preloaded into review agents. Apply these conventions when reviewing code.

## Tech Stack

- **Framework**: {{FRAMEWORK}}
- **ORM**: {{ORM}}
- **Auth**: {{AUTH}}
- **Testing**: {{TEST_FRAMEWORK}} — `{{TEST_CMD}}`
- **Language**: {{LANGUAGE}}
- **Architecture**: {{ARCHITECTURE}}
- **Docs reference**: `{{DOCS_DIR}}`

## Architecture Rules

{{LAYER_RULES}}

## Code Standards

- Prefer project-established type/interface conventions
- No unnecessary underscores for unused variables
- Proper type safety — avoid `any`
- Secrets never logged; environment vars flow only through config providers
- Database queries use parameter binding — no dynamic SQL or string interpolation

## Review Quality Rules

- **>80% confidence threshold**: only report findings you're confident about. False positives erode trust.
- **Consolidate similar issues**: "5 functions missing error handling" with a list, not 5 separate findings
- **Severity order**: CRITICAL → MAJOR → MINOR → INFO
- **Actionable**: every finding needs severity + location (`file:line`) + concrete suggestion
- **Constructive tone**: explain why issues matter, highlight positive practices

## Diff-Scoped Review (when `changed_files` provided)

- Primary scope: only review files in `changed_files`
- Use `full_diff` to focus on changed lines
- MAY read unchanged files for context (interfaces, contracts) — do NOT flag issues in unchanged code
- Pre-existing issues: do NOT flag unless changes make them worse

## Ownership Boundaries

Each agent owns specific concerns — do not duplicate other agents' work:

| Concern | Owner |
|---------|-------|
| Spec requirements match | `spec-compliance-reviewer` |
| Architecture fit, layers, module boundaries | `senior-architecture-reviewer` |
| Security, auth, injection, OWASP | `security-code-reviewer` |
| Code quality, naming, DRY, complexity | `code-quality-reviewer` |
| Test coverage and quality | `test-coverage-reviewer` |
| Documentation accuracy | `documentation-accuracy-reviewer` |
| Performance, N+1, memory | `performance-reviewer` |

If you spot something outside your scope, note it briefly as INFO — do not deep-dive.

## Project File Locations

- Architecture docs: `{{DOCS_DIR}}`
- Product docs (PRDs, JTBDs): `product-docs/`
- Task documents: `tasks/<task-dir>/tech-decomposition*.md`
- Test structure: `{{TEST_DIR}}`
