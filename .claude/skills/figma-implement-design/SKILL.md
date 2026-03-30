---
name: figma-implement-design
description: Translates Figma designs into production-ready React Native code for Wythm mobile app. Use when implementing UI from Figma files, when user mentions "implement design", "build from Figma", provides Figma URLs, or asks to build screens/components matching Figma specs. Requires Figma MCP server connection.
metadata:
  mcp-server: figma
---

# Implement Design (Wythm Mobile)

## Overview

Structured workflow for translating Figma designs into production-ready React Native code with pixel-perfect accuracy for the Wythm mobile app.

## Prerequisites

- Figma MCP server must be connected (verify `get_design_context` is available)
- User provides a Figma URL: `https://figma.com/design/:fileKey/:fileName?node-id=1-2`
- **MUST load the `design-tokens` skill** before writing any code — it defines the complete token naming grammar, creation workflow, and anti-patterns

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 1: Parse Figma URL

Extract from URL `https://figma.com/design/:fileKey/:fileName?node-id=1-2`:
- **File key**: segment after `/design/`
- **Node ID**: value of `node-id` param

### Step 2: Fetch Design Context

```
get_design_context(fileKey=":fileKey", nodeId="1-2")
```

If response is too large/truncated:
1. `get_metadata(fileKey, nodeId)` for high-level node map
2. Fetch individual child nodes with `get_design_context`

### Step 3: Capture Visual Reference

```
get_screenshot(fileKey=":fileKey", nodeId="1-2")
```

Keep this screenshot as source of truth throughout implementation.

### Step 4: Download Required Assets

- Use `localhost` sources from Figma MCP directly
- DO NOT import new icon packages — use assets from Figma payload
- DO NOT create placeholders if `localhost` source is provided
- Store assets in `mobile-app/assets/`

### Step 5: Translate to Wythm Conventions

**CRITICAL: Figma MCP outputs React + Tailwind. You MUST translate to React Native.**

#### Framework Translation

| Figma MCP Output | Wythm Convention |
|-------------------|------------------|
| `<div>` | `<View>` |
| `<span>`, `<p>`, `<h1>` | `<Text>` |
| `<img>` | `<Image>` from react-native |
| `<button>` | `<TouchableOpacity>` or `<Pressable>` |
| `<input>` | `<TextInput>` or `Input` from `@/shared/ui/common/Input` |
| `className="..."` | `style={[...]}` with theme tokens |
| Tailwind classes | StyleSheet or inline style objects |
| `onClick` | `onPress` |
| CSS Flexbox | React Native Flexbox (default `flexDirection: 'column'`) |

#### Color Token Mapping

**NEVER hardcode hex colors.** All colors MUST come from `theme.colors.*` via `useTheme()`.

**Full token reference**: See the `design-tokens` skill (`SKILL.md` for quick lookup, `references/token-grammar.md` for full grammar).

**Token structure**: `color.{usage}.{variant}` → in code: `theme.colors.{usage}.{variant}`

| Usage | Available Variants |
|-------|-------------------|
| `text` | `base`, `secondary`, `tertiary`, `brand`, `danger`, `onBrand`, `onDanger` |
| `background` | `base`, `secondary`, `brand`, `danger`, `transparent`, `overlay` |
| `border` | `base`, `secondary`, `danger` |
| `field` | `background`, `backgroundDisabled`, `border`, `borderDanger`, `placeholder`, `text`, `textDisabled` |
| `icon` | `base`, `brand`, `onBrand` |

Access via: `const { colors } = useTheme();`

#### When Figma Has a Color That Doesn't Exist in Tokens

If a Figma design uses a color that doesn't map to any existing token, **follow the token creation workflow** from the `design-tokens` skill:

1. Check if an existing token covers the use case (don't duplicate)
2. If new primitive needed → add to `colors.primitives.ts` (the ONLY place for hex literals)
3. Add semantic token to BOTH `light` and `dark` in `colors.semantic.ts`
4. Update `ThemeColors` type in `types.ts`
5. Use kebab-case naming: `color.{usage}.{variant}` (e.g., `color.text.success`, `color.background.warning`)

**IMPORTANT**: Prefer existing tokens over creating new ones. Only create when semantically distinct.

#### Component Reuse

**ALWAYS check existing components before creating new ones:**

| Component | Path | When to use |
|-----------|------|-------------|
| `Button` | `@/shared/ui/common/Button` | Any button (variants: primary, secondary, danger, ghost; sizes: small, medium, large) |
| `Input` | `@/shared/ui/common/Input` | Text inputs |
| `AppBottomSheet` | `@/shared/ui/common/AppBottomSheet` | Bottom sheets/modals |
| `Toast` | `@/shared/ui/Toast` | Notifications (via `useToast()`) |
| `LoadingView` | `@/shared/ui/common/loaders/LoadingView` | Loading states |
| `LanguageSelector` | `@/shared/ui/common/LanguageSelector` | Language picker |
| `ErrorBoundary` | `@/shared/ui/ErrorBoundary` | Error boundaries |

#### Architecture Rules

| Type | Location |
|------|----------|
| Screen components | `src/features/{feature}/screens/` |
| Feature-specific components | `src/features/{feature}/components/` |
| Shared UI primitives | `src/shared/ui/common/` |
| Hooks | `src/features/{feature}/hooks/` or `src/shared/hooks/` |

#### Styling Pattern

```typescript
// Use const object for static styles (NOT StyleSheet.create — see RN skill)
const styles = {
  container: {
    flex: 1,
  },
  title: {
    fontSize: 24,
    fontWeight: '600' as const,
  },
} as const;

// Apply theme colors dynamically
<View style={[styles.container, { backgroundColor: colors.background.base }]}>
  <Text style={[styles.title, { color: colors.text.base }]}>...</Text>
</View>
```

#### i18n

All user-facing strings MUST use Lingui:
```typescript
import { msg } from "@lingui/core/macro";
import { useTranslation } from "@/shared/i18n";

const { i18n } = useTranslation();
// Use: i18n._(msg`Your text here`)
```

### Step 6: Achieve 1:1 Visual Parity

- Match Figma design exactly using design tokens
- When project tokens differ from Figma values, prefer project tokens but adjust spacing/sizing to match visuals
- Follow WCAG accessibility requirements
- Ensure dark mode support (all tokens have light/dark variants)

### Step 7: Validate Against Figma

**Validation checklist:**
- [ ] Layout matches (spacing, alignment, sizing)
- [ ] Typography matches (font, size, weight, line height)
- [ ] Colors match via theme tokens (not hardcoded)
- [ ] Interactive states work (pressed, disabled, loading)
- [ ] Assets render correctly
- [ ] i18n strings wrapped with Lingui
- [ ] Dark mode works (uses semantic tokens, not hardcoded colors)
- [ ] Accessibility: touchable areas >= 44pt

## Common Issues

### Figma output is truncated
Use `get_metadata` first, then fetch specific nodes individually.

### React + Tailwind in output
This is expected. Translate to React Native + StyleSheet + theme tokens.

### Design token values differ from Figma
Prefer project tokens for consistency, adjust spacing/sizing to match visuals.

### Missing component variant
Extend existing component with new variant rather than creating duplicate.
