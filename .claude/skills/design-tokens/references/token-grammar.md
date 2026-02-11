# Design Tokens Grammar Reference

**Version**: 1.2.0
**Owner**: Design Systems / Engineering
**Date**: 2026-02-06

This document defines the naming and creation system for design tokens in Wythm.

---

## 1. Token Architecture

Wythm uses a **two-layer token system**:

### Layer 1: Primitives (`colors.primitives.ts`)

Raw color values. **Only place where hex literals are allowed.**

```typescript
colorPrimitives.neutral.black   // "#000000"
colorPrimitives.gray[500]       // "#999999"
colorPrimitives.blue[500]       // "#007AFF"
```

### Layer 2: Semantic Tokens (`colors.semantic.ts`)

Theme-aware tokens organized by **usage category**.

```typescript
semanticColorsByScheme.light.text.base      // → colorPrimitives.neutral.black
semanticColorsByScheme.dark.text.base       // → colorPrimitives.neutral.white
```

---

## 2. Semantic Token Structure (Dot Notation)

Tokens are named using **dot notation with kebab-case**:

```
color.{usage}.{variant}
```

### Current Usage Categories

| Usage        | Purpose                          |
| ------------ | -------------------------------- |
| `text`       | Text colors                      |
| `background` | Background fills                 |
| `border`     | Border/divider colors            |
| `field`      | Input field specific tokens      |
| `icon`       | Icon colors                      |

### Variant Naming Conventions (kebab-case)

| Variant Pattern        | Meaning                                    | Example                    |
| ---------------------- | ------------------------------------------ | -------------------------- |
| `base`                 | Default/primary variant                    | `color.text.base`          |
| `secondary`            | Less prominent                             | `color.text.secondary`     |
| `tertiary`             | Least prominent                            | `color.text.tertiary`      |
| `brand`                | Brand color applied                        | `color.text.brand`         |
| `danger`               | Error/destructive state                    | `color.text.danger`        |
| `on-brand`             | Used ON brand-colored background           | `color.text.on-brand`      |
| `on-danger`            | Used ON danger-colored background          | `color.text.on-danger`     |
| `{usage}-disabled`     | Disabled state (for field tokens)          | `color.field.text-disabled`|
| `{usage}-{sentiment}`  | Combined usage+sentiment (for field only)  | `color.field.border-danger`|

---

## 3. Naming Rules (MUST)

### 3.1 Dot Notation with Kebab-Case (Design)

All token names use **dot notation with kebab-case**:

```
# CORRECT (design naming)
color.text.on-brand
color.field.background-disabled
color.field.border-danger

# WRONG
color.text.onBrand          # no camelCase
color.field.background_disabled  # no snake_case
colorTextOnBrand            # no flat camelCase
```

### 3.2 TypeScript Mapping (Code)

In TypeScript code, dot notation maps to nested objects with camelCase keys:

| Dot Notation (design)         | TypeScript (code)                    |
| ----------------------------- | ------------------------------------ |
| `color.text.base`             | `theme.colors.text.base`             |
| `color.text.on-brand`         | `theme.colors.text.onBrand`          |
| `color.field.border-danger`   | `theme.colors.field.borderDanger`    |
| `color.field.text-disabled`   | `theme.colors.field.textDisabled`    |
| `color.background.secondary`  | `theme.colors.background.secondary`  |

**Conversion rule**: kebab-case → camelCase when writing TypeScript.

### 3.3 "on-" Prefix Rule

The `on-{sentiment}` pattern means "this element is placed ON a sentiment-colored background":

- `color.text.on-brand` → text color when placed on `color.background.brand`
- `color.icon.on-brand` → icon color when placed on `color.background.brand`

**Constraint**: `on-default` is not allowed (use `base` instead).

### 3.4 Field Tokens are Compound

Field tokens combine element + state in kebab-case:

