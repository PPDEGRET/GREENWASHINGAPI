🧭 Dev Checkpoint Doc — GreenCheck (AI Greenwashing Detector)

This is a living document used by AI agents to record their progress, share findings, and maintain context in the GreenCheck project.

**Last updated:** 2024-11-07 by an AI agent.
**Current objective:** Refine the unified FastAPI + static web app.

---

### Project Overview
-   **Name:** GreenCheck — AI Greenwashing Detector / Ad Screenshot Analyzer
-   **Tech Stack:** Python (FastAPI, ReportLab, OpenCV), vanilla JS/CSS/HTML
-   **Infrastructure:** Docker, GitHub Codespaces
-   **DB:** Supabase (for user data, not analysis results)
-   **Core Logic:**
    -   `ocr.py`: Extracts text from images.
    -   `judge_gpt.py`: Scores text for greenwashing risk using an LLM.
    -   `report.py`: Generates downloadable PDF reports.

---

### How to Run Locally

1.  **Backend (FastAPI):**
    ```bash
    python -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
    ```
2.  **Frontend (Static Site):**
    ```bash
    cd web && python -m http.server 5500
    ```
3.  **Access:**
    -   Frontend: `http://localhost:5500`
    -   Backend API: `http://localhost:8000`

---

### Key Findings & Agent Notes

*   **Initial setup (2024-11-04):** The repo started with a Streamlit app (`src/app.py`) and a separate Next.js marketing site (`/web-legacy`). The goal is to merge these into a single, modern user experience.
*   **Architecture shift (2024-11-06):**
    -   A new static frontend was created in `/web` (vanilla HTML/CSS/JS).
    -   A FastAPI server (`src/api.py`) was introduced to expose the core logic (OCR, judging) over a REST API.
    -   Streamlit is now considered legacy and should be phased out.
*   **CORS Configuration (as of 2024-11-07):** The FastAPI backend uses `CORSMiddleware` to allow requests from the frontend. The current configuration is permissive for local development (`allow_origins=["*"]`). This should be tightened for production.
*   **Environment Variables:** Secrets like `OPENAI_API_KEY` are loaded from a `.env` file locally and injected via Codespaces secrets in the cloud. `AGENTS.md` has the full list.
*   **Frontend State Management:** The new `/web` frontend is a single-page app that simulates different "screens" (Landing, Progress, Results) by toggling the `hidden` attribute on container divs. All logic is in `main.js`.
*   **Bug Watch:** There was a persistent CORS issue during development that was resolved by switching to a wildcard origin. This highlights the importance of checking server logs (`api_server.log`) and browser console output for connection errors.

---

### Deployment & Docker

-   GreenCheck runs in Codespaces via:
    -   `.devcontainer/devcontainer.json`: Defines the development environment.
    -   `dockerfile`: Packages the Python application.
-   The current Docker setup only runs the FastAPI backend. The static frontend is served separately. For production, these could be combined into a single container or served by a dedicated static host.

---

### User Roles & Supabase

-   **Anonymous users:** OCR + GreenCheck scoring + PDF export (no Supabase writes)
-   **Authenticated users (future):** Will have access to analysis history, saved reports, and team features. This will require integrating Supabase auth on the frontend and using the user-specific Supabase client in `db.py`.

---

✅ End of Dev Checkpoint — GreenCheck (AI Greenwashing Tool)
