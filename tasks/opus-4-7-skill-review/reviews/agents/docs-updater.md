# Review — `.claude/agents/wf-agents/docs-updater.md`

**Audited file:** `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/agents/wf-agents/docs-updater.md` (73 lines)
**Lens:** Opus 4.7 prompting insights (`tasks/opus-4-7-skill-review/INSIGHTS.md`).
**Rule followed:** Do not modify the agent file; only produce recommendations. Every finding cites a §1–§4 pattern from INSIGHTS.

---

## Frontmatter

```yaml
---
name: docs-updater
description: Direct documentation updater - Updates docs based on task analysis
model: sonnet
color: purple
---
```
(lines 1–5)

### Issues

1. **`description` is too broad and lacks dispatch triggers — High priority.**
   Opus 4.7 treats the subagent `description` field as an action-biased dispatcher (§1 "Tool use" / "Instruction following"; §3 "Default to using [tool]"). The current text — `"Direct documentation updater - Updates docs based on task analysis"` — is a generic label, not a trigger. It will either (a) cause the orchestrator to auto-invoke this agent any time the phrase "update docs" appears anywhere in a conversation, or (b) fail to invoke because no concrete when/when-not boundary is stated. Both failure modes are documented in §1 ("4.7 is more action-biased") and §3 ("`Default to using [tool]` — too broad").

   **Before:**
   ```yaml
   description: Direct documentation updater - Updates docs based on task analysis
   ```
   **After (proposed):**
   ```yaml
   description: Use after implementation is complete to update /docs when a tech-decomposition document in tasks/task-YYYY-MM-DD-*/tech-decomposition-*.md references changed ADRs, PRDs, DB schemas, dev-workflow, or onboarding docs. Scope is limited to files in /docs that are explicitly named or logically implied by the tech-decomposition's Implementation Changelog. Do NOT invoke for ad-hoc README edits, inline comment changes, or speculative doc cleanup unrelated to a task document.
   ```
   Rationale: §4 "State scope explicitly" + §3 "replace with 'use [tool] **when** it would enhance X'". The revised description names the precondition (tech-decomposition exists), the trigger (implementation complete), and the negative scope (what not to invoke for).

2. **No literal scope boundary for "which docs" — High priority.**
   §1 ("Instruction following — More literal; will NOT silently generalize") plus §4 ("State scope explicitly"). The description says "Updates docs based on task analysis" without stating whether it operates on: the whole repo, `/docs/` only, changed files only, or the PR diff. The body (line 11) says `/docs` but the frontmatter — which the dispatcher sees first — does not. 4.7 will not bridge that gap silently. Fix by putting the scope directive inside the `description` itself (see the proposed rewrite above).

3. **`model: sonnet` — Informational only, not a defect.**
   The review insights apply to Opus 4.7, but a docs-writing subagent running on Sonnet is a defensible choice (cheaper, sufficient). Flag only so the reviewer knows the INSIGHTS.md patterns still broadly apply to Sonnet 4.x but with less over-triggering risk.

---

## High priority

### H1. No "confirm-before-mass-rewrite" preview guard (§4 — Over-engineering mitigation; §1 — "more action-biased")
Lines 57–61 describe:
```
## EXECUTION APPROACH
1. **Read** the relevant `tech-decomposition-*.md` file
2. **Analyze** which documentation areas it references (PRDs, ADRs, onboarding, etc.)
3. **Update** only those files/directories in `docs/`
4. **Commit** the documentation updates together with a clear message
```
The agent jumps straight from analysis to file writes to a git commit. On 4.7's action-biased default, this combination (especially the auto-commit at step 4) means a single mis-parsed tech-decomposition can rewrite many doc files and land them in a commit before the user reviews.

Doc edits are recoverable via `git revert`, so this is not destructive in the hard sense — but the INSIGHTS.md task prompt specifically called out "mass-rewrites deserve a preview." Fix by inserting a preview step *before* any write:

