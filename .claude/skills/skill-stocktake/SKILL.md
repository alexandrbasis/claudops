---
name: skill-stocktake
description: >-
  Batch audit of all skills for quality, freshness, and coverage. Use when asked to
  'audit skills', 'skill stocktake', 'review all skills', 'skill health check',
  'check skill quality', 'which skills need updating', or 'skill inventory'.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /skill-stocktake — Batch Skill Quality Audit

> **Announcement**: Begin with: "I'm using the **skill-stocktake** skill to audit all skills."

## Purpose

Systematically evaluate every skill in `.claude/skills/` for quality, coverage, and relevance. Produces a summary report with actionable verdicts.

## Modes

### Quick Mode (default)
Audit only skills changed since the last git tag or in the last 30 days:
```bash
git diff --name-only $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~50) -- '.claude/skills/'
```
If no tag exists, audit skills modified in last 50 commits.

### Full Mode
Audit ALL skills. Triggered by: `skill-stocktake full`, `audit all skills`, `full skill review`.

---

## Evaluation Criteria

For each `SKILL.md`, evaluate:

| Criterion | What to check | Score |
|-----------|--------------|-------|
| **Description quality** | Is the `description` field specific with clear trigger phrases? Or is it vague/trigger-only? | Good / Needs work |
| **Announcement** | Does it have a `> **Announcement**: Begin with:` line? | Present / Missing |
| **Frontmatter** | Are `name`, `description`, `allowed-tools` present and valid? | Valid / Invalid |
| **Content freshness** | Does the content reference current project patterns? Are there stale references? | Fresh / Stale |
| **Trigger coverage** | Are trigger phrases comprehensive? Would a user naturally say these things? | Good / Gaps |
| **Overlap** | Does this skill overlap significantly with another skill? | Unique / Overlaps with [X] |
| **Complexity** | Is the skill doing too much? Could it be split? | Right-sized / Too broad |

## Verdicts

Assign each skill one verdict:

- **Keep** — Skill is healthy, no action needed
- **Improve** — Skill works but needs specific fixes (list them)
- **Retire** — Skill is unused, superseded, or no longer relevant
- **Merge** — Skill overlaps significantly with another; combine them

## Output Format

```markdown
# Skill Stocktake Report — [date]

**Mode**: Quick / Full
**Skills audited**: X of Y total
**Summary**: X Keep, X Improve, X Retire, X Merge

---

## Keep (X skills)
| Skill | Notes |
|-------|-------|
| `/si` | Healthy, well-triggered |
| `/quick` | Good coverage |

## Improve (X skills)
| Skill | Issues | Suggested fixes |
|-------|--------|-----------------|
| `/foo` | Missing announcement, vague triggers | Add announcement line, add 3 trigger phrases |

## Retire (X skills)
| Skill | Reason |
|-------|--------|
| `/bar` | Superseded by /baz, no usage in 3 months |

## Merge (X skills)
| Skills | Reason | Suggested target |
|--------|--------|-----------------|
| `/a` + `/b` | 80% overlap in functionality | Merge into `/a` |

---

## Top 3 Actions
1. [Most impactful improvement]
2. [Second]
3. [Third]
```

## Constraints

- **Read, don't modify** — this skill only produces a report, never edits skill files
- **Be specific** — "needs improvement" without details is useless
- **Check for orphans** — skills referenced in other skills but that don't exist
- **Check for conflicts** — skills with overlapping trigger phrases that might confuse routing
- **Count skills** — report total count at the top for tracking growth over time
