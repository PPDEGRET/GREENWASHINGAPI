# GreenCheck Authentication Flow

This document outlines the authentication and user management flow for the GreenCheck application.

## 1. Core Technology

The authentication system is built using **FastAPI-Users**, a robust and secure library that handles user registration, login, password management, and more. It is configured to use **JWT (JSON Web Tokens)** for authentication, with the token stored in a secure, HTTP-only cookie.

## 2. Authentication Flow

### 2.1. Registration

1.  A new user navigates to the registration page and submits their email and password.
2.  The frontend sends a `POST` request to `/api/v1/auth/register`.
3.  The backend validates the data, hashes the password, and creates a new user in the `users` table with `is_active=true` and `is_verified=false`.
4.  Upon successful registration, the user is automatically logged in.

### 2.2. Login

1.  An existing user navigates to the login page and submits their email and password.
2.  The frontend sends a `POST` request to `/api/v1/auth/jwt/login`.
3.  The backend verifies the credentials.
4.  If successful, the backend generates a JWT and sets it in a `greencheck` cookie.

### 2.3. Authenticated Requests

1.  For all subsequent requests to protected endpoints, the browser automatically includes the `greencheck` cookie.
2.  The backend validates the JWT from the cookie to identify and authenticate the user.

## 3. Onboarding

-   After the first successful login, the user is required to complete an onboarding questionnaire.
-   The frontend displays the onboarding form, and the user's profile information is collected.
-   This data is submitted via a `POST` request to `/api/v1/me/onboarding`.
-   The user cannot access the main application features until the onboarding is complete.

## 4. Premium Gating

-   Certain features are restricted to premium users.
-   API endpoints for these features are protected by a dependency that checks the `is_premium` flag on the user's profile.
-   If a non-premium user attempts to access a premium endpoint, the API will return a `403 Forbidden` error.

## 5. Testing

The authentication system is tested in `tests/test_auth.py`. The tests cover:
- User registration
- User login
- Accessing a protected endpoint (`/users/me`)

**Note:** The current test suite focuses on the core authentication flows. More advanced asynchronous scenarios are not yet fully covered.
