---
name: screen-flow
description: |
  Screen decomposition and flow analysis for Wythm mobile app UI planning.

  **Use this skill when:**
  - Decomposing a Figma screen into components
  - Mapping screens to API endpoints
  - Documenting a new screen flow (auth, training, vocabulary)
  - Creating screen specification before technical decomposition

  **Used by:** mobile-ui-planning-agent (invoked inside /ct for UI-heavy tasks)

  **NOT for:** component API lookup (use component-library), token naming (use design-tokens).
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Screen Flow

> **Announcement**: Begin with: "I'm using the **screen-flow** skill for screen flow analysis."

Analysis and decomposition framework for Wythm mobile app screens.

## Screen Inventory

### Auth Flow (`features/auth/`)

| Screen | File | Route |
|--------|------|-------|
| Sign In | `screens/SignInScreen.tsx` | `/(auth)/sign-in` |

> API endpoint — verify in `backend/docs/` or `backend/src/infrastructure/web/controllers/`. Do not hardcode here.

### Training Flow (`features/training/`) — PLANNED

| Screen | Status | Route |
|--------|--------|-------|
| Training Session | TODO | TBD |
| Word Card | TODO | TBD (modal) |
| Results | TODO | TBD |

> API endpoints for training — see `backend/docs/` or `backend/src/infrastructure/web/controllers/`. Do not hardcode here.

### Vocabulary Flow (`features/vocabulary/`) — PLANNED

| Screen | Status | Route |
|--------|--------|-------|
| Word List | TODO | TBD |
| Word Detail | TODO | TBD |

> API endpoints for vocabulary — see `backend/docs/` or `backend/src/infrastructure/web/controllers/`. Do not hardcode here.

## Decomposition Process

When analyzing a Figma screen:

### Step 1: Identify layout zones

```
Header zone     → navigation, title, actions
Content zone    → primary content (list, form, detail)
Footer zone     → CTA buttons, tab bar
Modal zone      → bottom sheets, overlays
```

### Step 2: Identify components

For each visual element, ask:
- Does it exist in `component-library`? → reuse
- Is it screen-specific? → create in `features/[feature]/components/`
- Is it used in 2+ screens? → create in `shared/ui/common/`

### Step 3: Map API endpoints

For each data element on screen:
- What data is displayed?
- Which API endpoint provides it?
- Is it paginated? (→ use FlatList/FlashList)
- Is it real-time? (→ polling or WebSocket)

### Step 4: Identify state

| State type | Where | Example |
|-----------|-------|---------|
| Server state (fetched) | React Query | word list, user profile |
| UI state (local) | `useState` | modal open, form values |
| Global app state | Zustand | auth session, theme |

## Screen Specification Template

Use `references/screen-template.md` to document each screen.

## When to load flow docs

- `references/flows/auth.md` — auth-related screens (exists)
- `references/flows/training.md` — training session screens (**not yet created**, create when needed)
- `references/flows/vocabulary.md` — vocabulary management screens (**not yet created**, create when needed)
