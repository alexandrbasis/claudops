# Opus 4.7 Review — `changelog-generator` and `create-pr-agent`

**Scope:** Two workflow-automation subagents that produce externally visible artifacts (changelog files, GitHub PRs, Linear updates). Review lens: INSIGHTS.md §1–§5, with special attention to confirm-before-destructive-action (§4 autonomy-and-safety), frontmatter `description:` dispatch hygiene, intensifier hygiene (§3), and literal-scope gaps (§4).

**Files reviewed:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/wf-agents/changelog-generator.md` (107 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/wf-agents/create-pr-agent.md` (235 lines)

---

## Agent 1 — `changelog-generator`

### Frontmatter

**Current (lines 1–6):**
```yaml
---
name: changelog-generator
description: Task-based changelog generator - Creates changelog entries from completed task documents
tools: Read, Write, Edit, Bash
model: sonnet
---
```

**Findings:**

- **[High] `description:` is under-specified for 4.7's action-biased dispatcher.** The current wording ("Task-based changelog generator - Creates changelog entries…") is purely descriptive of *what* the agent does, with no trigger guidance. Per INSIGHTS §1, 4.7 "will NOT silently generalize" and the dispatcher hook fires on `description` wording. This agent should fire only when a changelog artifact is explicitly requested (e.g. after task completion, before PR). A generic dispatcher could spawn it on any "update docs" request.

  **Before:**
  ```yaml
  description: Task-based changelog generator - Creates changelog entries from completed task documents
  ```

  **After:**
  ```yaml
  description: Use when the user explicitly asks to generate a changelog entry for a completed task, or when a workflow command (e.g. /update-docs, post-merge hook) needs to append a Keep-a-Changelog entry to docs/changelogs/YYYY-MM-DD/changelog.md. Do NOT invoke for general documentation updates or README edits. Requires a completed tech-decomposition-*.md with a populated "## Implementation Changelog" section.
  ```

- **[Medium] No `effort:` tier set.** The `create-pr-agent` sibling uses `effort: low` explicitly. This agent is equally mechanical (read → categorize → append). Per INSIGHTS §1, `xhigh` is the new default — leaving it unset risks unnecessary reasoning on a rote task.

  **Suggested add:**
  ```yaml
  effort: low
  ```

### High Priority

- **[High] Missing literal-scope guard for commit/task range (INSIGHTS §4 "literal-scope gaps").** The agent reads *one* `tech-decomposition-*.md` file (line 15: "Task Document: tasks/task-YYYY-MM-DD-[feature]/tech-decomposition-[feature].md"). It does not instruct the agent what to do if:
  - The caller passes multiple task documents
  - The `## Implementation Changelog` section is missing/empty
  - The task spans multiple dates
  - The task's completion date ≠ today (the WORKFLOW hardcodes `date +%Y-%m-%d` on line 48)

  4.7 will not silently generalize. Today, step 1 (line 48) says "Get current date … (or accept explicit date from the invoking command)" — but the agent is not told *how* to detect an explicit date vs. derive from the task folder name. This is an externally-visible artifact (commits to a dated changelog file), so scope ambiguity produces wrong-date entries.

  **Before (lines 47–50):**
  ```markdown
  ### Step 1: Determine Current Date and Directory
  - Get current date in `YYYY-MM-DD` format using `date +%Y-%m-%d` (or accept explicit date from the invoking command)
  - Create the directory if it doesn't exist: `mkdir -p docs/changelogs/YYYY-MM-DD/`
  ```

  **After:**
  ```markdown
  ### Step 1: Determine Target Date and Directory
  Resolve the target date in this order — do not guess:
  1. If the invoking command passed an explicit `--date YYYY-MM-DD`, use it.
  2. Otherwise extract the date from the task folder name (`tasks/task-YYYY-MM-DD-[feature]/`).
  3. Only fall back to `date +%Y-%m-%d` if neither is available.

  Apply this resolution to every task document passed in, not only the first. If multiple tasks resolve to different dates, process each into its own `docs/changelogs/<date>/changelog.md`.
  ```

- **[High] No confirm-before-destructive-action gate (INSIGHTS §4 autonomy-and-safety).** Unlike `create-pr-agent` which has an explicit "Permission Gate" section (create-pr-agent.md:9–17), this agent will write/append files to `docs/changelogs/` without any check. While less destructive than `gh pr create`, this is still an externally visible artifact that lands in git. If the agent is spawned in parallel or by an orchestrator that already ran it, double-appends produce duplicate changelog entries.

  **Suggested add (after the workflow header, line 46):**
  ```markdown
  ## Idempotency & Safety
  Before Step 5 (Generate and Insert), read the target `changelog.md` if it exists and check for an existing entry derived from the same task document (match by file references or section heading). If a matching entry already exists, report "already recorded — no changes" and exit without writing. Do not re-append.
  ```

