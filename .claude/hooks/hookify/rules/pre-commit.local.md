---
name: pre-commit-quality-gate
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'git\s+commit'
action: warn
---

**⚠️ REMINDER: Run quality checks before commit**

Execute in backend/ directory:
```bash
npm run format:check && npm run lint:check && npm run build && npm run test:silent
```

If checks fail, fix with:
```bash
npm run format && npm run lint
```

Only commit after all checks pass.
