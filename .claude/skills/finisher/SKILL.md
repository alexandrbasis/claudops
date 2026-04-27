---
name: finisher
description: >-
  Close out work by committing local changes, pushing, waiting for green CI,
  and merging the PR. Universal — works on any branch with an open PR; no
  task structure required. Use when asked to 'merge the PR', 'ship it', 'merge
  and close', 'commit push merge', 'finalize the PR', 'land it on main',
  'we're done — close it out', or whenever the user signals end-of-work and
  the next step is to merge. If (and only if) the current work is one phase
  of a multi-phase task in `tasks/**/phase-N-*/`, also propagate cross-phase
  handoff information into upcoming phase tech-decomposition documents
  before merging — otherwise this step is silently skipped. Make sure to
  use this skill whenever the user signals end-of-implementation and wants
  the changes merged — even if they don't say the word "skill".
  NOT for opening a new PR (use plain `gh pr create`).
  NOT for addressing review comments (use /prc).
  NOT for preparing a session handoff to a fresh context (use /ph).
argument-hint: "[task-or-phase-directory] [--no-merge]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - TodoWrite
---

# Finisher

> **Announcement**: Begin with: "I'm using the **finisher** skill to ship this work — commit, push, wait for green CI, then merge."

## PRIMARY OBJECTIVE

Land the current implementation on the base branch with the PR cleanly merged. The skill is **universal**: it works on any branch with an open PR. There does **not** need to be a task directory, a tech-decomposition document, or a phase structure. If those things happen to exist, the skill picks them up and uses them; if not, it just ships the PR.

Before merging:

1. Commit and push any pending local changes onto the PR branch.
2. **(Conditional)** If the current work is one phase of a multi-phase task, propagate cross-phase handoff information into upcoming phase tech-decomposition documents. Skip silently otherwise.
3. Wait for CI to be green. Do not merge or stop on red CI.
4. Merge the PR.

This skill is the close-out counterpart to `/si` (implement) and `/sr` (review). It assumes review has already happened and the user is ready to ship.

## RELATED SKILLS

- `/sr` — Code review before merge. Run **before** this skill.
- `/prc` — Address review comments. Run before this skill if reviewers left feedback.
- `/ph` — Mid-implementation handoff to a fresh chat session. Different concern: `/ph` snapshots in-flight state for **the same task in a new chat**. This skill ships finished work to main; for split tasks it can also propagate information **between sibling phase tasks** at completion time, but that's a side concern, not the main job.
- `/udoc` — Documentation update + changelog. The user may want this run before merging; ask if relevant.

---

## GATE 1: Resolve PR (and optionally task)

### Step 1: Resolve PR (required)

```bash
git branch --show-current
gh pr view --json number,title,url,state,mergeable,baseRefName,headRefName,statusCheckRollup
```

If no PR exists for the branch, stop and ask the user whether to create one (`gh pr create`) or whether they invoked the wrong skill.

If the PR is already merged, report that and stop — the work is already shipped.

If the PR is in **CLOSED** (not merged) state, stop and ask the user how to proceed.

### Step 2: Resolve Task Directory (optional)

This step is **best-effort and silent**. The skill works fine without a task directory — most invocations probably won't have one. Only enrich Gate 3 if a task is found cleanly.

1. If `$ARGUMENTS` includes a path, treat it as the task or phase directory and read its `tech-decomposition-*.md`. If the path doesn't exist or has no tech-decomposition file, surface that to the user — they pointed somewhere specific, so don't silently ignore it.
2. Otherwise, look at the project root:
   - If there's no `tasks/` directory at all → no task. Continue with PR-only flow. Do **not** prompt the user.
   - If `tasks/` exists, do a quick scan for a `tech-decomposition-*.md` whose path or contents reference the current branch.
     - **Exactly one match** → use it.
     - **Zero matches** → no task. Continue with PR-only flow. Do **not** prompt the user.
     - **Multiple matches** → ambiguous. Ask the user once: "Found N candidate task directories — which one is this PR closing out, or none?" Accept "none" as a valid answer.
3. If a task is resolved, capture:
   - Task name and goal
   - Whether it lives directly under `tasks/` (single task) or inside a `phase-N-*/` subfolder (one phase of a split task)
   - The parent task directory if this is a phase

**Why this matters:** The phase-handoff step in Gate 3 only fires when the resolved task is inside a `phase-N-*/` folder. No task → no phase → Gate 3 skips silently. This keeps the skill universal: if the user just wants to ship a quick fix branch, no questions about tasks get asked.

