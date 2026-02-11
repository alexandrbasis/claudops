---
description: "React Native + Expo critical rules for mobile-app. Prevents crashes and common pitfalls."
paths:
  - "mobile-app/**/*.ts"
  - "mobile-app/**/*.tsx"
---

# Mobile App - React Native + Expo Rules

**Applies to**: `mobile-app/**` directory

## Architecture

Clean Architecture with strict layer boundaries.
**Read first**: `mobile-app/docs/project-structure.md`

## Critical Rules (Never Violate)

1. **Never use `&&` with potentially falsy values** (0, "") — use ternary with `null`
2. **Always wrap strings in `<Text>` components** — bare strings in `<View>` crash
3. **Use virtualizers for all lists** — LegendList/FlashList, never ScrollView + `.map()`
4. **Install native deps in `mobile-app/package.json`** — autolinking only scans app's `node_modules`

## Full Rules

See skill `react-native-expo-mobile` for all rules (animations, navigation, state, compiler compat, etc.)

## Commands

```bash
npm run dev        # Start Expo dev server
npm run ios        # Run on iOS simulator
npm run test       # Run tests
npm run type-check # TypeScript check
npm run lint       # ESLint
```
