# Exploration Checklist

Structured checklists for what to explore based on feature type. Use these to guide Explore agent queries during Step 1.

## Table of Contents
- [Backend API Feature](#backend-api-feature)
- [Mobile Screen Feature](#mobile-screen-feature)
- [Cross-Cutting Feature](#cross-cutting-feature)
- [Data Model Change](#data-model-change)

---

## Backend API Feature

When the feature adds or modifies backend API functionality.

### Data Layer
- [ ] `backend/prisma/schema.prisma` — existing models, relations, enums relevant to the feature
- [ ] `backend/prisma/migrations/` — recent migrations for context on schema evolution
- [ ] Check if relevant seed data exists in `backend/prisma/seed.ts`

### Domain Layer
- [ ] Find the closest existing module: `backend/src/<module-name>/domain/`
- [ ] Study domain entities and value objects for naming conventions
- [ ] Review domain services for business logic patterns (anemic model — logic in services, not entities)
- [ ] Check `backend/src/shared/domain/` for base classes and shared types

### Application Layer
- [ ] Study use cases in `backend/src/<module-name>/application/`
- [ ] Review DTOs for input/output patterns
- [ ] Check for existing mappers (entity ↔ DTO transformations)
- [ ] Look for cross-module dependencies in application services

### Infrastructure Layer
- [ ] Review repository implementations in `backend/src/<module-name>/infrastructure/`
- [ ] Check Prisma repository patterns (how queries are structured)
- [ ] Look for external service integrations (AI service, Supabase auth, etc.)

### Presentation Layer
- [ ] Study controller patterns in `backend/src/<module-name>/presentation/`
- [ ] Review endpoint naming, HTTP methods, response formats
- [ ] Check validation decorators and guard usage
- [ ] Look at NestJS module registration pattern

### Testing
- [ ] Check test structure: `__tests__/unit/`, `__tests__/integration/`, `__tests__/e2e/`
- [ ] Review test factories and fixtures in closest module
- [ ] Note the test database setup pattern from `backend/docs/test-database-setup.md`

### Documentation
- [ ] `backend/AGENTS.md` — module reference and documentation index
- [ ] `backend/docs/project-structure.md` — DDD layer conventions
- [ ] Module-specific docs if they exist (e.g., `backend/docs/sessions-module.md`)

---

## Mobile Screen Feature

When the feature adds or modifies mobile app UI.

### Navigation & Routing
- [ ] `mobile-app/app/` — Expo Router file-based routing structure
- [ ] Identify where new screens fit in the navigation hierarchy
- [ ] Check for existing tab/stack navigator patterns

### Components
- [ ] `mobile-app/src/components/` — reusable components available
- [ ] Check the component library skill (`.claude/skills/component-library/`) for documented components
- [ ] Review design tokens (`.claude/skills/design-tokens/`) for colors, spacing, typography

### State Management
- [ ] Look for Zustand stores under `mobile-app/src/`
- [ ] Check how existing screens manage local vs. global state
- [ ] Review data fetching patterns (React Query, SWR, or direct fetch)

### API Integration
- [ ] Map required data to existing backend endpoints
- [ ] Identify if new backend endpoints are needed
- [ ] Check authentication/authorization patterns in API calls

### Styling & Animation
- [ ] Review existing animation patterns (Reanimated, Moti)
- [ ] Check if the feature needs list virtualization (FlashList)
- [ ] Note performance-critical areas (React Compiler considerations)

### Platform Considerations
- [ ] iOS vs. Android differences for this feature
- [ ] Safe area handling
- [ ] Accessibility requirements

---

## Cross-Cutting Feature

When the feature spans both backend and mobile.

### API Contract
- [ ] Define the API surface first — endpoints, request/response shapes
- [ ] Check existing DTOs on the backend side
- [ ] Review how the mobile app currently consumes similar endpoints

### Backend Checklist
- [ ] Follow the [Backend API Feature](#backend-api-feature) checklist above

### Mobile Checklist
- [ ] Follow the [Mobile Screen Feature](#mobile-screen-feature) checklist above

### Integration Points
- [ ] Authentication flow — how does auth propagate from mobile to backend?
- [ ] Error handling — how do backend errors surface in the mobile UI?
- [ ] Real-time updates — WebSockets, polling, or push notifications?
- [ ] Offline behavior — what happens when the mobile app is offline?

---

## Data Model Change

When the feature primarily involves schema or data model changes.

### Impact Analysis
- [ ] Read `backend/prisma/schema.prisma` fully for the affected models
- [ ] Grep for all references to affected model names across the codebase
- [ ] Identify all repositories that query the affected tables
- [ ] Check for cascade effects (relations, required fields, unique constraints)

### Migration Safety
- [ ] Is this an additive change (new fields/tables) or destructive (removing/renaming)?
- [ ] Does it require a data migration for existing records?
- [ ] Can the migration be applied without downtime?

### Downstream Effects
- [ ] Which DTOs need updating?
- [ ] Which use cases reference the changed entities?
- [ ] Are there seed data changes needed?
- [ ] Do existing tests assume the old schema shape?
