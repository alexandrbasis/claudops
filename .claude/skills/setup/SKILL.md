---
name: setup
description: >-
  Configure workflow for your codebase. Run after cloning .claude/ into your repo.
  Use when asked to 'setup', 'configure workflow', 'initialize .claude', 'setup wizard',
  'configure for my project', or when the codebase has unconfigured {{PLACEHOLDER}} variables.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - Edit
  - AskUserQuestion
  - Agent
  - TodoWrite
---

# Setup Wizard

> **Announcement**: "Running the **setup wizard** to configure this workflow for your codebase."

Configure all workflow skills, agents, and hooks to match the target codebase's tech stack, structure, and conventions. This skill reads the codebase, detects patterns, confirms with the user, then fills in `{{PLACEHOLDER}}` variables across all workflow files.

## When to Run

- First time after cloning `.claude/` into a new repo
- When switching to a different project
- When `{{PLACEHOLDER}}` variables are visible in skill/agent files
- When the user says "setup", "configure", or "initialize"

## Process

### Phase 1: Codebase Discovery (Parallel Agents)

Launch **3 Explore agents in parallel** to scan the target codebase:

**Agent 1 — Tech Stack Detection:**
```
Detect the project's technology stack by examining:
- package.json / go.mod / pyproject.toml / Gemfile / Cargo.toml / pom.xml
- Import patterns in source files (framework detection)
- ORM/database config files (prisma/, alembic/, db/migrate/, etc.)
- Auth configuration (firebase config, auth0, clerk, passport setup)
- Test configuration (jest.config, pytest.ini, vitest.config, .rspec)
- CI/CD files (.github/workflows/, .gitlab-ci.yml, Jenkinsfile)

Return a structured report:
- Language: [TypeScript/Python/Go/Ruby/Java/Rust/etc.]
- Framework: [NestJS/Express/Next.js/Django/FastAPI/Rails/Gin/Spring/etc.]
- ORM: [Prisma/TypeORM/Drizzle/SQLAlchemy/GORM/ActiveRecord/etc.] or "none"
- Auth: [Firebase JWT/Auth0/Clerk/Passport/custom JWT/etc.] or "none detected"
- Test framework: [Jest/Vitest/pytest/RSpec/go test/JUnit/etc.]
- Package manager: [npm/yarn/pnpm/pip/poetry/bundler/cargo/etc.]
- CI system: [GitHub Actions/GitLab CI/etc.] or "none detected"
```

**Agent 2 — Project Structure Detection:**
```
Map the project's directory structure:
- Is this a monorepo? (multiple package.json, workspaces, nx.json, turbo.json)
- Source directories (src/, app/, lib/, cmd/, backend/src/, etc.)
- Test directories (tests/, __tests__/, test/, spec/, *_test.go, etc.)
- Documentation directories (docs/, doc/, documentation/)
- Config files (tsconfig.json, pyproject.toml, go.mod, etc.)
- Schema/migration files (prisma/schema.prisma, db/schema.rb, alembic/, etc.)
- Architecture docs (any file describing project structure or conventions)

Return a structured report:
- Monorepo: yes/no (if yes, list workspace names and paths)
- Source dir(s): [paths]
- Test dir(s): [paths]
- Docs dir: [path] or "none"
- Config files: [list]
- Schema path: [path] or "N/A"
- Architecture docs found: [paths] or "none"
```

**Agent 3 — Commands & Conventions Detection:**
```
Detect the project's standard commands and conventions:
- Read package.json scripts / Makefile / pyproject.toml scripts / taskfile.yml
- Identify: test command, lint command, build command, format command, typecheck command, coverage command
- Check for existing .claude/ or .cursor/ configuration
- Read any architecture docs found to understand patterns (DDD, MVC, hexagonal, etc.)
- Detect architecture layers from directory structure (controllers/, services/, models/, etc.)

Return a structured report:
- Test command: [command]
- Lint command: [command] or "none"
- Build command: [command] or "none"
- Format command: [command] or "none"
- Typecheck command: [command] or "none"
- Coverage command: [command] or "none"
- Architecture pattern: [description] or "not detected"
- Layer structure: [description of layers and their responsibilities]
- Layer rules: [dependency direction, encapsulation rules]
- Existing .claude/: yes/no (if yes, list what's configured)
```

### Phase 2: User Confirmation (Interactive)

Present discovery results and confirm with user. Use `AskUserQuestion` for each category.

**Round 1 — Tech Stack:**
```
question: "We detected the following tech stack. Is this correct?"
options:
  - "Yes, this is correct"
  - "Let me correct some values" (then ask for corrections)
```
Show: Language, Framework, ORM, Auth, Test framework, Package manager

**Round 2 — Project Structure:**
```
question: "We detected this project structure. Correct?"
options:
  - "Yes, correct"
  - "Let me adjust paths"
```
Show: Monorepo status, Source/Test/Docs dirs, Schema path

**Round 3 — Commands:**
```
question: "These are the detected commands. Correct?"
options:
  - "Yes, correct"
  - "Let me fix some commands"
```
Show: All detected commands (test, lint, build, format, typecheck, coverage)

**Round 4 — Architecture:**
```
question: "This is the detected architecture pattern. Correct?"
options:
  - "Yes, correct"
  - "Let me describe the architecture"
  - "No specific architecture pattern"
```
Show: Architecture pattern, layer structure, layer rules

