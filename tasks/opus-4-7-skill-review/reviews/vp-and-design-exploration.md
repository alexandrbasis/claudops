# Review: `/vp` and `/design-exploration` Skills — Opus 4.7 Audit

Reviewed files:
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/vp/SKILL.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/vp/references/ui-playground-template.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/vp/references/backend-playground-template.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/vp/references/tips.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/design-exploration/SKILL.md`
- `/Users/alexandrbasis/Desktop/Coding/wythm-claude-workflows/.claude/skills/design-exploration/references/exploration-checklist.md`

Lens: `tasks/opus-4-7-skill-review/INSIGHTS.md` (§1 Frontend defaults + §3 anti-patterns + §4 positive patterns + §5 audit checklist).

Overall posture: both skills are **generally well-tuned**. They use neutral voice (very few intensifiers), XML-free but clearly structured, and already encourage parallelism (`design-exploration`). The meaningful gaps are concentrated in: (a) frontend aesthetic handling (`vp` delegates all styling to the downstream `playground` skill with only a "neutral, accessible default" guard — this is the 4.7 frontend-default hazard, INSIGHTS §1), (b) variety prompting (INSIGHTS §4 "propose N distinct directions" is missing), and (c) a few literal-scope gaps.

---

## Skill 1 — `/vp` (Visual Prototype)

### High priority

#### H1. Frontend defaults: no variety prompt when no project design context exists
**Files:** `vp/SKILL.md:94`, `vp/references/ui-playground-template.md:25`, `vp/references/ui-playground-template.md:64`
**Cross-ref:** INSIGHTS §1 "Frontend defaults" row; §4 "For design/variety: propose N distinct directions".

Exact offending text (SKILL.md:94):
> "If no project-specific design context exists, instruct the playground to use a neutral, accessible default style that is easy to adapt."

Exact offending text (ui-playground-template.md:25):
> "If no project-specific design context exists, keep the prototype visually coherent, accessible, and easy to adapt rather than inventing a heavy branded system."

Exact offending text (ui-playground-template.md:64):
> "If no project-specific styling is known, use a neutral, accessible default style."

Why this matters on 4.7: per INSIGHTS §1, Opus 4.7 has a strong "cream/serif/terracotta" persistent house style for frontend. "Neutral, accessible default" is exactly the kind of broad instruction §3 warns against ("these shift the model to *a different fixed default*, not variety"). The downstream `playground` skill inherits a single aesthetic with no anchor.

**Before → After (SKILL.md:94):**
```
If no project-specific design context exists, instruct the playground
to use a neutral, accessible default style that is easy to adapt.
```
→
```
If no project-specific design context exists, first propose 3–4 distinct
visual directions as one-line rationales (e.g. "editorial-serif",
"utility-mono", "soft-neumorphic", "dense-enterprise"). Ask the user to
pick one via AskUserQuestion before generating the playground. Avoid
defaulting to a cream/serif/warm-accent house style unless the user
explicitly picks it.
```

**Before → After (ui-playground-template.md:25 and :64):**
Replace the current "neutral default" guidance with a slot for the user-chosen direction:
```
**Chosen visual direction:** [ONE OF THE 3–4 DIRECTIONS THE USER PICKED]
(If the user has not chosen, stop and surface 3–4 one-line direction
rationales for them to pick from before generating HTML.)
```

#### H2. GATE 1 misses variety axis entirely
**File:** `vp/SKILL.md:60-77`
**Cross-ref:** INSIGHTS §4 variety guidance.

GATE 1 only classifies UI_FACING / BACKEND / MIXED. For UI_FACING, no gate asks "should we show the user alternative visual directions?" — this is a product gap given the 4.7 frontend-default behavior.

**Before → After (add a sub-step to GATE 1 for UI_FACING):**
```
Confirm the detected type with the user via AskUserQuestion before proceeding.
```
→
```
Confirm the detected type with the user via AskUserQuestion before proceeding.

If UI_FACING and no project design system is documented, add a second
AskUserQuestion offering 3–4 concrete visual directions (one-line each)
so the user anchors the aesthetic instead of inheriting model defaults.
```

### Medium priority

#### M1. Literal-scope gap on "required states"
**File:** `vp/SKILL.md:96-102`
**Cross-ref:** INSIGHTS §5 item 6 (literal-scope gaps), §1 "Instruction following — more literal".

Current text lists four required states (error, constraint, empty, success) as a bullet list above the `playground` hand-off, but nothing tells the downstream skill to apply them **per screen / per flow** rather than once globally. 4.7 will not generalize silently.

**Before → After (SKILL.md:96):**
```
**Required states in every prototype:**
```
→
```
**Required states — apply to every screen and every flow in the
prototype, not just the first:**
```

And in `ui-playground-template.md:37-41`, the "Scenarios to include" block should say:
```
1. Happy Path: [Main flow from discovery]
```
→
```
1. Happy Path: [Main flow from discovery]
   For each screen in the happy path, include the four required states
   (error, constraint, empty, success) — do not apply them only to the
   first screen.
