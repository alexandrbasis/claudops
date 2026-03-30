---
name: figma-design-system-rules
description: Generates and updates design system rules for Wythm project based on Figma analysis. Use when user says "create design system rules", "sync design rules", "update Figma rules", or wants to establish/refresh project conventions for Figma-to-code workflows. Requires Figma MCP server connection.
metadata:
  mcp-server: figma
---

# Create Design System Rules (Wythm)

## Overview

Analyzes the Wythm codebase and Figma design system to generate project-specific rules that guide AI agents to produce consistent, high-quality React Native code when implementing Figma designs.

## Prerequisites

- Figma MCP server must be connected (`create_design_system_rules` tool available)
- Access to the Wythm mobile-app codebase

## When to Use

- First time setting up Figma-to-code workflow
- After significant changes to design system (new tokens, components, patterns)
- When onboarding new contributors to understand conventions
- Periodically to keep rules in sync with evolving codebase

## Required Workflow

### Step 1: Run Figma's Design System Rules Tool

```
create_design_system_rules(
  clientLanguages="typescript",
  clientFrameworks="react"
)
```

Note: We specify "react" because Figma doesn't have a React Native option, but the output will be adapted.

### Step 2: Analyze Wythm Codebase

Examine these key areas:

**Component inventory:**
- `mobile-app/src/shared/ui/common/` — shared primitives (Button, Input, AppBottomSheet, etc.)
- `mobile-app/src/shared/ui/` — Toast, ErrorBoundary, StyledText, Themed
- `mobile-app/src/features/*/components/` — feature-specific components

**Design tokens:**
- `mobile-app/src/shared/theme/tokens/colors.primitives.ts` — raw color values
- `mobile-app/src/shared/theme/tokens/colors.semantic.ts` — semantic tokens (light/dark)
- `mobile-app/src/shared/theme/createTheme.ts` — theme construction
- `mobile-app/src/shared/theme/useTheme.ts` — theme hook

**Architecture:**
- `mobile-app/src/shared/` — shared layer (ui, hooks, utils, theme, i18n, errors)
- `mobile-app/src/features/` — feature modules (auth, etc.)
- `mobile-app/src/infrastructure/` — HTTP, repositories, analytics
- `mobile-app/src/composition/` — providers (Theme, Auth, Locale, Toast, API)
- `mobile-app/src/store/` — Zustand store with slices
- `mobile-app/app/` — Expo Router screens

**Patterns:**
- Theme: `useTheme()` → `theme.colors.*`
- i18n: Lingui `msg` + `useTranslation()`
- Navigation: Expo Router file-based routing
- State: Zustand for client state, React Query for server state
- HTTP: Axios with interceptors in `src/infrastructure/http/`

### Step 3: Generate Rules

Based on Figma tool output + codebase analysis, generate rules covering:

1. **Component organization** — where to place new components, naming conventions
2. **Styling approach** — React Native StyleSheet pattern with theme tokens
3. **Figma-to-RN translation** — how to convert React+Tailwind output to RN
4. **Token mapping** — Figma variables → `theme.colors.*` paths
5. **Asset handling** — where to store, how to reference
6. **i18n requirements** — Lingui wrapping for all user-facing strings
7. **Dark mode** — semantic tokens requirement
8. **Accessibility** — minimum touch targets, labels

### Step 4: Save Rules

Save generated rules to: `.claude/rules/figma-design-system.md`

This file will be auto-loaded by Claude Code for all mobile-app work.

**Format:**
```markdown
# Figma Design System Rules (Wythm Mobile)

## Component Organization
[generated rules]

## Styling
[generated rules]

## Figma MCP Integration
[generated rules]

## Token Mapping
[generated rules]

## Assets
[generated rules]

## i18n
[generated rules]

## Dark Mode
[generated rules]

## Accessibility
[generated rules]
```

### Step 5: Validate

Test the rules by implementing one simple Figma component and verifying:
- Correct component location
- Theme tokens used (no hardcoded colors)
- Lingui i18n applied
- Dark mode works
- Existing components reused where applicable

## Maintenance

- Re-run this skill when adding 3+ new shared components
- Re-run when token structure changes
- Re-run quarterly as a health check
