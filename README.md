# Wythm Claude Code Workflows

> Production-ready Claude Code workflows, hooks, agents, and commands for AI-assisted software development

**Follow us:** [@wythmapp](https://x.com/wythmapp) | [@MishkaKey](https://x.com/MishkaKey) | [@alexandrbasis](https://x.com/alexandrbasis)

---

This repository showcases the complete Claude Code setup used in the [Wythm](https://github.com/alexandrbasis/wythm) project — an AI-powered vocabulary learning platform. These workflows demonstrate advanced Claude Code patterns, multi-AI orchestration, and development automation.

## Highlights

- **24 specialized agents** for TDD, code review, task validation, and more
- **14 slash commands** + 7 utility commands for streamlined workflows
- **9 skills** including cross-AI integrations (Gemini CLI, Codex CLI)
- **Cross-AI Plan Review** — automatic Gemini verification of Claude's plans
- **Hookify rules system** — declarative behavior control
- **Linear integration** — seamless project management

---

## What's Inside

### Agents (24 total)

Specialized agents organized by function:

**Automation Agents** (`.claude/agents/automation-agents/`)
| Agent | Purpose |
|-------|---------|
| `test-developer` | TDD specialist — writes failing tests first |
| `implementation-developer` | Makes tests pass with clean code |
| `automated-quality-gate` | Runs lint, types, tests before review |
| `developer-agent` | Universal agent for scoped work items |
| `integration-test-runner` | E2E and integration test execution |
| `code-review-orchestrator` | Orchestrates multi-agent code review |
| `senior-approach-reviewer` | Reviews approach, TDD compliance, solution quality |

**Code Review Agents** (`.claude/agents/code-review-agents/`)
| Agent | Focus |
|-------|-------|
| `code-quality-reviewer` | SOLID, maintainability, code smells |
| `security-code-reviewer` | OWASP Top 10, injection, auth issues |
| `performance-reviewer` | N+1 queries, caching, optimization |
| `test-coverage-reviewer` | Coverage gaps, test quality |
| `documentation-accuracy-reviewer` | Docs completeness and accuracy |

**Task Validators** (`.claude/agents/tasks-validators-agents/`)
| Agent | Purpose |
|-------|---------|
| `plan-reviewer` | Technical plan validation |
| `task-pm-validator` | PM validation before code review |
| `task-splitter` | Evaluates if task needs breakdown |
| `task-decomposer` | Creates phase structure for split tasks |
| `task-validator` | Pre-flight validation before implementation |
| `architect-review` | Architecture consistency review |

**Workflow Agents** (`.claude/agents/wf-agents/`)
| Agent | Purpose |
|-------|---------|
| `changelog-generator` | Creates changelog from task docs |
| `create-pr-agent` | PR automation with Linear integration |
| `docs-updater` | Documentation synchronization |

**Other Agents**
| Agent | Purpose |
|-------|---------|
| `comprehensive-researcher` | In-depth research tasks |
| `conversation-analyzer` | Analyzes conversations for hookify rules |
| `nextjs-architecture-expert` | Next.js best practices and optimization |

---

### Slash Commands

**Core Development Workflow** (`.claude/commands/`)

| Command | Description |
|---------|-------------|
| `/ct` | Create task documentation (JTBD-based) |
| `/cb` | Create branch from Linear task |
| `/si` | Structured TDD implementation |
| `/dev` | Full orchestrator: implement → review → PR |
| `/nf` | New feature discovery interview |
| `/ph` | Prepare handover documentation |
| `/sr` | Comprehensive code review before PR |
| `/prc` | Review and address PR comments |
| `/fci` | Fix CI pipeline failures |
| `/mm` | Create and deploy Prisma migrations |
| `/mp` | Merge approved PR and archive task |
| `/brainstorm` | General brainstorming on any topic |

**Utility Commands** (`.claude/commands/other/`)

| Command | Description |
|---------|-------------|
| `/other:product` | Create product documentation (JTBD or PRD) |
| `/other:dopmwork` | Sync meeting discussions to Linear tasks |
| `/other:onboard` | Junior developer onboarding guide |
| `/other:rip` | Review implementation plan for business alignment |
| `/other:sbs` | Interactive step-by-step teaching |
| `/other:hookify` | Create hookify rules |
| `/other:sync-public` | Sync config to this public repository |

---

### Skills (9 total)

Advanced capabilities in `.claude/skills/`:

| Skill | Description |
|-------|-------------|
| `gemini-cli` | Google Gemini CLI for web-grounded research, automation, cross-AI validation |
| `codex-cli` | OpenAI Codex CLI for second-opinion code review and approach validation |
| `cc-linear` | Linear operations via Claude Code sessions (create issues, update status) |
| `context-loader` | Load project context before implementation |
| `parallelization` | Orchestrate parallel implementation with scoped workers |
| `brainstorming` | Creative exploration before implementation |
| `code-analysis` | Deep code analysis with metrics and patterns |
| `deep-research` | In-depth technical research with multiple sources |
| `hookify` | Create rules to prevent unwanted behaviors |

---

### Cross-AI Plan Review

Automatic Gemini CLI verification when Claude exits Plan Mode:

```
Claude creates plan → ExitPlanMode → PostToolUse hook →
Gemini CLI reviews (~30 sec) → Review appended to plan file
```

**What Gemini checks:**
- Security issues (auth, validation, injection)
- Architecture violations (DDD, Clean Architecture)
- Performance problems (N+1, missing indexes)
- Missing edge cases and error handling
- Testability concerns

**Configuration** (`.claude/settings.json`):
```json
{
  "plansDirectory": "./tasks/plans",
  "hooks": {
    "PostToolUse": [{
      "matcher": "ExitPlanMode",
      "hooks": [{
        "type": "command",
        "command": "$CLAUDE_PROJECT_DIR/.claude/scripts/review-plan-gemini.sh",
        "timeout": 300
      }]
    }]
  }
}
```

See [docs/dev-workflow/gemini-plan-review-hook.md](docs/dev-workflow/gemini-plan-review-hook.md) for full documentation.

---

### Hookify Rules System

Declarative behavior control in `.claude/hooks/hookify/rules/`:

| Rule | Purpose |
|------|---------|
| `dangerous-rm.local.md` | Block dangerous rm commands |
| `pre-commit.local.md` | Pre-commit validation |
| `schema-change.local.md` | Alert on database schema changes |
| `db-danger.local.md` | Block dangerous database operations |
| `arch-violation.local.md` | Detect architecture violations |
| `test-silent.local.md` | Prefer silent test execution |
| `no-console.local.md` | Prevent console.log in production |
| `interface-naming.local.md` | Enforce interface naming conventions |
| `first-commit-reminder.local.md` | First commit guidelines |

---

### Project Rules

Development guidelines in `.claude/rules/`:

| Rule | Scope |
|------|-------|
| `backend.md` | Backend architecture (NestJS, DDD, Clean Architecture) |
| `testing.md` | Testing standards and patterns |
| `git.md` | Git workflow and commit conventions |
| `research.md` | Research guidelines (Exa + Ref MCP) |
| `sync.md` | File synchronization rules |

---

## Repository Structure

```
.claude/
├── agents/                       # 24 specialized agents
│   ├── automation-agents/        # TDD, quality gates, orchestration
│   ├── code-review-agents/       # Quality, security, performance
│   ├── tasks-validators-agents/  # Task validation & splitting
│   ├── wf-agents/                # Workflow automation
│   ├── helpful-agents/           # Research helpers
│   └── hookify-agents/           # Rule creation helpers
├── commands/                     # 14 slash commands
│   └── other/                    # 7 utility commands
├── hooks/
│   └── hookify/                  # 9 declarative behavior rules
├── skills/                       # 9 specialized capabilities
├── rules/                        # 5 project-wide rules
├── scripts/                      # Automation scripts
│   ├── review-plan-gemini.sh     # Cross-AI plan review
│   └── sync-to-public.sh         # Repo sync utility
├── mcp/                          # MCP server configs
└── settings.json                 # Hooks & plansDirectory config

docs/
├── setup-guide.md                # Detailed setup instructions
└── dev-workflow/
    └── gemini-plan-review-hook.md  # Cross-AI plan review docs
```

---

## How to Use

### Option 1: Full Setup
```bash
git clone https://github.com/alexandrbasis/wythm-claude-workflows.git
cp -r wythm-claude-workflows/.claude your-project/
# Review and customize for your needs
```

### Option 2: Cherry-Pick Components
```bash
# Copy specific agent
cp wythm-claude-workflows/.claude/agents/automation-agents/developer-agent.md \
   your-project/.claude/agents/

# Copy Gemini plan review
cp wythm-claude-workflows/.claude/scripts/review-plan-gemini.sh \
   your-project/.claude/scripts/

# Copy hookify rules
cp -r wythm-claude-workflows/.claude/hooks/hookify \
   your-project/.claude/hooks/
```

### Option 3: Use as Reference
Study the patterns and create your own workflows based on these examples.

---

## Key Features

### 1. TDD-Driven Development Pipeline
```
test-developer → implementation-developer → automated-quality-gate → senior-approach-reviewer
```

### 2. Multi-Agent Code Review
```
code-quality-reviewer + security-code-reviewer + performance-reviewer + test-coverage-reviewer
```

### 3. Task-Driven Development (JTBD)
```
/ct (create task) → /cb (create branch) → /si (implement) → /sr (review) → /mp (merge)
```

### 4. Cross-AI Orchestration
- Gemini CLI for plan review and web-grounded research
- Codex CLI for second-opinion code review
- Multiple AI perspectives on critical decisions

### 5. Linear Integration
- Create/update issues from Claude
- Link PRs to Linear tasks
- Sync meeting notes to tasks
- Automated changelog generation

---

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Node.js 18+
- Git configured
- GitHub CLI (`gh`) installed
- Optional: Gemini CLI (`npm i -g @google/gemini-cli`)
- Optional: Linear API access

---

## Technology Context

This setup powers a NestJS backend with:
- TypeScript + Prisma + PostgreSQL (Supabase)
- Domain-Driven Design (DDD)
- Clean Architecture
- Comprehensive testing (Jest)

---

## Security & Privacy

**Not included (sensitive):**
- `settings.local.json` — API keys and tokens
- `*.log` files
- MCP configs with credentials

**Safe to share:**
- All agents, commands, skills
- Hook scripts and rules
- Configuration templates

---

## Contributing

Found a better pattern? Have suggestions?
- Open an issue with your idea
- Share your own workflows
- Contribute improvements via PR

---

## License

MIT License — See [LICENSE](LICENSE) for details

---

## Links

- **Main Project:** [Wythm Repository](https://github.com/alexandrbasis/wythm)
- **Claude Code Docs:** [Official Documentation](https://docs.anthropic.com/en/docs/claude-code)
- **Linear:** [Project Management](https://linear.app)

---

Built with [Claude Code](https://claude.com/claude-code) by Anthropic

**Last update:** 2026-01-22
