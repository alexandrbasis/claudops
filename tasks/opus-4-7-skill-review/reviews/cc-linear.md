# Review: `cc-linear` Skill (Opus 4.7 Audit)

**Files audited:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/cc-linear/SKILL.md` (142 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/cc-linear/references/linear-api-reference.md` (267 lines — pure API reference; no prompting issues)

**Overall verdict:** Mostly well-tuned for 4.7. The skill is notably disciplined — it avoids the CRITICAL/MUST/ALWAYS intensifier avalanche common in integration skills, and it treats each CLI invocation as atomic rather than wrapping it in verification nudges. The main gaps are **confirm-before-destructive-action coverage** (INSIGHTS §4 safety — creating/moving Linear issues is externally visible to a team) and **two residual negative-framing / absolute-intensifier lines** (INSIGHTS §3). Literal-scope on cross-skill triggering is borderline — 4.7 may over-trigger or under-trigger depending on how "TEAM-*" context surfaces.

---

## High priority

### H1. No confirm-before-action guidance for externally visible mutations
**File:** `SKILL.md` — entire Commands + Workflow Patterns sections (lines 21–123)
**INSIGHTS cross-ref:** §4 (autonomy and safety — "Investigate-before-answering" / safety patterns), §1 ("Tool use — less frequent; more action-biased").

**Problem.** The skill enumerates mutations (`create-issue`, `update-status`, `add-comment`, `assign`, `add-label`, `remove-label`, `add-relation`, `link-pr`) and the "Workflow Patterns" section (lines 86–112) shows multi-step chains that move issues across team-visible states ("In Progress", "In Review", "Done") and post comments. None of these are local, reversible operations — every one writes to a team workspace and generates notifications.

4.7 is more action-biased than 4.6 (INSIGHTS §1: "Do not suggest, make the changes — 4.7 is now more action-biased, this may over-trigger edits"). With no confirm step specified, the model is likely to fire off `create-issue` / `update-status` / `add-comment` the moment a user says "move TEAM-66 to review and tell the team it's done" — even if the user intended to review the body first.

The "Cross-Skill Integration" table (lines 115–123) softens this with *"Don't force these — suggest them when the context is clear"*, but that guidance lives only under the cross-skill section and does not cover direct user invocation.

**Quote (Workflow Patterns, lines 96–104):**
> ```
> .claude/scripts/linear-api.sh update-status TEAM-66 "In Review"
> .claude/scripts/linear-api.sh add-comment TEAM-66 "-" <<'EOF'
> Implementation completed.
> - Key changes: [list]
> - Test coverage: [X]%
> - PR ready for review.
> EOF
> ```

**Before → After.** Add a short section (after "Output Formatting", before "Configuration"):

```markdown
## Before Acting

Linear mutations are visible to the whole team and send notifications. Before
running any of these commands, echo back what you are about to do and wait for
confirmation on first use in a session:

- `create-issue`, `add-comment`, `add-relation`, `link-pr` (new visible content)
- `update-status`, `update-issue`, `assign`, `add-label`, `remove-label` (state changes)

Read-only commands (`get-issue`, `search`, `ai-search`, `list-*`, `my-issues`)
do not need confirmation — run them freely.

For multi-step patterns below, confirm the whole chain once, then execute
without re-prompting between steps.
```

**Priority:** **High** — creating or moving Linear issues without confirmation can spam a real team's inbox or corrupt a sprint board. This is the single most impactful change.

---

### H2. "Never silently swallow errors" uses a hard NEVER intensifier
**File:** `SKILL.md:134`
**INSIGHTS cross-ref:** §3 ("`CRITICAL:`, `You MUST`, `ALWAYS`, `NEVER` used as intensifiers — dial back to normal voice"). §2.6 (positive framing beats negative).

**Quote (line 134):**
> `- Never silently swallow errors — always report failures to the user.`

**Problem.** This line is low-stakes — it does not encode any non-obvious behavior — yet stacks two intensifiers (`Never` and `always`). On 4.7 this kind of line tends to cause the model to narrate every tool return in excessive detail ("I see the JSON response contains no error field, so the request succeeded, and…") when the user just wants the outcome.

**Before → After.**
```markdown
# Before
- Never silently swallow errors — always report failures to the user.

# After
- Report command failures (non-zero exits, GraphQL errors) to the user with the
  exact error message — don't retry hidden.
```

**Priority:** **High** — small text change, but removing it cuts a known 4.7 over-triggering pattern, and the rewrite preserves the intent (surface failures) while dropping the double-intensifier.

---

## Medium priority

