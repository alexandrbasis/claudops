---
description: Review and address code review comments on PR
---

# PR Review Comments Handler

Review and address code review comments on the current PR.

## Instructions

1. **Identify current branch and PR**:
   - Get the current git branch name
   - Find the open PR for this branch using `gh pr view`
   - Fetch all review comments using `gh api repos/{owner}/{repo}/pulls/{pr_number}/comments`

2. **Analyze each comment carefully**:
   For each review comment, evaluate:
   - Is this feedback valid and technically correct?
   - Is it applicable to the current code?
   - Does it align with project conventions and architecture?
   - Is it a blocker or a nice-to-have suggestion?

3. **Create action plan**:
   For valid and applicable comments:
   - List the specific changes needed
   - Identify affected files
   - Estimate complexity (simple fix / moderate / significant refactor)

4. **Implement fixes**:
   - Make the necessary code changes
   - Run tests to verify nothing is broken
   - Run lint/build checks

5. **Commit and push**:
   - Create a focused commit addressing the review feedback
   - Push changes to update the PR

6. **Reply to each comment**:
   - For addressed comments: briefly describe what was done (1-2 sentences)
   - For comments that won't be addressed: explain why respectfully
   - Use `gh api repos/{owner}/{repo}/pulls/comments/{comment_id}/replies` to reply

## Output Format

Provide a summary:
```
## PR Review Summary

**PR**: #XX - Title
**Reviewer(s)**: @username

### Comments Addressed:
1. [file:line] - Brief description of fix
2. [file:line] - Brief description of fix

### Comments Not Addressed (if any):
1. [file:line] - Reason why not applicable

### Changes Made:
- List of files modified
- New commit: {hash}
```
