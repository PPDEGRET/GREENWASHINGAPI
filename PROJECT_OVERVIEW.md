# GreenCheck: Project Overview & Contributor Guide

## 1. Project Goal & Vision

**GreenCheck** is an AI-powered tool designed to analyze marketing and advertising materials for potential "greenwashing." The primary goal is to provide users with an instant risk assessment, identifying vague, misleading, or unsubstantiated environmental claims that could mislead consumers and create regulatory risks.

The long-term vision is for GreenCheck to operate as a full-fledged SaaS platform, offering different tiers of service (e.g., free/premium) to a range of users, from marketing professionals and copywriters to legal and compliance teams. The analysis is personalized based on the user's professional context to provide the most relevant and actionable feedback.

---

## 2. High-Level Architecture

The application follows a modern, decoupled architecture consisting of a static frontend and a powerful backend API.

-   **Frontend (`/web`):** A lightweight, single-page application (SPA) built with vanilla HTML, CSS, and JavaScript. It is designed to be fast, responsive, and easy to maintain, with no build step required.
-   **Backend (`/src`):** A robust API built with Python and the **FastAPI** framework. It handles all core logic, including user authentication, image analysis, and database interactions.

---

## 3. Backend Deep Dive (`/src/app`)

The backend is organized into a modular, service-oriented structure.

-   **Technology Stack:**
    -   **FastAPI:** For building the high-performance, async-ready API.
    -   **SQLAlchemy:** As the ORM for all database interactions.
    -   **Alembic:** For managing database schema migrations.
    -   **Pydantic:** For data validation and API schema definition.
    -   **FastAPI-Users:** To handle the core user authentication and management system.

-   **Directory Structure:**
    -   `main.py`: The entry point of the FastAPI application, where middleware and routers are configured.
    -   `routers/`: Contains the API endpoints, separating concerns (e.g., `auth.py`, `analysis.py`).
    -   `services/`: Holds the business logic (e.g., `analysis_service.py`, `usage_service.py`, `gpt_service.py`).
    -   `models/`: Defines the SQLAlchemy ORM models (e.g., `user.py`, `usage.py`).
    -   `schemas/`: Contains the Pydantic models used for API request/response validation.
    -   `db/`: Manages the database connection and session handling.
    -   `auth/`: Contains authentication-specific logic, including dependencies and the user manager.

-   **Core Analysis Pipeline (`analysis_service.py`):**
    1.  Text is extracted from the uploaded image using an OCR service.
    2.  The extracted text is sent to the `gpt_service.py`.
    3.  A **personalized system prompt** is constructed based on the user's profile (sector, role, etc.).
    4.  OpenAI's GPT model analyzes the text against this personalized prompt, returning a risk score, reasons, and recommendations.
    5.  The results are augmented with a rule-based engine (`recommendation_engine.py`) for more deterministic feedback.

-   **User & Authentication System:**
    -   Authentication is **optional**. Anonymous users can use the core tool with usage limits.
    -   Anonymous usage is tracked by IP address in the `usage_logs` table.
    -   Authenticated users are managed by FastAPI-Users, using JWTs stored in secure, HTTP-only cookies.
    -   The `/api/v1/analyze` endpoint uses an optional authentication dependency (`get_optional_current_user`) to handle both anonymous and authenticated requests gracefully.
    -   Onboarding is required for authenticated users to personalize their experience.

---

## 4. Frontend Deep Dive (`/web`)

The frontend is a vanilla single-page application.

-   **Technology Stack:** Plain HTML, CSS, and JavaScript. This was a deliberate choice to ensure maximum performance and simplicity, with no build dependencies.

-   **Structure:**
    -   `index.html`: A single HTML file that contains different "views" (e.g., `<div id="view-app">`, `<div id="view-login">`).
    -   `main.js`: The heart of the frontend. It manages all application state, API communication, and view rendering. It dynamically shows/hides views to simulate a multi-page experience.
    -   `styles.css`: Contains all the styles for the application.

-   **State Management & Logic (`main.js`):**
    -   A simple `state` object holds the current user's information.
    -   The `router()` function determines which view to display based on the URL hash (`#app`, `#history`) and the user's authentication/onboarding status.
    -   Authentication views (login, register, onboarding) are rendered as modals that appear over the main application view.
    -   API communication is handled via a wrapper function, `apiFetch`, which automatically includes credentials (`credentials: 'include'`) to support the cookie-based authentication.

---

## 5. Development & Operations

-   **Running the Project:** The easiest way to get started is to use the unified development script, `./run_dev.sh` (or `.\run_dev.bat` on Windows). This script automatically:
    1.  Applies any pending database migrations using `alembic upgrade head`.
    2.  Starts the backend FastAPI server.
    3.  Starts the frontend static file server.
-   **Configuration:** The application is configured via a `.env` file in the root directory, which should contain `OPENAI_API_KEY` and a `SECRET_KEY`.
-   **Testing:** Backend tests are written with `pytest`. Run them with the `pytest` command. For more details on manual testing, refer to `TESTING.md`.

---

## 6. Future Vision & Next Steps

This project has a strong foundation, but there are many potential avenues for future development:

-   **Full-Fledged Billing:** Integrate a payment provider like Stripe to allow users to subscribe to a premium plan.
-   **"Projects" Feature:** Allow authenticated users to group their analyses into "projects" or "campaigns" for better organization.
-   **Enhanced Personalization:** Move the personalization logic from simple `if/else` conditions to a more sophisticated, configurable system (e.g., loading rule sets from JSON or a database).
-   **UI/UX Improvements:** Flesh out the "Account" and "History" pages, and improve the visual feedback for premium-gated features.
-   **Expanded Analysis:** Incorporate more advanced analysis techniques, such as checking for misleading imagery in addition to text.
-   **Robust Frontend Testing:** Introduce a dedicated frontend testing framework (like Playwright or Cypress) into the repository for more reliable end-to-end tests.

This guide should provide a solid starting point for any developer or agent looking to contribute to GreenCheck. The key is to maintain the simplicity of the architecture while thoughtfully adding new, valuable features.
