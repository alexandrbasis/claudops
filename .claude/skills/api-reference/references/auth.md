# Authentication Reference

## Bearer Token Auth

All protected endpoints require a JWT access token in the `Authorization` header:

```
Authorization: Bearer <accessToken>
```

Endpoints marked `**Auth**: Bearer token required` in `endpoints.md` require this header. Requests without it return `401 Unauthorized`.

## Sign-In Flow

1. Call `POST /auth/signin` with `{ email, password }`
2. On success (200), store the returned `accessToken` and `refreshToken`
3. Include `accessToken` in all subsequent protected requests

### Mobile app token storage

Tokens are persisted via `TokenStore` (see `mobile-app/docs/http-infrastructure.md`).
The Axios interceptor automatically attaches the access token to every request.

## Token Refresh

When a protected endpoint returns `401`, refresh the access token:

1. Call `POST /auth/refresh` with `{ refreshToken }`
2. On success (200), replace stored `accessToken` (and `refreshToken` if rotated)
3. Retry the original request

The mobile app's Axios interceptor handles refresh automatically (see `mobile-app/docs/http-infrastructure.md`).

## Session Bootstrap

After sign-in, call `POST /auth/session/bootstrap` to initialize the user's session state (e.g. set up vocabulary lists). This is called once after successful authentication.

## Sign-Out

Call `POST /auth/signout` to invalidate the session server-side. Clear stored tokens on the mobile side after this call.

## Password Reset Flow

1. `POST /auth/password/reset` — send reset email (no auth required, just `{ email }`)
2. User clicks link in email → `GET /auth/confirm?token_hash=...&type=recovery&next=wythm://auth/callback`
3. App receives deep link callback, user enters new password
4. `POST /auth/password/update` with `{ password }` (requires Bearer token from the confirmed session)

## 401 Handling

| Cause | Fix |
|-------|-----|
| Access token expired | Call `POST /auth/refresh`, retry original request |
| Refresh token expired/invalid | Re-authenticate (send user to sign-in screen) |
| Missing `Authorization` header | Ensure `TokenStore` has a token and interceptor is active |
| Invalid credentials (sign-in) | Show error to user — do not retry automatically |
