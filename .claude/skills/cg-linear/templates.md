# Linear Command Templates

Copy-paste-ready commands for common Linear operations. Replace `[placeholders]` with actual values.

---

## Status Updates

### To "In Progress"
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Progress'. Do NOT modify description."
```

### To "In Review"
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Review'. Do NOT modify description."
```

### To "Needs Fixes"
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'Needs Fixes'. Do NOT modify description."
```

### To "Ready to Merge"
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'Ready to Merge'. Do NOT modify description."
```

### To "Done"
```bash
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'Done'. Do NOT modify description."
```

---

## Comments

### Implementation Started
```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Implementation started.
Branch: [BRANCH-NAME]
Started: [TIMESTAMP]'"
```

### Implementation Completed
```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Implementation completed.
- Key changes: [LIST-CHANGES]
- Test coverage: [X]%
- Technical notes: [NOTES]
PR ready for review.'"
```

### Code Review Started
```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Code review started.
Task: [TASK-PATH]
Started: [TIMESTAMP]
Review doc: Will be created in task directory'"
```

### Code Review Completed
```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Code review completed.

**Status**: [APPROVED / NEEDS FIXES / NEEDS DISCUSSION]
**Review Doc**: [REVIEW-DOC-PATH]
**Completed**: [TIMESTAMP]
**Summary**: [KEY-FINDINGS]
**Issues**: [X critical, Y major, Z minor]
**Next Steps**: [ACTION-ITEMS]'"
```

### Task Merged
```bash
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Task completed and PR merged.

**Status**: COMPLETED
**SHA**: [COMMIT-SHA]
**PR**: [PR-URL]
**Date**: [TIMESTAMP]
**Archive**: tasks/completed/[TASK-DIR]/

**Summary**: [FUNCTIONALITY-DELIVERED]
**Quality**: Review passed, tests green'"
```

---

## Issue Creation

### Create Feature Task
```bash
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team:
- title: '[FEATURE-TITLE]'
- description: '## Context
[WHY-THIS-EXISTS]

## Requirements
- [REQUIREMENT-1]
- [REQUIREMENT-2]

## Acceptance Criteria
- [ ] [CRITERION-1]
- [ ] [CRITERION-2]'
- priority: 3

Return the created issue ID and URL."
```

### Create Bug Report
```bash
cg --mcp-config .claude/mcp/linear.json -p "Create Linear issue in WYT team:
- title: 'Bug: [BUG-TITLE]'
- description: '## Description
[BUG-DESCRIPTION]

## Steps to Reproduce
1. [STEP-1]
2. [STEP-2]

## Expected vs Actual
- Expected: [EXPECTED]
- Actual: [ACTUAL]'
- priority: 2

Return the created issue ID and URL."
```

---

## Queries

### Get Issue Details
```bash
cg --mcp-config .claude/mcp/linear.json -p "Get details for issue [ISSUE-ID]. Return: title, status, description, labels."
```

### Search Issues
```bash
cg --mcp-config .claude/mcp/linear.json -p "Search WYT issues containing '[SEARCH-TERM]'. Return top 5 results with ID and title."
```

### Get Top Priority Tasks
```bash
cg --mcp-config .claude/mcp/linear.json -p "Get top 5 tasks from WYT project ordered by priority. Return: ID, title, status, priority."
```

---

## Workflow Sequences

### Start Implementation (2 commands)
```bash
# 1. Update status
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Progress'. Do NOT modify description."

# 2. Add start comment
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Implementation started.
Branch: [BRANCH-NAME]
Started: [TIMESTAMP]'"
```

### Submit for Review (2 commands)
```bash
# 1. Update status
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'In Review'. Do NOT modify description."

# 2. Add completion comment
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Implementation completed.
- Key changes: [LIST-CHANGES]
- Test coverage: [X]%
PR ready for review.'"
```

### Complete Task (2 commands)
```bash
# 1. Update status
cg --mcp-config .claude/mcp/linear.json -p "Update issue [ISSUE-ID] status to 'Done'. Do NOT modify description."

# 2. Add merge comment
cg --mcp-config .claude/mcp/linear.json -p "Add comment to issue [ISSUE-ID]:
'Task completed and merged.
SHA: [COMMIT-SHA]
PR: [PR-URL]'"
```

---

## Valid Status Values

```
Backlog
Ready for Implementation
In Progress
In Review
Needs Fixes
Ready to Merge
Done
Canceled
```

## Priority Levels

```
0: None
1: Urgent
2: High
3: Normal (default)
4: Low
```
