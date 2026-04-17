# Skill Review — `setup` and `update-setup`

**Scope audited:**
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/setup/SKILL.md` (311 lines)
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/update-setup/SKILL.md` (295 lines)

**Lens:** Opus 4.7 prompting best practices (`tasks/opus-4-7-skill-review/INSIGHTS.md` §3, §4, §5).

Both skills are configuration/workflow-sync wizards. Because they mutate files wholesale and wire hooks that run shell/Python with user privileges, the audit emphasises **autonomy/safety gating** (INSIGHTS §1 "autonomy and safety" context from the user prompt), **literal-scope gaps** (§3 literal-instruction-following), and **intensifier hygiene** (§3).

---

## 1. `setup/SKILL.md`

### High priority

---

**H1 — Destructive action is executed without an explicit user gate (literal-scope gap, safety).**
*(INSIGHTS §3 "literal-scope gaps"; §1 autonomy/safety context.)*

File: `.claude/skills/setup/SKILL.md:247`

Offending text:
> `To disable a skill: rename `SKILL.md` to `SKILL.md.disabled` in the skill's directory. This prevents Claude Code from loading it while preserving the file for re-enabling later.`

The AskUserQuestion at L249-254 asks which skills to disable, but the instruction at L247 reads as a unilateral action. On 4.7, which is more action-biased (INSIGHTS §3, "4.7 is now more action-biased, this may over-trigger edits"), there is nothing explicitly scoping "only disable skills the user selected in the multi-select above; never disable skills not in the selected set". Phase 3 Step 6 also never says "echo back the final list before any rename happens".

Before:
```
To disable a skill: rename `SKILL.md` to `SKILL.md.disabled` in the skill's directory.
This prevents Claude Code from loading it while preserving the file for re-enabling
later.

Present as a single AskUserQuestion with multiSelect: …
```

After:
```
Gate: only rename skills the user explicitly selected in the multi-select below.
Never disable a skill that wasn't in the returned selection set, even if detection
flagged it as irrelevant. Before renaming, print the final list of skills to be
disabled and wait for a plain "yes" confirmation.

To disable an approved skill: rename `SKILL.md` to `SKILL.md.disabled` in that
skill's directory. This preserves the file for re-enabling later.
```

---

**H2 — `Step 4: Wire ALL hooks into settings.json` is both a destructive edit and uses an all-caps intensifier that 4.7 will over-trigger on.**
*(INSIGHTS §3 intensifier hygiene; §1 autonomy/safety.)*

File: `.claude/skills/setup/SKILL.md:206`

Offending text:
> `**Step 4: Wire ALL hooks into settings.json**`

Combined with L208 — `Wire every configured hook into .claude/settings.json` — 4.7 will literally wire every listed hook without re-prompting the user, even if the user's existing `settings.json` already contains custom matchers they don't want stomped. The "Wiring rules" at L227-231 say "Preserve all existing hooks" but never require a dry-run preview or confirmation step before writing.

Before:
```
**Step 4: Wire ALL hooks into settings.json**

Wire every configured hook into `.claude/settings.json`. Group by event and matcher:
```

After:
```
**Step 4: Wire hooks into settings.json**

Why this needs a preview: `settings.json` is user-owned; stomping existing
matchers silently is worse than a slower workflow. Before writing, show the
user the exact JSON diff (existing matchers + the additions) and ask
"Apply this settings.json update?" via AskUserQuestion. Only write on "Apply".
Group additions by event and matcher:
```

---

**H3 — Phase 3 Step 2 asks the model to batch-edit "every 5 files" without stating scope limits; combined with 4.7's more literal instruction-following this invites runaway edits.**
*(INSIGHTS §3 literal-scope gaps; §4 "Don't add features…beyond what was asked".)*

File: `.claude/skills/setup/SKILL.md:154-161`

Offending text:
> ```
> Scan ALL `.md` files under `.claude/skills/` and `.claude/agents/` for remaining
> `{{PLACEHOLDER}}` patterns. For each file with placeholders:
> 
> 1. Read the file
> 2. Identify all `{{VARIABLE}}` placeholders
> 3. Replace with confirmed values
> 4. Show the user a brief summary: "Updated [filename]: replaced X placeholders"
> 
> Ask user confirmation every 5 files: "Continue applying to next batch?"
> ```