```

#### M2. Handoff text duplicates itself — possible over-verbose output
**Files:** `vp/SKILL.md:169-176` and `vp/SKILL.md:200-211`
**Cross-ref:** INSIGHTS §1 "Response length — calibrated to task complexity".

The skill tells the model to print a near-identical "approved" block twice (once at GATE 4, once at "Handoff — Next Steps"). On 4.7 this will produce redundant terminal output. Collapse to one handoff block.

**Before → After:** remove the duplicate `## Handoff — Next Steps` section (lines 200–211) or remove the "Notify user" block in GATE 4 (169–176) — keep only one.

### Low priority

#### L1. `AskUserQuestion` options at GATE 3 could include rationale cues
**File:** `vp/SKILL.md:122-126`
**Cross-ref:** INSIGHTS §2 item 2 ("Explain the *why*").

The three options (Approve / Request Changes / Reject) are bare. Short rationales would help the user choose and help the model frame the question better.

**Before → After:** add a one-line rationale per option, e.g.:
```
- **Approve** — ready for technical decomposition
```
→
```
- **Approve** — design matches the intended feel; proceed to /ct
- **Request Changes** — close, but needs specific tweaks (stay in /vp)
- **Reject** — wrong direction entirely; discovery needs to be revisited
```

#### L2. `tips.md` "Overloading the playground" uses negative framing
**File:** `vp/references/tips.md:27`
**Cross-ref:** INSIGHTS §2 item 6 (positive framing beats negative).

Exact offending text:
> "**Overloading the playground** — Focus on the core flow. Avoid cramming every edge case into a single view."

**Before → After:**
```
**Overloading the playground** — Focus on the core flow. Avoid cramming
every edge case into a single view. Use presets/scenarios to separate
concerns.
```
→
```
**One flow per view** — keep each view focused on one flow. Split edge
cases across presets or scenarios so each view stays readable.
```

### Well-tuned aspects (no changes needed)

- Intensifier hygiene is good: SKILL.md has one `STOP` (line 141) that is load-bearing (rejection path), not used as emphasis. No reflexive `CRITICAL:` / `NEVER` chains.
- GATE structure is clear, each gate has a stopping condition — avoids the "be thorough with no stopping condition" anti-pattern (INSIGHTS §3).
- Routing section (SKILL.md:26-32) pre-empts wrong-skill drift; matches §2 foundational technique #1.
- No prefill / deprecated patterns. No hard-coded response-length caps.

---

## Skill 2 — `/design-exploration`

### Medium priority

#### M3. Parallel spawn instruction is soft — 4.7 under-parallelizes by default
**File:** `design-exploration/SKILL.md:35`
**Cross-ref:** INSIGHTS §1 "Subagent spawning — more conservative by default"; §4 parallel subagent prompting.

Exact offending text:
> "Launch **2-3 Explore agents in parallel** to scan different angles of the codebase simultaneously."

This is close to correct, but "in parallel" is a weak signal on 4.7 — the model has been observed to sequentialize regardless. INSIGHTS §4 prescribes an explicit sentence.

**Before → After:**
```
Launch **2-3 Explore agents in parallel** to scan different angles of
the codebase simultaneously. Use a faster model unless the task clearly
needs deeper reasoning.
```
→
```
Spawn 2–3 Explore agents in the **same turn** (single message with
multiple tool calls) so they run concurrently. The scan angles below
are independent — do not sequentialize them. Use a faster model unless
the task clearly needs deeper reasoning.
```

This also aligns with the "Key Principles" bullet at line 112 which already says "Parallel exploration: Always launch Explore agents simultaneously, not sequentially" — but the imperative there isn't connected to the operational step at line 35. The rewrite closes that loop.

#### M4. "Step 4: Incremental Design Summary" — interactive back-and-forth can balloon on 4.7
**File:** `design-exploration/SKILL.md:80-94`
**Cross-ref:** INSIGHTS §1 "Interactive coding — more post-user-turn reasoning → more tokens. Front-load full context in turn 1; minimize interactive back-and-forth."

Current step instructs 200–300 word sections with a "Does this look right so far?" check-in after each. On 4.7 this pattern multiplies reasoning tokens and can stall. Prefer one structured response with explicit "reply with `continue` or `revise [section]`" affordance, rather than a polling loop.

