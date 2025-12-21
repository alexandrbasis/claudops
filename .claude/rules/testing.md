---
paths: backend/**/*.{ts,spec.ts}
---

# Testing Standards

## Required Reading
- `backend/docs/tests-structure.md` - Testing strategy and patterns

## Test Types
- **Unit tests**: Business logic, domain services
- **Integration tests**: Repositories, external services
- **E2E tests**: API endpoints, user flows

## Pre-merge Requirements
- All tests must pass
- No skipped tests without justification
- Coverage targets per module

## Patterns
- Use test factories for data setup
- Isolate tests with proper cleanup
- Mock external dependencies in unit tests
