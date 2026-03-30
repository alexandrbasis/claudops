# Auth Flow

Authentication screens and navigation for Wythm mobile app.

## Screens

### Sign In (`SignInScreen`)

**File:** `mobile-app/src/features/auth/screens/SignInScreen.tsx`
**Route:** `/(auth)/sign-in`
**Status:** Implemented

**Layout:**
```
┌─────────────────────────────┐
│  Welcome to Wythm           │
│  Sign in to continue        │
├─────────────────────────────┤
│                             │
│  Email Input                │
│  Password Input             │
│                             │
│  [Sign In Button]           │
│                             │
└─────────────────────────────┘
```

**Components:**
- `Input` (email, password) — from `shared/ui/common/Input`
- `Button` (sign in, primary, fullWidth) — from `shared/ui/common/Button`
- `StyledText` (h1, body) — from `shared/ui/StyledText`

**Wrapper:** `KeyboardAvoidingView` (behavior: `"padding"` on iOS, `undefined` on Android)

**API:**
- Auth sign-in mutation via `useSignIn()` hook (React Query `useMutation`) — verify endpoint in `backend/docs/` or `backend/src/infrastructure/web/controllers/`

**State:**
- `email: string` — `useState`
- `password: string` — `useState`
- `signIn.isPending: boolean` — from React Query mutation (disables inputs + shows loading on button)
- Validation: inline via `Alert.alert` (no separate error state)

**Navigation:**
- Entry: `AuthGate` redirects unauthenticated users to `/(auth)/sign-in`
- Success: `useSignIn` hook calls `router.replace` to navigate after successful sign-in — see hook implementation for current target route

---

### Auth Gate (`AuthGate`)

**File:** `mobile-app/src/features/auth/components/AuthGate.tsx`
**Type:** Layout wrapper (not a screen)
**Purpose:** Protects app routes — redirects unauthenticated users to sign-in

**Logic:**
```
isAuthenticated === false → router.replace('/(auth)/sign-in') + return null
isAuthenticated === true  → render children
```

**State source:** `useStore` (Zustand) — reads `isAuthenticated` via `useShallow`

**Note:** No loading state in AuthGate itself — session restore is handled by `AuthProvider` before AuthGate runs.

---

## Future Auth Screens (PLANNED)

| Screen | Purpose | Priority |
|--------|---------|---------|
| Sign Up | New account creation | Medium |
| Forgot Password | Password reset via email | Low |
| Email Verification | Confirm email after registration | Low |
| Profile | User settings / logout | Medium |
