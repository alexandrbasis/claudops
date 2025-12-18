---
name: prisma-schema-change
enabled: true
event: file
conditions:
  - field: file_path
    operator: ends_with
    pattern: "schema.prisma"
action: block
---

**BLOCKED: Schema change requires migration workflow**

After editing schema.prisma, run:
```bash
cd backend
npm run prisma:migrate:dev -- --name <change_name> --create-only
# Review SQL in prisma/migrations/
npm run prisma:migrate:deploy
npm run prisma:generate
```

Do NOT edit schema without following this workflow.
