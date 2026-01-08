# Linear Operations - Patterns and Anti-Patterns

Safe and unsafe patterns for Linear operations via `cc` one-shot sessions.

## Core Principle: One Operation Per Command

The spawned `cc` session has **no feedback loop** — it cannot ask clarifying questions. Combined operations cause ambiguity and may result in:
- Description field overwritten with comment text
- Wrong MCP tool invoked
- Incomplete operations

---

## Atomic Operations (CORRECT)

Each command below invokes exactly ONE MCP tool. **Always use pipe syntax.**

### Update Status Only
```bash
echo 'Update issue WYT-66 status to "In Review". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -
```
- **Tool used**: `mcp__linear__update_issue`

### Add Comment Only
```bash
echo 'Add comment to WYT-66: "Implementation completed. PR #123 ready for review."' | cc --mcp-config .claude/mcp/linear.json -p -
```
- **Tool used**: `mcp__linear__create_comment`

### Create Issue
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Create Linear issue in WYT team:
- title: "Add user logout functionality"
- description: "Implement logout button in settings page"
- priority: 3
Return the created issue ID and URL.
EOF
```
- **Tool used**: `mcp__linear__create_issue`

### Get Issue Details
```bash
echo 'Get details for issue WYT-66. Return: title, status, description, labels.' | cc --mcp-config .claude/mcp/linear.json -p -
```
- **Tool used**: `mcp__linear__get_issue`

### Search Issues
```bash
echo 'Search WYT issues containing "authentication". Return top 5 results with ID and title.' | cc --mcp-config .claude/mcp/linear.json -p -
```
- **Tool used**: `mcp__linear__search_issues`

---

## Multi-Operation Sequences (CORRECT)

When multiple operations are needed, execute **SEPARATE** commands:

### Example: Complete Implementation → Ready for Review

```bash
# Command 1: Update status
echo 'Update issue WYT-66 status to "In Review". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# Command 2: Add completion comment (SEPARATE call)
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to WYT-66:
"Implementation completed.
- Key changes: Added logout endpoint, updated auth middleware
- Test coverage: 85%
- PR ready for review."
EOF
```

### Example: Code Review Complete → Approved

```bash
# Command 1: Update status
echo 'Update issue WYT-66 status to "Ready to Merge". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# Command 2: Add review comment
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to WYT-66:
"Code review completed.
Status: APPROVED
Summary: Clean implementation, tests passing.
Next steps: Merge PR."
EOF
```

### Example: Task Done → Archived

```bash
# Command 1: Update status to Done
echo 'Update issue WYT-66 status to "Done". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# Command 2: Add completion comment
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to WYT-66:
"Task completed and PR merged.
SHA: abc123
Archive: tasks/completed/task-2025-01-15-feature/"
EOF
```

---

## Anti-Patterns (WRONG - DO NOT USE)

### Combined Status + Comment

```bash
# WRONG - Causes description overwrite
echo 'Update WYT-66: 1. Set status to In Review 2. Add comment: Implementation completed' | cc --mcp-config .claude/mcp/linear.json -p -
```

**Why it fails**: Session may put comment text into description field.

### Vague Operations

```bash
# WRONG - Too vague, will trigger questions
echo 'Update the task with progress' | cc --mcp-config .claude/mcp/linear.json -p -
```

**Why it fails**: Missing issue ID, unclear what "progress" means.

### Ambiguous Status Values

```bash
# WRONG - ambiguous phrasing
echo 'Mark WYT-66 as Needs Fixes' | cc --mcp-config .claude/mcp/linear.json -p -

# CORRECT - explicit
echo 'Update issue WYT-66 status to "Needs Fixes". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -
```

### Missing Constraints

```bash
# RISKY - No explicit constraint
echo 'Update WYT-66 status to "Done"' | cc --mcp-config .claude/mcp/linear.json -p -

# CORRECT - explicit constraint
echo 'Update issue WYT-66 status to "Done". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -
```

---

## Safe Template for Any Operation

```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
ACTION: [EXACTLY ONE OF: create_issue | update_issue | create_comment | get_issue | search_issues]

TARGET: [issue ID, e.g., WYT-66]

PARAMETERS:
- [field]: [exact value]

CONSTRAINTS:
- Do NOT modify fields other than [specified field]

RETURN: [what you need back]
EOF
```

---

## Quick Reference

| Action | MCP Tool | Combinable? |
|--------|----------|-------------|
| Update status | `update_issue` | NO |
| Update priority | `update_issue` | NO |
| Add comment | `create_comment` | NO |
| Create issue | `create_issue` | YES |
| Get details | `get_issue` | YES |
| Search | `search_issues` | YES |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Description overwritten | Combined status+comment | Use separate commands |
| Comment in wrong field | Ambiguous prompt | Use explicit "Add comment to [ID]: ..." |
| Operation incomplete | Vague prompt | Add all required parameters |
