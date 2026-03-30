# Components Catalog — Detailed API

> **Living catalog**: Verify against actual source before implementing. Run `Glob "mobile-app/src/shared/ui/**/*.tsx"` to confirm.

## Table of Contents

1. [Button](#button)
2. [Input](#input)
3. [AppBottomSheet](#appbottomsheet)
4. [Toast](#toast)
5. [StyledText](#styledtext)
6. [LoadingView](#loadingview)
7. [LanguageSelector](#languageselector)
8. [Themed (Legacy)](#themed-legacy)

---

## Button

**File**: `mobile-app/src/shared/ui/common/Button.tsx`

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | required | Button label text |
| `variant` | `"primary" \| "secondary" \| "danger" \| "ghost"` | `"primary"` | Visual style |
| `size` | `"small" \| "medium" \| "large"` | `"medium"` | Padding/font size |
| `loading` | `boolean` | `false` | Show spinner, disable press |
| `disabled` | `boolean` | `false` | Disable press, reduce opacity |
| `fullWidth` | `boolean` | `false` | `width: "100%"` |
| `style` | `StyleProp<ViewStyle>` | — | Override container style |
| `textStyle` | `StyleProp<TextStyle>` | — | Override text style |
| `...TouchableOpacityProps` | — | — | All RN TouchableOpacity props (except `style`) |

### Variant → Token mapping

| Variant | Background | Text | Border |
|---------|-----------|------|--------|
| `primary` | `colors.background.brand` | `colors.text.onBrand` | — |
| `secondary` | `colors.background.secondary` | `colors.text.base` | `colors.border.base` (1px) |
| `danger` | `colors.background.danger` | `colors.text.onDanger` | — |
| `ghost` | `colors.background.transparent` | `colors.text.brand` | — |

### Size → Style mapping

| Size | paddingVertical | paddingHorizontal | fontSize |
|------|----------------|-------------------|---------|
| `small` | 8 | 12 | 14 |
| `medium` | 12 | 16 | 16 |
| `large` | 16 | 20 | 18 |

### Loading indicator color

- `primary` / `danger` → `colors.icon.onBrand`
- `secondary` / `ghost` → `colors.icon.brand`

---

## Input

**File**: `mobile-app/src/shared/ui/common/Input.tsx`

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | `string` | — | Field label shown above input |
| `error` | `string` | — | Error message shown below input |
| `required` | `boolean` | `false` | Adds red `*` to label |
| `containerStyle` | `StyleProp<ViewStyle>` | — | Override wrapper style |
| `...TextInputProps` | — | — | All RN TextInput props |

### Token mapping

| State | Token |
|-------|-------|
| Background (normal) | `colors.field.background` |
| Background (disabled) | `colors.field.backgroundDisabled` |
| Border (normal) | `colors.field.border` |
| Border (error) | `colors.field.borderDanger` |
| Text (normal) | `colors.field.text` |
| Text (disabled) | `colors.field.textDisabled` |
| Placeholder | `colors.field.placeholder` |
| Label text | `colors.text.base` |
| Required marker | `colors.text.danger` |
| Error text | `colors.text.danger` |

---

## AppBottomSheet

**File**: `mobile-app/src/shared/ui/common/AppBottomSheet.tsx`
**Dependency**: `@gorhom/bottom-sheet`

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `visible` | `boolean` | required | Whether sheet is visible |
| `onClose` | `() => void` | required | Called when sheet should close |
| `children` | `ReactNode` | required | Sheet content |
| `size` | `"content" \| "sm" \| "md" \| "lg"` | `"content"` | Preset sheet height |
| `snapPoints` | `Array<number \| string>` | — | Custom snap points (overrides `size`) |
| `backgroundStyle` | `StyleProp<ViewStyle>` | — | Override sheet background |
| `enablePanDownToClose` | `boolean` | `true` | Allow swipe-to-dismiss |
| `maxDynamicHeightPercent` | `number` | `0.85` | Max height as viewport % (for `size="content"`) |

### Size presets

| Size | Snap Point | Use for |
|------|-----------|---------|
| `content` | Auto (dynamic sizing) | Short forms, confirmations |
| `sm` | 35% viewport | Single-action sheets |
| `md` | 58% viewport | Forms, selection lists |
| `lg` | 78% viewport | Long content, full forms |

### Behavior

- Wraps in `<Modal>` for full-screen overlay
- Backdrop tap closes the sheet
- Smooth cubic-eased animation (170ms)
- Uses `useTheme()` for background and handle indicator colors

---

## Toast

**File**: `mobile-app/src/shared/ui/Toast.tsx`

Toast is a **presentational component** rendered by `ToastProvider`. You don't render it directly — use the toast store to add/dismiss toasts.

### Props (for reference)

| Prop | Type | Description |
|------|------|-------------|
| `id` | `string` | Unique toast ID |
| `type` | `"success" \| "error" \| "warning" \| "info"` | Semantic type |
| `title` | `string` | Toast title text |
| `message` | `string?` | Optional detail text |
| `position` | `"top" \| "bottom"` | Entry animation direction |
| `duration` | `number` | Auto-dismiss duration (ms) |
| `onDismiss` | `(id: string) => void` | Dismiss callback |

### Ref handle

```tsx
export interface ToastHandle {
  animateOut: (onComplete: () => void) => void;
}
```

`ToastProvider` calls `animateOut` before removing from store for smooth exit.

### Type → Token mapping

| Type | Background Token | Text Token |
|------|-----------------|------------|
| `success` | `colors.background.brand` | `colors.text.onBrand` |
| `error` | `colors.background.danger` | `colors.text.onDanger` |
| `warning` | `colors.background.secondary` | `colors.text.secondary` |
| `info` | `colors.background.secondary` | `colors.text.secondary` |

### Animation

- Entry: opacity 0→1, translateY ±20→0 (200ms parallel)
- Exit: opacity 1→0 (150ms)

---

## StyledText

**File**: `mobile-app/src/shared/ui/StyledText.tsx`

The primary text component for all typography. Prefer over `Themed.Text`.

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `"h1" \| "h2" \| "h3" \| "body" \| "caption" \| "label"` | `"body"` | Typography variant |
| `colorToken` | `keyof ThemeColors["text"]` | Per variant | Semantic text color from `theme.colors.text.*` |
| `bold` | `boolean` | `false` | Override fontWeight to 700 |
| `...TextProps` | — | — | All RN Text props |

### Typography scale

| Variant | fontSize | fontWeight | lineHeight | Default colorToken |
|---------|----------|-----------|-------------|-------------------|
| `h1` | 32 | 700 (bold) | 40 | `base` |
| `h2` | 24 | 600 (semibold) | 32 | `base` |
| `h3` | 20 | 600 (semibold) | 28 | `base` |
| `body` | 16 | 400 (regular) | 24 | `base` |
| `caption` | 12 | 400 (regular) | 16 | `secondary` |
| `label` | 14 | 500 (medium) | 20 | `base` |

### Color tokens

Override the default color by passing `colorToken`:

```tsx
<StyledText variant="body" colorToken="danger">Error text</StyledText>
<StyledText variant="caption" colorToken="brand">Branded caption</StyledText>
```

Any key from `ThemeColors["text"]` is valid (e.g., `base`, `secondary`, `brand`, `danger`, `onBrand`, `onDanger`).

---

## LoadingView

**File**: `mobile-app/src/shared/ui/common/loaders/LoadingView.tsx`

Full-screen centered loading indicator. No props.

```tsx
import { LoadingView } from "@/shared/ui/common/loaders/LoadingView";
<LoadingView />
```

---

## LanguageSelector

**File**: `mobile-app/src/shared/ui/common/LanguageSelector.tsx`
**Wraps**: `AppBottomSheet` (size `lg`)

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `visible` | `boolean` | required | Whether modal is visible |
| `onClose` | `() => void` | required | Called when modal closes |
| `style` | `StyleProp<ViewStyle>` | — | Override sheet background |

### Behavior

- Displays all `SUPPORTED_LOCALES` with native language names
- Shows checkmark for current locale, loading indicator for pending selection
- Calls `setLocale()` from `useLocale()` on selection
- Auto-closes on selection (after locale change completes)
- Prevents double-tap during locale switching

---

## Themed (Legacy)

**File**: `mobile-app/src/shared/ui/Themed.tsx`

> **Legacy component** — limited to 3 hardcoded color tokens (`text.base`, `text.secondary`, `background.base`). For new code, use `StyledText` for text and direct `useTheme()` for views.

Exports `Text` and `View` with optional `lightColor`/`darkColor` overrides:

```tsx
import { Text, View } from "@/shared/ui/Themed";
<View><Text>Theme-aware</Text></View>
```

Acceptable for simple wrappers where you only need base text/background color. For anything more specific (brand colors, danger states, typography variants), use `StyledText` or `useTheme()` directly.