### Step 3: Working Tree Snapshot

Run these in parallel:

```bash
git status --short
git diff --stat
git diff --cached --stat
git log --oneline @{u}..HEAD   # local commits not yet pushed
```

Hold this snapshot — Gate 2 commits, Gate 3 looks at completion summary, Gate 4 pushes.

---

## GATE 2: Commit Local Changes

### Step 1: Decide What Goes In

If the working tree is clean and there are no unpushed local commits, skip ahead to Gate 3 (handoff check) and Gate 4 (push is a no-op).

Otherwise, present what's pending:

- Modified/staged/untracked files (from `git status --short`)
- Diff summary (from `git diff --stat` and `--cached --stat`)
- Local-only commits (from `git log @{u}..HEAD`)

Ask the user:
- Confirm which files to include. Stage **specific files by name** — never `git add -A` or `git add .` (could pull in secrets, scratch files, or `tasks/` debug output).
- Confirm the commit message. Default to a single focused message describing the final delta; squash trivial scratch commits into the description if helpful.

### Step 2: Commit

Use a heredoc-style commit (the harness `Bash` tool guidance requires this for proper formatting):

```bash
git add <specific files>
git commit -m "$(cat <<'EOF'
<subject line>

<optional body>
EOF
)"
```

Do not pass `--no-verify`. If a pre-commit hook fails, **fix the underlying issue** and create a new commit — never amend or skip hooks. The hook exists for a reason.

---

## GATE 3: Phase Handoff Check (Conditional)

**Only run this gate if the current task lives inside a `phase-N-*/` folder under a parent task directory.**

For a single (non-split) task, skip directly to Gate 4.

### Step 1: Identify Upcoming Phases

```bash
# From the parent task directory (the one containing all phase-N-*/ folders):
ls -d phase-*/ | sort
```

The current phase is `phase-K-*`. Upcoming phases are `phase-N-*` for `N > K`.

If there are no upcoming phases (this is the final phase), record that and skip to Gate 4.

### Step 2: Identify Handoff-Worthy Information

Read the current phase's tech-decomposition document and look for things that **the upcoming phases must know but might not yet reflect**:

- **Decisions made during implementation** that diverged from the original plan (renamed module, swapped library, schema change, feature flag added).
- **Contract changes** — new exports, changed function signatures, new endpoints, changed event shapes that upcoming phases consume.
- **Deferred work** explicitly handed to a later phase ("X is stubbed; phase 3 wires it up").
- **Gotchas / surprises** discovered during implementation (test infra quirk, race condition workaround, ordering constraint).
- **New file or module locations** that upcoming phases reference.

Sources to mine: `Completion Summary`, `Implementation Decisions`, `Notes`, `Deferred Follow-ups`, and the actual diff (`git diff $(git merge-base HEAD <base>)..HEAD --stat`) — sometimes decisions live in code but never made it back into the doc.

If nothing is handoff-worthy, say so explicitly and skip to Gate 4. Empty handoffs are honest; padding them dilutes the signal in real ones.

### Step 3: Propose Updates Per Upcoming Phase

For each upcoming phase, propose **only** the items relevant to that phase. Do not blanket-copy the same notes everywhere.

Present the proposal as a table:

```
| Phase | Doc | Item to add | Why this phase needs it |
|-------|-----|-------------|--------------------------|
| phase-2-session-join | tech-decomposition-phase-2-session-join.md | "Profile lookup now returns `{ id, displayName }` (renamed from `name`)" | Phase 2 calls this endpoint |
| phase-3-presence | tech-decomposition-phase-3-presence.md | "Feature flag `presence_v2` controls rollout" | Phase 3 toggles behavior on this flag |
```

Use `AskUserQuestion` to confirm: approve, edit, or skip items. Only apply approved items.

### Step 4: Apply Updates

For each approved item, append to the relevant section of the upcoming phase's tech-decomposition document. Prefer additive edits under a clearly marked subsection, e.g.:

```markdown
### Handoff from phase-1-profile-lookup (added 2026-04-27)

- Profile lookup endpoint now returns `{ id, displayName }` (renamed from `name`)
  in commit abc1234. All consumers in this phase must use the new field.
```

Date-stamp the heading so future readers can tell when the note was added.

### Step 5: Commit Handoff Updates

If any upcoming phase docs changed:

