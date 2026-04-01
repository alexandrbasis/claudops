# Project-Specific Analysis Checks

Detailed commands for project-specific code analysis. Read this when analyzing the project codebase.

## DDD Layer Separation

The canonical structure is documented in `backend/docs/project-structure.md`.
Key rule: domain layer has NO dependencies on infrastructure.

```bash
# Domain files importing from infrastructure (VIOLATION)
grep -rn "from.*infrastructure" backend/src/*/domain/ 2>/dev/null

# Domain files importing Prisma directly (VIOLATION)
grep -rn "from.*@prisma\|from.*prisma" backend/src/*/domain/ 2>/dev/null

# Application layer importing infrastructure internals (CONCERN)
grep -rn "from.*\.repository\|from.*\.adapter" backend/src/*/application/ 2>/dev/null
```

## Prisma Schema Health

```bash
# Model count
grep -c "^model " backend/prisma/schema.prisma

# Index coverage
grep -c "@@index\|@@unique" backend/prisma/schema.prisma

# Migration count (high count may indicate schema churn)
ls backend/prisma/migrations/ 2>/dev/null | wc -l

# Relations (potential N+1 risk if unindexed)
grep -B2 "@relation" backend/prisma/schema.prisma
```

## NestJS Module Boundaries

```bash
# Services injected across modules
grep -rn "@Inject" backend/src/ --include="*.ts" | grep -v "node_modules"

# Module provider exports (what's shared between modules)
grep -rn "exports:" backend/src/ --include="*.module.ts"
```

## Error Handling Patterns

```bash
# Raw Error throws (should use domain exceptions instead)
grep -rn "throw new Error(" backend/src/ --include="*.ts" \
  | grep -v "node_modules\|spec\|test"

# Domain exception usage (expected pattern)
grep -rn "throw new.*Exception" backend/src/*/domain/ 2>/dev/null

# Empty catch blocks (swallowed errors)
grep -rn "catch.*{" backend/src/ --include="*.ts" \
  | grep -v "node_modules\|spec\|test"
```

## API Surface

```bash
# All controller endpoints
grep -rn "@Get\|@Post\|@Put\|@Patch\|@Delete" backend/src/ --include="*.ts"

# Guards applied (auth coverage)
grep -rn "@UseGuards" backend/src/ --include="*.ts"

# DTOs defined
find backend/src -name "*.dto.ts" | wc -l

# Validators used
grep -rn "class-validator\|IsString\|IsNumber\|IsNotEmpty" backend/src/ --include="*.dto.ts"
```
