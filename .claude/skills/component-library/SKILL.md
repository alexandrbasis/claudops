---
name: component-library
description: |
  Catalog of reusable UI components for Wythm mobile app — buttons, inputs, text, bottom sheets, toasts, and loading states.

  **Use this skill when:**
  - Building any screen in mobile-app/ that uses buttons, forms, text, bottom sheets, toasts, or loading indicators
  - Deciding whether to create a new component or reuse an existing one
  - Looking up component API (props, variants, sizes)
  - Creating new reusable components (patterns and conventions)
  - Composing complex UI from primitives (e.g., a form inside a bottom sheet)

  Trigger on phrases like "add a button", "need a bottom sheet", "show a toast", "loading state", "form screen", "text styles", "typography", "which component should I use", or any UI implementation in mobile-app/.

  **NOT for:** design token naming/creation (use design-tokens), RN platform rules (use react-native-expo-mobile).
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Component Library

> **Announcement**: Begin with: "I'm using the **component-library** skill for UI component reference."

Wythm mobile app component catalog. All shared components live in `mobile-app/src/shared/ui/`.

> **Living catalog**: The design system is actively evolving. Before implementing UI, run `Glob "mobile-app/src/shared/ui/**/*.tsx"` to confirm the current state.

## Workflow: Building UI

Use these skills in sequence when implementing screens:

1. **component-library** (this skill) — check for existing components, reuse before creating
2. **design-tokens** — if you need new color tokens for a component
3. **react-native-expo-mobile** — for RN-specific patterns (animations, gestures, platform APIs)

## Decision: Reuse vs Create

**Before creating a new component:**

1. Search existing: `Glob "mobile-app/src/shared/ui/**/*.tsx"`
2. Check if an existing component's props can be extended (add a variant/size)
3. Only create new if behavior fundamentally differs

## Component Catalog

### Primitives (`shared/ui/common/`)

| Component | File | Key Props |
|-----------|------|-----------|
| `Button` | `common/Button.tsx` | `title`, `variant` (primary/secondary/danger/ghost), `size` (small/medium/large), `loading`, `disabled`, `fullWidth` |
| `Input` | `common/Input.tsx` | `label`, `error`, `required`, `containerStyle`, all TextInput props |
| `AppBottomSheet` | `common/AppBottomSheet.tsx` | `visible`, `onClose`, `size` (content/sm/md/lg), `snapPoints`, `enablePanDownToClose` |
| `LoadingView` | `common/loaders/LoadingView.tsx` | No props — full-screen centered ActivityIndicator |
| `LanguageSelector` | `common/LanguageSelector.tsx` | Locale picker — check source for current API |

### Feedback (`shared/ui/`)

| Component | File | Key Props |
|-----------|------|-----------|
| `Toast` | `Toast.tsx` | `id`, `type` (success/error/warning/info), `title`, `message?`, `position` (top/bottom), `onDismiss`. Uses `forwardRef` with `animateOut` handle. |

### Typography & Layout (`shared/ui/`)

| Component | File | Key Props |
|-----------|------|-----------|
| `StyledText` | `StyledText.tsx` | `variant` (h1/h2/h3/body/caption/label), `colorToken`, `bold` |
| `Themed` | `Themed.tsx` | **Legacy** — limited to 3 hardcoded tokens. Prefer `StyledText` for text or direct `useTheme()` for views. |

## Quick Reference: StyledText Typography Scale

| Variant | Size | Weight | Line Height | Default Color |
|---------|------|--------|-------------|---------------|
| `h1` | 32 | 700 | 40 | `text.base` |
| `h2` | 24 | 600 | 32 | `text.base` |
| `h3` | 20 | 600 | 28 | `text.base` |
| `body` | 16 | 400 | 24 | `text.base` |
| `caption` | 12 | 400 | 16 | `text.secondary` |
| `label` | 14 | 500 | 20 | `text.base` |

```tsx
<StyledText variant="h2">Title</StyledText>
<StyledText variant="caption" colorToken="secondary">Subtitle</StyledText>
<StyledText variant="body" bold>Emphasized text</StyledText>
```

## Quick Reference: Button

```tsx
<Button title="Save" onPress={handleSave} />
<Button title="Cancel" variant="secondary" />
<Button title="Delete" variant="danger" />
<Button title="Learn more" variant="ghost" size="small" />
<Button title="Submit" loading={isLoading} fullWidth />
```

## Quick Reference: AppBottomSheet

```tsx
<AppBottomSheet visible={isOpen} onClose={() => setIsOpen(false)} size="md">
  {/* content */}
</AppBottomSheet>
```

Size presets: `content` (auto-fit), `sm` (35%), `md` (58%), `lg` (78%).

## Quick Reference: Toast

Toast is rendered by `ToastProvider` — you don't use it directly. Add toasts via the store:

```tsx
import { useToastStore } from "@/store";

const { addToast } = useToastStore();
addToast({ type: "success", title: "Saved!", message: "Your changes were saved." });
addToast({ type: "error", title: "Failed", message: "Could not save." });
```

## Composition Patterns

### Form inside Bottom Sheet

```tsx
<AppBottomSheet visible={isOpen} onClose={close} size="md">
  <View style={{ padding: 16, gap: 12 }}>
    <StyledText variant="h3">Edit Profile</StyledText>
    <Input label="Name" value={name} onChangeText={setName} error={errors.name} required />
    <Input label="Email" value={email} onChangeText={setEmail} error={errors.email} required />
    <Button title="Save" onPress={handleSave} loading={saving} fullWidth />
  </View>
</AppBottomSheet>
```

### Screen with Loading → Content → Actions

```tsx
function MyScreen() {
  const { isLoading, data } = useData();
  if (isLoading) return <LoadingView />;

  return (
    <View style={{ flex: 1 }}>
      <StyledText variant="h2">{data.title}</StyledText>
      <StyledText variant="body">{data.description}</StyledText>
      <Button title="Continue" onPress={handleNext} fullWidth />
      <Button title="Skip" variant="ghost" size="small" onPress={handleSkip} />
    </View>
  );
}
```

## Creating New Components

Follow `references/creation-guide.md` for step-by-step rules.

**Quick checklist:**
- [ ] Does similar component already exist? (search first)
- [ ] File in `shared/ui/common/` for primitives
- [ ] Uses `useTheme()` for colors (no hardcoded colors)
- [ ] Props interface exported with JSDoc
- [ ] Supports `style` prop override
- [ ] Named export + default export
- [ ] Follows existing variant/size patterns

## When to Read Full References

- `references/components-catalog.md` — detailed props table, token mappings, size styles per component
- `references/usage-examples.md` — real usage patterns from screens
- `references/creation-guide.md` — step-by-step creation workflow
