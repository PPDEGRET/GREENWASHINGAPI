# GreenCheck Testing Guide

This document provides instructions for testing the GreenCheck application, including a manual QA checklist for the user system.

## Automated Tests

The backend has a suite of automated tests that cover the core authentication and user management functionality. To run these tests, use `pytest`:

```bash
pytest
```

## Manual QA Checklist

Due to environment-specific timing issues, the full end-to-end frontend verification script is currently disabled. Please use the following manual checklist to verify the complete user flow.

**1. Open the application:**

Navigate to `http://localhost:5500`.

**2. Register a new account:**

-   Click the "Register" button.
-   Enter a valid email and password.
-   Click "Register".

**3. Complete the onboarding questionnaire:**

-   You should be redirected to the onboarding page.
-   Fill out the form with your company details.
-   Click "Save and Continue".

**4. Verify the main application view:**

-   You should be redirected to the main analysis view.
-   Verify that your name and other profile information are displayed correctly in the navigation bar.

**5. Test premium vs. non-premium features:**

-   As a non-premium user, you should see a message indicating your usage limit.
-   Attempt to perform more than 3 analyses in a day. The 4th attempt should be blocked.

**6. Log out and log back in:**

-   Click the "Logout" button.
-   You should be redirected to the landing page.
-   Click the "Login" button and enter your credentials.
-   You should be logged in and see the main application view.
-   The onboarding questionnaire should not be shown again.

## Known Limitations

-   The automated frontend tests only cover the initial page load. The full end-to-end user flow is not currently covered by automated tests.