### Medium Priority

- **[Medium] Intensifier hygiene is clean — no action needed here.** I scanned for `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` as emphasis — the file is well-behaved. Only one `especially` (line 17) which is load-bearing.

- **[Medium] "Focus on the `## Implementation Changelog` and completion summary" (line 53) is a soft nudge that may under-specify.** Per INSIGHTS §4 "State scope explicitly," 4.7 won't generalize "completion summary" to mean any of several possible sections. State the exact section names expected.

  **Before (line 53):**
  ```markdown
  - Read the `tech-decomposition-*.md` file to understand what was implemented
  - Focus on the `## Implementation Changelog` and completion summary for file paths, timestamps, and user impact
  ```

  **After:**
  ```markdown
  - Read the `tech-decomposition-*.md` file. Extract from these specific sections, in order:
    1. `## Implementation Changelog` — primary source for file paths, timestamps, user impact
    2. `## Primary Objective` — for the user-facing summary
    3. `## Acceptance Criteria` — to confirm scope of what landed
  - If `## Implementation Changelog` is missing or empty, stop and return "task document not ready — no Implementation Changelog section found." Do NOT fabricate entries from step checkboxes alone.
  ```

- **[Medium] `docs/changelogs/` path is hardcoded without configurability.** The sibling agents use template tokens (e.g. `{{SRC_DIR}}` appears on line 67). The changelog path should likewise be a project-configurable token (`{{CHANGELOG_DIR}}`). Not strictly a 4.7 issue, but the agent's own examples mix `{{SRC_DIR}}` (configurable) with a hardcoded `docs/changelogs/` (not configurable) — inconsistent scope handling that 4.7 will obey literally.

### Low Priority

- **[Low] "user-focused descriptions" and "clear" on line 66 are value-laden without a definition.** Per INSIGHTS §2 "Explain the *why*," add rationale. Example: "Write entries for a future developer reading history: what changed, where it lives, and why it matters to them. Not for the author recording what they did."

- **[Low] The file has three smart-quote characters (lines 14, 53, 54, 62, 66 — "`task’s`", "`doesn’t`"). Not a 4.7 issue, just hygiene.** Unicode apostrophes in filenames or regex patterns would break bash matching; they are inside prose here so benign.

---

## Agent 2 — `create-pr-agent`

### Frontmatter

**Current (lines 1–7):**
```yaml
---
name: create-pr-agent
description: Creates GitHub Pull Requests for completed tasks with Linear integration and traceability. Validates task documents, creates PRs with proper formatting, updates Linear issues, and maintains audit trail.
model: sonnet
effort: low
color: green
---
```

**Findings:**

- **[High] `description:` lacks trigger discipline for the highest-blast-radius agent in the repo.** This agent runs `gh pr create` and `git push` — externally visible, irreversible-ish actions (PRs can be closed but notifications have already fired). Per INSIGHTS §1, 4.7 is "more action-biased" and the dispatcher fires literally on `description`. Current wording describes what it *does*, not *when to invoke*. An orchestrator could spawn it opportunistically from "prepare this task for review."

  **Before:**
  ```yaml
  description: Creates GitHub Pull Requests for completed tasks with Linear integration and traceability. Validates task documents, creates PRs with proper formatting, updates Linear issues, and maintains audit trail.
  ```

  **After:**
  ```yaml
  description: Use ONLY when the user or orchestrator has explicitly approved creating a GitHub PR for a specific completed task document (e.g. "create the PR", "open a pull request for task X"). Requires an explicit `git_writes_approved: true` flag from the orchestrator — without it, the agent only produces a dry-run report. Do NOT invoke for "prepare for review," "get ready to merge," or any phrasing that does not explicitly request PR creation. Runs `git push` and `gh pr create` (externally visible).
  ```

- **[Info] `effort: low` is correctly set** — mechanical extract-and-template task; `low` is right here.

- **[Info] `tools:` field is missing.** Unlike `changelog-generator` which declares `tools: Read, Write, Edit, Bash`, this agent's frontmatter does not restrict tools. For an agent that runs `git push` and `gh pr create`, whitelisting only `Read, Edit, Bash` (no `Write` if not needed) limits blast radius. Consider: `tools: Read, Edit, Bash`.

### High Priority

- **[High] Permission Gate is present but wording is weakened by over-qualification (INSIGHTS §4 autonomy-and-safety).** Lines 9–17 establish the gate, but the word "MUST" is wrapped in a negative ("you must NOT run") which is correct structurally, while the surrounding document then uses `CRITICAL:` (line 83), `MUST` (line 83, 100, 108), `REQUIRED` (line 55) several more times for non-safety-related emphasis. Per INSIGHTS §3, overusing these intensifiers dilutes the ones that actually matter — the safety gate loses relative weight.

  The gate itself is good. The recommendation is to **remove intensifiers elsewhere** so the gate's imperative stands out. See the per-line list under "Intensifier hygiene" below.

- **[High] Literal-scope gap: PR base branch and head branch are never explicitly scoped (INSIGHTS §4).** The PR creation on line 65 uses `gh pr create` with no `--base` flag, and the workflow example on line 155 uses `--head "$(git branch --show-current)"` — but no instruction tells 4.7 which *base* branch to target. `gh pr create` will default to the repo's default branch (typically `main`), which is often correct but not always (release branches, long-lived feature branches, fork PRs). 4.7 "will NOT silently generalize" — if the task was branched off `develop` or a release branch, this creates a malformed PR targeting `main`.

  **Before (lines 60–68):**
  ```bash
  # Create comprehensive PR with Linear ID in title (REQUIRED)
  gh pr create --title "[type]($linear_id): $task_title" --body "$(cat <<EOF
  ...
  EOF
  )"
  ```

  **After:**
  ```bash
  # Resolve base branch explicitly. Do not assume "main".
  # 1. If orchestrator passed --base, use it.
  # 2. Otherwise read upstream tracking: git rev-parse --abbrev-ref <branch>@{upstream}
  # 3. Otherwise default to the repo's default branch via: gh repo view --json defaultBranchRef -q .defaultBranchRef.name
  base_branch="${PR_BASE:-$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)}"
  head_branch=$(git branch --show-current)

  # Confirm head branch is pushed to origin before creating PR
  git ls-remote --heads origin "$head_branch" | grep -q . || {
    echo "❌ Head branch $head_branch not on origin. Push required (git_writes_approved must be true)."
    exit 1
  }

  gh pr create \
    --base "$base_branch" \
    --head "$head_branch" \
    --title "[type]($linear_id): $task_title" \
    --body "$(cat <<EOF
  ...
  EOF
  )"
  ```

- **[High] Dry-run mode from the Permission Gate is never wired into the workflow section.** Lines 13–17 say "return a report with what information is missing, the exact commands that would be run if approved, the PR body text you would use" — but the workflow (section 2, lines 54–82) jumps straight to `gh pr create` with no conditional on `git_writes_approved`. A literal 4.7 could read section 2 as overriding the gate.

  **Suggested add at the top of Section 2 (line 55):**
  ```markdown
  ### 2. GitHub PR Creation

  **Precondition:** Proceed with the `gh pr create` and `git push` calls in this section only if the orchestrator prompt explicitly provided `git_writes_approved: true`. If not, produce the dry-run report described in the Permission Gate above — including the rendered PR body, base branch, head branch, and the exact `gh pr create` command that would run — and stop.
  ```

### Medium Priority

- **[Medium] Intensifier over-use dilutes the safety gate (INSIGHTS §3).** The file uses `CRITICAL:` / `MUST` / `REQUIRED` / `NEVER` as emphasis in places where they are not actually load-bearing. Concrete instances:

  | Line | Text | Status |
  |---|---|---|
  | 11 | "you must **NOT** run any `git push`…" | **Keep** — load-bearing safety |
  | 55 | "…with Linear ID in title (REQUIRED)" | Downgrade to normal voice: "Include the Linear ID in the title." |
  | 83 | "**CRITICAL**: PR titles MUST include the Linear issue ID for traceability." | Downgrade: "PR titles include the Linear issue ID so Linear auto-links the PR to the issue." (adds the *why* per INSIGHTS §2) |
  | 100 | "**Validation**: Before creating PR, ensure:" | Fine as-is — it's a section label, not an intensifier |
  | 38 | "Do **NOT** require per-step changelogs" | Keep — genuinely scoping behavior |

  Net effect: once the non-safety `CRITICAL`/`MUST`/`REQUIRED` are dialed back, the remaining `MUST NOT` in the Permission Gate carries the weight it's supposed to.

- **[Medium] "comprehensive" used 8 times without a stopping condition (INSIGHTS §3 "Be thorough / exhaustive / comprehensive").** Occurrences: lines 24, 57, 59, 84 (in example), 121, 148, 155, 161, and "thoroughly read" on line 29. Per INSIGHTS §3, this causes overthinking and scope creep. The agent is fundamentally a template-filler; "comprehensive" here should be replaced with concrete lists of required fields.

  **Before (line 24):**
  ```markdown
  Prepare comprehensive documentation in the task document to enable efficient code review with all necessary context and information.
  ```

  **After:**
  ```markdown
  Update the task document's "PR Traceability & Code Review Preparation" section (template below) so a reviewer opening the task has: PR URL, branch, Linear ID, step completion status, key files modified, and breaking-change callouts.
  ```

  Apply the same transform to lines 57, 59, 121, 148, 155, 161 — replace "comprehensive" with the concrete field list. This is particularly important for the PR body template (section 2) since 4.7 will otherwise pad the body with filler.

- **[Medium] "Thoroughly read and analyze" (line 29) is a classic 4.7 over-triggering phrase.** Per INSIGHTS §3, reflexive "be thorough" causes overthinking. The actual requirement is just field extraction.

  **Before (line 29):**
  ```markdown
  Thoroughly read and analyze the provided **technical decomposition file** (the orchestrator must pass the exact path) to extract:
  ```

  **After:**
  ```markdown
  Read the technical decomposition file at the path supplied by the orchestrator. Extract these fields (best-effort for optional ones):
  ```

- **[Medium] Literal-scope gap on Linear ID extraction (line 106).** The regex `[A-Z]+-[0-9]+` matches *any* uppercase-hyphen-digits pattern anywhere in the doc — including inline code, URLs from other projects, or quoted examples. 4.7 will obey literally and pick the first match, which may not be the task's actual Linear ID. State scope: "Extract the Linear ID from the 'Linear Issue' or 'Tracking' section only, not from anywhere in the document."

  **Before (line 105–107):**
  ```bash
  # Extract Linear ID and validate
  linear_id=$(grep -oE "[A-Z]+-[0-9]+" "$task_file" | head -1)
  [[ -z "$linear_id" ]] && echo "❌ No Linear ID found in task document" && exit 1
  ```

  **After:**
  ```bash
  # Extract Linear ID from the Tracking / Linear Issue section only, not from free text elsewhere.
  linear_id=$(awk '/^## (Tracking|Linear Issue)/,/^## [^#]/' "$task_file" \
    | grep -oE "[A-Z]+-[0-9]+" \
    | head -1)
  [[ -z "$linear_id" ]] && echo "❌ No Linear ID found in Tracking section. Halt — do not guess." && exit 1
  ```

- **[Medium] Breaking-changes extraction on line 75 is fragile and silent on failure.** `grep -A 5 "Breaking Changes" "$task_file" | tail -n +2 || echo "None"` — the `||` only fires if `grep` exits non-zero, but `grep -A 5` will succeed with empty output if the line exists but is the last in the file. 4.7 will produce a PR body with a blank "Breaking Changes" section, which is worse than "None." State the scope: extract the section only if it's present and has content.

### Low Priority

- **[Low] The `## DEFINITION OF DONE` checkbox list (lines 222–232) is a positive pattern — 4.7 can check its own work against it.** Keep as-is.

