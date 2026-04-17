# Review: `gemini-cli` and `dev-server` skills vs Opus 4.7 Prompting Best Practices

**Reviewer lens:** `tasks/opus-4-7-skill-review/INSIGHTS.md` (sections 3 and 4).
**Scope:** `.claude/skills/gemini-cli/{SKILL.md, reference.md, templates.md}` and `.claude/skills/dev-server/SKILL.md`.
**Focus per task brief:**
- `gemini-cli` → tool-use over-nudging (INSIGHTS §3: "Default to using [tool]" / "If in doubt, use [tool]").
- `dev-server` → verification (UI / frontend testing) guidance (INSIGHTS §4: "verification tools" / investigate-before-answering).

---

## Skill 1 — `gemini-cli`

**Overall verdict:** Mostly well-tuned. The skill is *about* invoking an external tool, so strong "use gemini when X" guidance is appropriate and not the same as the over-nudging anti-pattern (which is about Claude reaching for `Read`/`Bash`/etc. reflexively). The skill already has explicit **"When NOT to Use"** gating (`SKILL.md:157–162`), which is the correct pattern per INSIGHTS §3 ("replace with 'use [tool] **when** it would enhance X'"). Remaining issues are mostly intensifier hygiene, a couple of anti-pattern phrasings, and a few positive-framing opportunities.

### High priority

#### H1. `CRITICAL:` intensifier on `@path` safety is load-bearing but over-emphasized
**File:** `.claude/skills/gemini-cli/SKILL.md:108`
**Cross-ref:** INSIGHTS §3 — `CRITICAL:` as intensifier causes over-triggering on 4.7.
**Offending text (line 108):**
> `**CRITICAL**: Verify that `@path` references point to files/directories that actually exist. Gemini CLI can hang indefinitely on nonexistent `@path` references...`

This *is* load-bearing (hang risk is real), so don't remove the guidance — but drop the `CRITICAL` intensifier and explain the *why* inline, which is stronger on 4.7 (INSIGHTS §2 "Explain the why — rationale > rules").

**Before:**
```
### 6. @path Safety

**CRITICAL**: Verify that `@path` references point to files/directories that actually exist. Gemini CLI can hang indefinitely on nonexistent `@path` references (see [#6440]...). Before running, mentally verify the paths or use `ls` to check.
```

**After:**
```
### 6. @path Safety

Verify every `@path` reference points to a real file or directory before invoking — Gemini CLI can hang indefinitely on a missing path (upstream bug [#6440]...), and a hung background job will silently eat your timeout budget. A quick `ls` or `[ -f path ]` guard is enough.
```

---

#### H2. `mandatory` framing on token optimization
**File:** `.claude/skills/gemini-cli/SKILL.md:138`
**Cross-ref:** INSIGHTS §3 — intensifier hygiene.
**Offending text (line 138):**
> `### Token Optimization (mandatory)`

"mandatory" is redundant — the *why* (line 140: "~30 tokens vs thousands") is the persuasive part. On 4.7 this kind of framing tends to nudge the model to treat the section as a rigid rule rather than a rationale it can adapt.

**Before:**
```
### Token Optimization (mandatory)

Without redirection, Bash returns thousands of tokens of verbose output. With the redirect pattern, you get ~30 tokens.
```

**After:**
```
### Token Optimization

Without redirection, Bash returns thousands of tokens of verbose gemini output; the redirect + `jq` pattern below collapses that to ~30 tokens, which is why every template uses it.
```

---

### Medium priority

#### M1. "Always include" is an `ALWAYS` intensifier
**File:** `.claude/skills/gemini-cli/SKILL.md:144`
**Cross-ref:** INSIGHTS §3 — `ALWAYS` used as intensifier.
**Offending text (lines 144–147):**
> `Gemini starts with zero context. Always include in your prompt:`
> `- **Task/requirement file paths** using `@path` syntax`
> `- **Implementation file paths** for review targets`
> `- **Directory paths** for broader context (`@src/`)`

The rationale ("starts with zero context") is the real lever — that already implies the requirement.

**Before:**
```
### Gemini Has No Context From This Conversation

Gemini starts with zero context. Always include in your prompt:
- **Task/requirement file paths** using `@path` syntax
- **Implementation file paths** for review targets
- **Directory paths** for broader context (`@src/`)
```

**After:**
```
### Gemini Has No Context From This Conversation

Gemini starts with zero context — it cannot see this conversation, open files, or prior turns. For any useful answer, the prompt itself has to carry what it needs:
- Task/requirement file paths via `@path`
- Implementation file paths for review targets
- Directory paths (`@src/`) when broader context matters
```

