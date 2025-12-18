---
name: dangerous-rm-command
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'rm\s+(-rf|-fr|--recursive.*--force|--force.*--recursive)\s+.*\b(node_modules|src|backend|prisma)\b|rm\s+(-rf|-fr)\s+(/|~|\$HOME)\s*$'
action: block
---

**BLOCKED: Dangerous recursive delete**

This command targets a critical path. Use safer alternative:

- For `node_modules`: `rm -rf node_modules && npm install`
- For other paths: `mv <path> ~/.Trash/` or `rm -ri <path>`

Verify the exact path before retrying with a safer command.
