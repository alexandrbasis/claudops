---
name: i18n-lingui
description: >
  Internationalization rules for Wythm mobile app using Lingui v5. Use this skill whenever working
  with translatable text, locale switching, language selectors, i18n extraction, PO files, locale
  persistence, or any component in mobile-app/ that displays user-facing strings. Also use when
  touching LocaleProvider, useTranslation, useLocale, catalog loading, or backend locale sync.
  Trigger on any mention of translations, i18n, localization, multilingual, or language support.
---

# i18n — Lingui v5 for Wythm Mobile

> **Announcement**: Begin with: "I'm using the **i18n-lingui** skill for internationalization with Lingui."

## Supported Locales (9)

`en` (source), `ru`, `es`, `fr`, `sr`, `zh-CN`, `zh-TW`, `de`, `pt`

## Import Rules

Lingui v5 uses **macro imports** for compile-time string extraction. Using the wrong import path silently breaks extraction — strings won't appear in `.po` files.

```tsx
// JSX and hooks — from @lingui/react/macro
import { Trans, Plural, Select } from "@lingui/react/macro";
import { useLingui } from "@lingui/react/macro";

// Message descriptors (non-JSX) — from @lingui/core/macro
import { msg } from "@lingui/core/macro";

// WRONG — runtime imports, no extraction
import { Trans } from "@lingui/react";        // ← won't extract
import { useLingui } from "@lingui/react";    // ← won't extract
```

## Usage Patterns (by priority)

### 1. `msg` + `i18n._()` — Non-JSX contexts (MOST USED)

For any place that needs a **plain string** (not JSX) — tab titles, alert messages, accessibility labels, navigation options:

```tsx
import { msg } from "@lingui/core/macro";
import { useTranslation } from "@/shared/i18n";

function MyScreen() {
  const { i18n } = useTranslation();

  return (
    <Tabs.Screen
      options={{
        title: i18n._(msg`Home`),
        tabBarLabel: i18n._(msg`Words`),
      }}
    />
  );
}
```

`msg` creates a `MessageDescriptor` at compile time; `i18n._()` evaluates it with the active locale at render time. This is the pattern used in tab layouts, screen headers, alerts, and anywhere React Native needs a string prop.

**Alert messages** — a common case where `msg` + `i18n._()` is required:

```tsx
const { i18n } = useTranslation();

Alert.alert(
  i18n._(msg`Validation Error`),
  i18n._(msg`Email is required`),
  [{ text: i18n._(msg`OK`) }]
);
```

### 2. `<Trans>` — JSX text content

For visible text inside `<Text>` components:

```tsx
import { Trans } from "@lingui/react/macro";

// All translated text MUST be inside <Text> — bare <Trans> inside <View> crashes on native
<Text><Trans>Welcome to Wythm</Trans></Text>

// Variables
<Text><Trans>Hello, {name}!</Trans></Text>

// Pluralization
<Text>
  <Plural value={count} one="# word" other="# words" />
</Text>
```

### 3. `` t` ` `` — Template literal (quick inline strings)

```tsx
import { useTranslation } from "@/shared/i18n";

function MyComponent() {
  const { t } = useTranslation();
  return <Text>{t`Sign in to continue`}</Text>;
}
```

### Hook: `useTranslation` (project wrapper)

Always use `@/shared/i18n` instead of importing `useLingui` directly — it provides both `t` and `i18n`:

```tsx
import { useTranslation } from "@/shared/i18n";
const { t, i18n } = useTranslation();
```

Source: `mobile-app/src/shared/i18n/useTranslation.ts`

### Locale Display Names (for language selector UI)

```tsx
import { LOCALE_DISPLAY_NAMES } from "@/i18n/localeDisplayNames";

// Each entry has { native: string, english: string }
LOCALE_DISPLAY_NAMES["ru"];     // { native: "Русский", english: "Russian" }
LOCALE_DISPLAY_NAMES["zh-CN"]; // { native: "简体中文", english: "Chinese Simplified" }
```

## Critical Rules

1. **All translated text inside `<Text>`** — `<View><Trans>Hello</Trans></View>` crashes on native
2. **Use macro imports** — `@lingui/react/macro` and `@lingui/core/macro`, never bare `@lingui/react`
3. **Don't interpolate outside Trans** — `<Trans>{"Hello, " + name}</Trans>` breaks translation
4. **Don't split translatable content** — `<Trans>Click</Trans> <Trans>here</Trans>` loses context for translators
5. **Don't use dynamic message IDs** — `t(key)` can't be extracted; use conditional expressions instead

## Translation Workflow

```bash
cd mobile-app

# Extract new strings from src/ and app/ → updates .po files
npm run i18n:extract

# Compile .po → .js (CI uses this; dev can too)
npm run i18n:compile
```

Edit PO files in `src/i18n/locales/*.po`. The compiled `.js` files are what the app actually loads at runtime.

