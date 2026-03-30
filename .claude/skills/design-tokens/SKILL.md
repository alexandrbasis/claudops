---
name: design-tokens
description: |
  Design tokens naming, creation, and consumption rules for Wythm mobile app (color tokens).

  **Use this skill when:**
  - Creating or renaming color tokens
  - Replacing hardcoded hex colors or styles with theme tokens
  - Reviewing PRs where styles, colors, or theme files are touched
  - Adding new UI components that need theming or dark mode support
  - Working with any file in `mobile-app/src/shared/theme/`
  - Seeing hex color literals (e.g. `#007AFF`, `#FF3B30`) in component code

  Even if the user doesn't say "design tokens" explicitly, use this skill whenever colors, theming, or dark mode come up in mobile-app work.
---

# Design Tokens

> **Announcement**: Begin with: "I'm using the **design-tokens** skill for design token management."

Ensures consistent token naming and usage across Wythm's mobile app.

## Data Flow

```
colors.primitives.ts → colors.semantic.ts → createTheme() → ThemeProvider → useTheme() → component
       (hex)             (light/dark)          (Theme obj)     (context)      (hook)       (styles)
```

## Token Architecture

Two-layer system — primitives hold raw values, semantic tokens give them meaning:

1. **Primitives** (`colors.primitives.ts`) — Raw hex values. The ONLY place for color literals.
2. **Semantic Tokens** (`colors.semantic.ts`) — Theme-aware tokens organized by usage, referencing primitives.

Components never touch either file directly. They consume tokens via `useTheme()`.

## Quick Reference

### Token Structure (dot notation)

```
color.{usage}.{variant}
```

In code: `theme.colors.{usage}.{variant}`

| Usage        | Examples                                                         |
| ------------ | ---------------------------------------------------------------- |
| `text`       | `color.text.base`, `color.text.secondary`, `color.text.on-brand` |
| `background` | `color.background.base`, `color.background.brand`, `color.background.overlay` |
| `border`     | `color.border.base`, `color.border.secondary`, `color.border.danger` |
| `field`      | `color.field.background`, `color.field.border-danger`, `color.field.placeholder` |
| `icon`       | `color.icon.base`, `color.icon.brand`, `color.icon.on-brand`    |

### Variant Patterns

| Pattern              | Meaning                              |
| -------------------- | ------------------------------------ |
| `base`               | Default variant                      |
| `secondary`          | Less prominent                       |
| `tertiary`           | Least prominent                      |
| `brand`              | Brand color applied                  |
| `danger`             | Error/destructive state              |
| `on-brand`           | Used ON brand-colored background     |
| `on-danger`          | Used ON danger-colored background    |
| `transparent`        | Fully transparent (background only)  |
| `overlay`            | Semi-transparent overlay (background only) |
| `{element}-disabled` | Disabled state (field only)          |

## Using Tokens in Components

```typescript
import { useTheme } from "@/shared/theme/useTheme";

function MyComponent() {
  const { colors } = useTheme();

  return (
    <View style={{ backgroundColor: colors.background.base }}>
      <Text style={{ color: colors.text.base }}>Hello</Text>
      <Icon color={colors.icon.brand} />
    </View>
  );
}
```

## Legacy File Warning

`mobile-app/src/shared/theme/colors.ts` is a **legacy file** with a flat color pattern (`ColorsLight.text`, `ColorsDark.tint`). Do NOT import from it. Always use the semantic token system via `useTheme()`. When you encounter components importing from `colors.ts`, migrate them to `useTheme()`.

## Critical Rules

### DO

- Use `theme.colors.{usage}.{variant}` via `useTheme()` in all components
- Add new tokens to BOTH `light` and `dark` schemes in `colors.semantic.ts`
- Follow dot notation naming: `color.{usage}.{variant}`
- Use kebab-case for multi-word variants: `on-brand`, `border-danger`
- Check for existing tokens before creating new ones

### DON'T

- Import from legacy `colors.ts` — use `useTheme()` instead
- Use hex literals outside `colors.primitives.ts`
- Create deeply nested tokens (max 2 levels: `color.{usage}.{variant}`)
- Use `on-default` (use `base` instead)
- Add tokens to only one color scheme
- Use camelCase in token names (use kebab-case: `on-brand` not `onBrand`)

## Dot Notation to Code Mapping

| Dot notation (design)       | TypeScript (code)                  |
| --------------------------- | ---------------------------------- |
| `color.text.base`           | `theme.colors.text.base`           |
| `color.text.on-brand`       | `theme.colors.text.onBrand`        |
| `color.field.border-danger` | `theme.colors.field.borderDanger`  |
| `color.background.overlay`  | `theme.colors.background.overlay`  |

**Rule**: Dot notation uses kebab-case, TypeScript uses camelCase for object keys.

## File Locations

| File | Purpose |
| ---- | ------- |
| `mobile-app/src/shared/theme/tokens/colors.primitives.ts` | Raw hex colors (only place for literals) |
| `mobile-app/src/shared/theme/tokens/colors.semantic.ts` | Semantic tokens (light + dark) |
| `mobile-app/src/shared/theme/types.ts` | `ThemeColors`, `Theme`, `ColorScheme` types |
| `mobile-app/src/shared/theme/createTheme.ts` | Builds `Theme` object from scheme |
| `mobile-app/src/shared/theme/useTheme.ts` | `useTheme()` hook for components |
| `mobile-app/src/shared/theme/colors.ts` | **LEGACY — do not use** |

## Checklist for New Tokens

1. [ ] Does a similar token already exist? (search `colors.semantic.ts`)
2. [ ] Is a new raw value needed? (add to `colors.primitives.ts`)
3. [ ] Added to correct usage category?
4. [ ] Uses dot notation with kebab-case? (`color.text.on-brand`)
5. [ ] Added to BOTH light and dark schemes?
6. [ ] Updated `ThemeColors` type in `types.ts` if new keys added?
7. [ ] Component uses `useTheme()` — not hex literal, not legacy `colors.ts`?

## When to Read Full Reference

Load `references/token-grammar.md` when:

- Creating a new usage category (beyond text/background/border/field/icon)
- Adding a new sentiment color (success, warning, info)
- Understanding the complete token creation workflow with examples
- Adding component-specific token groups (e.g., button, card)
- Reviewing naming convention edge cases
