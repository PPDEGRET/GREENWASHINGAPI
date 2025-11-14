# GreenCheck Authentication Flow

This document outlines the authentication and user management flow for the GreenCheck application.

## 1. Core Technology

The authentication system is built using **FastAPI-Users**, a robust and secure library that handles user registration, login, password management, and more. It is configured to use **JWT (JSON Web Tokens)** for authentication, with the token stored in a secure, HTTP-only cookie.

## 2. Optional Authentication

Authentication is **optional** to use the core GreenCheck tool. Anonymous users can perform analyses, while authenticated users gain access to additional features.

## 3. Authentication Flow

### 3.1. Registration

1.  A user can choose to register at any time via a modal form.
2.  The frontend sends a `POST` request to `/api/v1/auth/register`.
3.  The backend creates a new user and automatically logs them in.

### 3.2. Login

1.  A user can choose to log in at any time via a modal form.
2.  The frontend sends a `POST` request to `/api/v1/auth/jwt/login`.
3.  If successful, the backend generates a JWT and sets it in a `greencheck` cookie.

### 3.3. Authenticated Requests

1.  For all API requests, the browser automatically includes the `greencheck` cookie if it exists.
2.  The backend uses an optional authentication dependency to identify the user if a valid token is present.

## 4. Onboarding

-   Onboarding is only triggered for **authenticated users** who have not yet completed their profile.
-   After the first successful login, a modal is displayed to collect the user's profile information.

## 5. Premium Gating

-   Premium features are gated on the backend.
-   If an anonymous or non-premium user attempts to access a premium feature, the UI will prompt them to log in or upgrade.

## 6. Testing

The authentication system is tested in `tests/test_auth.py`. The tests cover:
- User registration
- User login
- Accessing a protected endpoint (`/users/me`)

**Note:** The current test suite focuses on the core authentication flows.
