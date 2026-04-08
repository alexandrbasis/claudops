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

- Prefer project-established type/interface conventions
- No `any` — use proper types
- No unnecessary `_` prefixes for unused vars
- Secrets via config providers only — never hardcoded, never logged
- DTOs match API schemas and tech-decomposition acceptance criteria
- Database queries use parameter binding — no dynamic SQL or string interpolation

## Testing

- **TDD**: RED → GREEN → REFACTOR
- Run tests: `{{TEST_CMD}}`
- Lint: `{{LINT_CMD}}`
- Types: `{{TYPECHECK_CMD}}`
- Test patterns reference: `{{TEST_DIR}}`
- Arrange-Act-Assert pattern, descriptive test names
- Proper mocking of data-access layer in unit tests

## Implementation Rules

- Read task document FIRST — it's the source of truth for WHAT to build
- Minimal code — only what tests require
- No scope creep — implement exactly the assigned work item
- No over-engineering or speculative abstractions
- Follow existing codebase patterns — new code should look like it belongs
- No git writes unless explicitly approved by orchestrator
