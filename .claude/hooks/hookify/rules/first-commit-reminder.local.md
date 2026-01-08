---
name: first-commit-reminder
enabled: true
event: bash
once: true
conditions:
  - field: command
    operator: regex_match
    pattern: 'git\s+commit'
action: warn
---

**📋 Session First Commit Reminder**

Before committing, verify:
- [ ] Linear issue status updated to "In Progress"
- [ ] Branch follows naming convention: `feature/wyt-XXX-description`
- [ ] Quality checks passed: `npm run format:check && npm run lint:check && npm run build`
