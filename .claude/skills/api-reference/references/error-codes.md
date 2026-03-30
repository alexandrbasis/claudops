# Error Codes Reference

## HTTP Status Codes Used by Backend

| Status | Meaning | Common causes |
|--------|---------|---------------|
| 200 | OK | Successful GET/POST/PATCH/DELETE |
| 201 | Created | Resource created successfully (signup, user creation) |
| 400 | Bad Request | Validation error, missing/malformed fields |
| 401 | Unauthorized | Missing/expired/invalid access token |
| 403 | Forbidden | Authenticated but not authorized for resource |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g. email already registered) |
| 422 | Unprocessable Entity | Valid JSON but business rule violation |
| 500 | Internal Server Error | Unexpected backend error |

## Error Response Shape

The backend returns NestJS default error responses:

```json
{
  "statusCode": 400,
  "message": "Validation failed",
  "error": "Bad Request"
}
```

For validation errors (class-validator), `message` may be an array:

```json
{
  "statusCode": 400,
  "message": ["email must be an email", "password must be longer than or equal to 6 characters"],
  "error": "Bad Request"
}
```

## Common Error Scenarios

### Authentication Errors

| Endpoint | Status | Cause | Mobile handling |
|----------|--------|-------|-----------------|
| `POST /auth/signin` | 401 | Invalid credentials | Show "Invalid email or password" |
| Any protected endpoint | 401 | Expired access token | Auto-refresh via interceptor |
| `POST /auth/refresh` | 401 | Expired/invalid refresh token | Navigate to sign-in screen |
| `POST /auth/signup` | 409 | Email already registered | Show "Account already exists" |

### Validation Errors (400)

Returned when request body fails `class-validator` checks. The `message` field is an array of validation messages. Display the first message or a generic "Please check your input" fallback.

### Network / Timeout Errors

These are not HTTP errors from the backend but Axios-level errors. Handle with:
- No response: show "No internet connection"
- Timeout: show "Request timed out, please try again"

## Axios Error Handling Pattern

```typescript
try {
  const response = await apiClient.post('/auth/signin', body);
  return response.data;
} catch (error) {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    if (status === 401) {
      throw new InvalidCredentialsError();
    }
    if (status === 400) {
      const messages = error.response?.data?.message;
      throw new ValidationError(Array.isArray(messages) ? messages[0] : messages);
    }
  }
  throw new NetworkError();
}
```

See `mobile-app/docs/http-infrastructure.md` for the full interceptor setup.
