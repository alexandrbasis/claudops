# Backend Playground Template

Prompt template for invoking the `playground` skill for backend/architecture tasks.

## Template

```
Use the playground skill to create a code-map playground for [FEATURE_NAME].

**Context from discovery:** [PASTE TECHNICAL CONSIDERATIONS SECTION]

**Requirements:**
- SVG-based architecture diagram with Mermaid.js
  - Prefer C4 diagram type for DDD layer visualization
  - Use flowcharts for process flows
- Show DDD layers: Domain, Application, Infrastructure
- Click-to-comment enabled on all components
- Connection types: data-flow (blue), dependency (gray), event (red)

**Components to visualize:**
- Entities: [From discovery]
- Use Cases: [From discovery]
- Repositories: [From discovery]
- API Endpoints: [From discovery]

**Presets:**
1. Full System — All layers visible
2. Domain Focus — Entities and domain services only
3. API Flow — Request path through layers

**Output file:** [TASK_DIRECTORY]/playground-[feature-name].html
```

## Quick Prototype Variant

When running without a full discovery document (quick prototype mode):

```
Use the playground skill to create a code-map playground for [FEATURE_NAME].

**Feature description:** [USER'S BRIEF DESCRIPTION]

**Requirements:**
- SVG-based architecture diagram with Mermaid.js (C4 or flowchart)
- Show DDD layers: Domain, Application, Infrastructure
- Click-to-comment enabled
- Label as "Exploratory Prototype" in the header

**Known components:**
[From quick interview answers]

**Output file:** [TASK_DIRECTORY]/playground-[feature-name].html
```
