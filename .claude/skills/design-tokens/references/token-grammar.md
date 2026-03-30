# Design Tokens Grammar Reference

**Version**: 1.3.0
**Owner**: Design Systems / Engineering
**Updated**: 2026-03-04

Extended reference for the Wythm design token system. For quick lookup, see SKILL.md.
This file covers the full creation workflow, naming edge cases, and examples.

---

## Table of Contents

1. [Primitive Layer Details](#1-primitive-layer-details)
2. [Semantic Token Naming Deep Dive](#2-semantic-token-naming-deep-dive)
3. [Token Creation Workflow](#3-token-creation-workflow)
4. [Examples](#4-examples)
5. [Anti-Patterns](#5-anti-patterns)
6. [Complete File Map](#6-complete-file-map)

---

## 1. Primitive Layer Details

Primitives live in `mobile-app/src/shared/theme/tokens/colors.primitives.ts`.
They are the only file where hex literals are allowed.

Current primitive groups:

| Group     | Keys                                         |
| --------- | -------------------------------------------- |
| `neutral` | `black`, `white`, `transparent`, `overlay`   |
| `gray`    | `100`, `200`, `300`, `400`, `500`, `600`     |
| `blue`    | `500`                                        |
| `red`     | `500`                                        |

When adding a new color (e.g. green for `success`), add a new group following this pattern:

```typescript
green: {
  500: "#34C759",
}
```

Use Apple HIG / iOS system colors as the default palette reference.

---

## 2. Semantic Token Naming Deep Dive

### The "on-" Prefix Rule

The `on-{sentiment}` pattern means "this element is placed ON a sentiment-colored background":

- `color.text.on-brand` → text color when placed on `color.background.brand`
- `color.icon.on-brand` → icon color when placed on `color.background.brand`
- `color.text.on-danger` → text color when placed on `color.background.danger`

**Constraint**: `on-default` is not allowed — use `base` instead. The reasoning is that "default" is implied; you only need the `on-` prefix for non-standard backgrounds.

### Field Tokens are Compound

Field tokens combine element + state in a single kebab-case variant because input fields have multiple visual parts (background, border, text, placeholder) that each need independent styling:

```
color.field.background              # base state
color.field.background-disabled     # disabled state
color.field.border                  # base state
color.field.border-danger           # error state
color.field.text                    # base state
color.field.text-disabled           # disabled state
color.field.placeholder             # placeholder text
```

### Special Background Variants

Two background variants exist for overlay/transparency needs:

- `color.background.transparent` → fully transparent (used for invisible touchable areas)
- `color.background.overlay` → semi-transparent black (used for modal backdrops, toasts)

These map to `colorPrimitives.neutral.transparent` and `colorPrimitives.neutral.overlay` respectively.

### Kebab-to-CamelCase Conversion

Design names use kebab-case, TypeScript object keys use camelCase:

| Dot Notation (design)         | TypeScript (code)                    |
| ----------------------------- | ------------------------------------ |
| `color.text.on-brand`         | `theme.colors.text.onBrand`          |
| `color.field.border-danger`   | `theme.colors.field.borderDanger`    |
| `color.field.text-disabled`   | `theme.colors.field.textDisabled`    |
| `color.background.transparent`| `theme.colors.background.transparent`|

Simple rule: split on `-`, capitalize subsequent words, join.

---

## 3. Token Creation Workflow

### Step 1: Check Existing Tokens

Search `colors.semantic.ts` for similar tokens. Prefer extending existing patterns over creating new categories.

### Step 2: Determine Layer

| Need                          | Action                              |
| ----------------------------- | ----------------------------------- |
| New raw color value           | Add to `colors.primitives.ts`       |
| New semantic meaning          | Add to `colors.semantic.ts`         |

Never put semantic meaning in the primitives file, and never put hex literals in the semantic file.

### Step 3: Choose Correct Category

Ask: "What element is this color applied to?"

- Text → `color.text.{variant}`
- Background/fill → `color.background.{variant}`
- Border/divider → `color.border.{variant}`
- Input field element → `color.field.{element}-{state?}`
- Icon → `color.icon.{variant}`

If none of these fit, you may be creating a new usage category (see Step 3b).

### Step 3b: Creating a New Usage Category

Only create a new category when existing categories genuinely can't represent the use case. A button's background is still `color.background.brand` — you don't need `color.button.background` unless the button needs tokens that semantically differ from generic backgrounds.

If a new category is justified (e.g., `color.button.*`), follow this pattern:

```
color.{category}.{element}
color.{category}.{element}-{state}
```

### Step 4: Name the Variant (kebab-case)

Follow existing patterns:
- Prominence: `base` → `secondary` → `tertiary`
- Sentiment: `brand`, `danger`, `success`, `warning`, `info`
- On-surface: `on-brand`, `on-danger`
- States (field only): `{element}-disabled`, `{element}-{sentiment}`

### Step 5: Add to Both Schemes

Add the token to BOTH `light` and `dark` objects in `colors.semantic.ts`. This is the most commonly missed step — a token in only one scheme causes a runtime crash in the other.

### Step 6: Update TypeScript Types

Add new keys (camelCase) to the `ThemeColors` type in `types.ts`. The type system ensures both schemes implement all tokens — if you miss a scheme, TypeScript will catch it.

---

## 4. Examples

### Adding a New Sentiment Color (success)

Design naming: `color.text.success`, `color.text.on-success`, `color.background.success`

```typescript
// 1. Add primitive (colors.primitives.ts)
green: {
  500: "#34C759",
}

// 2. Add semantic tokens (colors.semantic.ts) — light scheme
text: {
  // ...existing
  success: colorPrimitives.green[500],
  onSuccess: colorPrimitives.neutral.white,  // on-success → onSuccess
}
background: {
  // ...existing
  success: colorPrimitives.green[500],
}

// 3. Repeat for dark scheme (may use different primitive values)

// 4. Update ThemeColors in types.ts
text: {
  // ...existing
  success: string;
  onSuccess: string;
}
background: {
  // ...existing
  success: string;
}
```

### Adding a Component-Specific Token Group

Only when a component needs tokens that don't map to existing categories. Example: a card component with unique elevation semantics.

Design naming:
- `color.card.background`
- `color.card.background-elevated`
- `color.card.border`

```typescript
// colors.semantic.ts (camelCase keys)
card: {
  background: colorPrimitives.neutral.white,
  backgroundElevated: colorPrimitives.gray[100],
  border: colorPrimitives.gray[200],
}

// types.ts
card: {
  background: string;
  backgroundElevated: string;
  border: string;
}
```

---

## 5. Anti-Patterns

| Don't                                      | Do Instead                                     | Why |
| ------------------------------------------ | ---------------------------------------------- | --- |
| Use hex literals in components             | Use `theme.colors.{category}.{variant}`        | Tokens enable theming and dark mode |
| Import from `colors.ts`                    | Use `useTheme()` hook                          | Legacy file, not theme-aware |
| Use camelCase in token names               | Use kebab-case: `color.text.on-brand`          | Design ↔ code naming convention |
| Create `color.field.border.danger`         | Use flat: `color.field.border-danger`           | Max 2 levels deep |
| Add token only to light scheme             | Add to BOTH light and dark                     | Missing scheme = runtime crash |
| Use `on-default`                           | Use `base` variant                             | "Default" is implied |
| Duplicate primitive colors                 | Reference existing primitive                   | Single source of truth |
| Create `color.button.background`           | Use `color.background.brand` if semantically same | Avoid unnecessary categories |

---

## 6. Complete File Map

| File | Purpose | When to Edit |
| ---- | ------- | ------------ |
| `mobile-app/src/shared/theme/tokens/colors.primitives.ts` | Raw hex values | Adding a new color to the palette |
| `mobile-app/src/shared/theme/tokens/colors.semantic.ts` | Semantic tokens (light + dark) | Adding/modifying token meanings |
| `mobile-app/src/shared/theme/types.ts` | `ThemeColors`, `Theme`, `ColorScheme` | Adding new token keys |
| `mobile-app/src/shared/theme/createTheme.ts` | Builds Theme from scheme name | Rarely — only if theme structure changes |
| `mobile-app/src/shared/theme/useTheme.ts` | Hook for components | Rarely — already delegates to ThemeProvider |
| `mobile-app/src/shared/theme/colors.ts` | **LEGACY — do not modify** | Never — migrate away from this file |
