---
name: cg-linear
description: Execute atomic Linear operations via one-shot `cg` session with Linear MCP. Use for creating issues, updating status, adding comments, querying tasks. CRITICAL: Each command performs ONE operation only. For multi-step workflows (update status THEN add comment), execute SEPARATE `cg` commands sequentially. Spawned sessions cannot ask clarifying questions - prompts must be self-contained and unambiguous. See OPERATIONS.md for patterns and anti-patterns.
---

# CG Linear

Interact with Linear task management via `cg` alias — spawns a one-shot Claude Code session with Linear MCP connected.

## When to Use

- Create Linear issues from current session
- Update issue status (In Progress, In Review, Done, etc.)
- Query issue details or search issues
- Add comments to issues
- Any Linear operation without leaving current context

## Critical: One-Shot Limitation

```
Main Chat → Bash → cg session (one-shot) → Results back
                        ↑
                  NO FEEDBACK LOOP
```

**The Problem:**
- Spawned session executes prompt and returns output
- If it asks a clarifying question → you see it but CANNOT respond
- `--dangerously-skip-permissions` removes permission prompts, but NOT clarification questions

**The Solution: Self-Contained Prompts**

All prompts MUST be:
- **Concrete** — specify exactly what to do
- **Self-contained** — include ALL required parameters
- **Unambiguous** — no room for interpretation

```bash
# BAD - vague, will trigger questions
cg --mcp-config .claude/mcp/linear.json -p "Create a task"

# GOOD - self-contained
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team: title='Add logout button', description='Add logout functionality to settings page', priority=3"
```

## Basic Syntax

```bash
# One-shot command (recommended)
cg --mcp-config .claude/mcp/linear.json -p "your prompt"

# Interactive session (for complex operations)
cg --mcp-config .claude/mcp/linear.json
```

## Linear Operations

### Get Issues

```bash
# Top tasks from project
cg --mcp-config .claude/mcp/linear.json -p "Get top 5 tasks from WYT project ordered by priority"

# Specific issue details
cg --mcp-config .claude/mcp/linear.json -p "Get details for issue WYT-66"

# Search issues
cg --mcp-config .claude/mcp/linear.json -p "Search WYT issues containing 'authentication'"
```

### Create Issue

```bash
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team:
- title: 'Add user logout functionality'
- description: 'Implement logout button in settings page that clears session and redirects to login'
- priority: 3 (Normal)
Return the created issue ID and URL."
```

### Update Issue Status

```bash
# Update to In Progress
cg --mcp-config .claude/mcp/linear.json -p "Update WYT-66 status to 'In Progress'"

# Update to In Review
cg --mcp-config .claude/mcp/linear.json -p "Update WYT-66 status to 'In Review'"

# Update to Done
cg --mcp-config .claude/mcp/linear.json -p "Update WYT-66 status to 'Done'"
```

### Add Comment

```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66:
'Implementation completed. PR #123 ready for review.
- Added logout endpoint
- Updated auth middleware
- Tests passing'"
```

## Critical: Separate Operations

**NEVER combine status updates and comments in one prompt!**

The cg session may interpret "Add comment" as modifying the description field, causing loss of the original task description.

### WRONG - Combined prompt (causes description overwrite):
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66:
1. Set status to 'In Review'
2. Add comment: 'Implementation completed'"
```

### CORRECT - Separate prompts:
```bash
# First: Update status only
cg --mcp-config .claude/mcp/linear.json -p "Update issue WYT-66 status to 'In Review'. Do NOT modify the description."

# Second: Add comment separately
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66: 'Implementation completed. PR ready for review.'"
```

This ensures `update_issue` only changes status, and `create_comment` adds the comment.

## Configuration

### WYT Project Settings

```yaml
Team ID: WYT
```

### Task States (in order)

```yaml
- Backlog
- Ready for Implementation
- In Progress
- In Review
- Needs Fixes
- Ready to Merge
- Done
- Canceled
```

### Priority Levels

```yaml
0: None
1: Urgent
2: High
3: Normal (default)
4: Low
```

## Usage in Commands

When commands (like `/ct`, `/si`, `/sr`) need Linear operations, use this pattern:

```bash
# Instead of Task tool with linear-task-manager agent:
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT:
- title: '[Task Title]'
- description: '[Full description with context, requirements, acceptance criteria]'
- priority: [0-4]
Update the task document at [path] with the created issue ID and URL."
```

### Self-Contained Prompt Template for Commands

```bash
cg --mcp-config .claude/mcp/linear.json -p "
ACTION: [create_issue | update_issue | add_comment | get_issue | search_issues]

PARAMETERS:
- team: WYT
- [action-specific params...]

CONTEXT:
[Any relevant context the session needs]

OUTPUT:
Return [what you need back]
"
```

## Important Notes

1. **MCP Config Path**: Always use `.claude/mcp/linear.json`
2. **Working Directory**: Run from project root (relative path works)
3. **No Session Context**: Spawned session knows nothing about parent conversation
4. **Auth**: Linear MCP uses SSO — ensure authenticated in browser first
5. **Print Mode**: `-p` flag executes and exits — no hanging processes

## Troubleshooting

### Empty or Unexpected Output

Prompt was too vague. Add more specifics:
```bash
# Add team ID, full description, exact parameters
```

### MCP Connection Failed

Test connectivity:
```bash
cg --mcp-config .claude/mcp/linear.json -p "List all available Linear MCP tools"
```

### Authentication Issues

Linear MCP uses browser SSO. Open Linear in browser, ensure logged in, then retry.

## References

See `references/linear-mcp-tools.md` for detailed MCP tool signatures and templates.