- **[Low] Emoji in bash output (`✅`, `❌`, `🚀`, `📋`, `📝`, `🔗`) is fine for CLI logging but note that it appears in the PR body template too (e.g. line 116 "✅ Passed").** PR bodies render on GitHub, which supports emoji — no action needed. Calling it out so the reviewer knows this was considered.

- **[Low] "Handle failures gracefully - continue workflow even if Linear update fails" (line 125).** Good positive framing. The rationale ("Linear is non-blocking for PR creation") is implicit; stating it would strengthen per INSIGHTS §2. Minor.

- **[Low] The workflow example (lines 140–178) duplicates much of section 2 above.** For a 4.7 agent that reads more literally, two full procedural blocks risk the model merging them or picking the wrong one. Consider folding the example into section 2 or labeling it `<example>` (INSIGHTS §2 XML-tag structure).

---

## Summary per agent

| Agent | Frontmatter | High | Medium | Low | Overall |
|---|---|---|---|---|---|
| `changelog-generator` | description too generic; no `effort` | 2 (literal-scope date, idempotency) | 2 | 2 | Clean prose, mechanical agent — tightening the dispatcher `description:` and adding an idempotency guard are the main wins. |
| `create-pr-agent` | description too generic; missing `tools:` whitelist | 3 (dispatcher, base-branch scope, gate-to-workflow wiring) | 4 | 4 | Has a real safety gate; intensifier overuse elsewhere dilutes it. Base-branch and Linear-ID scope gaps are the load-bearing issues. |

Both agents are structurally sound. The highest-leverage changes on 4.7 are:
1. Rewriting `description:` to trigger narrowly (both agents).
2. Wiring the existing Permission Gate into the PR workflow body (create-pr-agent).
3. Explicitly scoping base branch, Linear-ID source section, and task date resolution (both agents).
4. Dialing back non-safety intensifiers so the safety ones retain weight (create-pr-agent).
