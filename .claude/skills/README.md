# Wythm Skills

## Core Workflow

Feature lifecycle: discovery → implementation → review → merge.

| Skill | Purpose |
|-------|---------|
| [/nf](./nf) | New feature discovery (interview) |
| [/vp](./vp) | Visual prototype playground |
| [/ct](./ct) | Create technical task (TDD) |
| [/cb](./cb) | Create git branch |
| [/si](./si) | Start implementation |
| [/ph](./ph) | Prepare handover |
| [/sr](./sr) | Code review |
| [/prc](./prc) | Address PR comments |

### Workflow Patterns

- **Standard**: `/ct` → `/cb` → `/si` → `/sr`
- **Full Product**: `/nf` → `/vp` → `/ct` → `/cb` → `/si` → `/sr`
- **With Handoff**: `/ct` → `/cb` → `/si` → `/ph` → `/si` → `/sr`

## Supporting Workflow

| Skill | Purpose |
|-------|---------|
| [/udoc](./udoc) | Update docs & changelog from task |
| [/dbg](./dbg) | Debug mode with instrumentation |
| [/fci](./fci) | Fix CI pipeline failures |
| [/mm](./mm) | Create Prisma migrations |
| [/dopmwork](./dopmwork) | Sync meetings to Linear |
| [/sync-public](./sync-public) | Sync config to public repo |

## Product & Planning

| Skill | Purpose |
|-------|---------|
| [/product](./product) | Create JTBD or PRD |
| [/rip](./rip) | Review implementation plan |

## Exploration & Research

| Skill | Purpose | Runs in |
|-------|---------|---------|
| [/brainstorm](./brainstorm) | General brainstorming | inline |
| [/design-exploration](./design-exploration) | Design exploration | subagent (Explore) |
| [/code-analysis](./code-analysis) | Architecture review | subagent (Explore) |
| [/deep-research](./deep-research) | Technical research | subagent |

## Teaching & Onboarding

| Skill | Purpose |
|-------|---------|
| [/onboard](./onboard) | Junior developer onboarding |
| [/sbs](./sbs) | Step-by-step teaching |

## Framework References

| Skill | Purpose |
|-------|---------|
| [/react-native-expo-mobile](./react-native-expo-mobile) | React Native + Expo best practices |
| [/vercel-react-best-practices](./vercel-react-best-practices) | React/Next.js optimization (Vercel) |
| [/design-tokens](./design-tokens) | Design token naming rules |
| [/web-design-guidelines](./web-design-guidelines) | UI/UX review patterns |

## Integrations

| Skill | Purpose |
|-------|---------|
| [/cc-linear](./cc-linear) | Linear MCP operations |
| [/codex-cli](./codex-cli) | OpenAI Codex cross-validation |
| [/gemini-cli](./gemini-cli) | Google Gemini integration |

## Meta

| Skill | Purpose |
|-------|---------|
| [/hookify](./hookify) | Manage hookify rules |
| [/parallelization](./parallelization) | Parallel worker orchestration |
| [/skill-creator](./skill-creator) | Create new skills |
| [/so](./so) | Analyze and optimize existing skills |
| [workflow-reference](./workflow-reference) | Workflow index (Claude-only, not user-invocable) |
| [docs-index](./docs-index) | Documentation index (auto-triggered) |
| [sync](./sync) | CLAUDE.md/agents.md sync rules (auto-triggered) |
| [template-skill](./template-skill) | Empty skill template |