Two issues:
- `Scan ALL .md files` — the all-caps intensifier (§3) is unnecessary; `every .md file under the listed directories` does the same job without triggering overcorrection.
- "Replace with confirmed values" is literal-scope-thin: what if a file has a placeholder name the wizard never confirmed (e.g. new upstream placeholder)? There is no rule for "skip unknown placeholders".

Before:
```
Scan ALL `.md` files under `.claude/skills/` and `.claude/agents/` for remaining
`{{PLACEHOLDER}}` patterns. For each file with placeholders:
…
3. Replace with confirmed values
```

After:
```
Scan every `.md` file under `.claude/skills/` and `.claude/agents/` for remaining
`{{PLACEHOLDER}}` patterns. For each match:
…
3. If the placeholder name appears in the confirmed Phase-2 values, substitute it.
   If the name is unknown (not confirmed), leave it intact and add the file to a
   "needs follow-up" list shown at the end. Do not invent values.
```

---

### Medium priority

---

**M1 — Parallel-agent prompt lacks the explicit "run in the same turn" clause 4.7 now needs.**
*(INSIGHTS §4 "Parallel subagent prompting — because 4.7 under-parallelizes, spawn multiple subagents in the same turn".)*

File: `.claude/skills/setup/SKILL.md:34-36`

Offending text:
> `Launch **3 Explore agents in parallel** to scan the target codebase:`

"In parallel" is the old idiom. 4.7 under-parallelises by default (INSIGHTS §1 "Subagent spawning — more conservative by default") and will happily run them sequentially unless told to fan out in one turn.

Before:
```
### Phase 1: Codebase Discovery (Parallel Agents)

Launch **3 Explore agents in parallel** to scan the target codebase:
```

After:
```
### Phase 1: Codebase Discovery (parallel agents, same turn)

Spawn all 3 Explore subagents in a single turn — do not run them sequentially.
The three scans (tech stack, project structure, commands) have no dependencies
between them, so batching them saves wall-clock time.
```

---

