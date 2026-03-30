# API Endpoints Reference

> Auto-generated from `backend/openapi.json`. Do not edit manually.
> Re-generate with: `npx ts-node scripts/generate-api-skill.ts` from repo root.

## POST /auth/signup
**operationId**: AuthController_signup
**Auth**: None
**Request body**: SignUpDto -- { email: string, password: string }
**Response 201**: (empty)

## POST /auth/signin
**operationId**: AuthController_signin
**Auth**: None
**Request body**: SignInDto -- { email: string, password: string }
**Response 200**: (empty)

## POST /auth/refresh
**operationId**: AuthController_refresh
**Auth**: None
**Summary**: Refresh access token using refresh token
**Request body**: RefreshTokenDto -- { refreshToken: string }
**Response 200**: Returns new tokens and user info
**Response 400**: Missing or invalid refresh token format
**Response 401**: Invalid or expired refresh token

## GET /auth/me
**operationId**: AuthController_me
**Auth**: Bearer token required
**Response 200**: (empty)

## POST /auth/signout
**operationId**: AuthController_signout
**Auth**: Bearer token required
**Response 200**: (empty)

## POST /auth/password/reset
**operationId**: AuthController_requestPasswordResetHandler
**Auth**: None
**Request body**: RequestPasswordResetDto -- { email: string }
**Response 200**: (empty)

## GET /auth/confirm
**operationId**: AuthController_confirm
**Auth**: None
**Parameters**: token_hash: string (Token hash from the email link), type: recovery|signup|email (Type of verification), next?: string (Deep link URL to redirect to after verification. Must use wythm:// scheme.)
**Response 200**: (empty)

## POST /auth/password/update
**operationId**: AuthController_updatePasswordHandler
**Auth**: Bearer token required
**Request body**: UpdatePasswordDto -- { password: string }
**Response 200**: (empty)

## POST /auth/session/bootstrap
**operationId**: AuthController_bootstrapSession
**Auth**: Bearer token required
**Response 200**: (empty)

## POST /users
**operationId**: UsersController_create
**Auth**: Bearer token required
**Request body**: CreateUserDto -- { firstName: string, lastName: string, nativeLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt, interfaceLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt }
**Response 201**: UserResponseDto -- { id: string, email: string, firstName: string, lastName: string, nativeLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt, interfaceLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt }

## GET /users/me
**operationId**: UsersController_getMe
**Auth**: Bearer token required
**Response 200**: UserResponseDto -- { id: string, email: string, firstName: string, lastName: string, nativeLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt, interfaceLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt }

## PATCH /users/me
**operationId**: UsersController_updateMe
**Auth**: Bearer token required
**Request body**: UpdateUserDto -- { email: string, firstName: string, lastName: string, nativeLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt, interfaceLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt }
**Response 200**: UserResponseDto -- { id: string, email: string, firstName: string, lastName: string, nativeLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt, interfaceLang: en|ru|he|fr|es|sr|zh_TW|zh_CN|de|pt }

## DELETE /users/me
**operationId**: UsersController_deleteMe
**Auth**: Bearer token required
**Response 200**: { ok: boolean }
