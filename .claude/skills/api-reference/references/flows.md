# API Flows Reference

## Sign-In Flow

```
Client                          Backend
  |                                |
  |-- POST /auth/signin ---------->|
  |   { email, password }          |
  |                                |-- validate credentials
  |<-- 200 OK --------------------|
  |   { accessToken,               |
  |     refreshToken? }            |
  |                                |
  |-- POST /auth/session/bootstrap>|  (initialize session state)
  |   Authorization: Bearer <tok>  |
  |<-- 200 OK --------------------|
```

**Notes:**
- `refreshToken` may be absent if Supabase session handles persistence differently
- Always call `/auth/session/bootstrap` after sign-in to initialize server-side session state
- Store both tokens in `TokenStore` before bootstrapping

## Token Refresh Flow

```
Client                          Backend
  |                                |
  |-- POST /auth/refresh --------->|
  |   { refreshToken }             |
  |                                |-- validate refresh token
  |<-- 200 OK --------------------|  (new tokens issued)
  |   { accessToken, ... }         |
  |                                |
  | (update TokenStore)            |
  | (retry original request)       |
```

**When triggered:** Automatically by the Axios interceptor when any request returns 401.

**On failure (401 from /auth/refresh):** Session is expired — navigate user to sign-in screen and clear TokenStore.

## Sign-Up + Confirm Flow

```
Client                          Backend          Email
  |                                |                |
  |-- POST /auth/signup ---------->|                |
  |   { email, password }          |                |
  |<-- 201 Created ----------------|                |
  |                                |-- send email ->|
  |                                |                |
  | (user clicks link in email)    |                |
  |-- GET /auth/confirm ---------->|                |
  |   ?token_hash=...&type=signup  |                |
  |   &next=wythm://auth/callback  |                |
  |<-- redirect to deep link ------|                |
  |                                |
  | (app handles wythm:// deep link)
```

**After confirm:** User needs to sign in with their credentials. The confirmed session from the deep link callback can be used directly if the backend returns tokens.

## Password Reset Flow

```
Client                          Backend          Email
  |                                |                |
  |-- POST /auth/password/reset -->|                |
  |   { email }                    |                |
  |<-- 200 OK --------------------|                |
  |                                |-- send email ->|
  |                                |                |
  | (user clicks link in email)    |                |
  |-- GET /auth/confirm ---------->|                |
  |   ?token_hash=...&type=recovery|                |
  |   &next=wythm://auth/callback  |                |
  |<-- redirect to deep link ------|                |
  |                                |
  | (app receives deep link with session tokens)
  |-- POST /auth/password/update ->|
  |   { password }                 |
  |   Authorization: Bearer <tok>  |
  |<-- 200 OK --------------------|
```

## User Profile Update Flow

```
Client                          Backend
  |                                |
  |-- PATCH /users/me ------------>|
  |   Authorization: Bearer <tok>  |
  |   { firstName?, lastName?,     |
  |     nativeLang?,               |
  |     interfaceLang? }           |
  |<-- 200 OK --------------------|
  |   UserResponseDto              |
```

All fields are optional — send only what changed.

## Get Current User

```
Client                          Backend
  |                                |
  |-- GET /users/me -------------->|
  |   Authorization: Bearer <tok>  |
  |<-- 200 OK --------------------|
  |   UserResponseDto              |
```

Used for: hydrating user state after app start, verifying authentication status.
