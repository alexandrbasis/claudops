---
name: no-console-log
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: '/backend/src/.*\.ts$'
  - field: new_text
    operator: regex_match
    pattern: 'console\.(log|warn|error|info|debug)\('
action: block
---

**BLOCKED: Use NestJS Logger instead of console.log**

Replace with:
```typescript
private readonly logger = new Logger(MyService.name);

this.logger.log('message');    // instead of console.log
this.logger.error('message');  // instead of console.error
```

Do NOT use console.log/warn/error/info/debug in backend code.
