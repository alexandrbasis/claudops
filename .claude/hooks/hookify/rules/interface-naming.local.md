---
name: interface-naming-convention
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/backend/src/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: 'export\s+interface\s+(?!I[A-Z])[A-Z]\w+'
action: block
---

**BLOCKED: Interface must start with "I" prefix**

Add `I` prefix to the interface name:
- `UserRepository` → `IUserRepository`
- `SessionService` → `ISessionService`

ESLint will reject interfaces without `I` prefix. Just add it.
