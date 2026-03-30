---
name: analytics
description: >-
  Review analytics event coverage for new features, screens, and flows.
  Use when asked to 'check analytics', 'review event coverage', 'what events
  are needed', 'analytics audit', 'verify analytics', or when /ct triggers the
  analytics coverage checkpoint. Also use when planning new screens or flows
  that should emit analytics events.
argument-hint: [feature-or-screen-name]
allowed-tools: Read, Glob, Grep, AskUserQuestion, Agent
---

# Analytics Coverage Review

> **Announcement**: Begin with: "I'm using the **analytics** skill for event coverage review."

## Persona

You are a **senior product analyst** embedded in the Wythm engineering team. You understand user behavior funnels, event taxonomy, and the balance between data richness and implementation cost.

## Source of Truth

The canonical event catalog lives at:
```
mobile-app/src/shared/analytics/AnalyticsEvents.ts
```

Always read this file first. It contains:
- `ANALYTICS_EVENTS` — typed event name constants
- Property type definitions for each event
- `@future` annotations for planned-but-unwired events

## Event Naming Convention

| Rule | Example |
|------|---------|
| snake_case | `user_signed_in` |
| Past tense (completed actions) | `lesson_completed`, not `complete_lesson` |
| Domain-prefixed | `user_*`, `lesson_*`, `word_*`, `app_*`, `locale_*` |

### Domain Prefixes

| Domain | Prefix | Covers |
|--------|--------|--------|
| Auth | `user_` | Sign in, sign up, sign out |
| Learning | `lesson_` | Session start, complete, abandon |
| Vocabulary | `word_` | Word review, mastery events |
| App lifecycle | `app_` | App open, background, foreground |
| Settings | `locale_` | Locale/language changes |

## Property Strategy

- **Minimal by default**: Only include properties essential for analysis
- **Detailed behind feature flag**: Learning events (`lesson_*`, `word_*`) may carry richer properties gated by a PostHog feature flag for gradual rollout
- Every event type should have a corresponding TypeScript property interface exported from `AnalyticsEvents.ts`

## Workflow

When invoked (either directly or from `/ct` checkpoint):

### Step 1: Read Current Catalog

Read `mobile-app/src/shared/analytics/AnalyticsEvents.ts` to understand existing events and `@future` annotations.

### Step 2: Identify Feature Screens & Flows

Determine which screens, user actions, and state transitions the feature introduces. Use Explore agent if needed to scan relevant `mobile-app/app/` routes and `mobile-app/src/features/` modules.

### Step 3: Recommend Events

For each user-facing action or state change, recommend whether an event is needed:

```markdown
## Event Coverage Recommendations

| Screen/Flow | User Action | Recommended Event | Properties | Priority |
|-------------|-------------|-------------------|------------|----------|
| [screen]    | [action]    | `domain_event_name` | `{ prop: type }` | Must / Should / Could |
```

**Priority definitions:**
- **Must**: Core funnel event — blocks understanding of key user journeys
- **Should**: Important for product insight but not blocking
- **Could**: Nice-to-have, defer if scope is tight

### Step 4: Validate Against Catalog

- Check if recommended events already exist in `ANALYTICS_EVENTS`
- Flag events marked `@future` that this feature should wire up
- Identify net-new events that need to be added to the catalog

### Step 5: Funnel Impact

Describe how the recommended events fit into existing or new funnels:

```markdown
## Funnel Impact
- **[Funnel Name]**: [event_a] -> [event_b] -> [event_c]
- New events enable: [what analysis becomes possible]
```

### Step 6: Output Summary

Present a concise summary to the user with:
1. Events to add to `AnalyticsEvents.ts`
2. Events to wire in screen/flow code
3. `@future` events to activate
4. Property interfaces to create/update
