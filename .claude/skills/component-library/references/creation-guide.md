# Component Creation Guide

Step-by-step guide for creating new reusable components in Wythm mobile app.

## Step 1: Verify the need

```
1. Glob "mobile-app/src/shared/ui/**/*.tsx" — list existing components
2. Can existing component be extended (new variant/prop)?
   → YES: add variant/prop, don't create new component
   → NO: proceed to Step 2
```

## Step 2: Choose location

| Type | Location | Export from |
|------|----------|-------------|
| Primitive UI element | `shared/ui/common/ComponentName.tsx` | `shared/ui/common/` |
| Screen-specific component | `features/[feature]/components/` | local import |
| Layout helper | `shared/ui/ComponentName.tsx` | `shared/ui/` |

**Rule**: Only components reused in 2+ places go to `shared/ui/`.

## Step 3: File structure

```tsx
/**
 * ComponentName
 * [One-line description of purpose]
 */

import React from "react";
import { View, type StyleProp, type ViewStyle } from "react-native";
import { useTheme } from "@/shared/theme/useTheme";

// 1. Types
export type ComponentVariant = "default" | "secondary";

// 2. Props interface (exported, with JSDoc)
export interface ComponentNameProps {
  /** [describe prop] */
  variant?: ComponentVariant;
  /** Override container style */
  style?: StyleProp<ViewStyle>;
}

// 3. Static styles (outside component — no re-allocation on render)
const baseStyles = {
  container: { ... },
};

// 4. Named export (primary)
export function ComponentName({ variant = "default", style }: ComponentNameProps) {
  const { theme } = useTheme();
  const { colors } = theme;

  return (
    <View style={[baseStyles.container, style]}>
      {/* content */}
    </View>
  );
}

// 5. Default export (for convenience)
export default ComponentName;
```

## Step 4: Token rules

- **NEVER** hardcode hex colors: `backgroundColor: "#FF0000"` ❌
- **ALWAYS** use theme tokens: `backgroundColor: colors.background.brand` ✅
- For new token needs → use `design-tokens` skill first

## Step 5: Checklist before committing

- [ ] Searched for existing component first
- [ ] File in correct location (`shared/ui/common/` for primitives)
- [ ] Props interface exported with JSDoc comments
- [ ] `style` prop override supported (for container)
- [ ] Named export + default export
- [ ] No hardcoded colors (all from `useTheme()`)
- [ ] Static styles defined outside component function
- [ ] Variants follow existing pattern (`primary`, `secondary`, `danger`, `ghost`)
- [ ] Added to `components-catalog.md` (with full props table and token mapping)

## Common Mistakes

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| Inline style objects `style={{ color: "#333" }}` | Static styles + theme tokens |
| Anonymous export `export default function(){}` | Named export `export function Foo(){}` |
| Props without types | Typed `interface FooProps {}` |
| Component in `features/` shared across features | Move to `shared/ui/common/` |
| New component for minor variation | Extend existing with new prop |