```bash
git add tasks/<parent-task>/phase-*/tech-decomposition-*.md
git commit -m "docs: handoff notes to upcoming phases from <current-phase>"
```

Keep this commit separate from the implementation commit — it touches different files for a different reason and may need to be reverted independently.

---

## GATE 4: Push & Wait for Green CI

### Step 1: Push

```bash
git push
```

If the branch has no upstream yet, set it: `git push -u origin <branch>`.

### Step 2: Wait for CI

```bash
gh pr checks --watch
```

`--watch` blocks until all checks complete. Do not stop early; do not declare success based on partial results.

If checks pass: continue to Gate 5.

If checks fail:
- Capture the failing check names and any log excerpts: `gh pr checks` (without `--watch`) shows the final state.
- **Stop and report to the user.** Do not merge. Do not declare the skill complete. The user's instruction was explicit: CI must be green before stopping.
- Offer to investigate (read failing job logs via `gh run view <run-id> --log-failed | tail -100`) but do not auto-fix without approval — a CI failure may indicate a real bug or a flaky test, and the right action depends on which.

If checks are stuck "queued" or "in_progress" for an unreasonable time, surface that too — sometimes a runner is wedged and the user needs to retrigger manually.

---

## GATE 5: Merge

### Step 1: Final Confirmation

Before merging, summarize for the user:

```
Ready to merge:
- PR: #NN — <title>
- Base: <base-branch>
- Head: <feature-branch>
- Commits being merged: <count>
- CI: all checks green
- Phase handoff: <"updated N upcoming phase docs" | "not applicable" | "no handoff needed">
```

Ask once: "Merge now?" Use `AskUserQuestion`. Merging is hard to reverse cleanly (especially after the branch is deleted), so confirm even in auto-mode flows.

### Step 2: Merge

Use the merge method the project prefers. If unsure, ask. Common options:

```bash
# Squash (most projects' default)
gh pr merge <PR#> --squash --delete-branch

# Merge commit
gh pr merge <PR#> --merge --delete-branch

# Rebase
gh pr merge <PR#> --rebase --delete-branch
```

`--delete-branch` removes the remote branch after merge. Skip it if the project keeps merged branches around (rare).

### Step 3: Verify Merge Succeeded

```bash
gh pr view <PR#> --json state,merged,mergedAt
```

Confirm `merged: true`. If not, surface the error from `gh` and stop.

### Step 4: Local Cleanup

Switch back to the base branch and pull:

```bash
git checkout <base-branch>
git pull
git branch -d <feature-branch>   # safe delete; refuses if unmerged
```

If `git branch -d` refuses, do **not** force-delete with `-D` automatically — that would silently discard work. Surface it to the user; it usually means the local branch has commits the remote PR didn't (e.g., something committed after the last push).

---

## OUTPUT FORMAT

Final summary:

```
## Shipped: <PR title>

**PR**: <url> (merged at <timestamp>)
**Base**: <base-branch>
**Commits merged**: <count>
**CI**: all green (<N> checks)

### Phase handoff
<one of>
- N/A (single task, not a phase)
- Final phase — no upcoming phases to update
- Updated <count> upcoming phase docs:
  - phase-2-session-join: <one-line summary of what was added>
  - phase-3-presence: <one-line summary>

### Local
- Switched to <base-branch>, pulled latest
- Deleted local branch <feature-branch>
```

---

## STOP CONDITIONS (do not declare success if any of these hold)

- CI is not green. Failed, cancelled, or still-running checks all count as not-green. The user's instruction is explicit on this.
- The PR is not in `merged: true` state after Gate 5.
- An approved handoff update silently failed to apply (file write error, merge conflict in upcoming phase doc).

In any of these cases, report the actual state honestly and let the user decide next steps. Optimistic summaries that mask failures cost the user real debugging time later.

---

## NOTES ON SAFETY

- Never use `--no-verify`, `--force`, `--force-with-lease`, or `git push -f` from this skill. Pushing to a PR branch is normal `git push`; if it's rejected, that's a signal something changed remotely (someone else pushed, a bot rebased) and the right move is to investigate, not overwrite.
- Never `git add -A` or `git add .`. Stage by filename so you don't accidentally commit `.env`, scratch files in `tasks/`, or local debugging artifacts.
- The `--no-merge` argument lets the user run everything up to (but not including) Gate 5, useful when they want CI green and handoff notes applied but want to merge manually via the GitHub UI.
