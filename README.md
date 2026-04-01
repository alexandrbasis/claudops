# claudops

> Claude Code best practices — skills, agents, hooks, and workflows

**Author:** [@alexandrbasis](https://x.com/alexandrbasis) | [@MishkaKey](https://x.com/MishkaKey)

---

A curated collection of production-tested Claude Code configurations. Agents, skills, hooks, and rules that turn Claude Code into a full development pipeline — from feature discovery to code review and deployment.

## Highlights

- **20 specialized agents** — TDD, code review, task validation, research
- **33+ skills** — full dev lifecycle, cross-AI integrations (Gemini CLI, Codex CLI)
- **Cross-AI Plan Review** — automatic Gemini verification of Claude's plans
- **Hookify rules system** — declarative behavior control
- **Linear integration** — project management from your terminal

---

## What's Inside

### Agents (20 total)

**Automation** (`.claude/agents/automation-agents/`)
| Agent | Purpose |
|-------|---------|
| `automated-quality-gate` | Runs lint, types, tests before review |
| `developer-agent` | Universal agent for scoped work items |
| `integration-test-runner` | E2E and integration test execution |
| `senior-architecture-reviewer` | Reviews approach, architecture, TDD compliance |

**Code Review** (`.claude/agents/code-review-agents/`)
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

**Workflow** (`.claude/agents/wf-agents/`)
| Agent | Purpose |
|-------|---------|
| `changelog-generator` | Creates changelog from task docs |
| `create-pr-agent` | PR automation with Linear integration |
| `docs-updater` | Documentation synchronization |

**Other**
| Agent | Purpose |
|-------|---------|
| `comprehensive-researcher` | In-depth research tasks |
| `conversation-analyzer` | Analyzes conversations for hookify rules |

---

### Skills (33+)

**Core Development Workflow**
| Skill | Command | Description |
|-------|---------|-------------|
| `ct` | `/ct` | Create task documentation (JTBD-based) |
| `si` | `/si` | Structured TDD implementation |
| `sr` | `/sr` | Comprehensive code review before PR |
| `prc` | `/prc` | Review and address PR comments |
| `ph` | `/ph` | Prepare handover documentation |

**Feature Discovery & Design**
| Skill | Command | Description |
|-------|---------|-------------|
| `nf` | `/nf` | New feature discovery interview |
| `brainstorm` | `/brainstorm` | Collaborative brainstorming on any topic |
| `product` | `/product` | Create product documentation (JTBD or PRD) |
| `vp` | `/vp` | Visual prototype playground |
| `design-exploration` | — | Pre-implementation design exploration |

**Cross-AI Integrations**
| Skill | Command | Description |
|-------|---------|-------------|
| `gemini-cli` | — | Google Gemini CLI for web-grounded research & image generation |
| `codex-cli` | — | OpenAI Codex CLI for second-opinion code review |
| `cc-linear` | — | Linear operations via Claude Code sessions |

**Code Quality & Analysis**
| Skill | Command | Description |
|-------|---------|-------------|
| `code-analysis` | `/code-analysis` | Deep code analysis with metrics and patterns |
| `dbg` | `/dbg` | Debug mode with runtime evidence |
| `so` | `/so` | Analyze and improve existing skills |

**Research & Learning**
| Skill | Command | Description |
|-------|---------|-------------|
| `deep-research` | `/deep-research` | In-depth technical research with multiple sources |
| `sbs` | `/sbs` | Interactive step-by-step teaching |

**Workflow Automation**
| Skill | Command | Description |
|-------|---------|-------------|
| `parallelization` | — | Parallel implementation with scoped workers |
| `rip` | `/rip` | Review implementation plan for business alignment |
| `hookify` | `/hookify` | Create hookify rules to prevent unwanted behaviors |
| `sync` | — | CLAUDE.md and agents.md synchronization |

---

### Cross-AI Plan Review

Automatic Gemini CLI verification when Claude exits Plan Mode:

```
Claude creates plan → ExitPlanMode → PostToolUse hook →
Gemini CLI reviews (~30 sec) → Review appended to plan file
```

**What Gemini checks:**
- Security issues (auth, validation, injection)
- Architecture violations
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

---

### Hookify Rules System

Declarative behavior control in `.claude/hooks/hookify/rules/`:

| Rule | Purpose |
|------|---------|
| `dangerous-rm` | Block dangerous rm commands |
| `pre-commit` | Pre-commit validation |
| `schema-change` | Alert on database schema changes |
| `db-danger` | Block dangerous database operations |
| `arch-violation` | Detect architecture violations |
| `test-silent` | Prefer silent test execution |
| `no-console` | Prevent console.log in production |
| `interface-naming` | Enforce interface naming conventions |
| `first-commit-reminder` | First commit guidelines |

Additional hooks: auto-lint on file write, file synchronization, pre-commit validation.

---

## Repository Structure

```
.claude/
├── agents/                       # 20 specialized agents
│   ├── automation-agents/        # Quality gates, orchestration
│   ├── code-review-agents/       # Quality, security, performance
│   ├── tasks-validators-agents/  # Task validation & splitting
│   ├── wf-agents/                # Workflow automation
│   ├── helpful-agents/           # Research helpers
│   └── hookify-agents/           # Rule creation helpers
├── hooks/
│   ├── hookify/                  # Declarative behavior rules + engine
│   ├── lint/                     # Auto-lint on write
│   ├── sync/                     # File synchronization
│   └── validation/               # Pre-commit validation
├── skills/                       # 33+ specialized capabilities
├── rules/                        # Project-wide rules
├── scripts/                      # Automation scripts
│   └── review-plan-gemini.sh     # Cross-AI plan review
├── mcp/                          # MCP server configs
└── settings.json                 # Hooks & plansDirectory config

docs/
├── setup-guide.md                # Detailed setup instructions
└── dev-workflow/
    └── gemini-plan-review-hook.md
```

---

## How to Use

### Full Setup
```bash
git clone https://github.com/alexandrbasis/claudops.git
cp -r claudops/.claude your-project/
# Review and customize for your needs
```

### Cherry-Pick Components
```bash
# Copy specific agent
cp claudops/.claude/agents/automation-agents/developer-agent.md \
   your-project/.claude/agents/

# Copy a skill (e.g., TDD implementation)
cp -r claudops/.claude/skills/si \
   your-project/.claude/skills/

# Copy Gemini plan review
cp claudops/.claude/scripts/review-plan-gemini.sh \
   your-project/.claude/scripts/

# Copy hookify rules
cp -r claudops/.claude/hooks/hookify \
   your-project/.claude/hooks/
```

### Use as Reference
Study the patterns and create your own workflows.

---

## Key Workflows

### TDD Pipeline
```
/ct (create task) → /si (implement with TDD) → automated-quality-gate → senior-architecture-reviewer
```

### Multi-Agent Code Review
```
code-quality + security + performance + test-coverage + code-simplifier
```

### Task-Driven Development (JTBD)
```
/ct → /si → /sr → /prc → merge
```

### Cross-AI Orchestration
- Gemini CLI for plan review, web-grounded research, and image generation
- Codex CLI for second-opinion code review
- Multiple AI perspectives on critical decisions

---

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Git + GitHub CLI (`gh`)
- Optional: Gemini CLI (`npm i -g @google/gemini-cli`)
- Optional: Linear API access

---

## Security & Privacy

**Not included (sensitive):** `settings.local.json`, API keys, MCP credentials, log files

**Safe to share:** All agents, skills, rules, hook scripts, configuration templates

---

## Contributing

Found a better pattern? Have suggestions?
- Open an issue with your idea
- Share your own workflows
- Contribute improvements via PR

---

## License

MIT — See [LICENSE](LICENSE)

---

Built with [Claude Code](https://claude.ai/code) by Anthropic
