# Linear MCP Tools Reference

Detailed documentation for Linear MCP tools available when using `--mcp-config .claude/mcp/linear.json`.

## Configuration

### Workspace Settings (WYT Project)

```yaml
Team ID: WYT
```

### Task States (in order)

```yaml
- Backlog              # Intake
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

### Common Labels

```yaml
- backend
- frontend
- bug
- feature
```

## MCP Tools

### 1. Create Issue

```javascript
mcp__linear__create_issue({
  title: "Task title",           // required
  teamId: "WYT",                 // required
  description: "Markdown desc",  // optional
  priority: 3,                   // optional (0-4)
  projectId: "...",              // optional
  labelIds: ["..."]              // optional
})
```

**Description Template:**

```markdown
## Context
[Why this exists]

## Requirements
- [What needs to be done]
- [What needs to be done]

## Acceptance Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]
```

### 2. Update Issue

```javascript
mcp__linear__update_issue({
  id: "WYT-123",              // required
  state: "In Progress",       // optional
  priority: 2,                // optional
  assigneeId: "..."           // optional
})
```

### 3. Add Comment

```javascript
mcp__linear__create_comment({
  issueId: "WYT-123",         // required
  body: "Markdown comment"    // required
})
```

**Brief Update Template:**

```markdown
**Status**: [Old State] → [New State]
**Reason**: [1-2 sentence explanation]
```

**Detailed Progress Template:**

```markdown
## [Emoji] [Title]

**[Key Info]**: [Value]
**[Key Info]**: [Value]

[Brief details about what happened or what's next]
```

### 4. Get Issue

```javascript
mcp__linear__get_issue({
  id: "WYT-123"               // required
})
```

### 5. Search Issues

```javascript
mcp__linear__search_issues({
  query: "search terms",      // required
  teamId: "WYT"               // optional
})
```

## Response Format

After executing Linear operations, format response as:

```
✅ [Created/Updated/Commented on] Linear task [ISSUE-ID]

[2-3 lines of key details]

URL: [Linear URL if available]
```

## Error Handling

- **Missing info**: Ask user for required fields
- **API fails**: Explain error and suggest fix
- **Unclear request**: State interpretation and confirm

## Common Prompts for cg

```bash
# List tasks
cg --mcp-config .claude/mcp/linear.json -p "Get top 5 tasks from WYT"

# Get specific issue
cg --mcp-config .claude/mcp/linear.json -p "Get details for WYT-66"

# Create issue
cg --mcp-config .claude/mcp/linear.json -p "Create issue in WYT: title='Add logout button', description='Add logout functionality to settings page', priority=3"

# Update status
cg --mcp-config .claude/mcp/linear.json -p "Update WYT-66 status to 'Done'"

# Add comment
cg --mcp-config .claude/mcp/linear.json -p "Add comment to WYT-66: 'PR merged, ready for QA'"

# Search
cg --mcp-config .claude/mcp/linear.json -p "Search WYT issues for 'authentication'"
```