**Before → After:**
```
1. Present the design in **200-300 word sections**
2. After each section, check: "Does this look right so far?"
```
→
```
1. Present all sections in a single structured response (each section
   200–300 words, clearly labeled).
2. End with: "Reply `continue` to proceed, or `revise: <section name>`
   to iterate on a specific section." Do not pause between sections.
```

### Low priority

#### L3. "YAGNI ruthlessly" — intensifier without stopping condition
**File:** `design-exploration/SKILL.md:108`
**Cross-ref:** INSIGHTS §3 "Be thorough / exhaustive / comprehensive with no stopping condition".

Exact offending text:
> "**YAGNI ruthlessly**: Strip unnecessary features from all proposals"

"Ruthlessly" is an intensifier. On 4.7 (§1 "more literal"), this may over-prune valid tradeoffs in the "2–3 design approaches" step. Dial to a neutral rule with a stop condition.

**Before → After:**
```
- **YAGNI ruthlessly**: Strip unnecessary features from all proposals
```
→
```
- **YAGNI**: Each proposed approach should cover only what the caller's
  goal requires. If an approach adds abstraction beyond the stated goal,
  either drop it or label the extra clearly as "optional — not required
  by the brief."
```

#### L4. `exploration-checklist.md` is long — risk of checklist-driven over-coverage on 4.7
**File:** `design-exploration/references/exploration-checklist.md` (entire file, ~135 lines of checkboxes)
**Cross-ref:** INSIGHTS §3 "Be thorough / exhaustive / comprehensive with no stopping condition"; §1 "Instruction following — more literal".

4.7 will tend to treat an unchecked box as work-to-do. The file's header already says:
> "Adapt paths, layer names, and framework assumptions to the actual project rather than forcing this checklist onto the repo."

This is good, but it should be reinforced with a stopping condition.

**Before → After (add one sentence after the TOC, ~line 10):**
```
> Use these checklists as a **menu**, not a requirement. Pick 3–5 items
> per scan angle that are most relevant to the caller's goal. Stop when
> you have enough evidence to propose approaches — unchecked items are
> not debts.
```

### Well-tuned aspects (no changes needed)

- No `CRITICAL:` / `MUST` / `ALWAYS` / `NEVER` intensifiers anywhere in the skill. Voice is already calm.
- Evidence-based principle (line 107) matches INSIGHTS §4 "Investigate-before-answering".
- Output Contract (lines 96–103) gives the caller a predictable return shape — matches §2 foundational technique #4 (explicit structure).
- Caller-sensitive depth (line 110) — good guard against over-engineering (§4 "minimize over-engineering").
- No prefill patterns. No hard-coded response-length caps that fight §1 adaptive length.
- Correctly scopes itself NOT to do tech decomposition (line 94) — good literal-scope hygiene.

---

## Summary of priorities

| # | Skill | Priority | File:line | Issue |
|---|-------|----------|-----------|-------|
| H1 | vp | High | `vp/SKILL.md:94`, `ui-playground-template.md:25,64` | Frontend aesthetic default — need N-directions variety prompt |
| H2 | vp | High | `vp/SKILL.md:60-77` | GATE 1 has no aesthetic-direction gate for UI_FACING |
| M1 | vp | Medium | `vp/SKILL.md:96-102`, `ui-playground-template.md:37-41` | Literal-scope: "every screen" not stated for required states |
| M2 | vp | Medium | `vp/SKILL.md:169-176` + `200-211` | Duplicate handoff block — redundant output |
| M3 | design-exploration | Medium | `design-exploration/SKILL.md:35` | Parallel-spawn instruction too soft for 4.7 |
| M4 | design-exploration | Medium | `design-exploration/SKILL.md:80-94` | Per-section polling loop → ballooned interactive tokens |
| L1 | vp | Low | `vp/SKILL.md:122-126` | GATE 3 options lack rationale |
| L2 | vp | Low | `tips.md:27` | Negative framing ("avoid cramming") |
| L3 | design-exploration | Low | `design-exploration/SKILL.md:108` | "YAGNI ruthlessly" — intensifier, no stop condition |
| L4 | design-exploration | Low | `exploration-checklist.md` (whole file) | No explicit "menu not requirement" stopping condition |

Neither skill has prefill patterns, broken parallel-tool batching instructions, response-length caps, or filter-leakage issues. The biggest leverage is H1/H2 — anchoring the frontend aesthetic before the `playground` skill runs, which is the single most impactful 4.7 behavior delta for visual skills.
