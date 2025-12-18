---
name: use-silent-tests
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'npm\s+run\s+test(?!.*:silent)(?::unit|:integration|:e2e)?\s*$'
action: block
---

**BLOCKED: Use silent test command instead**

Replace your command with the `:silent` variant:
- `npm run test` → `npm run test:silent`
- `npm run test:unit` → `npm run test:unit:silent`
- `npm run test:integration` → `npm run test:integration:silent`
- `npm run test:e2e` → `npm run test:e2e:silent`

Do NOT search for scripts or check package.json. Just run the `:silent` version.