### M1. Announcement line is a forced preamble — fights adaptive response length
**File:** `SKILL.md:16`
**INSIGHTS cross-ref:** §1 ("Response length — calibrated to task complexity"), §3 (hard-coded response-length caps / fixed openers fight adaptive length), §2.9 ("Match prompt style to desired output").

**Quote (line 16):**
> `> **Announcement**: Begin with: "I'm using the **cc-linear** skill for Linear project management."`

**Problem.** For a quick `get-issue TEAM-66` invocation, the ideal 4.7 response is one-line title + status + URL. Forcing a fixed opener inflates every response and — more importantly — signals to the model that verbose framing is expected, biasing subsequent content upward too. This is exactly the "fixed verbosity fighting adaptive length" anti-pattern INSIGHTS §1 warns about.

If the announcement is a project requirement (skill-routing telemetry), keep it but make it small and single-line. Otherwise drop it.

**Before → After.**
```markdown
# Before
> **Announcement**: Begin with: "I'm using the **cc-linear** skill for Linear project management."

# After (option A — keep but de-emphasize)
> Prefix the first response in a session with a one-line tag: `[cc-linear]`.

# After (option B — drop entirely if no routing need)
(remove the line)
```

**Priority:** **Medium** — low-risk but touched on every invocation.

---

### M2. Literal-scope gap in the description triggers
**File:** `SKILL.md:3–10`
**INSIGHTS cross-ref:** §1 ("Instruction following — more literal; will NOT silently generalize"), §5.6 ("literal-scope gaps").

**Quote (lines 3–10):**
> ```
> Execute Linear operations via direct GraphQL API — create issues, update
> status/priority/title, add comments, search tasks, manage labels, assign work,
> and link PRs. Use this skill whenever the user mentions Linear, refers to
> TEAM-* issue identifiers, says "create a ticket/issue", "move to done/in
> progress/review", "update the task status", "close the issue", "what's in our
> backlog", "assign this to", "my issues", or any project management operation
> targeting Linear. …
> ```

**Problem.** Two literal-scope issues:

1. **"TEAM-*"** is the default team key baked into the description, but the Configuration section (lines 79–82) says the actual key comes from `LINEAR_TEAM_KEY`. A 4.7 reading literally will *only* recognize issues like `TEAM-66` as triggers and miss `ENG-123` or `OPS-7` from a real team. `TEAM` is a placeholder in the config, but the trigger text treats it as a literal.

2. **"create a ticket/issue"** without a project-management qualifier can false-trigger against GitHub Issues (which most codebases also have). There is no disambiguator saying "use this only for Linear, not GitHub Issues."

**Before → After.**
```markdown
# Before
Use this skill whenever the user mentions Linear, refers to TEAM-* issue
identifiers, says "create a ticket/issue", …

# After
Use this skill when the user mentions Linear explicitly, or references a
Linear-style identifier (uppercase team prefix + dash + number, e.g. ENG-123,
OPS-7; the project's team key is in $LINEAR_TEAM_KEY). Trigger on phrases like
"create a Linear ticket/issue", "move TEAM-X to done/in progress/review",
"update the Linear task status", …

Do NOT trigger on ambiguous "create an issue" when the user clearly means a
GitHub Issue (repo context, `gh issue` commands, issues.md), unless they also
reference Linear.
```

**Priority:** **Medium** — affects invocation correctness, but only partially (most users do say "Linear" explicitly).

---

### M3. "Proactively suggest or perform" in Cross-Skill Integration
**File:** `SKILL.md:115`
**INSIGHTS cross-ref:** §3 ("`Default to using [tool]` — too broad"), §1 ("Tool use — 4.7 reasons more before calling tools; prompts that previously nudged may now over-trigger").

**Quote (line 115):**
> `When working with other skills, proactively suggest or perform Linear operations:`

**Problem.** "Proactively perform" is exactly the kind of tool-use-over-nudge INSIGHTS §3 flags. Combined with the action-biased 4.7 default, this can cause `update-status` or `create-issue` calls to fire during `/ct`, `/si`, or `/sr` runs without user confirmation. The softer line 123 ("*Don't force these — suggest them*") contradicts line 115, and 4.7's literal reading may weight whichever came first.

**Before → After.**
```markdown
# Before
When working with other skills, proactively suggest or perform Linear operations:

# After
When other skills touch Linear-adjacent work, offer the matching Linear
operation as a suggestion — do not run it unprompted. Only execute when the
user agrees or when the outer skill explicitly delegates to you.
```

**Priority:** **Medium** — aligns line 115 with the already-correct line 123 guidance and removes a direct trigger for 4.7's action bias.

---

