---
name: prc
description: >-
  Review and address code review comments on PR. Use when asked to
  'address review comments', 'fix PR feedback', 'handle review comments',
  'respond to PR comments', or 'address CR comments'.
  NOT for initiating code review (use /sr),
  NOT for task-based implementation with CR mode (use /si).
argument-hint: [pr-number]
allowed-tools: Bash, Read, Edit, Glob, Grep, AskUserQuestion, TodoWrite
---

# PR Review Comments Handler

> **Announcement**: Begin with: "I'm using the **prc** skill for PR comment resolution."

## PRIMARY OBJECTIVE

Fetch, analyze, and address code review comments on the current PR. Present an action plan for user approval before implementing fixes, then commit and reply to reviewers.

## Related Skills

- `/sr` — Initiate a code review (before merge). Use that skill to start a review, this skill to address the results.
- `/si` — Task-based implementation with "Address CR" mode. Use `/si` when review feedback requires structured task-driven changes; use `/prc` for direct, ad-hoc PR comment handling.

---

## GATE 1: Identify PR & Fetch Comments

### Step 1: Resolve PR

If `$ARGUMENTS` contains a PR number, use it. Otherwise:

1. Run `git branch --show-current` to get the current branch
2. Run `gh pr view --json number,title,url` to find the open PR

**Error — no PR found:**
Inform user: "No open PR found for branch `{branch}`. Verify the branch is pushed and the PR is open." Stop execution.

### Step 2: Fetch Comments

1. Run `gh api repos/{owner}/{repo}/pulls/{pr_number}/reviews` to get reviews
2. Run `gh api repos/{owner}/{repo}/pulls/{pr_number}/comments` to get inline comments
3. Also check `gh pr view {pr_number} --json comments` for general PR comments

**Error — no comments found:**
Inform user: "No review comments found on PR #{number}. Nothing to address." Stop execution.

---

## GATE 2: Analyze & Present Plan

### Step 1: Categorize Comments

List **every** comment fetched in Gate 1 — do not drop any. Reviewer noise, nits, and resolved threads all appear in the plan so the user sees what was received.

For each comment, evaluate:
- Is the feedback valid and technically correct?
- Is it applicable to the current code?
- Does it align with project conventions and architecture?
- Is it a blocker or a nice-to-have suggestion?

For each comment, propose one of:
- **Address** — Valid feedback, will fix.
- **Skip** — Not applicable, already handled, or nit you recommend ignoring. Always include a one-line reason so the user can override.
- **Discuss** — Ambiguous, contested, or would change scope — escalate to user.

When in doubt between Address and Skip, pick Discuss. The user decides in Gate 2 whether to drop it.

### Step 2: Present Action Plan

Display a table:

```
| # | File:Line | Comment Summary | Action | Complexity |
|---|-----------|-----------------|--------|------------|
| 1 | src/foo.ts:42 | Missing null check | Address | Simple |
| 2 | src/bar.ts:15 | Rename variable | Address | Simple |
| 3 | src/baz.ts:88 | Architecture concern | Discuss | Significant |
```

Before implementing anything, confirm the plan with AskUserQuestion. Ask the user to approve, edit, or flag items they disagree with — including items you marked Skip. Implementation starts only after approval.

---

## GATE 3: Implement & Verify

### Step 1: Apply Fixes

For each approved "Address" item:
1. Read the target file
2. Make the necessary code change using Edit
3. Track progress with TodoWrite

For "Discuss" items the user resolved: apply the agreed-upon fix.

### Step 2: Run Verification

1. Run project tests (`npm test` or equivalent)
2. Run lint checks (`{{LINT_CMD}}` or equivalent)
3. Run type checks if applicable (`tsc --noEmit`)

**Error — tests or lint fail:**
Present failures to user. Work with user to resolve, or revert changes if needed before moving to GATE 4.

---

## GATE 4: Commit, Push & Reply

### Step 1: Commit & Push

1. Stage changed files with `git add` (specific files only)
2. **Ask user permission** before committing
3. Create a focused commit: `fix: address PR review feedback`
4. Push to update the PR

### Step 2: Reply to Comments

For each addressed comment:
- Reply with a brief description of what was done (1-2 sentences)
- Use `gh api repos/{owner}/{repo}/pulls/comments/{comment_id}/replies -f body="..."` to reply

For skipped comments:
- Reply explaining why respectfully

**Error — gh API reply fails:**
Report the error and suggest manual reply via GitHub UI.

---

## Output Format

Provide a final summary:

```
## PR Review Summary

**PR**: #XX - Title
**Reviewer(s)**: @username

### Comments Addressed:
1. [file:line] - Brief description of fix
2. [file:line] - Brief description of fix

### Comments Skipped (if any):
1. [file:line] - Reason why not applicable

### Changes Made:
- List of files modified
- New commit: {hash}
```