**Before:**
```
3. **Update** only those files/directories in `docs/`
4. **Commit** the documentation updates together with a clear message
```
**After:**
```
3. **Plan** — produce a table of (file path → sections to change → 1-line summary of the edit) and stop. Do not write yet.
4. **Confirm** — if more than 3 files or more than 1 section per file will change, wait for user sign-off on the plan. For smaller edits, proceed.
5. **Apply** — make the edits exactly as planned. Do not expand scope.
6. **Commit** — stage only the files listed in the plan; use a message that names the docs touched.
```
Rationale: §4 "Minimize over-engineering" ("Don't add features, abstractions, or cleanup beyond what was asked"). The tech-decomposition is the source of truth; the preview step guards against the agent inferring bonus edits.

### H2. Literal-scope gap — "mentions in the task document" is under-specified (§1 — Instruction following; §4 — State scope explicitly)
Lines 33–37:
```
- Cross-reference mentions in the task document with actual doc paths:
  - **Architecture / ADRs** → `docs/adr/`, `docs/db-scheme-mvp/`
  - **Product / PRDs / Research** → `docs/product-docs/PRD/`, `docs/product-docs/JTBD/`, `docs/product-docs/Research/`, `docs/product-docs/Features/`
  - **Process / Workflow** → `docs/dev-workflow/`, `docs/development/`
  - **Onboarding / Training** → `docs/onboarding/`
```
"Mentions" is ambiguous — a passing reference to a PRD in the Primary Objective is different from an Implementation Changelog entry that says "added column X to table Y." 4.7 will not silently pick the stricter reading.

**Before:**
```
- Cross-reference mentions in the task document with actual doc paths:
```
**After:**
```
- Treat an item as "affected" only if ONE of these is true:
  1. The tech-decomposition's `Implementation Changelog` names the doc file or ADR number directly.
  2. The implementation added/removed/renamed something whose contract lives in the doc (e.g., new DB table → `docs/db-scheme-mvp/`; new bot command → the command reference doc).
  3. The `Primary Objective` explicitly lists the doc as an acceptance criterion.
- A passing mention in prose ("this relates to the PRD") is NOT sufficient — skip it.
```
Rationale: §4 "State scope explicitly" — the prompt tells 4.7 exactly when an item qualifies, and lists the negative case.

### H3. Literal-scope gap — "PR scope" is never mentioned (§4 — State scope explicitly)
The task-prompt reviewer asked specifically: "scoped to PR? scoped to changed files only?" The agent file is silent on both. It operates on a tech-decomposition file, not on a git diff or PR. If the intent is that docs-updater should only touch docs corresponding to code that was actually changed in the current branch, that is a separate constraint and must be stated. If the intent is that the tech-decomposition is the authoritative scope even when it diverges from the diff, say that too.

**Proposed addition to `CONTEXT & CONSTRAINTS` (line 9):**
```
- **Source of scope**: the tech-decomposition document is authoritative. Do NOT read the git diff to discover additional docs to update, and do NOT skip docs that the tech-decomposition calls out just because the current diff doesn't touch the code area.
- **Out of scope**: docs referenced in the PR description but absent from the tech-decomposition Implementation Changelog.
```

---

## Medium priority

### M1. Missing "investigate before writing" directive (§4 — Investigate-before-answering)
Line 41 says "Read the existing document before editing to preserve tone and structure." This is good but weak — it does not stop 4.7 from drafting edits based on what it assumes the file contains if the file is long. Add the stronger form from §4:

**Before:**
```
- Read the existing document before editing to preserve tone and structure
```
**After:**
```
- Never edit a doc you have not opened in this session. Read the full file (or the specific section when the file is large) before proposing any change. Do not infer the structure from the filename.
```
Rationale: §4 "Never speculate about code you have not opened" — applies equally to docs.

### M2. "Maintain existing formatting" lacks the *why* (§2 — Explain the why)
Line 43:
```
- Maintain existing formatting (headings, tables, bullet styles)
```
§2 "Explain the *why*" says rationale beats rules. Add a one-clause reason so the model trades off correctly when the source file is inconsistent with itself:

**After:**
```
- Match the existing file's heading depth, list markers, and table style. Reason: docs in this repo are rendered by multiple tools (GitHub, Obsidian, in-repo tooling), and heterogeneous formatting within one file breaks rendering and review diffs.
```

### M3. Frontmatter `color: purple` is unverified (§2 — cite sources)
Not a defect; noting for completeness. If the harness ignores unknown frontmatter keys, this is harmless; if not, confirm the schema. No action required unless the schema rejects it.

---

## Low priority

