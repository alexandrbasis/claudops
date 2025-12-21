---
paths: backend/**/*.ts
---

# Backend Development Rules

## Architecture
- **Pattern**: Domain-Driven Design + Clean Architecture
- **Framework**: NestJS with TypeScript
- **ORM**: Prisma with PostgreSQL (Supabase)

## Required Reading Before Work
- `backend/docs/project-structure.md` - DDD layers and module structure
- `backend/docs/migration-structure.md` - Prisma migration workflow
- `backend/AGENTS.md` - Backend-specific agent instructions

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
