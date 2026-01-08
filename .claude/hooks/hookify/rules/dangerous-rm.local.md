---
name: dangerous-rm-command
enabled: true
event: bash
conditions:
  - field: command
    operator: regex_match
    pattern: 'rm\s+(-rf|-fr|--recursive.*--force|--force.*--recursive)\s+.*\b(node_modules|src|backend|prisma)\b|rm\s+(-rf|-fr)\s+(/|~|\$HOME)\s*$'
action: ask
---

**⚠️ Dangerous rm -rf detected**

This command targets a critical path. Consider safer alternatives:

| Instead of | Use |
|------------|-----|
| `rm -rf node_modules` | `rm -rf node_modules && npm install` |
| `rm -rf <path>` | `trash <path>` (trash-cli) |
| `rm -rf <path>` | `mv <path> ~/.Trash/` |
| `rm -rf <path>` | `rm -ri <path>` (interactive) |

**Options:**
- **Allow** - proceed with original command (risky)
- **Deny** - cancel and use safer alternative manually
