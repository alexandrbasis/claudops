---
name: dangerous-db-operations
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'prisma\s+(migrate\s+reset|db\s+push|migrate\s+dev(?!.*--create-only))'
action: block
---

**BLOCKED: Dangerous Prisma command**

Use safe migration workflow instead:

```bash
# Create migration WITHOUT applying
npm run prisma:migrate:dev -- --name <change_name> --create-only

# Review SQL, then deploy
npm run prisma:migrate:deploy
```

Do NOT use `migrate reset`, `db push`, or `migrate dev` without `--create-only`.
