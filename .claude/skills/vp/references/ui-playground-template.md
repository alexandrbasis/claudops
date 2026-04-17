# UI Playground Template

Prompt template for invoking the `playground` skill for UI-facing tasks.

## Template

```
Use the playground skill to create a design playground for [FEATURE_NAME].

**Context from discovery:**
- Feature Overview: [PASTE FEATURE OVERVIEW]
- How It Works: [PASTE HOW IT WORKS]
- In Scope: [PASTE IN SCOPE]
- Key Requirements: [PASTE KEY REQUIREMENTS]
- Constraints: [PASTE CONSTRAINTS]
- Optional Context: [PASTE USAGE CONTEXT OR CHOSEN DIRECTION IF RELEVANT]

**Project UI Context:**
- Product or project name: [PROJECT_NAME]
- Platform: [mobile app | responsive web | desktop | tablet | component playground]
- Existing design system or component library: [NAME or "none documented"]
- Theme, tokens, or style-guide sources: [PATHS, FILES, OR NOTES]
- Existing components or screens to visually align with: [PATHS, LINKS, OR NOTES]
- Brand cues or visual tone: [e.g. minimal, playful, editorial, enterprise]
- **Chosen visual direction:** [ONE OF THE 3–4 DIRECTIONS THE USER PICKED]
  (If the user has not chosen, stop and surface 3–4 one-line direction
  rationales for them to pick from before generating HTML.)

**Playground Requirements:**
- Create an interactive playground with controls, preview, and implementation notes.
- Match documented project conventions where they exist.
- Use a viewport or frame appropriate to the platform:
  - Mobile: representative phone frame
  - Web/Desktop: responsive or desktop canvas
  - Component-only: focused component stage without unnecessary app chrome
- Include realistic states and interactions rather than a single static screen.
- Label implementation assumptions clearly when the discovery doc leaves room for interpretation.

**Scenarios to include:**
1. Happy Path: [Main flow from discovery]
   For each screen in the happy path, include the four required states
   (error, constraint, empty, success) — do not apply them only to the
   first screen.
2. Empty / Loading / Error States: [If applicable]
3. Edge Cases: [From discovery]
4. Key Variants / Breakpoints / Modes: [If applicable]

**Output file:** [TASK_DIRECTORY]/playground-[feature-name].html
```

## Quick Prototype Variant

When running without a full discovery document (quick prototype mode), use this lighter template:

```
Use the playground skill to create a design playground for [FEATURE_NAME].

**Feature description:** [USER'S BRIEF DESCRIPTION]

**Project UI Context:**
- Platform: [mobile app | responsive web | desktop | tablet | component playground]
- Existing design system or component library: [NAME or "none documented"]
- Brand cues or visual tone: [if known]
- Existing screens or components to align with: [if known]

**Requirements:**
- Create an interactive playground with controls, preview, and implementation notes.
- Use a viewport or frame appropriate to the platform.
- **Chosen visual direction:** [ONE OF THE 3–4 DIRECTIONS THE USER PICKED]
  (If the user has not chosen, stop and surface 3–4 one-line direction
  rationales for them to pick from before generating HTML.)
- Label as "Exploratory Prototype" in the header.

**Key screens/interactions:**
[From quick interview answers]

**Output file:** [TASK_DIRECTORY]/playground-[feature-name].html
```