## Low priority

### L1. Empty-string / dash-stdin pattern is undocumented
**File:** `SKILL.md:28, 36`
**INSIGHTS cross-ref:** §2.2 ("Explain the why — rationale > rules").

**Quote (lines 28, 36):**
> ```
> .claude/scripts/linear-api.sh create-issue "Title" "-" 3 <<< "Multiline desc"
> .claude/scripts/linear-api.sh add-comment TEAM-66 "-" <<'EOF'
> ```

**Problem.** The `"-"` sentinel meaning "read body from stdin" is used but never explained. 4.7 is more literal — if the user asks for a multi-paragraph description, the model may not realize `"-"` triggers stdin mode and will instead fall back to inline quoting, which breaks on newlines or quotes.

**Before → After.** Add one line under the "Issues" code block:
```markdown
Use `"-"` as the body argument to read from stdin — preferred for any
description or comment longer than one line or containing quotes.
```

**Priority:** **Low** — affects formatting quality on long comments only.

---

### L2. "Always include the Linear URL" — minor intensifier
**File:** `SKILL.md:48`
**INSIGHTS cross-ref:** §3 ("ALWAYS used as intensifier").

**Quote (line 48):**
> `Always include the Linear URL so the user can click through.`

**Problem.** The *why* is already stated ("so the user can click through"), which is good. The `Always` adds nothing — 4.7 is responsive enough without the emphasis.

**Before → After.**
```markdown
# Before
Always include the Linear URL so the user can click through.

# After
Include the Linear URL in every issue response — the user will want to click
through.
```

**Priority:** **Low** — cosmetic.

---

### L3. "Each command is atomic — chain them together" is a weak nudge
**File:** `SKILL.md:88`
**INSIGHTS cross-ref:** §4 ("Parallel tool-calling: When calls have no dependencies, batch them in one turn").

**Quote (line 88):**
> `Common multi-step sequences. Each command is atomic — chain them together.`

**Observation.** This is currently *correct* for 4.7 (encourages batching), but it could be sharper. The workflow patterns below it are strictly sequential (status → comment), so batching across steps is fine. Consider stating the parallel-tool-calling intent explicitly when the steps are genuinely independent (e.g., `add-label` + `assign` can run in parallel in one turn).

**Before → After (optional).**
```markdown
# Before
Common multi-step sequences. Each command is atomic — chain them together.

# After
Common multi-step sequences. Each command is atomic. When the steps have no
dependency on each other (e.g. adding a label and assigning at the same time),
batch them in a single turn; run sequentially only when a later step needs
output from an earlier one.
```

**Priority:** **Low** — refinement, not a fix.

---

## Not issues (explicitly noted so the audit is falsifiable)

- **No filter-leakage in a review sense** (INSIGHTS §5.4) — this is an integration skill, not a review skill. N/A.
- **No prefill / `<assistant>` patterns** (INSIGHTS §3) — none found.
- **No subagent fan-out** (INSIGHTS §5.3) — the skill doesn't spawn subagents, so the "tell it to parallelize" guidance doesn't apply. (The minor L3 nudge is the only relevant refinement.)
- **No context-compaction concern** (INSIGHTS §4) — invocations are short CLI commands, not long-running analysis. N/A.
- **Over-engineering guard** (INSIGHTS §4) — N/A; this skill doesn't generate code.
- **XML structure** (INSIGHTS §2.3) — the SKILL.md is reference-style (tables, code blocks) and mostly non-instructional; XML tags would add noise here. N/A.
- **API reference file** (`references/linear-api-reference.md`) — pure GraphQL documentation, no prompting directives, no changes needed.

---

## Summary of recommended changes, by priority

| # | Location | Change | Priority |
|---|---|---|---|
| H1 | After line 48 (new section) | Add "Before Acting" confirm-first guardrail for write operations | **High** |
| H2 | Line 134 | Drop `Never … always …` double intensifier, keep the intent | **High** |
| M1 | Line 16 | Replace the forced opener with a minimal tag or remove | Medium |
| M2 | Lines 3–10 (frontmatter `description`) | Tighten `TEAM-*` literal, disambiguate from GitHub Issues | Medium |
| M3 | Line 115 | Change "proactively … perform" → "suggest, don't run unprompted" | Medium |
| L1 | After line 37 (Issues block) | Document the `"-"` stdin sentinel | Low |
| L2 | Line 48 | Drop `Always` | Low |
| L3 | Line 88 | Sharpen into explicit parallel-when-independent guidance | Low |

Total: 2 High, 3 Medium, 3 Low. No changes needed to `references/linear-api-reference.md`.
