# Screen Specification Template

Use this template when creating a new screen specification for UI planning.

---

## Screen: [ScreenName]

**Feature:** `features/[feature-name]/`
**File:** `screens/[ScreenName].tsx`
**Route:** `/[route-path]`
**Status:** TODO | In Progress | Done

---

### Purpose

[One paragraph: what the user accomplishes on this screen]

---

### Layout Overview

```
┌─────────────────────────────┐
│  [Header: title / back btn] │
├─────────────────────────────┤
│                             │
│  [Content area]             │
│  - [element 1]              │
│  - [element 2]              │
│                             │
├─────────────────────────────┤
│  [Footer: CTA button]       │
└─────────────────────────────┘
```

---

### Component Inventory

| UI Element | Component | Source | Notes |
|-----------|-----------|--------|-------|
| Submit button | `Button` | `shared/ui/common/Button` | `variant="primary"`, `fullWidth` |
| Email field | `Input` | `shared/ui/common/Input` | `keyboardType="email-address"` |
| [New element] | `[NewComponent]` | CREATE in `features/[f]/components/` | [description] |

---

### API Integration

> **Note:** Do not copy API endpoints from this template — always verify against `backend/docs/` or the backend controllers. Endpoints change and skills must not hardcode contracts.

| Data / Action | Endpoint | Method | Notes |
|--------------|----------|--------|-------|
| [action] | `[verify in backend/docs/]` | POST/GET | [notes] |

---

### State

> **Note:** For Zustand store shape, read `mobile-app/src/store/` — do not copy field names from this template, they may be outdated.

| State | Type | Where | Notes |
|-------|------|-------|-------|
| `[field]` | `string` | `useState` | local form state |
| `[mutation].isPending` | `boolean` | React Query | loading state |
| `[field]` | `[Type]` | Zustand `useStore` | global app state — verify field name in store |

---

### Design Tokens Used

| Element | Token |
|---------|-------|
| Background | `colors.background.base` |
| Button | `colors.background.brand` |
| Input border | `colors.field.border` |

---

### RN Patterns Applied

- [ ] Core Rendering: no `&&` with numbers, all text in `<Text>`
- [ ] No hardcoded colors
- [ ] `KeyboardAvoidingView` if form with keyboard
- [ ] `SafeAreaView` for safe area
- [ ] Loading state handled

---

### Navigation

**Entry points:**
- [From which screen/event]

**Exit points:**
- On success → `router.replace('/[next-route]')`
- On cancel → `router.back()`

---

### Notes for Technical Decomposition

[Any implementation notes, gotchas, or decisions to highlight]
