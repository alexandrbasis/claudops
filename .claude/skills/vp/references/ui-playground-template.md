# UI Playground Template

Prompt template for invoking the `playground` skill for UI-facing tasks.

## Template

```
Use the playground skill to create a design playground for [FEATURE_NAME].

**Context from discovery:** [PASTE UI/UX SPECIFICATIONS SECTION]

**Requirements:**
- Use Wythm design system tokens (see "Design Token Quick Reference" below)
- Phone frame: 375x780px with notch
- Three-column layout: Controls | Preview | Implementation Notes

**Wythm Design Token Quick Reference:**
Token system: two-layer (primitives → semantic)
- Brand: `color.background.brand` / `color.text.on-brand`
- Backgrounds: `color.background.base`, `color.background.secondary` (cards/surfaces)
- Text: `color.text.base` (primary), `color.text.secondary` (muted), `color.text.tertiary`
- Borders: `color.border.base`, `color.border.secondary`
- Fields: `color.field.background`, `color.field.border-danger` (errors)
- Icons: `color.icon.base`, `color.icon.brand`, `color.icon.on-brand`
- Overlay: `color.background.overlay` (modal backdrops)
For the full palette, read `.claude/skills/design-tokens/SKILL.md`.

**Scenarios to include:**
1. Happy Path: [Main flow from discovery]
2. Edge Cases: [From discovery edge cases section]
3. Error States: [From error handling section]
4. Empty State: [If applicable]

**Output file:** [TASK_DIRECTORY]/playground-[feature-name].html
```

## Quick Prototype Variant

When running without a full discovery document (quick prototype mode), use this lighter template:

```
Use the playground skill to create a design playground for [FEATURE_NAME].

**Feature description:** [USER'S BRIEF DESCRIPTION]

**Requirements:**
- Use Wythm design system tokens (see quick reference above)
- Phone frame: 375x780px with notch
- Three-column layout: Controls | Preview | Implementation Notes
- Label as "Exploratory Prototype" in the header

**Key screens/interactions:**
[From quick interview answers]

**Output file:** [TASK_DIRECTORY]/playground-[feature-name].html
```
