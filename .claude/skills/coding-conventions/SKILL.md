---
name: coding-conventions
description: "Internal reference skill — coding standards and patterns for developer agents. Not user-invocable."
---

# Coding Conventions

Shared knowledge preloaded into developer agents. Follow these when implementing features.

## Tech Stack

- **Framework**: {{FRAMEWORK}}
- **ORM**: {{ORM}}
- **Auth**: {{AUTH}}
- **Testing**: {{TEST_FRAMEWORK}} — `{{TEST_CMD}}`
- **Language**: {{LANGUAGE}}
- **Architecture**: {{ARCHITECTURE}}
- **Docs reference**: `{{DOCS_DIR}}`

## Architecture Layers

{{LAYERS}}

{{LAYER_RULES}}

## Code Style

- Match the project's existing type/interface conventions — new code should look
  like it was written by the same person as the surrounding code.
- Use proper types instead of `any`. `any` hides type errors that only surface at
  runtime, which is the failure mode our type system exists to prevent.
- Drop the `_` prefix on unused vars unless the project's lint config requires it.
- Route secrets through config providers only — never hardcoded, never logged
  (logs ship to observability tools; hardcoded secrets leak via git history).
- Keep DTOs aligned with API schemas and the tech-decomposition's acceptance
  criteria — these are the contract downstream consumers rely on.
- Use parameter binding for database queries (not string interpolation) to prevent
  SQL injection.

## Testing

- **TDD**: RED → GREEN → REFACTOR — vertical slices only (one RED→GREEN per behavior). Canonical: `.claude/skills/tdd/SKILL.md`.
- Run tests: `{{TEST_CMD}}`
- Lint: `{{LINT_CMD}}`
- Types: `{{TYPECHECK_CMD}}`
- Test patterns reference: `{{TEST_DIR}}`
- Arrange-Act-Assert pattern, descriptive test names
- Proper mocking of data-access layer in unit tests

## Implementation Rules

- Start by reading the task document — it's the source of truth for what to build,
  and implementation choices should flow from it rather than from prior assumptions.
- Write the minimum code that makes the tests pass and the acceptance criteria
  hold. Don't add features, abstractions, or cleanup that weren't asked for.
- Bug fixes don't need surrounding refactors — fix the bug, leave the rest.
- Skip defensive error handling for scenarios that can't actually happen in this
  codebase's flow.
- Match existing codebase patterns — new code should look like it belongs.
- No git writes unless explicitly approved by orchestrator