---

#### M2. Negative framing: "Output ONLY the final answer. No chain of thought. No reasoning."
**Files:**
- `.claude/skills/gemini-cli/SKILL.md:56–57` (Code Review template)
- `.claude/skills/gemini-cli/SKILL.md:73` (Web Research template)
- `.claude/skills/gemini-cli/templates.md:19, 30, 39, 48, 57, 65, 76, 88, 96, 104, 114, 122, 129, 140, 149` (every template)
**Cross-ref:** INSIGHTS §2.6 ("Positive framing beats negative") and §3 ("Verbosity-nudging instructions — negative framing should become positive").

**Offending pattern (example, `templates.md:19`):**
> `gemini -p "Output ONLY the final answer.`

And the stronger variant (`SKILL.md:56`):
> `gemini -p "Output ONLY the final answer. No chain of thought. No reasoning.`

Note: This instruction is going to the *Gemini* model, not Claude, so the 4.7 anti-pattern guidance applies only indirectly — however, Gemini 3 Pro is a thinking model too and responds better to positive framing. More importantly, the *Claude agent* reads these templates repeatedly and mirrors the style (INSIGHTS §2.9 "Match prompt style to desired output").

**Before:**
```
gemini -p "Output ONLY the final answer. No chain of thought. No reasoning.
Review these files for bugs, security issues, and improvements:
```

**After:**
```
gemini -p "Respond with the final review only — concise, fact-forward.
Review these files for bugs, security issues, and improvements:
```

For `templates.md`, apply `Respond with the final answer only.` uniformly as a one-line drop-in.

---

#### M3. "Always Use `-p` Flag" — positive-frame with rationale
**File:** `.claude/skills/gemini-cli/SKILL.md:125–127`
**Cross-ref:** INSIGHTS §2.2, §3.
**Offending text:**
> `### Always Use `-p` Flag`
>
> `The `-p` flag forces non-interactive mode. Without it, commands may default to interactive REPL in a TTY, which breaks one-shot execution from Claude Code.`

The *reason* is already given — the heading's `Always` is redundant intensifier.

**Before:**
```
### Always Use `-p` Flag

The `-p` flag forces non-interactive mode. Without it, commands may default to interactive REPL in a TTY, which breaks one-shot execution from Claude Code.
```

**After:**
```
### Use `-p` for One-Shot

Claude Code can only drive Gemini non-interactively. Without `-p`, the CLI may drop into an interactive REPL in a TTY and hang the Bash call.
```

---

#### M4. Parallel / background execution guidance is present but could be sharper
**File:** `.claude/skills/gemini-cli/SKILL.md:79–91` (Background Execution)
**Cross-ref:** INSIGHTS §4 — "Parallel tool-calling ... When calls have no dependencies, batch them in one turn."

The skill correctly tells Claude to continue working while a background gemini runs (`SKILL.md:86–90`). But it does not mention that **independent gemini calls should be fired in parallel** (e.g. a security review and a performance review of the same diff). On 4.7 this needs to be explicit.

**Before (SKILL.md:79–91, in situ):**
```
### 4. Background Execution (for long tasks)

For complex tasks that take 2-10 minutes:
[...]
**Workflow**:
1. Run with `run_in_background: true` on the Bash tool
2. Continue working on other tasks while gemini runs
3. You will be notified automatically when it completes
4. Read `/tmp/gemini-result.txt` with the Read tool
5. Summarize findings to the user
```

**After (add a new bullet 6 plus a sentence at the top):**
```
### 4. Background Execution (for long tasks)

For complex tasks that take 2-10 minutes. When you have multiple *independent* gemini queries (e.g. a security review and a perf review of the same diff), launch them in the same turn as separate background Bash calls — don't serialize.
[...]
**Workflow**:
1. Run with `run_in_background: true` on the Bash tool
2. If there are other independent gemini calls, fire them in the same turn (different output files: `/tmp/gemini-sec.txt`, `/tmp/gemini-perf.txt`)
3. Continue working on other tasks while gemini runs
4. You will be notified automatically when each completes
5. Read each result with the Read tool
6. Summarize findings to the user
```

---

#### M5. Templates use `@[file1.ts]` placeholders but never remind Claude to verify those paths exist
**File:** `.claude/skills/gemini-cli/templates.md` (all templates)
**Cross-ref:** INSIGHTS §4 — "Investigate-before-answering ... Never speculate about code you have not opened."

