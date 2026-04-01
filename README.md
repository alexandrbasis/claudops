# claudops

> Claude Code best practices — skills, agents, hooks, and workflows

**Author:** [@alexandrbasis](https://x.com/alexandrbasis) | [@MishkaKey](https://x.com/MishkaKey)

---

A curated collection of production-tested Claude Code configurations: agents, skills, and hooks for a full development pipeline — from feature discovery to code review.

## Highlights

- **17 specialized agents** — TDD, code review, task validation, research
- **26 skills** — full dev lifecycle and cross-AI helpers (Gemini CLI, Codex CLI, Cursor CLI)
- **Cross-AI plan review** — optional Gemini verification of plans (see `review-plan-gemini.sh`)
- **Hooks** — lint on write, sync, validation, guards, metrics
- **Linear integration** — project management from your terminal (`cc-linear` skill)

---

## What's Inside

### Agents (17)

**Automation** (`.claude/agents/automation-agents/`)
| Agent | Purpose |
|-------|---------|
| `automated-quality-gate` | Runs lint, types, tests before review |
| `developer-agent` | Universal agent for scoped work items |
| `integration-test-runner` | E2E and integration test execution |
| `senior-architecture-reviewer` | Reviews approach, architecture, TDD compliance |

**Code review** (`.claude/agents/code-review-agents/`)
| Agent | Focus |
|-------|-------|
| `code-quality-reviewer` | SOLID, maintainability, code smells |
| `documentation-accuracy-reviewer` | Docs completeness and accuracy |
| `performance-reviewer` | N+1 queries, caching, optimization |
| `security-code-reviewer` | OWASP Top 10, injection, auth issues |
| `spec-compliance-reviewer` | Spec and requirements alignment |
| `test-coverage-reviewer` | Coverage gaps, test quality |

**Task validators** (`.claude/agents/tasks-validators-agents/`)
| Agent | Purpose |
|-------|---------|
| `plan-reviewer` | Technical plan validation |
| `task-splitter` | Evaluates if a task needs breakdown |
| `task-decomposer` | Phase structure for split tasks |

**Workflow** (`.claude/agents/wf-agents/`)
| Agent | Purpose |
|-------|---------|
| `changelog-generator` | Changelog from task docs |
| `create-pr-agent` | PR automation with Linear integration |
| `docs-updater` | Documentation synchronization |

**Helpers** (`.claude/agents/helpful-agents/`)
| Agent | Purpose |
|-------|---------|
| `comprehensive-researcher` | In-depth research tasks |

---

### Skills (26)

See [`.claude/skills/README.md`](.claude/skills/README.md) for the full index. Summary:

| Area | Examples |
|------|----------|
| Core workflow | `ct`, `si`, `si-quick`, `sr`, `prc`, `ph`, `nf`, `product`, `vp`, `blueprint` |
| Discovery & design | `brainstorm`, `design-exploration`, `analyze`, `grill-me`, `rip` |
| Quality & debugging | `code-analysis`, `dbg`, `fci` |
| Cross-AI | `gemini-cli`, `codex-cli`, `cursor-cli` |
| Integrations & meta | `cc-linear`, `deep-research`, `parallelization`, `sbs`, `update-docs` |

---

### Cross-AI plan review

Optional flow when Gemini CLI is configured — see `.claude/scripts/review-plan-gemini.sh` and hook wiring in `.claude/settings.json`.

**What Gemini can check:** security, architecture, performance, edge cases, testability.

---

### Hooks

Python/shell hooks under `.claude/hooks/` — lint on write, agent sync, pre-commit checks, bash/file guards, cost tracking, etc. Details: [`.claude/hooks/README.md`](.claude/hooks/README.md).

---

## Repository structure

```
.claude/
├── agents/           # Specialized subagents
├── docs/
│   ├── templates/    # PRD, JTBD, decomposition, review templates
│   └── references/
├── hooks/            # Claude Code hooks (see hooks/README.md)
├── scripts/          # e.g. review-plan-gemini.sh, linear-api.sh
├── skills/           # Slash-command skills (see skills/README.md)
└── settings.json     # Hook and project settings (copy & customize)

workflow-visualization.html   # Interactive workflow map (open in browser)
```

---

## How to use

### Full setup
```bash
git clone https://github.com/alexandrbasis/claudops.git
cp -r claudops/.claude your-project/
# Add workflow-visualization.html or templates if you want them at repo root
# Review settings.json and hooks for your environment
```

### Cherry-pick
```bash
cp -r claudops/.claude/skills/si your-project/.claude/skills/
cp claudops/.claude/scripts/review-plan-gemini.sh your-project/.claude/scripts/
```

### As reference
Study the patterns and adapt them to your own workflows.

---

## Key workflows

### TDD pipeline
```
/ct → /si → automated-quality-gate → senior-architecture-reviewer
```

### Multi-agent code review
```
code-quality + security + performance + test-coverage + documentation
```

### Task-driven flow
```
/ct → /si → /sr → /prc → merge
```

### Cross-AI
- Gemini CLI — plan review, web-grounded research
- Codex / Cursor CLI — second-opinion review (see `cross-ai-protocol` template)

---

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- Git + GitHub CLI (`gh`)
- Optional: Gemini CLI (`npm i -g @google/gemini-cli`)
- Optional: Linear API access

---

## Security & privacy

**Not included (sensitive):** `settings.local.json`, API keys, MCP credentials, log files

**Safe to share:** Agents, skills, hook scripts, and templates in this repo (exclude local overrides)

---

## Contributing

Found a better pattern? Have suggestions?
- Open an issue with your idea
- Share your own workflows
- Contribute improvements via PR

---

## License

MIT — See [LICENSE](LICENSE)
