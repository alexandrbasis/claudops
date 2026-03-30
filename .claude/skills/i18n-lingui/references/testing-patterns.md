# i18n Testing Patterns

## Table of Contents
1. [Mocking Lingui Provider](#mocking-lingui-provider)
2. [Mocking loadCatalog](#mocking-loadcatalog)
3. [Mocking LocaleProvider](#mocking-localeprovider)
4. [Mocking localeStorage](#mocking-localestorage)
5. [Integration Test Setup](#integration-test-setup)

---

## Mocking Lingui Provider

Replace `I18nProvider` with a passthrough so tests don't need a real i18n instance:

```typescript
jest.mock("@lingui/react", () => ({
  I18nProvider: ({ children }: { children: React.ReactNode }) => children,
}));
```

## Mocking loadCatalog

```typescript
jest.mock("@/i18n", () => ({
  ...jest.requireActual("@/i18n"),
  loadCatalog: jest.fn().mockResolvedValue(undefined),
}));
const mockLoadCatalog = loadCatalog as jest.Mock;
```

## Mocking LocaleProvider

For unit tests that don't need the real provider:

```typescript
jest.mock("@/composition/LocaleProvider", () => ({
  useLocale: () => ({
    locale: "en",
    setLocale: jest.fn().mockResolvedValue(undefined),
    setLocaleLocal: jest.fn().mockResolvedValue(undefined),
  }),
}));
```

## Mocking localeStorage

```typescript
jest.mock("@/i18n/localeStorage", () => ({
  setLocale: jest.fn().mockResolvedValue(undefined),
  setLocaleWithoutTimestamp: jest.fn().mockResolvedValue(undefined),
  markLocaleSyncComplete: jest.fn().mockResolvedValue(undefined),
  getLocale: jest.fn().mockResolvedValue("en"),
}));
```

## Integration Test Setup

For tests that use the real `LocaleProvider`, mock its dependencies:

```typescript
// Required mocks for LocaleProvider
jest.mock("expo-secure-store");
jest.mock("expo-localization");
jest.mock("@/i18n", () => ({
  ...jest.requireActual("@/i18n"),
  loadCatalog: jest.fn().mockResolvedValue(undefined),
}));
jest.mock("@/composition/ApiProvider", () => ({
  useUserService: () => ({
    getMe: jest.fn(),
    updateInterfaceLang: jest.fn(),
  }),
}));
jest.mock("@/infrastructure/http/core/TokenStore", () => ({
  tokenStore: { getToken: () => null },
}));

// Import AFTER mocks
import { LocaleProvider, useLocale } from "@/composition/LocaleProvider";
```

### Verifying locale changes in integration tests

```typescript
function LocaleDisplay() {
  const { locale } = useLocale();
  return <Text testID="current-locale">{locale}</Text>;
}

it("updates locale when user selects a language", async () => {
  const { getByTestId, findByTestId } = render(
    <LocaleProvider>
      <LocaleDisplay />
      <LanguageSelector visible={true} onClose={jest.fn()} />
    </LocaleProvider>
  );

  await findByTestId("current-locale");
  expect(getByTestId("current-locale").props.children).toBe("en");

  await act(async () => {
    fireEvent.press(getByTestId("language-option-ru"));
  });

  await waitFor(() => {
    expect(getByTestId("current-locale").props.children).toBe("ru");
  });
});
```

## Test File Locations

- Unit: `tests/unit/i18n/localeStorage.spec.ts`
- Unit: `tests/unit/i18n/utils/resolveLocale.spec.ts`
- Unit: `tests/unit/composition/LocaleProvider.spec.tsx`
- Unit: `tests/unit/shared/ui/LanguageSelector.spec.tsx`
- Integration: `tests/integration/shared/ui/LanguageSelector.integration.spec.tsx`
- Integration: `tests/integration/composition/LocaleProvider.sync.spec.tsx`
- Integration: `tests/integration/composition/AuthProvider.localeSync.spec.tsx`