The `@path` safety warning lives in `SKILL.md:108` but templates are likely dropped in isolation. Add a one-line reminder at the top of `templates.md`.

**Before (`templates.md:1–4`):**
```
# Gemini CLI Prompt Templates

> **Model**: Auto routing (do NOT pass `-m`). Classifier → `gemini-3-flash-preview` or `gemini-3.1-pro-preview` based on complexity. Fallback: 2.5 Pro → 2.5 Flash.
```

**After:**
```
# Gemini CLI Prompt Templates

> **Model**: Auto routing (do NOT pass `-m`). Classifier → `gemini-3-flash-preview` or `gemini-3.1-pro-preview` based on complexity. Fallback: 2.5 Pro → 2.5 Flash.
>
> **Before running**: every `@path` must exist — Gemini CLI can hang on a missing path. Quick `ls` or `[ -f ... ]` check before invoking.
```

---

### Low priority

#### L1. `do NOT pass -m flag` — negative emphasis
**Files:** `.claude/skills/gemini-cli/SKILL.md:114`, `.claude/skills/gemini-cli/reference.md:34, 48`.
**Cross-ref:** INSIGHTS §2.6.

**Offending text (SKILL.md:114):**
> `Do NOT pass `-m` flag — rely on **Auto** routing...`

Reasonable as-is (it's a genuine footgun), but positive framing is marginally stronger:

**Before:** `Do NOT pass `-m` flag — rely on **Auto** routing (requires `previewFeatures: true`...).`
**After:** `Rely on **Auto** routing (omit `-m`, set `previewFeatures: true` in `~/.gemini/settings.json`); Auto handles the Gemini-3 fallback chain for you.`

---

#### L2. Announcement banner is a known-good pattern but feels heavy
**File:** `.claude/skills/gemini-cli/SKILL.md:15`
**Cross-ref:** INSIGHTS §2.2 (rationale > boilerplate). Low priority — only flag if the project strips announcement banners from other skills; otherwise leave.
**Offending text:**
> `> **Announcement**: Begin with: "I'm using the **gemini-cli** skill for cross-AI validation with Gemini."`

This is a UX choice more than a 4.7 concern. Leave as-is unless harmonizing with other skills.

---

#### L3. Intensifier: "never `cat`"
**Files:** `.claude/skills/gemini-cli/SKILL.md:142`, `.claude/skills/gemini-cli/templates.md:12`
**Cross-ref:** INSIGHTS §3.
**Offending text:**
> `Always read the result with the **Read tool**, never `cat`.`

**Before:** `Always read the result with the **Read tool**, never `cat`.`
**After:** `Read the result file with the **Read tool** — `cat` will dump the full payload back into the conversation and defeat the token-optimization pipeline above.`

---

### What's already well-tuned in `gemini-cli`

- **Gating phrase style for tool use** (`SKILL.md:157–162` "When NOT to Use") matches the §3 recommended pattern ("use [tool] **when** it would enhance X"). No "If in doubt, use gemini" or "default to gemini" phrasing anywhere.
- **One-shot framing** (`SKILL.md:151–155`) is explicit and correct — sets expectations before Claude tries to converse with Gemini.
- **Auto routing + fallback chain** documentation (`SKILL.md:114–121`, `reference.md:34–60`) gives the *why* behind the rule.
- **Self-update section** (`SKILL.md:17–30`) is a forward-looking pattern — the skill knows when it's stale and how to refresh. This is the right shape for a cross-AI bridge where upstream changes.
- **Response-length** — there are no hard caps on Claude's output (only on Gemini's), so §3 "hard-coded length caps" doesn't apply.
- **Subagent spawning** — not used, so §4 parallel-subagent guidance is N/A for this skill.

---

## Skill 2 — `dev-server`

**Overall verdict:** Solid operational skill for *starting* and *error-monitoring* a dev server, but it has a **significant gap on verification**: it never tells Claude to actually *look at the running app* (UI/frontend check, HTTP probe, screenshot) after startup to confirm it's working. The skill assumes "no error notification = green", which on 4.7 (more literal, less generalizing — INSIGHTS §1) means Claude will not proactively verify. This is the headline finding per the task brief's §4 "verification tools" cross-ref.

### High priority

#### H1. No verification step — "started" ≠ "working"
**File:** `.claude/skills/dev-server/SKILL.md` (entire Workflow, esp. §3 "Start with Monitor" lines 79–108 and §4 "React to errors" lines 110–116)
**Cross-ref:** INSIGHTS §4 — "Investigate-before-answering ... Never speculate about code you have not opened" and §1 "Instruction following — more literal; will NOT silently generalize."

