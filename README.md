# Wythm Claude Code Workflows

> Production-ready Claude Code workflows, hooks, agents, and skills for AI-assisted software development

**Follow us:** [@wythmapp](https://x.com/wythmapp) | [@MishkaKey](https://x.com/MishkaKey) | [@alexandrbasis](https://x.com/alexandrbasis)

---

This repository showcases the complete Claude Code setup used in the [Wythm](https://github.com/alexandrbasis/wythm) project — an AI-powered vocabulary learning platform. These workflows demonstrate advanced Claude Code patterns, multi-AI orchestration, and development automation.

## Highlights

- **20 specialized agents** for TDD, code review, task validation, and more
- **33 skills** covering the full dev lifecycle, cross-AI integrations (Gemini CLI, Codex CLI), and mobile development
- **Cross-AI Plan Review** — automatic Gemini verification of Claude's plans
- **Hookify rules system** — declarative behavior control with 9 rules
- **Linear integration** — seamless project management

---

## What's Inside

### Agents (20 total)

Specialized agents organized by function:

**Automation Agents** (`.claude/agents/automation-agents/`)
| Agent | Purpose |
|-------|---------|
| `automated-quality-gate` | Runs lint, types, tests before review |
| `developer-agent` | Universal agent for scoped work items |
| `integration-test-runner` | E2E and integration test execution |
| `senior-architecture-reviewer` | Reviews approach, architecture, TDD compliance |

**Code Review Agents** (`.claude/agents/code-review-agents/`)
| Agent | Focus |
|-------|-------|
| `code-quality-reviewer` | SOLID, maintainability, code smells |
| `code-simplifier` | Reduces complexity, simplifies code |
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

---

### Skills (33 total)

All workflows are powered by skills in `.claude/skills/`. Skills replace the previous slash commands system and provide richer, context-aware capabilities.

**Core Development Workflow**
| Skill | Command | Description |
|-------|---------|-------------|
| `ct` | `/ct` | Create task documentation (JTBD-based) |
| `si` | `/si` | Structured TDD implementation |
| `sr` | `/sr` | Comprehensive code review before PR |
| `prc` | `/prc` | Review and address PR comments |
| `fci` | `/fci` | Fix CI pipeline failures |
| `mm` | `/mm` | Create and deploy Prisma migrations |
| `ph` | `/ph` | Prepare handover documentation |

**Feature Discovery & Design**
| Skill | Command | Description |
|-------|---------|-------------|
| `nf` | `/nf` | New feature discovery interview |
| `brainstorm` | `/brainstorm` | Collaborative brainstorming on any topic |
| `product` | `/product` | Create product documentation (JTBD or PRD) |
| `vp` | `/vp` | Visual prototype playground for user approval |
| `design-exploration` | — | Pre-implementation design exploration (auto-triggered) |
| `design-tokens` | — | Design token naming and creation rules |

**Cross-AI Integrations**
| Skill | Command | Description |
|-------|---------|-------------|
| `gemini-cli` | — | Google Gemini CLI for web-grounded research, automation, image generation |
| `codex-cli` | — | OpenAI Codex CLI for second-opinion code review |
| `cc-linear` | — | Linear operations via Claude Code sessions |

**Code Quality & Analysis**
| Skill | Command | Description |
|-------|---------|-------------|
| `code-analysis` | `/code-analysis` | Deep code analysis with metrics and patterns |
| `dbg` | `/dbg` | Debug mode with runtime evidence and instrumentation |
| `web-design-guidelines` | — | Review UI code for Web Interface Guidelines compliance |
| `so` | `/so` | Analyze and improve existing skills |

**Research & Learning**
| Skill | Command | Description |
|-------|---------|-------------|
| `deep-research` | `/deep-research` | In-depth technical research with multiple sources |
| `sbs` | `/sbs` | Interactive step-by-step teaching |
| `docs-index` | — | Documentation index and reference lookup |

**Mobile Development**
| Skill | Command | Description |
|-------|---------|-------------|
| `react-native-expo-mobile` | — | 35+ rules for React Native/Expo best practices |

**Workflow Automation**
| Skill | Command | Description |
|-------|---------|-------------|
| `parallelization` | — | Orchestrate parallel implementation with scoped workers |
| `dopmwork` | — | Sync meeting discussions to Linear tasks |
| `rip` | `/rip` | Review implementation plan for business alignment |
| `hookify` | `/hookify` | Create hookify rules to prevent unwanted behaviors |
| `sync` | — | CLAUDE.md and agents.md file synchronization |
| `sync-public` | `/sync-public` | Sync config to this public repository |
| `udoc` | — | Documentation updates |

**Meta & Tooling**
| Skill | Command | Description |
|-------|---------|-------------|
| `skill-creator` | — | Guide for creating new skills |
| `template-skill` | — | Skill template for bootstrapping |

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

Additional hooks beyond hookify:
- **lint/** — Auto-lint on file write
- **sync/** — Auto-sync public repo, CLAUDE.md/agents sync
- **validation/** — Pre-commit validation

---

### Project Rules

Development guidelines in `.claude/rules/`:

| Rule | Scope |
|------|-------|
| `backend.md` | Backend architecture (NestJS, DDD, Clean Architecture) |
| `mobile-app.md` | Mobile app architecture (React Native, Expo) |
| `testing.md` | Testing standards and patterns |
| `git.md` | Git workflow and commit conventions |
| `tasks.md` | Task documentation workflow |

---

## Repository Structure

```
.claude/
├── agents/                       # 20 specialized agents
│   ├── automation-agents/        # Quality gates, orchestration
│   ├── code-review-agents/       # Quality, security, performance, simplification
│   ├── tasks-validators-agents/  # Task validation & splitting
│   ├── wf-agents/                # Workflow automation
│   ├── helpful-agents/           # Research helpers
│   └── hookify-agents/           # Rule creation helpers
├── hooks/
│   ├── hookify/                  # 9 declarative behavior rules + engine
│   ├── lint/                     # Auto-lint on write
│   ├── sync/                     # File synchronization hooks
│   └── validation/               # Pre-commit validation
├── skills/                       # 33 specialized capabilities
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

# Copy a skill (e.g., TDD implementation)
cp -r wythm-claude-workflows/.claude/skills/si \
   your-project/.claude/skills/

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
/ct (create task) → /si (implement with TDD) → automated-quality-gate → senior-architecture-reviewer
```

### 2. Multi-Agent Code Review
```
code-quality-reviewer + security-code-reviewer + performance-reviewer + test-coverage-reviewer + code-simplifier
```

### 3. Task-Driven Development (JTBD)
```
/ct (create task) → /si (implement) → /sr (review) → /prc (address comments) → merge
```

### 4. Cross-AI Orchestration
- Gemini CLI for plan review, web-grounded research, and image generation
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

And a React Native mobile app (planned) with:
- Expo + TypeScript
- Zustand state management
- Reanimated + Gesture Handler

---

## Security & Privacy

**Not included (sensitive):**
- `settings.local.json` — API keys and tokens
- `*.log` files
- MCP configs with credentials

**Safe to share:**
- All agents, skills, rules
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

**Last update:** 2026-02-11