```
color.field.background          # base state
color.field.background-disabled # disabled state
color.field.border              # base state
color.field.border-danger       # error state
color.field.text                # base state
color.field.text-disabled       # disabled state
color.field.placeholder         # placeholder text
```

---

## 4. Token Creation Workflow

When adding a new token:

### Step 1: Check Existing Tokens

Search `colors.semantic.ts` for similar tokens. Prefer extending existing patterns.

### Step 2: Determine Layer

| Need                          | Action                              |
| ----------------------------- | ----------------------------------- |
| New raw color value           | Add to `colors.primitives.ts`       |
| New semantic meaning          | Add to `colors.semantic.ts`         |

### Step 3: Choose Correct Category

Ask: "What element is this color applied to?"

- Text → `color.text.{variant}`
- Background/fill → `color.background.{variant}`
- Border/divider → `color.border.{variant}`
- Input field element → `color.field.{element}-{state?}`
- Icon → `color.icon.{variant}`

### Step 4: Name the Variant (kebab-case)

Follow existing patterns:
- Prominence: `base` → `secondary` → `tertiary`
- Sentiment: `brand`, `danger`, `success`, `warning`, `info`
- On-surface: `on-brand`, `on-danger`
- States (field only): `{element}-disabled`, `{element}-{sentiment}`

### Step 5: Add to Both Schemes

**CRITICAL**: Add token to BOTH `light` and `dark` schemes in `colors.semantic.ts`.

### Step 6: Update TypeScript Types

Add new keys (camelCase) to `ThemeColors` type in `types.ts`.

---

## 5. File Locations

| File                                              | Purpose                    |
| ------------------------------------------------- | -------------------------- |
| `src/shared/theme/tokens/colors.primitives.ts`    | Raw hex color values       |
| `src/shared/theme/tokens/colors.semantic.ts`      | Theme-aware semantic tokens|
| `src/shared/theme/types.ts`                       | TypeScript type definitions|
| `src/shared/theme/createTheme.ts`                 | Theme creation logic       |

---

## 6. Examples

### Adding a New Sentiment Color (success)

Design naming: `color.text.success`, `color.text.on-success`, `color.background.success`

```typescript
// 1. Add primitive (if needed)
// colors.primitives.ts
green: {
  500: "#34C759",
}

// 2. Add semantic tokens (use camelCase in code)
// colors.semantic.ts - light
text: {
  // ...existing
  success: colorPrimitives.green[500],
  onSuccess: colorPrimitives.neutral.white,  // on-success → onSuccess
}
background: {
  // ...existing
  success: colorPrimitives.green[500],
}

// 3. Repeat for dark scheme
```

### Adding a New Component Context (button)

If button needs special tokens not covered by existing categories:

Design naming:
- `color.button.background`
- `color.button.background-hover`
- `color.button.background-disabled`
- `color.button.text`
- `color.button.text-disabled`

```typescript
// colors.semantic.ts (use camelCase)
button: {
  background: colorPrimitives.blue[500],
  backgroundHover: colorPrimitives.blue[600],     // background-hover
  backgroundDisabled: colorPrimitives.gray[300],  // background-disabled
  text: colorPrimitives.neutral.white,
  textDisabled: colorPrimitives.gray[500],        // text-disabled
}
```

---

## 7. Anti-Patterns

| Don't                                      | Do Instead                                     |
| ------------------------------------------ | ---------------------------------------------- |
| Use hex literals in components             | Use `theme.colors.{category}.{variant}`        |
| Use camelCase in token names               | Use kebab-case: `color.text.on-brand`          |
| Create `color.field.border.danger`         | Use flat: `color.field.border-danger`          |
| Add token only to light scheme             | Add to BOTH light and dark                     |
| Use `on-default`                           | Use `base` variant                             |
| Duplicate primitive colors                 | Reference existing primitive                   |
| Create deeply nested tokens                | Keep max 2 levels: `color.{usage}.{variant}`   |
