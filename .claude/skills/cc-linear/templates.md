# Linear Command Templates

Copy-paste-ready commands. Replace `[placeholders]` with actual values.

---

## Status Updates

```bash
# To "In Progress"
echo 'Update issue [ISSUE-ID] status to "In Progress". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# To "In Review"
echo 'Update issue [ISSUE-ID] status to "In Review". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# To "Needs Fixes"
echo 'Update issue [ISSUE-ID] status to "Needs Fixes". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# To "Ready to Merge"
echo 'Update issue [ISSUE-ID] status to "Ready to Merge". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# To "Done"
echo 'Update issue [ISSUE-ID] status to "Done". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -
```

---

## Comments

### Implementation Started
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Implementation started.
Branch: [BRANCH-NAME]
Started: [TIMESTAMP]"
EOF
```

### Implementation Completed
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Implementation completed.
- Key changes: [LIST-CHANGES]
- Test coverage: [X]%
- Technical notes: [NOTES]
PR ready for review."
EOF
```

### Code Review Started
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Code review started.
Task: [TASK-PATH]
Started: [TIMESTAMP]
Review doc: Will be created in task directory"
EOF
```

### Code Review Completed
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Code review completed.

**Status**: [APPROVED / NEEDS FIXES / NEEDS DISCUSSION]
**Review Doc**: [REVIEW-DOC-PATH]
**Completed**: [TIMESTAMP]
**Summary**: [KEY-FINDINGS]
**Issues**: [X critical, Y major, Z minor]
**Next Steps**: [ACTION-ITEMS]"
EOF
```

### Task Merged
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Task completed and PR merged.

**Status**: COMPLETED
**SHA**: [COMMIT-SHA]
**PR**: [PR-URL]
**Date**: [TIMESTAMP]
**Archive**: tasks/completed/[TASK-DIR]/

**Summary**: [FUNCTIONALITY-DELIVERED]
**Quality**: Review passed, tests green"
EOF
```

---

## Issue Creation

### Create Feature Task
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Create Linear issue in WYT team:
- title: "[FEATURE-TITLE]"
- description: "## Context
[WHY-THIS-EXISTS]

## Requirements
- [REQUIREMENT-1]
- [REQUIREMENT-2]

## Acceptance Criteria
- [ ] [CRITERION-1]
- [ ] [CRITERION-2]"
- priority: 3

Return the created issue ID and URL.
EOF
```

### Create Bug Report
```bash
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Create Linear issue in WYT team:
- title: "Bug: [BUG-TITLE]"
- description: "## Description
[BUG-DESCRIPTION]

## Steps to Reproduce
1. [STEP-1]
2. [STEP-2]

## Expected vs Actual
- Expected: [EXPECTED]
- Actual: [ACTUAL]"
- priority: 2

Return the created issue ID and URL.
EOF
```

---

## Queries

```bash
# Get issue details
echo 'Get details for issue [ISSUE-ID]. Return: title, status, description, labels.' | cc --mcp-config .claude/mcp/linear.json -p -

# Search issues
echo 'Search WYT issues containing "[SEARCH-TERM]". Return top 5 results with ID and title.' | cc --mcp-config .claude/mcp/linear.json -p -

# Get top priority tasks
echo 'Get top 5 tasks from WYT ordered by priority. Return: ID, title, status, priority.' | cc --mcp-config .claude/mcp/linear.json -p -
```

---

## Workflow Sequences

### Start Implementation (2 commands)
```bash
# 1. Update status
echo 'Update issue [ISSUE-ID] status to "In Progress". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# 2. Add start comment
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Implementation started.
Branch: [BRANCH-NAME]
Started: [TIMESTAMP]"
EOF
```

### Submit for Review (2 commands)
```bash
# 1. Update status
echo 'Update issue [ISSUE-ID] status to "In Review". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# 2. Add completion comment
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Implementation completed.
- Key changes: [LIST-CHANGES]
- Test coverage: [X]%
PR ready for review."
EOF
```

### Complete Task (2 commands)
```bash
# 1. Update status
echo 'Update issue [ISSUE-ID] status to "Done". Do NOT modify description.' | cc --mcp-config .claude/mcp/linear.json -p -

# 2. Add merge comment
cat <<'EOF' | cc --mcp-config .claude/mcp/linear.json -p -
Add comment to issue [ISSUE-ID]:
"Task completed and merged.
SHA: [COMMIT-SHA]
PR: [PR-URL]"
EOF
```

---

## Reference

### Valid Status Values
```
Backlog | Ready for Implementation | In Progress | In Review | Needs Fixes | Ready to Merge | Done | Canceled
```

### Priority Levels
```
0: None | 1: Urgent | 2: High | 3: Normal (default) | 4: Low
```