The current workflow is: detect → preflight → start → *announce* → *react to errors as they arrive*. There is no step that **verifies the server is actually reachable** or that the UI rendered. A Next.js process can start, print "Ready on :3000", and still serve a broken page with a silent runtime exception that the grep filter on `SKILL.md:88` does not catch (hydration mismatches, 500s with custom error pages, CORS misconfig, etc.). On 4.7, absent an explicit step Claude will not improvise a `curl` probe or a Playwright screenshot — it will just announce "started" and stop.

The skill already allows `Bash` and has the **browser-use** skill available in the user's environment (CLAUDE.md references it), so the tooling is there — it's purely a prompt gap.

**Recommended insertion — new §3.5 between "Start with Monitor" and "React to errors":**

```
### 3.5. Verify it's actually serving

"No error in the Monitor" ≠ "the app works." After the dev command announces readiness, confirm the server is reachable before handing control back to the user:

1. **HTTP probe** — `curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:<port>` with a 5s timeout. Expect 2xx/3xx. Non-2xx, connection refused, or timeout → investigate.
2. **UI smoke check (frontend projects)** — when the project is a frontend framework (Next.js, Vite, Remix, Astro, SvelteKit, Nuxt, Angular, Gatsby, Expo web), invoke the `browser-use` skill to load the root URL, take a screenshot, and check for a visible error overlay (Next.js red box, Vite overlay, React error boundary fallback). Report what you see.
3. **Backend-only projects** — if there's a known health/root route (`/health`, `/api/health`, `/`), `curl` it and show the status code. Otherwise one HTTP probe is enough.

If verification fails, surface it with the same classification as §4 (build/runtime/dependency/port) — don't just re-announce success.
```

Also update the announcement template on `SKILL.md:103–104` so "started and monitoring" is contingent on the probe:

**Before (`SKILL.md:103–104`):**
```
**Announce** once started:
> Started **Next.js** dev server (`bun run dev`) on :3000 — monitoring for errors.
```

**After:**
```
**Announce** once started *and* verified:
> Started **Next.js** dev server (`bun run dev`) on :3000 — root URL returned 200, no error overlay. Monitoring for errors.
```

Rationale (INSIGHTS §2.2 "Explain the why"): silent runtime failures look identical to success from the Monitor's perspective, and 4.7 will not generalize "check for errors" into "probe the server" on its own (INSIGHTS §1).

---

#### H2. `critical piece` is an intensifier, and the filter regex lacks a rationale hook
**File:** `.claude/skills/dev-server/SKILL.md:83–86`
**Cross-ref:** INSIGHTS §3 (intensifier hygiene) + §2.2 (rationale).
**Offending text:**
> `The filter is the critical piece — raw dev server output floods the conversation. Pipe through grep to catch only errors, warnings, and crashes:`

The *reason* ("floods the conversation") is the good part; "critical piece" is filler. Minor edit:

**Before:**
```
The filter is the critical piece — raw dev server output floods the conversation. Pipe through grep to catch only errors, warnings, and crashes:
```

**After:**
```
The grep filter matters because a raw dev-server stdout stream is mostly routine request logs — thousands of lines of noise that would flood the conversation and hide real errors. The pattern below surfaces only startup failures, runtime exceptions, build errors, and warnings:
```

---

### Medium priority

#### M1. "Only important" filter bias — low-severity warnings get demoted
**File:** `.claude/skills/dev-server/SKILL.md:115`
**Cross-ref:** INSIGHTS §3 — "Only report high-severity / important issues" in review skills — 4.7 obeys literally → recall drops." Also §4 "Coverage-then-filter split."
**Offending text:**
> `4. **Warnings are low-priority** — mention briefly, don't alarm.`

On 4.7, "don't alarm" combined with "low-priority" can cause Claude to silently drop warnings that are actually signals (deprecated dependency = upcoming breakage; hydration warning = visible bug). Split coverage from filtering.

**Before:**
```
### 4. React to errors

When a Monitor notification fires:

1. **Classify** — build error, runtime exception, missing dependency, port conflict, type error, syntax error?
2. **Context** — quote the error, name the file and line if visible.
3. **Fix or ask** — for obvious issues (missing dep, typo, known pattern), suggest or apply the fix. For ambiguous ones, ask.
4. **Warnings are low-priority** — mention briefly, don't alarm.
```

