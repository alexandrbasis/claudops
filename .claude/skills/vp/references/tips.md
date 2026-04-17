# Tips for Effective Playgrounds

## UI Playgrounds

- Include realistic data (names, numbers, text) — not lorem ipsum
- Show loading states and transitions between screens
- Test with different content lengths (short names vs long names)
- Include accessibility indicators (focus rings, contrast)
- Show both light and dark theme variants if the feature is theme-sensitive

## Backend Playgrounds

- Focus on data flow, not implementation details
- Use comments to capture architectural concerns and open questions
- Show error paths, not just happy path
- Indicate async vs sync operations
- Mark external dependencies clearly (DB, third-party APIs)

## Prompt Output

- The playground's "Copy Prompt" button generates implementation notes
- These notes can be pasted directly into `/ct` for technical decomposition
- Include in `vp-approval.md` under "Notes for Technical Decomposition"

## Common Pitfalls

- **One flow per view** — keep each view focused on one flow. Split edge cases across presets or scenarios so each view stays readable.
- **Ignoring empty states** — The first thing a new user sees is often an empty state. Always include one.
- **Static-only preview** — Even backend diagrams benefit from interaction (click to expand, hover for details). Use the playground's interactivity, don't just render a static image.
