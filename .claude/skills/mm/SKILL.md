---
name: mm
description: >-
  Run Prisma migrations after schema changes. Use when schema.prisma was modified,
  migration guard fires, or asked to 'run migrations', 'create migration',
  'deploy migration', 'migrate the database'. NOT for schema design decisions.
argument-hint: [migration-name]
disable-model-invocation: true
---

# Command: Make Migrations (`/mm`)

> **Announcement**: Begin with: "I'm using the **mm** skill for Prisma migration management."

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

## Troubleshooting
- **Generation fails** — Fix schema errors and re-run.
- **Shadow DB error** — Check `SHADOW_DATABASE_URL` in `.env`. Must be a separate DB, not the main one.
- **Migration drift** — Run `npx prisma migrate diff` to inspect. May need `prisma migrate resolve`.
- **Dirty database** — If dev DB has manual changes, consider `prisma migrate reset` (destroys data).

## See also
- Full migration docs: `backend/docs/migration-structure.md`
- Schema file: `backend/prisma/schema.prisma`

## Notes
- This command is non-interactive and safe for CI usage.