**After:**
```
### 4. React to errors

When a Monitor notification fires, surface *everything* the filter caught — do not silently drop items because they look minor. Claude's job is coverage; the user decides what to ignore.

1. **Classify** — build error, runtime exception, missing dependency, port conflict, type error, syntax error, warning, deprecation.
2. **Context** — quote the error, name the file and line if visible.
3. **Fix or ask** — for obvious issues (missing dep, typo, known pattern), suggest or apply the fix. For ambiguous ones, ask.
4. **Severity shape** — label each item (error / warning / info) so the user can filter; do not pre-filter on their behalf.
```

---

#### M2. Port-conflict preflight asks the user instead of offering a default
**File:** `.claude/skills/dev-server/SKILL.md:65–70`
**Cross-ref:** INSIGHTS §1 — "Instruction following — more literal; will NOT silently generalize" (here, *in favor* of the instruction as-written; this is a minor UX note).
**Offending text:**
> `If occupied, tell the user and ask: kill the process or use a different port?`

Fine as-is on correctness; the nit is that the skill could state a default recommendation. Low-to-medium impact.

**Before:**
```
1. **Port conflict** — check if the default (or user-specified) port is taken:
   ```bash
   lsof -i :<port> -t 2>/dev/null
   ```
   If occupied, tell the user and ask: kill the process or use a different port?
```

**After:**
```
1. **Port conflict** — check if the default (or user-specified) port is taken:
   ```bash
   lsof -i :<port> -t 2>/dev/null
   ```
   If occupied, identify the occupying process (`ps -p <pid>`) and present two options to the user: kill PID N, or bind to port+1. Pick a default — don't block on the question if the occupying process is clearly another dev-server instance of the same project.
```

---

#### M3. "Multiple servers" edge case doesn't explicitly instruct parallel startup
**File:** `.claude/skills/dev-server/SKILL.md:124` ("Multiple servers: Frontend + backend? Start multiple Monitors with distinct descriptions.")
**Cross-ref:** INSIGHTS §4 — "Parallel tool-calling ... When calls have no dependencies, batch them in one turn."

4.7 is conservative about parallelism by default. The line says "start multiple Monitors" but doesn't say "in the same turn."

**Before:**
```
- **Multiple servers**: Frontend + backend? Start multiple Monitors with distinct descriptions.
```

**After:**
```
- **Multiple servers**: Frontend + backend? Start each Monitor in the **same turn** (parallel Bash calls) with distinct descriptions like `"Rails API :3001"` and `"Vite web :5173"`. Don't serialize — they're independent.
```

---

#### M4. Stack detection table has no "what if it guessed wrong" guidance
**File:** `.claude/skills/dev-server/SKILL.md:18–60`
**Cross-ref:** INSIGHTS §1 — "Instruction following — more literal" — 4.7 will commit to the first-match-wins rule without sanity-checking.
**Issue:** First-match-wins is right for speed but if e.g. a Python project has a stray `package.json` from tooling (eslint config for docs), the skill will start an npm dev server. The skill says at the bottom (`SKILL.md:62`) "If nothing matches, tell the user..." but not "if you're unsure, confirm."

**Before (add after line 62):**
```
If nothing matches, tell the user you couldn't detect the stack and ask what command to run.
```

**After:**
```
If nothing matches, tell the user you couldn't detect the stack and ask what command to run.

If the detection picks a stack that seems wrong for the directory (e.g. `package.json` exists but it's just dev tooling in a Python project, or both `manage.py` and `package.json` present and unclear which is primary), show the user your guess and confirm before starting. Don't silently commit to a wrong stack.
```

---

### Low priority

#### L1. `critical` phrasing in `@path` (N/A — belongs to gemini-cli, included here for symmetry of search)
No dev-server occurrences.

#### L2. Filter regex is a wall-of-text without grouping rationale
**File:** `.claude/skills/dev-server/SKILL.md:88`
**Cross-ref:** INSIGHTS §2.3 (XML structure / organized structure) — very low priority, more a readability note than a 4.7 issue.

The 80+ alternations in the regex are hard to maintain. A follow-up could group them as `errors | warnings | language-specific | build` via a comment block above the regex, so Claude can later extend one category without breaking others. Not urgent.

---

#### L3. No compaction-awareness note for long sessions
**File:** `.claude/skills/dev-server/SKILL.md` (skill is inherently long-running — persistent Monitor for the session)
**Cross-ref:** INSIGHTS §4 — "Context-awareness for long skills ... Context will be automatically compacted."

