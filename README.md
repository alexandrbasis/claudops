# Wythm Claude Code Workflows

> Production-ready Claude Code workflows, hooks, agents, and commands for AI-assisted software development

This repository showcases the complete Claude Code setup used in the [Wythm](https://github.com/alexandrbasis/wythm) project - an AI-powered vocabulary learning platform. These workflows demonstrate advanced Claude Code usage patterns, custom automation, and development best practices.

## What's Inside

### Custom Agents (25+)

Specialized agents for different development tasks:

**Automation Agents** (`.claude/agents/automation-agents/`)
- `test-developer.md` - TDD test specialist, writes failing tests first
- `implementation-developer.md` - Implements code to make tests pass
- `automated-quality-gate.md` - Runs automated quality checks
- `developer-agent.md` - Universal developer for scoped work items
- `integration-test-runner.md` - E2E and integration test execution
- `code-review-orchestrator.md` - Orchestrates multi-agent code review
- `senior-approach-reviewer.md` - Reviews implementation approach and TDD compliance

**Code Review Agents** (`.claude/agents/code-review-agents/`)
- `code-quality-reviewer.md` - Code quality and maintainability
- `documentation-accuracy-reviewer.md` - Documentation completeness
- `performance-reviewer.md` - Performance optimization
- `security-code-reviewer.md` - Security vulnerability scanning
- `test-coverage-reviewer.md` - Test coverage analysis

**Task Validators** (`.claude/agents/tasks-validators-agents/`)
- `plan-reviewer.md` - Technical plan validation
- `task-pm-validator.md` - Project management validation
- `task-splitter.md` - Task breakdown evaluation
- `task-decomposer.md` - Creates phase structure for split tasks
- `task-validator.md` - Pre-flight validation before implementation
- `architect-review.md` - Architecture consistency review

**Workflow Agents** (`.claude/agents/wf-agents/`)
- `changelog-generator.md` - Automated changelog creation
- `create-pr-agent.md` - Pull request automation with Linear integration
- `docs-updater.md` - Documentation synchronization

**Helper Agents** (`.claude/agents/helpful-agents/`)
- `comprehensive-researcher.md` - In-depth research tasks

**Hookify Agents** (`.claude/agents/hookify-agents/`)
- `conversation-analyzer.md` - Analyzes conversations for rule creation

**Specialized Agents**
- `nextjs-architecture-expert.md` - Next.js best practices and optimization

### Slash Commands

Custom commands for streamlined workflows (`.claude/commands/`):

**Development Workflow**
- `/ct` - Create task documentation (JTBD-based)
- `/cb` - Create branch from Linear task
- `/si` - Structured TDD implementation
- `/dev` - Full development orchestrator (implement → review → PR)
- `/nf` - New feature discovery interview
- `/ph` - Prepare handover documentation

**Code Review & Quality**
- `/sr` - Comprehensive code review before PR
- `/prc` - Review and address PR comments
- `/fci` - Fix CI pipeline failures

**Database & Migrations**
- `/mm` - Create and deploy Prisma migrations

**Merge & Deploy**
- `/mp` - Merge approved PR and archive task

**General**
- `/brainstorm` - General brainstorming on any topic

**Other Commands** (`.claude/commands/other/`)
- `/other:product` - Create product documentation (JTBD or PRD)
- `/other:dopmwork` - Sync meeting discussions to Linear tasks
- `/other:onboard` - Junior developer onboarding guide
- `/other:rip` - Review implementation plan for business alignment
- `/other:sbs` - Interactive teaching guide
- `/other:hookify` - Create hookify rules
- `/other:sync-public` - Sync config to public repository

### Skills

Specialized capabilities (`.claude/skills/`):

- `cc-linear/` - Linear operations via Claude Code sessions
- `brainstorming/` - Creative exploration before implementation
- `code-analysis/` - Deep code analysis with metrics
- `context-loader/` - Load project context before implementation
- `deep-research/` - In-depth technical research
- `parallelization/` - Orchestrate parallel implementation
- `gemini-cli/` - Google Gemini CLI integration
- `hookify/` - Create rules to prevent unwanted behaviors

### Hooks & Rules

Event-driven automation (`.claude/hooks/`):

**Hookify System** (`.claude/hooks/hookify/`)
Declarative rules for Claude Code behavior:
- `dangerous-rm.local.md` - Prevent dangerous rm commands
- `pre-commit.local.md` - Pre-commit validation
- `schema-change.local.md` - Database schema change alerts
- `db-danger.local.md` - Dangerous database operations
- `arch-violation.local.md` - Architecture violation detection
- `test-silent.local.md` - Silent test execution
- `no-console.local.md` - Prevent console.log in production
- `interface-naming.local.md` - Interface naming conventions
- `first-commit-reminder.local.md` - First commit guidelines

**Project Rules** (`.claude/rules/`)
- `backend.md` - Backend development guidelines
- `testing.md` - Testing standards
- `git.md` - Git workflow rules
- `research.md` - Research guidelines (Exa + Ref MCP)
- `sync.md` - Sync configuration

### MCP Servers

Model Context Protocol integrations (`.claude/mcp/`):
- Linear integration for issue management
- Exa integration for code-aware search
- IDE integration for diagnostics

## Repository Structure

```
.claude/
├── agents/                       # 25+ specialized agents
│   ├── automation-agents/        # TDD, quality gates, orchestration
│   ├── code-review-agents/       # Quality & security reviewers
│   ├── tasks-validators-agents/  # Task validation & splitting
│   ├── wf-agents/                # Workflow automation
│   ├── helpful-agents/           # Research helpers
│   └── hookify-agents/           # Rule creation helpers
├── commands/                     # Slash commands
│   └── other/                    # Additional commands
├── hooks/                        # Event-driven automation
│   └── hookify/                  # Declarative behavior rules
├── skills/                       # Specialized capabilities
├── rules/                        # Project-wide rules
├── mcp/                          # MCP server configs
└── scripts/                      # Utility scripts

docs/
└── setup-guide.md                # Detailed setup instructions
```

## How to Use These Workflows

### Option 1: Full Setup (Recommended)
1. Clone this repository
2. Copy `.claude/` directory to your project root
3. Review and customize configuration for your needs
4. Install dependencies (see [Setup Guide](docs/setup-guide.md))
5. Configure MCP servers and hooks

### Option 2: Cherry-Pick Components
Pick specific agents, commands, or hooks:

```bash
# Copy specific agent
cp wythm-claude-workflows/.claude/agents/automation-agents/developer-agent.md \
   your-project/.claude/agents/

# Copy specific command
cp wythm-claude-workflows/.claude/commands/ct.md \
   your-project/.claude/commands/

# Copy hookify rules
cp -r wythm-claude-workflows/.claude/hooks/hookify \
   your-project/.claude/hooks/
```

### Option 3: Learn and Adapt
Study the patterns and create your own:
- Read agent prompts to understand specialization patterns
- Examine hookify rules for behavior control
- Review commands for workflow optimization

## Key Features

### 1. TDD-Driven Development Pipeline
Multi-agent system for test-driven development:
- `test-developer` - Writes failing tests first
- `implementation-developer` - Makes tests pass
- `automated-quality-gate` - Validates quality
- `senior-approach-reviewer` - Reviews approach

### 2. Automated Code Review Pipeline
Multi-agent review system covering:
- Architecture patterns (SOLID, DDD)
- Security vulnerabilities (OWASP Top 10)
- Performance optimization
- Test coverage
- Documentation accuracy

### 3. Task-Driven Development
JTBD (Jobs-to-be-Done) based workflow:
- `/ct` - Create comprehensive task documentation
- `/cb` - Create feature branch from task
- `/si` - Structured TDD implementation
- `/dev` - Full orchestration (implement → review → PR)
- Automatic traceability and audit trail

### 4. Linear Integration
Seamless project management via `cc-linear` skill:
- Create/update issues from Claude
- Link PRs to Linear tasks
- Sync meeting notes to tasks
- Automated changelog generation

### 5. Hookify Rules System
Declarative behavior control:
- Prevent dangerous operations
- Enforce coding standards
- Alert on schema changes
- Maintain architecture boundaries

## Technology Stack

**Backend Project Context:**
- NestJS + TypeScript
- PostgreSQL + Prisma ORM
- Domain-Driven Design (DDD)
- Clean Architecture

**Development Tools:**
- Claude Code (AI-assisted development)
- Linear (Project management)
- GitHub Actions (CI/CD)
- MCP Servers (Integrations)

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Node.js 18+ (for project context)
- Git configured
- GitHub CLI (`gh`) installed
- Linear API access (optional, for full workflow)

## Configuration

### Required Environment Variables

Create `.claude/settings.local.json` (not tracked in this repo):

```json
{
  "hooks": {
    "PostToolUse": [...],
    "PreToolUse": [...]
  },
  "env": {
    "PUBLIC_REPO_PATH": "/path/to/wythm-claude-workflows",
    "LINEAR_API_KEY": "your-linear-key"
  }
}
```

See [docs/setup-guide.md](docs/setup-guide.md) for detailed configuration.

## Security & Privacy

**What's NOT Included:**
- `settings.local.json` - Contains sensitive tokens and IDs
- `history.jsonl` - Conversation history
- `*.log` files - May contain sensitive paths
- Runtime directories (`session-env/`, `todos/`, etc.)
- MCP configs with API keys

**Safe to Share:**
- Agent definitions
- Command templates
- Hook scripts and rules
- MCP configurations (anonymized)
- Skills and workflows

## Real-World Usage

This setup powers the development of [Wythm](https://github.com/alexandrbasis/wythm), a production NestJS application with:
- 25+ custom agents for specialized tasks
- TDD-driven development workflow
- Automated task creation and PR workflows
- Linear integration for project tracking
- Multi-stage code review pipeline
- JTBD-based feature development
- Hookify rules for behavior control

## Contributing

Found a better pattern? Have suggestions?
- Open an issue with your idea
- Share your own Claude Code workflows
- Contribute improvements via PR

## License

MIT License - See [LICENSE](LICENSE) for details

## Links & Resources

- **Main Project:** [Wythm Repository](https://github.com/alexandrbasis/wythm)
- **Claude Code Docs:** [Official Documentation](https://docs.anthropic.com/en/docs/claude-code)
- **Linear:** [Project Management Tool](https://linear.app)

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) - AI-assisted software development by Anthropic.

---

**Auto-synced from main repository** | Last update: 2026-01-08