### L1. "only" intensifier used as emphasis (§3 — Intensifier hygiene)
Counts in the file:
- line 7: "directly update **only** the documentation files"
- line 14: "Update **only** affected documentation"
- line 38: "**Only** touch files explicitly impacted"
- line 46: "Stage **only** the modified documentation files"
- line 60: "**Update** only those files/directories"
- line 69: "**Only** documentation that was actually affected gets updated"

Six uses of "only" across 73 lines. §3 warns about intensifier inflation. After the scope clarifications in H2/H3, most of these become redundant — trim to one or two canonical statements. The behavior will not change on 4.7 because the scope is already pinned by the earlier rules; the extra "only"s just add noise.

### L2. Decorative emoji in EXAMPLE OUTPUT (§2 — match prompt style to output)
Lines 64–68:
```
🔍 Task analysis: Added user authentication feature
📂 Categories affected: technical, architecture
📝 Updated: docs/technical/bot-commands.md, docs/architecture/api-design.md
✅ Documentation update complete - 2 files modified
```
Minor. §2.9 "Match prompt style to desired output" — if the team prefers emoji-free commit logs and CI output, strip these from the example so 4.7 does not imitate the style when reporting back. If emoji output is intentional, keep.

### L3. Example output references paths that don't match the declared structure (§2 — consistency)
The `DOCUMENTATION STRUCTURE` block (lines 17–25) lists `docs/adr/`, `docs/db-scheme-mvp/`, `docs/dev-workflow/`, etc. — but the example output (line 67) shows `docs/technical/bot-commands.md` and `docs/architecture/api-design.md`, which aren't in the declared structure. 4.7 is literal; it may either follow the structure (and never produce output matching the example) or follow the example (and write to paths that don't exist). Fix by updating the example to use real paths from the declared structure.

**After (example):**
```
Task analysis: Added user authentication feature
Categories affected: ADR, dev-workflow
Updated: docs/adr/ADR-0012-auth.md, docs/dev-workflow/authentication.md
Documentation update complete — 2 files modified
```

---

## What's already well-tuned

- **No `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` intensifiers.** The file avoids the §3 anti-patterns that plague other skills in the repo.
- **No "be thorough / exhaustive" stopping-condition traps** (§3).
- **No prefill patterns** (§3).
- **No forced response-length caps** fighting adaptive length (§3).
- **No tool-use over-nudging** ("if in doubt, use X"). The agent does not spawn subagents or call external tools unnecessarily.
- **Positive framing throughout** (§2.6). Instructions say "preserve tone," "stage only modified files" — not "don't break formatting."
- **Tight, scannable structure** — short sections, clear step numbering. Matches §2.9.

---

## Priority summary

| # | Priority | Area | Fix cost |
|---|----------|------|----------|
| Frontmatter #1 | **High** | `description` trigger too broad | 1 line rewrite |
| Frontmatter #2 | **High** | literal scope missing from dispatcher | folded into #1 |
| H1 | **High** | No preview / confirm step before mass write + auto-commit | 4 lines added |
| H2 | **High** | "mentions" rule ambiguous | 6 lines added |
| H3 | **High** | PR vs tech-decomposition scope unspecified | 2 lines added |
| M1 | Medium | "read before edit" is too soft | 1 line rewrite |
| M2 | Medium | "maintain formatting" has no *why* | 1 line rewrite |
| M3 | Medium | verify `color:` key | 0 lines (verify only) |
| L1 | Low | "only" over-used as intensifier | 4 deletions |
| L2 | Low | emoji in example output | optional |
| L3 | Low | example paths don't match declared structure | 2 lines rewrite |

---

## References to INSIGHTS.md

- §1 "Instruction following — more literal; will NOT silently generalize" → Frontmatter #2, H2, H3
- §1 "Tool use — less frequent, reasons more" / "more action-biased" → Frontmatter #1, H1
- §2.2 "Explain the *why*" → M2
- §2.9 "Match prompt style to desired output" → L2
- §3 "`Default to using [tool]` — too broad" → Frontmatter #1
- §3 Intensifier hygiene → L1
- §4 "State scope explicitly" → Frontmatter #1, H2, H3
- §4 "Investigate-before-answering" → M1
- §4 "Minimize over-engineering" → H1
