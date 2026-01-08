---
allowed-tools: Read, Write, Edit, Grep, Glob, AskUserQuestion, Task, Skill, WebSearch, WebFetch
argument-hint: [topic]
description: General brainstorming on any topic with collaborative exploration
---

# Brainstorming Session

## Objective
Conduct a collaborative brainstorming session on any topic - project-related or general - through natural dialogue, exploration of options, and structured capture of insights.

## Guidelines
- **Use `AskUserQuestion` tool for ALL clarifications** - provides interactive options for user to choose from
- Ask **non-obvious and thought-provoking** questions that challenge assumptions
- **Continue until the topic is fully explored** - don't stop early
- Present multiple perspectives and approaches
- Capture key insights and decisions in the brainstorm notes

## Workflow

### Step 1: Determine Scope
Ask the user whether the topic is:
- **Project-related**: Will explore codebase context first
- **General**: Skip context gathering, proceed to exploration

### Step 2: Context Phase (Project-Related Only)
If project-related, **invoke the `brainstorming` skill** which will:
- Use multiple Explore agents in parallel (Sonnet) to gather project context
- Identify relevant files, patterns, and existing implementations
- Build understanding of constraints and opportunities

### Step 3: Exploration Phase
For ALL topics (project-related or general):

**Understanding the Topic:**
- Ask clarifying questions (batch related questions)
- Prefer multiple choice when possible
- Focus on: goals, constraints, success criteria, concerns

**Exploring Approaches:**
- Propose 2-3 different perspectives or options
- Present trade-offs clearly
- Lead with your recommendation and reasoning

**Deep Exploration** - Ask non-obvious questions across categories:

**Practical & Implementation:**
- What could go wrong? Edge cases?
- What resources/dependencies are needed?
- How would this scale or evolve?

**Perspective & Assumptions:**
- What assumptions are we making?
- Who else is affected by this?
- What's the opposite approach look like?

**Impact & Value:**
- How do we measure success?
- What's the minimum viable version?
- What happens if we don't do this?

**Trade-offs:**
- Speed vs quality considerations
- Short-term vs long-term implications
- Complexity vs simplicity

**Presenting Ideas:**
- Break into 200-300 word sections
- Validate understanding after each section
- Be ready to pivot if direction changes

### Step 3.5: Research Phase (When Needed)
If exploration reveals topics requiring up-to-date data or external research:

**Quick Research:**
- Use `WebSearch` for current trends, market data, best practices
- Use `WebFetch` to pull specific documentation or articles

**Deep Research:**
- Launch `comprehensive-researcher` agent (Task tool) for topics requiring:
  - Multiple sources and cross-verification
  - Industry benchmarks or competitive analysis
  - Technical documentation deep-dives
  - Structured research reports with citations
- **Parallel research**: Launch multiple researcher agents simultaneously for different topics
  - No limits on concurrent agents - spin up as many as needed
  - Example: Research "competitor pricing models" AND "industry UX patterns" in parallel
  - Collect and synthesize findings once all agents complete

**Launch research proactively when:**
- Topic requires current or up-to-date information
- Market trends, competitor analysis, or industry standards are relevant
- Technical decisions benefit from external validation
- Exploring unfamiliar domains or technologies
- Knowledge gaps are identified during exploration

**No permission needed** - launch research agents proactively when the conversation reveals a need. Inform user what's being researched and continue the brainstorming while agents work in background.

### Step 4: Capture Phase
After exploration is complete:

1. **Create brainstorm notes**: `docs/brainstorming/brainstorm-YYYY-MM-DD-[topic-slug].md`
2. **Use template**: `docs/product-docs/templates/brainstorm-template.md`
3. **Include**:
   - Topic overview and type (project/general)
   - Key questions explored
   - Options discussed with pros/cons
   - Conclusions and insights
   - Action items (if any)
4. **Present summary** to user for confirmation

## Output
`docs/brainstorming/brainstorm-YYYY-MM-DD-[topic-slug].md`