A dev-server session can run for hours with many error notifications. The skill could benefit from a one-liner reminding Claude that the Monitor persists across compactions and that the session state (port, PID, framework) should be re-surfaced if the user asks after a gap.

**Suggested addition (new subsection at end):**
```
## Session continuity

The Monitor is `persistent: true` and outlives context compaction. If the conversation has been compacted and the user asks about the server, restate: framework, port, PID (from startup), and how long it's been running. Don't assume the user remembers which dev server was started.
```

---

### What's already well-tuned in `dev-server`

- **Stack detection tables** (`SKILL.md:22–40, 42–54, 56–60`) are exactly the compact, scannable structure that 4.7 parses well — first-match-wins is explicit, no ambiguity.
- **Preflight checks** (`SKILL.md:64–77`) correctly gate dangerous actions (port kill, dep install) behind user confirmation. No "just do it" over-action bias.
- **Monitor tool choice** is the right abstraction — this is precisely what it's for, and the description field guidance (`SKILL.md:90`) gives the user a readable process name.
- **No `CRITICAL` / `ALWAYS` / `NEVER` spam** — only one `critical piece` phrase (flagged H2), which is mild. Good hygiene overall.
- **No tool over-nudging** — the skill is invoked by explicit user intent keywords (see the `description` frontmatter), not "if in doubt, start a dev server."
- **`allowed-tools` scope** (line 16) is tight (`Bash, Monitor, Read, Glob`) — no over-granted permissions.
- **Framework / package-manager detection order** is pragmatic and matches the ecosystem's actual precedence rules.

---

## Summary of all recommendations

### High priority (3)
1. `gemini-cli` SKILL.md:108 — Replace `CRITICAL: @path Safety` intensifier with rationale.
2. `gemini-cli` SKILL.md:138 — Drop `(mandatory)` from Token Optimization heading; keep the *why*.
3. `dev-server` SKILL.md (new §3.5) — Add a verification step: HTTP probe + browser-use UI smoke check for frontend stacks. This is the headline finding.

### Medium priority (9)
1. `gemini-cli` SKILL.md:144 — De-intensify "Always include" in context guidance.
2. `gemini-cli` SKILL.md:56, 73 + templates.md (all) — Replace "Output ONLY / No chain of thought / No reasoning" with positive framing.
3. `gemini-cli` SKILL.md:125 — Rename "Always Use `-p` Flag" to "Use `-p` for One-Shot".
4. `gemini-cli` SKILL.md:79–91 — Add explicit parallel-calls guidance for independent gemini queries.
5. `gemini-cli` templates.md:1–4 — Add `@path` existence reminder at top.
6. `dev-server` SKILL.md:83 — Replace "critical piece" with rationale-first phrasing.
7. `dev-server` SKILL.md:115 — Coverage-then-filter split for warnings ("Warnings are low-priority" → label-and-surface).
8. `dev-server` SKILL.md:124 — "Multiple servers" edge case should explicitly say "same turn" for parallel Monitor launches.
9. `dev-server` SKILL.md:62 — Add fallback when stack detection is ambiguous (don't silently commit to a wrong guess).

### Low priority (5)
1. `gemini-cli` SKILL.md:114, reference.md:34, 48 — Soften "Do NOT pass `-m`" to positive framing.
2. `gemini-cli` SKILL.md:15 — Announcement banner is fine, only harmonize if needed.
3. `gemini-cli` SKILL.md:142, templates.md:12 — "Never `cat`" → add the *why*.
4. `dev-server` SKILL.md:88 — Filter regex could be grouped with category comments.
5. `dev-server` SKILL.md (new section) — Add session-continuity / compaction-awareness note.

---

## Cross-reference map (INSIGHTS § → findings)

| INSIGHTS section | Findings |
|---|---|
| §1 Behavior deltas (literal following, subagent conservatism) | dev-server H1, M3, M4 |
| §2.2 Explain the why | gemini-cli H1, M3; dev-server H2 |
| §2.6 Positive framing | gemini-cli M2, L1 |
| §2.9 Match prompt style | gemini-cli M2 |
| §3 Anti-patterns (intensifiers, "only important") | gemini-cli H1, H2, M1, L3; dev-server H2, M1 |
| §4 Verification tools / investigate-before-answering | **dev-server H1 (headline)** |
| §4 Parallel tool-calling / subagents | gemini-cli M4; dev-server M3 |
| §4 Coverage-then-filter split | dev-server M1 |
| §4 Context-awareness for long skills | dev-server L3 |
