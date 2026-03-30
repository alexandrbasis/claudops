---
name: search-first
description: >-
  Search for existing solutions before building from scratch. Use when asked to 'search first',
  'check if this exists', 'find existing solution', 'before we build', 'is there already',
  'reuse existing', 'find a library for', or before implementing anything new. Also suggested
  as a pre-step when /si starts a new implementation. Applies the Adopt/Extend/Compose/Build
  decision matrix.
argument-hint: <what-you-need>
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
  - WebSearch
  - WebFetch
---

# /search-first — Find Before You Build

> **Announcement**: Begin with: "I'm using the **search-first** skill to check for existing solutions before building."

## Purpose

Prevent reinventing the wheel. Before writing new code, systematically search for existing solutions at four levels. This saves time, reduces maintenance burden, and improves consistency.

## Decision Matrix

After searching, recommend one of four verdicts:

| Verdict | Condition | Action |
|---------|-----------|--------|
| **Adopt** | Exact match found in codebase or npm | Use it directly — no new code needed |
| **Extend** | Partial match in codebase | Extend existing code to cover the new requirement |
| **Compose** | Multiple weak matches | Combine existing pieces into the solution |
| **Build** | Nothing suitable found | Build from scratch (justified) |

## Search Order

Execute searches in this order, stopping early if a strong match is found:

### 1. Project Codebase (always)
```
- Grep for keywords, function names, class names related to the need
- Glob for file patterns (e.g., *.service.ts, *.util.ts, *.helper.ts)
- Check shared/ and common/ directories
- Search test files — they often reveal capabilities not obvious from source
```

### 2. Package Registry (if no codebase match)
```bash
# Check already-installed packages
cat backend/package.json | grep -i "<keyword>"
cat mobile-app/package.json | grep -i "<keyword>"

# Search npm for established solutions
npm search <keyword> --json | head -20
```

### 3. MCP Tools (if specialized search needed)
```
- web_search_exa for general solutions
- get_code_context_exa for code patterns and library usage
- ref_search_documentation for official docs
```

### 4. GitHub (if building novel functionality)
```
- Search for similar implementations in well-maintained repos
- Look for patterns, not copy-paste code
```

## Output Format

```markdown
## Search Results: [what was searched for]

### Codebase Matches
- [file:line] — [description of what it does] — **Relevance**: High/Medium/Low

### Package Matches
- [package-name] — [what it provides] — **Already installed**: Yes/No

### External Matches
- [source] — [description] — **Applicability**: Direct/Partial/Inspiration

---

### Verdict: **[Adopt | Extend | Compose | Build]**

**Reasoning**: [1-2 sentences explaining why this verdict]

**Recommended approach**: [Specific next steps]
```

## Integration with /si

When `/si` starts a new implementation step, consider suggesting:
> "Before implementing [step], should I run `/search-first` to check for existing solutions?"

This is especially valuable for:
- Utility functions (date formatting, validation, string manipulation)
- Common patterns (pagination, filtering, sorting)
- Third-party integrations (auth, email, file upload)
- UI components (in mobile-app)

## Constraints

- **Do NOT recommend unmaintained packages** (check last publish date, open issues)
- **Do NOT recommend packages for trivial operations** (e.g., `is-odd` for checking odd numbers)
- **Prefer codebase solutions over external packages** — less dependency, more control
- **If extending, show the specific code to extend** — don't just say "extend it"
- **Time-box**: Spend no more than 2-3 minutes searching before reporting results
