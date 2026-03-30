---
name: api-reference
description: >-
  Look up Wythm API endpoint contracts, auth flows, and error codes. Use when
  answering questions about API endpoints, implementing repository calls in mobile-app,
  debugging HTTP errors, or reviewing code that calls the backend API.
  NOT for creating new endpoints (use /si).
---

# API Reference Skill

> **Announcement**: Begin with: "I'm using the **api-reference** skill for API reference lookup."

## When to use this skill

Load this skill when:
- Answering questions about Wythm API endpoints (what parameters, what it returns)
- Writing repository calls in the mobile app (which endpoint to call, what shape the request/response is)
- Debugging 401/403/4xx errors (checking auth requirements, error responses)
- Implementing a new repository and need to know the endpoint contract
- Reviewing code that calls the backend API

## Reference files

| File | Contents | Use when |
|------|----------|----------|
| [references/endpoints.md](./references/endpoints.md) | All API endpoints with auth, params, request/response | Checking endpoint contracts |
| [references/auth.md](./references/auth.md) | Bearer token auth, sign-in flow, header format | Implementing auth headers or handling 401s |
| [references/flows.md](./references/flows.md) | Key multi-step API flows (sign-in, refresh, bootstrap) | Understanding full auth/session flows |
| [references/error-codes.md](./references/error-codes.md) | Error response shapes and HTTP status codes | Handling errors, implementing error boundaries |

## Regenerating endpoints.md

`endpoints.md` is auto-generated from `backend/openapi.json`. To update it:

```bash
# From repo root
TS_NODE_COMPILER_OPTIONS='{"module":"commonjs"}' npx ts-node scripts/generate-api-skill.ts
```

Or if root `package.json` has the script:
```bash
npm run generate:api-skill
```

## Important notes

- All authenticated endpoints require `Authorization: Bearer <accessToken>` header
- Access tokens are short-lived — use the refresh flow when you get 401
- The mobile app never calls Supabase directly — all calls go through this backend API
