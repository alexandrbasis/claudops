# Skill Evaluation Rubric

7 dimensions, each scored 0-10. Use this rubric for consistent, repeatable analysis.

---

## 1. Frontmatter Quality

**What to check:**
- `name`: kebab-case, matches folder name, no spaces/capitals, <40 chars
- `description`: third-person ("This skill should be used when..."), includes WHAT + WHEN + trigger phrases, <1024 chars, no XML tags
- `argument-hint`: present if skill accepts arguments, shows clear usage pattern
- `allowed-tools`: lists all tools the skill actually references
- Optional fields used appropriately: `license`, `context`, `agent`, `disable-model-invocation`

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | All fields present, description has specific trigger phrases, negative triggers if needed |
| 7-8 | Required fields correct, description adequate but could be more specific |
| 5-6 | Required fields present but description too vague or missing triggers |
| 3-4 | Partial frontmatter, name or description has issues |
| 0-2 | Missing or broken frontmatter |

**Common anti-patterns:**
- Description says "Helps with X" without trigger phrases
- Missing `argument-hint` when skill parses `$ARGUMENTS`
- `allowed-tools` missing tools that SKILL.md references
- Description in imperative form ("Use this when...") instead of third-person

**Good example (from hookify):**
```yaml
description: Guide for creating hookify rules to prevent unwanted behaviors. Use when creating, editing, or understanding hookify rule files.
argument-hint: help | list | configure | <behavior description>
```

**Bad example:**
```yaml
description: Manages projects.
```

---

## 2. Structure & Organization

**What to check:**
- Clear opening section (PRIMARY OBJECTIVE, Overview, or equivalent)
- Logical section progression matching the skill's purpose
- GATE/STEP pattern for multi-step workflows
- Clear section headers (H2/H3) for scanability
- Reasonable SKILL.md length (<5000 words for body)
- No orphaned sections or dead-end flows

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | Clear objective, logical flow, proper GATE/STEP pattern for workflows, concise |
| 7-8 | Good structure, minor organizational improvements possible |
| 5-6 | Structure present but sections feel disorganized or missing clear flow |
| 3-4 | Flat structure, hard to follow, no workflow pattern where one is needed |
| 0-2 | No clear structure, wall of text |

**Common anti-patterns:**
- Jumping between topics without clear section breaks
- Workflow skill without GATE/STEP progression
- All content in SKILL.md when references/ would be more appropriate
- Sub-command skill without clear sub-command sections (see hookify for good pattern)

**Good pattern (sub-command skill):**
```markdown
## Usage
- `/skill help` - Show documentation
- `/skill list` - List items
- `/skill <arg>` - Main action

Parse $ARGUMENTS to determine which sub-command to run.

## Sub-command: help
...
## Sub-command: list
...
```

---

## 3. Instruction Clarity

**What to check:**
- Imperative/infinitive voice ("Read the file", "Create the document"), not second-person ("You should read")
- Each step is actionable and specific
- Error handling guidance present
- Examples with realistic user requests
- Explicit tool references (AskUserQuestion, Task, Skill, Bash, etc.)
- Decision points clearly defined with conditions

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | All instructions actionable, imperative voice, error handling, examples, explicit tools |
| 7-8 | Mostly clear, minor voice inconsistencies or missing edge cases |
| 5-6 | Instructions understandable but vague in places, missing error handling |
| 3-4 | Mix of clear and vague instructions, inconsistent voice |
| 0-2 | Instructions too vague to follow reliably |

**Common anti-patterns:**
- "Validate the data before proceeding" (how? what validation?)
- "Handle errors appropriately" (what errors? what action?)
- Mixing "you should" with imperative voice
- Referencing tools without specifying which tool (e.g., "search for files" vs "Glob for `*.md` files")