**M2 — `NEVER delete user-customized content` uses a bare intensifier without *why*.**
*(INSIGHTS §3 intensifier hygiene; §2 foundational technique #2 "Explain the why".)*

File: `.claude/skills/setup/SKILL.md:307`

Offending text:
> `- NEVER delete user-customized content outside of `{{PLACEHOLDER}}` regions`

On 4.7, bare `NEVER` over-triggers. Replacing with a rationale-grounded instruction is more effective.

Before:
```
- NEVER delete user-customized content outside of `{{PLACEHOLDER}}` regions
```

After:
```
- Only modify text inside `{{PLACEHOLDER}}` regions. Content the user wrote
  outside those regions is theirs — leaving it intact is how the wizard stays
  idempotent and safe to re-run.
```

---

**M3 — "Always show what will change before writing" is a bare rule without a mechanism.**
*(INSIGHTS §3 intensifier hygiene; §2 technique #2 "why > rule".)*

File: `.claude/skills/setup/SKILL.md:308`

Offending text:
> `- Always show what will change before writing`

4.7 will obey literally but the rule is mechanism-free: a summary line? A diff? A full file preview? Ambiguity means inconsistent behaviour between runs.

Before:
```
- Always show what will change before writing
```

After:
```
- Before writing to a file, print a one-line summary (`path — N placeholders
  replaced: NAME1, NAME2, …`) so the user can stop the wizard if a substitution
  looks wrong. For `settings.json`, show the JSON diff, not just the summary.
```

---

**M4 — Phase 2 "Round 1/2/3/4" uses a fixed four-round structure but L140-141 and L130 never tell 4.7 to apply the rounds to every detection category found, not only the listed ones.**
*(INSIGHTS §3 literal-scope gaps; §4 "state scope explicitly".)*

File: `.claude/skills/setup/SKILL.md:101-141`

If Phase 1 surfaces something not in the four rounds (e.g. package manager, Docker, IaC), 4.7 will literally stick to the listed four rounds and never ask.

Before:
```
### Phase 2: User Confirmation (Interactive)

Present discovery results and confirm with user. Use `AskUserQuestion` for each category.

**Round 1 — Tech Stack:** …
**Round 2 — Project Structure:** …
**Round 3 — Commands:** …
**Round 4 — Architecture:** …
```

After:
```
### Phase 2: User Confirmation (Interactive)

Present discovery results and confirm with user. Use `AskUserQuestion` for
**every detection category** returned by Phase 1 — the four rounds below are the
minimum, not the maximum. If Phase 1 surfaced additional categories (e.g.
container runtime, IaC tool, custom tool registry), add matching rounds.
```

---

**M5 — Hook-wiring instruction assumes the model will infer how to merge with existing matcher arrays, but provides no worked example.**
*(INSIGHTS §2 technique #5 "examples: 3-5, relevant + diverse"; §3 literal-scope gaps.)*

File: `.claude/skills/setup/SKILL.md:227-231`

Offending text:
> ```
> **Wiring rules:**
> - Add to **existing** matcher arrays when the event+matcher already exists in settings.json
> - Create new matcher entries when they don't exist
> - Preserve all existing hooks …
> ```

No worked before/after JSON example. On 4.7, wiring is deterministic enough that a small example pays for itself.

Before: (as above)

After: append a worked example:
```
Example — existing `settings.json` has:
  "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "existing.sh"}]}]

Adding `bash-guard.sh` and `test-before-pr.sh` should produce:
  "PreToolUse": [{"matcher": "Bash", "hooks": [
    {"type": "command", "command": "existing.sh"},
    {"type": "command", "command": ".claude/hooks/bash-guard.sh"},
    {"type": "command", "command": ".claude/hooks/test-before-pr.sh", "timeout": 120}
  ]}]
```

---

### Low priority

---

**L1 — Numbered step skip: Step 5 is missing between Step 4 (L206) and Step 6 (L235).**

File: `.claude/skills/setup/SKILL.md:206`, `235`

Purely cosmetic but on 4.7's literal-instruction-following, a missing number can prompt the model to invent a Step 5. Renumber 6 → 5, or insert the paragraph at L233 (architecture checks file) as an explicit Step 5 header.

Before:
```
**Step 4: Wire ALL hooks into settings.json** …
…
**Step 6: Prune irrelevant skills**
```

After:
```
**Step 4: Wire hooks into settings.json** …
…
**Step 5: Generate architecture checks** (the paragraph currently at L233)
…
**Step 6: Prune irrelevant skills**
```

---

**L2 — Announcement line uses bold markdown inside a quote but the surrounding skill body uses different emphasis style.**

File: `.claude/skills/setup/SKILL.md:21`

> `> **Announcement**: "Running the **setup wizard** to configure this workflow for your codebase."`

Low-impact. Matching prompt style to desired output (INSIGHTS §2 technique #9) is still useful, but no change required.

---

## 2. `update-setup/SKILL.md`

### High priority

---

**H1 — File deletion is a `rm` against the local `.claude/` with no preview gate.**
*(INSIGHTS §3 literal-scope gaps; §1 autonomy/safety.)*

File: `.claude/skills/update-setup/SKILL.md:234-238`

Offending text:
> ```
> **Deleted files**: Remove from local:
> ```bash
> rm .claude/{path}
> ```
> If removing the last file in a directory, also remove the empty directory.
> ```

Phase 3 does ask whether to delete (L183-185: `"These files were removed upstream. Delete them locally?"`), but the apply step at L234 has no re-confirmation, no `ls` of what will be removed, and no bulk-guard (e.g. "if more than N files would be deleted, re-confirm"). Given the skill's own warning at L293 about "Major update" scale, a bulk-guard would be consistent.

Before:
```
**Deleted files**: Remove from local:
```bash
rm .claude/{path}
```
If removing the last file in a directory, also remove the empty directory.
```

After:
```
**Deleted files**: Before running `rm`, print the final list of paths selected
for deletion and the count. If the count is > 3, re-confirm with AskUserQuestion
("Delete these N files? Yes / No / Let me deselect some"). Then run:

```bash
rm .claude/{path}
```

If removing the last file in a directory, `rmdir` the now-empty directory;
never `rm -r` a non-empty directory.
```

---

**H2 — Merge-mode subagent prompt (L218-232) is terse, gives no failure contract, and uses literal-scope-thin language that 4.7 will under-generalise on.**
*(INSIGHTS §3 literal-scope gaps; §4 "state scope explicitly".)*

File: `.claude/skills/update-setup/SKILL.md:218-232`

Offending text:
> ```
> Rules:
> - Keep ALL local filled-in values (anything that replaced a {{PLACEHOLDER}})
> - Adopt new sections, rewritten instructions, removed sections, and logic changes from upstream
> - If upstream added new {{PLACEHOLDER}} variables not present in local, keep them as-is …
> - If upstream renamed a placeholder, carry the local value to the new name
> - Preserve the file's frontmatter structure (YAML header in skills/agents)
> - Write the merged result directly to the local file path
> ```

Gaps:
- "Keep ALL" — all-caps intensifier (§3), 4.7 will treat this as a hard floor and may refuse to drop a local value that upstream explicitly deleted.
- No guidance for a section that upstream *deleted* but that the user had customised (ambiguity between "adopt removed sections" and "keep local customisation").
- "Write the merged result directly to the local file path" — on 4.7 this will happen without a diff preview. For a merge, the user should at least see a summary.
- No failure contract: what if the merge is uncertain? No "if unsure, ask the user" fallback.

Before: (as above)

After:
```
Rules:
- Preserve local filled-in values (anything that replaced a {{PLACEHOLDER}}), unless
  upstream deleted the placeholder entirely — in that case, drop the value and
  note the removal in the merge summary.
- Adopt upstream's new sections, rewritten instructions, and logic changes.
- For sections upstream removed: if local had custom content in that section,
  stop and ask the user ("Upstream removed section X; your local copy has
  custom content there. Keep local / adopt upstream removal / show me?").
- If upstream added new {{PLACEHOLDER}} variables, keep them literal — /setup fills them.
- If upstream renamed a placeholder, carry the local value to the new name.
- Preserve the file's frontmatter YAML structure.
- After merging, print a 3-line summary ("kept N local values, adopted M upstream
  changes, K open questions") and write to the local path.
- If any merge step is uncertain, emit the uncertainty to the summary instead of
  guessing silently.
```

---

**H3 — `CRITICAL SCOPE RULE` block uses an intensifier that 4.7 is known to over-trigger on, and the adjacent rules miss a *why*.**
*(INSIGHTS §3 intensifier hygiene; §2 technique #2 "explain the why".)*

File: `.claude/skills/update-setup/SKILL.md:69-71`

Offending text:
> ```
> ## CRITICAL SCOPE RULE
> Only iterate over UPSTREAM files. Never flag, mention, or categorize local-only files.
> The user may have custom skills, agents, hooks that don't exist upstream — those are theirs and must be invisible to this comparison.
> ```

The rationale in the second sentence is good — the `CRITICAL` label is the anti-pattern. The `Never` intensifier here is genuinely load-bearing (safety-critical) so keeping it is fine; dial back `CRITICAL` and `must be invisible` → `stay out of the comparison`.

Before:
```
## CRITICAL SCOPE RULE
Only iterate over UPSTREAM files. Never flag, mention, or categorize local-only files.
The user may have custom skills, agents, hooks that don't exist upstream — those are theirs and must be invisible to this comparison.
```

After:
```
## Scope rule — upstream-only

Iterate only over upstream files. Local-only files (custom skills, agents, hooks
the user built themselves) stay out of the comparison entirely — don't flag,
mention, or categorise them. Why: the whole promise of this skill is that it
won't touch user customisations; leaking them into the report violates that
promise and trains the user to distrust the tool.
```

---

### Medium priority

---

**M1 — "Launch 1 general-purpose Agent" — subagent prompt lacks explicit parallel-tool-calling guidance for the per-file diffs.**
*(INSIGHTS §4 "Parallel tool-calling — when calls have no dependencies, batch them in one turn".)*

File: `.claude/skills/update-setup/SKILL.md:60`, `93`

Offending text:
> `1. Run: diff <upstream_file> <local_file> | head -120`

This runs per file with no batching guidance. For a large `.claude/` with tens of upstream files, 4.7's conservative default will serialise these diffs.

Before:
```
2. For EACH upstream file, determine its status:
   …
   - **Exists locally** → compare them:
     1. Run: diff <upstream_file> <local_file> | head -120
```

After:
```
2. For each upstream file, determine its status. Batch the diffs: when you have
   a list of N upstream/local file pairs to compare, run the `diff` calls in a
   single turn (parallel tool calls) rather than one-at-a-time. There are no
   dependencies between per-file diffs.
   …
   - **Exists locally** → compare them:
     1. Run: diff <upstream_file> <local_file> | head -120
```

---

**M2 — Deletion-heuristic section (L107-115) is explicitly speculative and should be gated harder, not just by "err on the side of NOT flagging".**
*(INSIGHTS §4 "Investigate-before-answering — never speculate about code you have not opened".)*

File: `.claude/skills/update-setup/SKILL.md:107-115`

Offending text:
> ```
> 3. To detect upstream DELETIONS: This is trickier because we only have a snapshot. …
>    NOTE: Err on the side of NOT flagging. If uncertain whether something is an upstream file or a user's custom file, skip it.
> ```

The instruction is already cautious, which is good. But the heuristic asks 4.7 to compare "folder names typical of upstream skills" without providing a canonical list. 4.7 will infer heuristically and will sometimes be wrong. A concrete allowlist of known upstream top-level directory names removes the guesswork.

Before: (as above)

After: replace the vague "name pattern typical of upstream skills" with a literal list. Example:
```
   - For candidate "removed upstream" files, restrict the check to folders whose
     names appear in upstream's current `skills/README.md` or `agents/README.md`
     listing. If the folder name isn't in that listing, treat it as user-custom
     and skip. Do not infer upstream membership from naming style.
```

---

**M3 — The Phase-3 "If ALL categories are empty" sentence at L172 uses an all-caps intensifier for no reason.**
*(INSIGHTS §3 intensifier hygiene.)*

File: `.claude/skills/update-setup/SKILL.md:172`

Offending text:
> `If ALL categories are empty (only UNCHANGED + PLACEHOLDER_ONLY): announce **"Your workflow is up to date with upstream. No changes needed."** and stop.`

Before:
```
If ALL categories are empty (only UNCHANGED + PLACEHOLDER_ONLY): announce …
```

After:
```
If every category is empty (only UNCHANGED + PLACEHOLDER_ONLY), announce …
```

---

**M4 — Conflict-detection Phase 4 shows only the first 80 lines; no instruction for "if the file is shorter, show the whole thing; if longer, paginate".**
*(INSIGHTS §3 literal-scope gaps.)*

File: `.claude/skills/update-setup/SKILL.md:193-195`

Offending text:
> ```
> 1. **CONFLICT RISK = high**: Show a preview before applying:
>    - Read the upstream version (first 80 lines)
>    - Read the local version (first 80 lines)
> ```

On a 300-line merged SKILL.md, the first 80 lines rarely contain the meaningful conflict region. 4.7 will literally read only the first 80.

Before:
```
1. **CONFLICT RISK = high**: Show a preview before applying:
   - Read the upstream version (first 80 lines)
   - Read the local version (first 80 lines)
```

After:
```
1. **CONFLICT RISK = high**: Show a preview before applying:
   - Read both files fully (both versions are small enough that full reads are fine).
   - If either side exceeds 300 lines, fall back to a unified diff so the user
     sees every hunk rather than the head of the file.
   - Summarise what upstream changed vs what the user customised locally.
```

---

### Low priority

---

**L1 — `**Upstream repo**` block (L36-41) is good but doesn't explain why `/tmp/claudops-upstream-sync` was chosen; low-impact, but adds *why* discipline.**

File: `.claude/skills/update-setup/SKILL.md:36-41`

Optional: add a one-line rationale (`shallow clone into /tmp because we only need a diff snapshot, not a working copy`). No change strictly required.

---

**L2 — Phase-7 summary template mentions "[count] local-only files untouched (your custom additions)" but Phase-2 rule forbids even counting local-only files.**
*(Minor internal inconsistency.)*

File: `.claude/skills/update-setup/SKILL.md:69-71` vs `.claude/skills/update-setup/SKILL.md:285`

Offending text at L285:
> `- [count] local-only files untouched (your custom additions)`

The scope rule says local-only files should be invisible to the comparison (L71 "must be invisible"). Reporting a count of them in the summary breaks that invariant. Either drop the line or relax the scope rule to "count but never name them".

Before:
```
**Skipped:**
- [count] files skipped by user choice
- [count] local-only files untouched (your custom additions)
```

After (drop the local-only count):
```
**Skipped:**
- [count] files skipped by user choice
- [count] placeholder-only differences (not real changes)
```

---

## Cross-cutting observations

Both skills share a few patterns worth calling out once:

- **Announcement lines (setup:21, update-setup:23)** are well-tuned: they describe behaviour without intensifiers. No change needed.
- **Neither skill includes the context-compaction guard** from INSIGHTS §4 (`"Context will be automatically compacted. Do not stop early due to token concerns."`). The setup wizard iterates over potentially 30+ files (skills + agents + hooks) and the update-setup wizard diffs all upstream files — both qualify as long-running. Adding one sentence to the top of each skill is a **Medium-priority** additive improvement.

Proposed insertion (put near the top of each skill's body, after the announcement line):

```
> Context will be automatically compacted during long runs. Do not stop early
> due to token concerns. If you need to, write interim state (files touched,
> placeholders filled) to a TodoWrite list so it survives compaction.
```

- **Intensifier density**: setup has 3 `ALL`/`NEVER`/`Always` instances (L154, L206, L307, L308). update-setup has `CRITICAL`, `ALL`, and two `Never`s (L69, L70, L99, L172, L225). All flagged above where load-bearing. Where genuinely safety-critical (the scope rule in update-setup L70), keeping `Never` is correct; everywhere else, drop the intensifier in favour of *why*.

- **Well-tuned parts worth keeping untouched**: the `PLACEHOLDER_ONLY` classifier (update-setup:97-105), the hook placeholder mapping table (setup:169-203), and the Edge Cases block (update-setup:288-295) are all concrete, rationale-grounded, and don't rely on intensifiers. No changes needed there.

---

## Priority summary

| Priority | setup | update-setup |
|---|---|---|
| High | H1 skill-disable gate (L247); H2 hook-wiring preview (L206); H3 "Scan ALL" + unknown-placeholder guard (L154) | H1 rm preview gate (L234); H2 merge-mode failure contract (L218); H3 `CRITICAL` intensifier (L69) |
| Medium | M1 parallel-same-turn (L34); M2 `NEVER delete` + why (L307); M3 "show what will change" mechanism (L308); M4 Phase-2 every-category (L101); M5 worked JSON example (L227) | M1 parallel diff calls (L60); M2 deletion allowlist (L107); M3 `If ALL` intensifier (L172); M4 conflict preview read-length (L193) |
| Low | L1 renumber Step 5 (L206/235); L2 announcement emphasis (L21) | L1 `/tmp` rationale (L36); L2 scope-rule vs summary inconsistency (L285) |
| Cross-cutting (Medium) | — | Add compaction-awareness sentence to both skills |

---

## Verdict

Neither skill is broken on 4.7, but both have the classic pre-4.7 prompting habits — heavy intensifiers, optimistic literal-scope assumptions, and destructive actions separated from confirmation by several steps. The highest-value fixes are the three destructive-action gates (setup H1, setup H2, update-setup H1) and the merge-mode failure contract (update-setup H2). Everything else is polish.
