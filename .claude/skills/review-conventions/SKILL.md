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

Reviews run in two stages so we get recall AND precision:

1. **Find stage (this skill)** — report every issue you notice, including low-severity
   and uncertain ones. For each finding, include:
   - `severity`: CRITICAL | MAJOR | MINOR | INFO
   - `confidence`: high | medium | low
   - `location`: `file:line`
   - `suggestion`: concrete fix or next step
   Do not self-censor based on severity or confidence — a later verification pass
   will filter before anything reaches the user.

2. **Presentation** — consolidate repeats ("5 functions missing error handling" with
   a list, not 5 separate findings). Explain why each issue matters. Highlight
   positive practices alongside problems.

## Diff-Scoped Review (when `changed_files` provided)

- Primary scope: only review files in `changed_files`
- Use `full_diff` to focus on changed lines
- You may read unchanged files for context (interfaces, contracts), but don't raise
  findings against unchanged code — the author isn't touching it in this PR.
- Skip pre-existing issues unless the current changes make them worse (e.g., a bug
  that used to be in dead code is now reachable).

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

If you spot something outside your scope, note it as a one-line INFO finding with
the likely owner (e.g. "possible security concern — flag for `security-code-reviewer`")
and move on.

## Project File Locations

- Architecture docs: `{{DOCS_DIR}}`
- Product docs (PRDs, JTBDs): `product-docs/`
- Task documents: `tasks/<task-dir>/tech-decomposition*.md`
- Test structure: `{{TEST_DIR}}`
