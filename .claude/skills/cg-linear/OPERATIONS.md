# Linear Operations - Patterns and Anti-Patterns

This document defines safe and unsafe patterns for Linear operations via `cg` one-shot sessions.

## Core Principle: One Operation Per Command

The spawned `cg` session has **no feedback loop** — it cannot ask clarifying questions. Combined operations cause ambiguity and may result in:
- Description field overwritten with comment text
- Wrong MCP tool invoked
- Incomplete operations

---

## Atomic Operations (CORRECT)

Each command below invokes exactly ONE MCP tool:

### Update Status Only
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'In Review'. Do NOT modify description or other fields."
```
- **Tool used**: `mcp__linear__update_issue`
- **Safe**: Yes

### Add Comment Only
```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66: 'Implementation completed. PR #123 ready for review.'"
```
- **Tool used**: `mcp__linear__create_comment`
- **Safe**: Yes

### Create Issue
```bash
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team:
- title: 'Add user logout functionality'
- description: 'Implement logout button in settings page'
- priority: 3
Return the created issue ID and URL."
```
- **Tool used**: `mcp__linear__create_issue`
- **Safe**: Yes (description is part of creation, not an update)

### Get Issue Details
```bash
cg --mcp-config .claude/mcp/linear.json -p "Get details for issue WYT-66. Return: title, status, description, labels."
```
- **Tool used**: `mcp__linear__get_issue`
- **Safe**: Yes (read-only)

### Search Issues
```bash
cg --mcp-config .claude/mcp/linear.json -p "Search WYT issues containing 'authentication'. Return top 5 results with ID and title."
```
- **Tool used**: `mcp__linear__search_issues`
- **Safe**: Yes (read-only)

---

## Multi-Operation Sequences (CORRECT)

When multiple operations are needed, execute **SEPARATE** commands:

### Example: Complete Implementation → Ready for Review

```bash
# Command 1: Update status to 'In Review'
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'In Review'. Do NOT modify description."

# Command 2: Add completion comment (SEPARATE call)
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66:
'Implementation completed.
- Key changes: Added logout endpoint, updated auth middleware
- Test coverage: 85%
- PR ready for review.'"
```

### Example: Code Review Complete → Approved

```bash
# Command 1: Update status
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'Ready to Merge'. Do NOT modify description."

# Command 2: Add review comment
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66:
'Code review completed.
Status: APPROVED
Summary: Clean implementation, tests passing.
Next steps: Merge PR.'"
```

### Example: Task Done → Archived

```bash
# Command 1: Update status to Done
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'Done'. Do NOT modify description."

# Command 2: Add completion comment
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66:
'Task completed and PR merged.
SHA: abc123
Archive: tasks/completed/task-2025-01-15-feature/'"
```

---

## Anti-Patterns (WRONG - DO NOT USE)

### Combined Status + Comment

```bash
# WRONG - Causes description overwrite
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66:
1. Set status to 'In Review'
2. Add comment: 'Implementation completed'"
```

**Why it fails**: The spawned session interprets the entire prompt as an update request and may:
- Put "Add comment: 'Implementation completed'" into the description field
- Use `update_issue` instead of `create_comment`
- Overwrite the original task description

### Vague Operations

```bash
# WRONG - Too vague, will trigger questions
cg --mcp-config .claude/mcp/linear.json -p "Update the task with progress"
```

**Why it fails**: Missing issue ID, unclear what "progress" means.

### Ambiguous Status Values

```bash
# WRONG - "Needs Fixes" could be interpreted as text
cg --mcp-config .claude/mcp/linear.json -p "Mark WYT-66 as Needs Fixes"
```

**Better**:
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'Needs Fixes'. Do NOT modify description."
```

### Missing Constraints

```bash
# RISKY - No explicit constraint
cg --mcp-config .claude/mcp/linear.json -p "Update WYT-66 status to 'Done'"
```

**Better** (explicit constraint):
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'Done'. Do NOT modify description or other fields."
```

---

## Safe Template for Any Operation

Use this template for maximum safety:

```bash
cg --mcp-config .claude/mcp/linear.json -p "
ACTION: [EXACTLY ONE OF: create_issue | update_issue | create_comment | get_issue | search_issues]

TARGET: [issue ID, e.g., WYT-66]

PARAMETERS:
- [field]: [exact value]

CONSTRAINTS:
- Do NOT modify fields other than [specified field]
- Use Linear MCP tool directly

RETURN:
- [what you need back, e.g., 'Confirm status changed']
"
```

---

## Quick Reference: Which Tool for What

| Action | MCP Tool | Safe to Combine? |
|--------|----------|------------------|
| Update status | `update_issue` | NO - separate call |
| Update priority | `update_issue` | NO - separate call |
| Add comment | `create_comment` | NO - separate call |
| Create issue | `create_issue` | YES - description is part of creation |
| Get details | `get_issue` | YES - read-only |
| Search | `search_issues` | YES - read-only |

---

## Troubleshooting

### Description was overwritten
**Cause**: Combined status+comment prompt
**Fix**: Always use separate commands for status and comments

### Comment appeared in wrong field
**Cause**: Ambiguous prompt interpreted as update
**Fix**: Use explicit "Add comment to [ISSUE-ID]: '[text]'" format

### Operation didn't complete
**Cause**: Vague prompt triggered clarifying question (no response possible)
**Fix**: Make prompt self-contained with all required parameters