### Phase 3: Apply Configuration

After confirmation, fill in all `{{PLACEHOLDER}}` variables **directly in the files** across the workflow. No intermediate config files — the wizard edits skills, agents, and hooks in-place.

**Step 1: Fill convention skills**

Update `coding-conventions/SKILL.md` and `review-conventions/SKILL.md` — these are the most important files as they're preloaded into all review agents and the developer agent via `skills:` frontmatter.

Replace ALL `{{VARIABLE}}` placeholders with detected values. For multi-line sections (`{{LAYERS}}`, `{{LAYER_RULES}}`), generate complete, well-structured content based on detection results.

**Step 2: Fill remaining skills and agents**

Scan ALL `.md` files under `.claude/skills/` and `.claude/agents/` for remaining `{{PLACEHOLDER}}` patterns. For each file with placeholders:

1. Read the file
2. Identify all `{{VARIABLE}}` placeholders
3. Replace with confirmed values
4. Show the user a brief summary: "Updated [filename]: replaced X placeholders"

Ask user confirmation every 5 files: "Continue applying to next batch?"

**Step 3: Fill hook scripts**

Scan `.sh` files in `.claude/hooks/` for `{{PLACEHOLDER}}` patterns and replace with confirmed values. Hook scripts use the same `{{VARIABLE}}` syntax as skills — the wizard treats them identically.

Also update hook-specific configuration variables based on the detected stack:
- `bash-guard.sh`: Set `PROTECTED_DIRS`, `DB_DANGER_PATTERN`, `DB_SAFE_CMD` based on detected ORM
- `file-guard.sh`: Set `PROTECTED_FILE_PATTERN`, `CORE_LAYER_PATH`, `CORE_FORBIDDEN_IMPORTS` based on detected architecture
- `stop-guard.sh` and `test-before-pr.sh`: Already covered by `{{TEST_CMD}}` and `{{BUILD_CMD}}`

**Step 4: Generate project-specific checks**

If the codebase has a clear architecture pattern (DDD, MVC, etc.), generate `code-analysis/references/project-checks.md` with architecture-specific grep commands tailored to the detected source directory and patterns.

**Step 5: RTK token optimization (optional)**

Check if `rtk` is installed (`which rtk`). If installed:
- Verify the RTK hook is present in `.claude/settings.json` PreToolUse hooks (it should already be wired as `rtk hook default`)
- Inform the user: "RTK is installed and wired — Bash commands will be auto-compressed for 60-90% token savings."

If NOT installed:
- Ask: "RTK (Rust Token Killer) can reduce token usage by 60-90%. Install it?"
  - "Yes, install via Homebrew" → run `brew install rtk`
  - "Yes, install via curl" → run `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh`
  - "Skip for now"
- If installed, the hook in `settings.json` will automatically activate on next session.

**Step 6: Prune irrelevant skills**

Based on detected tech stack, identify skills that are not applicable to this project. For each irrelevant skill, ask the user whether to disable it.

Irrelevant skill detection rules:
- `fci` (Fix CI) — skip if no CI config detected
- `cc-linear` — skip if no Linear integration detected
- `codex-cli` — skip if user doesn't use Codex
- `cursor-cli` — skip if user doesn't use Cursor
- `gemini-cli` — skip if user doesn't use Gemini CLI
- `parallelization` — skip if project is too small (< 5 source files)

To disable a skill: rename `SKILL.md` to `SKILL.md.disabled` in the skill's directory. This prevents Claude Code from loading it while preserving the file for re-enabling later.

Present as a single AskUserQuestion with multiSelect:
```
question: "These skills may not be relevant to your project. Which ones should we disable?"
options: [list of detected irrelevant skills with reasons]
multiSelect: true
```

### Phase 4: Verification

After all files are updated:

1. Run: `grep -r '{{' .claude/skills/ .claude/agents/ --include='*.md' | head -20`
2. If any `{{PLACEHOLDER}}` variables remain, report them to the user
3. Show a summary of all changes made

## Output

Print a completion summary:
```
Setup complete!

Tech stack: [LANGUAGE] + [FRAMEWORK] + [ORM]
Architecture: [ARCHITECTURE]
Files configured: X skills, Y agents, Z hooks
RTK: [installed and wired / not installed]
Skills disabled: [list or "none"]

Next steps:
- Run /sr to test the code review pipeline
- Run /ct to test task decomposition
- Edit .claude/skills/coding-conventions/SKILL.md to fine-tune conventions
```

## Re-running Setup

If the user runs `/setup` again on an already-configured repo:
1. Grep for `{{` in `.claude/` — if none found, the workflow is already configured
2. Ask: "This workflow is already configured. What would you like to do?"
   - "Reconfigure everything" — re-detect codebase, show current vs. new values, confirm changes, overwrite
   - "Update specific values" — ask which variables to change, edit only those files
   - "Cancel"

## Constraints

- NEVER delete user-customized content outside of `{{PLACEHOLDER}}` regions
- Always show what will change before writing
- All values are written directly into files — no intermediate config files
- Support monorepos by asking which workspace to configure (or configure all)
- If architecture is not detected, leave architecture sections with helpful generic content rather than empty placeholders
