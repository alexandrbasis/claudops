---
paths:
  - "backend/**/*.ts"
---

# Backend Development Rules

## Architecture
- **Pattern**: Domain-Driven Design + Clean Architecture
- **Framework**: NestJS with TypeScript
- **ORM**: Prisma with PostgreSQL (Supabase)

## Reference
See `backend/AGENTS.md` for commands, module reference, and documentation index.

## Code Standards
- Strict TypeScript typing (`strict: true`)
- ESLint + Prettier formatting
- Unit tests for business logic
- Integration tests for repositories

## Layer Responsibilities
- **Domain**: Pure business logic, no framework dependencies
- **Application**: Use cases, orchestration, DTOs
- **Infrastructure**: Database, external services, NestJS specifics
- **Presentation**: Controllers, REST endpoints, validation

## AI Service Integration
- See `backend/docs/ai-service.md` for AI module patterns
- See `backend/docs/ai-proms-guide.md` for prompt maintenance