**Good example:**
```markdown
1. Glob for `.claude/hooks/hookify/rules/*.local.md`
2. Read each file, extract frontmatter (name, enabled, event, pattern)
3. Present as table:
| Name | Enabled | Event | Pattern | File |
```

**Bad example:**
```markdown
1. Find the rule files
2. Show them to the user
```

---

## 4. Token Efficiency

**What to check:**
- SKILL.md word count (target: <5000 words)
- Progressive disclosure: detailed docs in references/, not inline
- Directive style: CRITICAL, MANDATORY, STOP used for emphasis (not verbose explanation)
- No redundancy between SKILL.md and reference files
- Table/list format for dense information
- No unnecessary explanatory text ("why") in action steps

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | Under 2000 words, excellent progressive disclosure, no redundancy |
| 7-8 | Under 3500 words, good use of references, minimal redundancy |
| 5-6 | Under 5000 words, some content could move to references |
| 3-4 | Over 5000 words, significant redundancy or inlining |
| 0-2 | Massively oversized, no progressive disclosure |

**Common anti-patterns:**
- Duplicating reference content in SKILL.md
- Long explanatory paragraphs where bullet lists suffice
- Inlining large code examples instead of referencing assets/
- Repeating the same instruction in multiple sections

**Optimization techniques:**
- Move >500-word reference blocks to `references/`
- Replace paragraph explanations with tables
- Link to reference files with grep patterns for large docs (>10k words)
- Delete "why" text from step-by-step instructions (save for comments only)

---

## 5. Trigger Precision

**What to check:**
- Description contains specific phrases users would say
- Not too broad (doesn't conflict with other skills)
- Not too narrow (covers paraphrased requests)
- Negative triggers present if skill has close neighbors (e.g., "Do NOT use for simple data exploration")
- File types mentioned if relevant

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | Multiple specific trigger phrases, negative triggers where needed, no conflicts |
| 7-8 | Good triggers, minor overlap risk with other skills |
| 5-6 | Adequate triggers but could be more specific |
| 3-4 | Too broad or too narrow, likely under/over-triggers |
| 0-2 | No meaningful trigger information in description |

**Testing approach:**
Ask: "When would Claude load this skill?" — the answer should match the description.

**Conflict detection:**
Compare the skill's description with other skills in the same category. Flag overlapping trigger phrases.

**Common anti-patterns:**
- Description: "Helps with projects" (triggers on everything project-related)
- No mention of file types when skill is file-type specific
- Two skills with nearly identical trigger phrases

---

## 6. Composability

**What to check:**
- Skill delegates to other skills via Skill tool where appropriate
- Uses Task tool for subagent work (Explore, Plan, etc.)
- Doesn't assume it's the only active skill
- References related skills by name (e.g., "For X, use /other-skill instead")
- Uses AskUserQuestion for interactive decisions (not hardcoded paths)
- Follows shared conventions (file paths, naming, templates)

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | Actively delegates, references related skills, uses subagents appropriately |
| 7-8 | Some delegation, acknowledges other skills exist |
| 5-6 | Standalone but doesn't conflict with others |
| 3-4 | Reinvents functionality available in other skills |
| 0-2 | Actively conflicts with or duplicates other skills |

**Common anti-patterns:**
- Reimplementing git branch creation instead of referencing `/cb`
- Hardcoding decisions that should use AskUserQuestion
- Not mentioning related skills in scope boundaries

---

## 7. Bundled Resources

**What to check:**
- `scripts/` — executable code for deterministic/repeatable tasks, with shebangs
- `references/` — documentation loaded as needed, properly linked from SKILL.md
- `assets/` — templates/files for output, not loaded into context
- No orphaned files (referenced but missing, or present but unreferenced)
- No README.md inside skill folder (use SKILL.md instead)
- Proper category: code in scripts/, docs in references/, templates in assets/

**Scoring:**
| Score | Criteria |
|-------|----------|
| 9-10 | All resources properly categorized, linked, no orphans, progressive disclosure works |
| 7-8 | Resources present and mostly well-organized, minor categorization issues |
| 5-6 | Some resources exist but organization could improve |
| 3-4 | Resources misplaced or orphaned |
| 0-2 | No resources when they'd clearly help, or broken references |
| N/A | Skill genuinely doesn't need bundled resources |

**Common anti-patterns:**
- Large code blocks in SKILL.md that should be scripts/
- API documentation inline that should be references/
- Template files in references/ instead of assets/
- Files present in directories but never referenced from SKILL.md

---

## Overall Score

Calculate: average of all 7 dimensions (skip N/A dimensions).

| Overall | Rating |
|---------|--------|
| 9-10 | Excellent — production-ready, exemplary |
| 7-8 | Good — solid skill, minor improvements possible |
| 5-6 | Adequate — functional but needs attention |
| 3-4 | Needs Work — significant issues to address |
| 0-2 | Critical — fundamental problems, consider rewrite |