**Keep PO and JS in sync** — always run extract then compile together. The `.po` files are the source of truth; `.js` files are derived artifacts. If you only run `compile` without a prior `extract`, compiled catalogs may contain stale strings from deleted source code.

Config: `mobile-app/lingui.config.ts` (scans both `src/` and `app/` directories).

## Architecture

### File Structure

```
mobile-app/src/i18n/
├── index.ts              # Lingui setup, loadCatalog(), re-exports
├── lingui.d.ts           # TS declarations for .po imports
├── localeDisplayNames.ts # Native + English names (for LanguageSelector UI)
├── localeStorage.ts      # SecureStore persistence (locale + sync metadata)
├── supportedLocales.ts   # SupportedLocale type, isSupportedLocale guard
├── utils/
│   ├── resolveLocale.ts  # 3-step: SecureStore → expo-localization → "en"
│   └── localeMapper.ts   # BCP-47 ↔ backend format (zh-CN ↔ zh_CN)
└── locales/
    ├── {locale}.po       # Source translations (human-editable)
    └── {locale}.js       # Compiled catalogs (runtime)

mobile-app/src/shared/i18n/
├── index.ts              # Re-exports useTranslation
└── useTranslation.ts     # Wrapper over useLingui macro
```

### Locale Resolution (on app start)

`resolveLocale()` follows a 3-step priority:
1. **SecureStore** — user's persisted preference
2. **System locale** — `expo-localization` → map to supported (incl. Chinese variants)
3. **Fallback** — `"en"`

### Provider Nesting Order (`app/_layout.tsx`)

`ApiProvider > LocaleProvider > AuthProvider > ThemeProvider`

LocaleProvider must be above AuthProvider because AuthProvider needs locale context for backend reconciliation.

### LocaleProvider Context

```tsx
type LocaleContextValue = {
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => Promise<void>;      // User-facing: persists + syncs to backend
  setLocaleLocal: (locale: SupportedLocale) => Promise<void>; // @internal: auth reconciliation only
};
```

- `setLocale` — **local-first**: loads catalog → persists to SecureStore → updates React state → background-syncs to backend API (non-blocking, fire-and-forget)
- `setLocaleLocal` — same but skips timestamp/sync metadata (used by AuthProvider when backend locale overrides local)
- Provider blocks rendering (`null`) until locale is resolved

Access via: `import { useLocale } from "@/composition/LocaleProvider";`

### Backend Locale Mapping

Mobile uses BCP-47 dashes (`zh-CN`), backend uses underscores (`zh_CN`):

```tsx
import { toBackendLanguageCode, toMobileLocale } from "@/i18n/utils/localeMapper";

toBackendLanguageCode("zh-CN"); // → "zh_CN"
toMobileLocale("zh_CN");        // → "zh-CN"
toMobileLocale("he");           // → undefined (Hebrew is backend-only)
```

### Chinese Variant Mapping

System locale → supported locale:
- `zh-Hans`, `zh-CN`, `zh-Hans-*` → `zh-CN` (Simplified)
- `zh-Hant`, `zh-TW`, `zh-Hant-*` → `zh-TW` (Traditional)
- `zh` (bare) → `zh-CN` (default to Simplified)

## Anti-Patterns

```tsx
// BAD: Hardcoded string
<Text>Welcome</Text>
// GOOD (JSX):
<Text><Trans>Welcome</Trans></Text>
// GOOD (string prop):
<Screen options={{ title: i18n._(msg`Welcome`) }} />

// BAD: Dynamic message ID — can't extract
const key = isError ? "error" : "success";
t(key);
// GOOD:
isError ? i18n._(msg`Error occurred`) : i18n._(msg`Success`);

// BAD: Split translatable content
<Text><Trans>Click</Trans> <Trans>here</Trans></Text>
// GOOD:
<Text><Trans>Click here</Trans></Text>

// BAD: msg without i18n._() — returns a descriptor object, not a string
const title = msg`Home`;
// GOOD:
const title = i18n._(msg`Home`);

// BAD: Direct useLingui import
import { useLingui } from "@lingui/react/macro";
// GOOD: Use project wrapper
import { useTranslation } from "@/shared/i18n";
```

## Testing

See `references/testing-patterns.md` for i18n mocking patterns, Lingui provider setup, and test examples.

## Scope Boundaries

- **RTL**: Not supported — none of the 9 locales are RTL (ADR-006 explicitly out of scope)
- **Date/number formatting**: No `@formatjs/intl-numberformat` or `intl-datetimeformat` polyfills installed yet — only `intl-locale` and `intl-pluralrules`
- **Phase 3-4 migration**: Many screens still have hardcoded English strings (migration ongoing per ADR-006)

## References

- ADR: `mobile-app/docs/adr/ADR-006-i18n-architecture.md`
- Lingui Docs: https://lingui.dev/
- Testing patterns: `references/testing-patterns.md`
