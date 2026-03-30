---
name: nf
description: >-
  Conduct in-depth feature discovery interview to explore, challenge, and document a new feature.
  Use when asked to 'detail a feature', 'explore a new feature', 'feature discovery',
  'interview about feature', 'spec out a feature', 'design a feature',
  'think through a feature', 'let's spec this out', 'deep dive on a feature',
  'what should we consider for [feature]', or 'discover [feature-name]'.
  NOT for quick brainstorming (use /brainstorm),
  NOT for PRD/JTBD docs (use /product), NOT for implementation tasks (use /ct).
argument-hint: [feature-name]
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion, Task, Skill
---

# New Feature Discovery

> **Announcement**: Begin with: "I'm using the **nf** skill for feature discovery."

## Objective
Conduct a comprehensive interview to fully understand and document a new feature through collaborative exploration and structured challenge, then create a formal specification.

## Guidelines
- **Use `AskUserQuestion` tool for ALL clarifications** — provides interactive options for user to choose from
- **Never assume behavior**: if any behavior is unclear/ambiguous (UX flow, edge cases, error handling, states), ask the user to define expected behavior (preferred via `AskUserQuestion`)
- Ask non-obvious and thought-provoking questions
- Actively challenge assumptions; do not be a yes-boy. Grill.
- Offer alternatives, shortcuts, and "go deeper" paths
- Continue until the feature is fully understood
- Document everything in the specification file

## Workflow

### Argument Validation

**If no `[feature-name]` argument is provided:**
1. Use `AskUserQuestion`: "What feature would you like to explore?"
   - Search `tasks/` and recent Linear issues for planned/in-progress features as options
   - Include a free-text "Describe a new feature" option
2. Derive the feature-name slug from the user's response

### Resume Check

Before starting a new discovery, check for an existing draft:
1. Search for `tasks/task-*-[feature-name]/discovery-[feature-name].md`
2. If found with `Status: Draft`:
   - Read the existing document
   - `AskUserQuestion`: "Found existing draft discovery for [feature-name]."
     Options: "Continue from where we left off" / "Start fresh (overwrite)" / "Review and revise existing"
   - **Continue**: identify which sections are complete vs template placeholders, pick up from the first incomplete section
   - **Start fresh**: proceed with full workflow
   - **Review**: present the existing document for user feedback, then revise

### Mobile-app Skill Gate (MANDATORY when feature touches `mobile-app/`)

**Trigger:** If the feature will **create or modify any code under `mobile-app/`** (new screens/components, animations, lists, navigation, Expo APIs).

**MANDATORY steps (do BEFORE writing recommendations/implementation details in the discovery/spec):**
- Read the skill docs:
  - `.claude/skills/react-native-expo-mobile/SKILL.md`
  - `.claude/skills/react-native-expo-mobile/AGENTS.md`
- Explicitly state in the discovery/spec that the skill was read and will be applied in implementation.
- Extract the relevant rules for this feature area (minimum: Core Rendering; plus Animation/List Performance/React Compiler/UI as applicable) and record them under a short section like: "Skill Compliance: react-native-expo-mobile".

### Step 1: Context Gathering & Design Exploration

**Invoke the `design-exploration` skill** — it handles both codebase scanning and design proposal in one pass:
- Launches 1-3 parallel Explore agents (Sonnet) to gather codebase context
- Asks questions to refine the idea (batches related questions)
- Proposes 2-3 different approaches with trade-offs
- Presents design incrementally (200-300 word sections) for validation

**Before invoking**, pass the feature context:
- Feature name and initial description from user
- Known constraints or requirements mentioned so far
- Specific areas to explore (e.g., "focus on backend/src/application/sessions/")

**After design-exploration returns**, synthesize:
- Key codebase findings (existing patterns, data models, integration points)
- Initial design approach with alternatives considered
- Questions raised during exploration

**Checkpoint:** Present findings summary and initial approach. `AskUserQuestion`: "Does this direction look right?" Options: "Continue with this approach" / "Explore a different direction" / "I have corrections"

### Step 2: External Research (If Needed)

When you need current information, best practices, or technical research:

- **Quick lookups**: Use Exa MCP tools directly
- **In-depth research**: Spawn `comprehensive-researcher` subagent via Task tool for complex topics requiring multiple sources and cross-verification

Topics to research:
- Industry best practices for the feature type
- Competitor implementations and patterns
- API/library capabilities and limitations
- Security considerations and compliance requirements

### Step 3: Deep-Dive Questions

Ask additional **non-obvious** questions to build the complete picture before challenging it:

**Technical Implementation:**
- Edge cases and failure scenarios
- Performance implications at scale
- Integration points with existing systems
- Security and privacy implications

**UI/UX:**
- User mental models and expectations
- Error states and recovery flows
- Accessibility considerations

**Business & Product:**
- Success metrics and how to measure them
- MVP vs future scope boundaries
- Potential abuse scenarios

**Tradeoffs:**
- Complexity vs flexibility
- Development speed vs technical debt
- Short-term wins vs long-term maintainability

Continue deep-dive until user confirms all questions are addressed.

### Step 4: "Grill Me" Challenge Round

Now that the full picture is gathered, **invoke the `/grill-me` skill** to run a structured challenge on the feature design.

**Before invoking**, summarize the current state for the grill session:
- Feature name and description
- Design approach chosen in Steps 1-3
- Key assumptions and decisions made so far
- Any areas of uncertainty or risk already identified

**Invoke:** `Skill("grill-me")` — this will interview the user relentlessly about the design, walking down each branch of the decision tree and resolving dependencies one-by-one.

**After the grill session completes:**
- Incorporate all findings and decisions back into the feature understanding
- Update any design choices that changed during the challenge

**Checkpoint:** `AskUserQuestion`: "How should we proceed?" Options: "Proceed to specification" / "Revisit design based on findings" / "Cut scope based on grill findings"

### Step 5: Specification Writing

After interview completion:

1. **Read template**: Read `docs/product-docs/templates/discovery-template.md` to load the structure
2. **Create task directory**: `tasks/task-YYYY-MM-DD-[feature-name]/`
3. **Write specification** following the template structure
   - Output file: `discovery-[feature-name].md`
4. **Present summary** to user for confirmation

**If design exploration reveals the feature is not viable**: Document the reasons in a brief `discovery-[feature-name]-rejected.md` with rationale, and stop here.

### Step 6: Cross-AI Validation

Invoke `/codex-cli`, `/gemini-cli`, and `/cursor-cli` skills in parallel.
Format output per `docs/product-docs/templates/cross-ai-protocol.md` (comparison table, validation, verdict).

- **FOCUS**: Discovery document review as senior product analyst — completeness, consistency, clarity, feasibility, scope, no conflicts with existing architecture
- **FILE_REFS**: `discovery-[feature-name].md` + relevant codebase paths
- **OUTPUT**: Append "Cross-AI Validation: PASSED/FAILED" with consolidated verdict

**If validation fails**: Present valid findings via `AskUserQuestion`: "Revise discovery doc" / "Override and proceed" / "Abandon feature".

**Skip conditions**: No CLI available, or user explicitly skips.

## Output
`tasks/task-YYYY-MM-DD-[feature-name]/discovery-[feature-name].md`

## Handoff — Next Steps

After discovery is complete, present to the user:

```
Discovery complete for [feature-name]:
- Document: tasks/task-YYYY-MM-DD-[feature-name]/discovery-[feature-name].md

Next steps:
→ Visualize the design: /vp [feature-name]
→ Skip to tech planning: /ct [feature-name]
→ Create product docs: /product jtbd [feature-name]
```
