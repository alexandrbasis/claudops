---
description: Create and deploy Prisma database migrations
---

# Command: Make Migrations (`/mm`)

Purpose: Create and deploy Prisma migrations for the backend when the schema changes.

## When to use
- You modified `backend/prisma/schema.prisma` and need to generate a migration.
- The pre-commit migration guard indicates a missing migration.

## What it does
1) Generate a migration (files only) with a given or auto-generated name
2) Deploy all pending migrations to the database
3) Regenerate Prisma Client

## Usage

```bash
# From repo root — auto name: auto_YYYYMMDD_HHMMSS
npm --prefix backend run prisma:migrate:dev -- --name "auto_$(date +%Y%m%d_%H%M%S)" --create-only

# Deploy and regenerate client
npm --prefix backend run prisma:migrate:deploy
npm --prefix backend run prisma:generate
```

Or with a custom name:

```bash
npm --prefix backend run prisma:migrate:dev -- --name my_change --create-only
npm --prefix backend run prisma:migrate:deploy
npm --prefix backend run prisma:generate
```

## Requirements
- Environment variables configured as per `backend/docs/migration-structure.md`:
  - `DATABASE_URL` (pooled)
  - `DIRECT_URL` (direct for migrations)
  - `SHADOW_DATABASE_URL` (shadow schema/DB)

## Notes
- This command is non-interactive and safe for CI usage.
- If generation fails, fix schema and re-run.


