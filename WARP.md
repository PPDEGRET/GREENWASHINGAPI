# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

---

## Project Overview

GreenCheck is an "AI greenwashing detector" that scores marketing creatives (images) for greenwashing risk.

The current architecture is:

- **Backend API (canonical):** FastAPI app in `src/app/main.py` exposing `/api/v1` endpoints.
- **Frontend SPA (canonical):** Static HTML/CSS/JS in `web/` served as a single-page app.
- **Legacy code:** Older Streamlit and Next.js implementations plus top-level `src/*.py` utilities. Treat these as legacy unless explicitly asked to modify them.

Prefer working in `src/app` (backend) and `web/` (frontend) for new features and fixes.

---

## How to Run the App Locally

### 1. Environment setup

From the repo root:

- Create and activate a virtualenv (recommended):
  - **Windows (PowerShell):** `python -m venv venv; .\venv\Scripts\Activate.ps1`
  - **macOS/Linux:** `python -m venv venv && source venv/bin/activate`
- Install backend dependencies:
  - `pip install -r requirements.txt`
- Configure environment variables in `.env` (root):
  - At minimum: `OPENAI_API_KEY=...`
  - Project-specific variables (see `AGENTS.md`): `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE`, `APP_BASE_URL`.

Tesseract OCR must be installed on the system for `pytesseract` to work.

### 2. Recommended dev commands

#### One-shot helper scripts

- **Windows:** `run_dev.bat`
  - Starts FastAPI backend with: `uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload`
  - Starts static frontend with: `python -m http.server 5500 -d web`
- **macOS/Linux:** `./run_dev.sh`
  - Uses `./run_api.sh` (if present) to start the backend and `python -m http.server 5500 -d web` for the frontend.

After either script, access:

- Frontend: `http://localhost:5500`
- Backend API: `http://localhost:8000`

#### Manual backend/frontend commands (useful in CI or separate terminals)

From repo root, with venv active:

- **Backend (FastAPI):**
  - `python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Frontend (static web):**
  - `python -m http.server 5500 -d web`

> Note: `web/main.js` expects the API at `http://localhost:8000/api/v1`.

#### Devcontainer / Docker

- `.devcontainer/devcontainer.json` and `dockerfile` currently reference `src.api:app`; the canonical app entrypoint is now `src.app.main:app`.
- If you need to run via container, update these to point at `src.app.main:app` before relying on them for new flows.

---

## Testing & Quality Checks

### Python tests (FastAPI + services)

From repo root with dependencies installed:

- Run all tests:
  - `pytest`
- Verbose output:
  - `pytest -v`
- Single test file (example):
  - `pytest tests/test_gpt_service.py`
- Single test case (example):
  - `pytest tests/test_gpt_service.py::TestGetClient::test_get_client_raises_runtime_error_when_api_key_missing`
- Coverage (if `pytest-cov` is available):
  - `pytest --cov=src --cov-report=html`

### Linting / formatting (from `AGENTS.md`)

These tools are not in `requirements.txt` and may need to be installed separately (`pip install black ruff`):

- Format a Python file:
  - `python -m black path/to/file.py`
- Lint/fix a Python file:
  - `python -m ruff check --fix path/to/file.py`

### Frontend formatting (from `AGENTS.md`)

- Format web assets (requires Node/Prettier):
  - `npx prettier --write web/index.html web/styles.css web/main.js`

---

## Backend Architecture (FastAPI Layered Design)

The FastAPI backend is organized in a classic layered structure under `src/app`:

- **Entry point:**
  - `src/app/main.py`
    - Loads environment variables early via `dotenv.load_dotenv()` so the OpenAI client and other modules see them.
    - Creates the `FastAPI` app (`"GreenCheck API", version "2.0.0"`).
    - Configures CORS for local origins: `http://localhost`, `http://localhost:5500`, `http://127.0.0.1:5500`.
    - Includes the analysis router under `/api/v1`.
    - Exposes `/health` for a simple readiness check.

- **Routing layer:**
  - `src/app/routers/analysis.py`
    - `POST /api/v1/analyze`:
      - Accepts an image file upload, validates content type and non-emptiness.
      - Delegates to `src.app.services.analysis_service.analyze_image`.
      - Returns an `AnalysisResponse` model as JSON.
    - `POST /api/v1/report.pdf`:
      - Accepts an image upload, reuses the same `analyze_image` pipeline.
      - Uses `PDFService` to generate a PDF report and streams it back as `application/pdf`.

- **Schema layer (Pydantic models):**
  - `src/app/schemas/analysis.py`
    - `RecommendationItem` describes structured recommendations (type, message, severity, triggered_by).
    - `AnalysisResponse` wraps the full response shape consumed by the frontend: `score`, `level`, `reasons`, `text`, `recommendations`.
  - `src/app/schemas/report.py`
    - Placeholder `ReportResponse` model (current PDF endpoint returns a binary stream instead).

- **Service layer (core logic):**
  - `src/app/services/analysis_service.py`
    - Orchestrates the full pipeline:
      1. OCR via `extract_text_from_image`.
      2. GPT-based qualitative analysis via `analyze_text_with_gpt`.
      3. Rule-based trigger detection via `RecommendationEngine.detect_rule_based_triggers`.
      4. Combination of GPT `subtle_triggers` and deterministic triggers.
      5. Recommendation generation into `RecommendationItem` objects.
    - Returns a fully populated `AnalysisResponse` instance.
  - `src/app/services/ocr_service.py`
    - Wraps Tesseract (`pytesseract`) to extract text from uploaded image bytes using Pillow.
    - Returns a stripped string; on failure logs and returns an empty string.
  - `src/app/services/gpt_service.py`
    - Responsible for all OpenAI calls.
    - `_get_client()` reads `OPENAI_API_KEY` from the environment (via `dotenv` and `os.getenv`) and fails loudly if missing.
    - Uses `OpenAI().chat.completions.create` with a detailed `SYSTEM_PROMPT` focused on subtle greenwashing patterns.
    - Forces `response_format={"type": "json_object"}` and parses/normalizes the result into `risk_score`, `level`, `reasons`, `subtle_triggers`.
    - On any exception, logs and returns a low-risk placeholder with a reason indicating configuration problems.
  - `src/app/services/recommendation_engine.py`
    - Hybrid rule engine that maps deterministic textual patterns to recommendation templates.
    - `detect_rule_based_triggers(text)` uses regexes to detect:
      - **`superlatives`** ("100%", "eco-friendly", "carbon neutral", etc.).
      - **`future_claims`** ("net-zero", "by 2040", goal-style phrasing).
      - **`offsets`** ("offset", "carbon credit", etc.).
    - `generate_recommendations(triggers)` converts triggers into structured `RecommendationItem` objects using an internal map of templates.
  - `src/app/services/pdf_service.py`
    - Builds a `reportlab` PDF including:
      - Title header.
      - Uploaded image.
      - Extracted text.
      - Risk score, risk level, and bullet-point reasons.
    - Returns `(pdf_bytes, filename)` where filename is `GreenCheck_Report_<YYYY-MM-DD>.pdf`.

- **Tests (back-end focused):**
  - `tests/test_main.py` ensures `dotenv` is loaded at startup and `src.app.main` imports cleanly.
  - `tests/test_analysis.py` tests the `/api/v1/analyze` endpoint end-to-end via `TestClient`, mocking `analyze_image`.
  - `tests/test_recommendation_engine.py` covers trigger detection and recommendation mapping.

When adding new backend features, follow this pattern: define Pydantic schemas, add service-layer functions, expose them via routers, and cover them with `pytest` tests under `tests/`.

---

## Frontend Architecture (Static SPA in `web/`)

The frontend is a static single-page app with no bundler or framework:

- **HTML shell:** `web/index.html`
  - Defines three main UI "states" as top-level containers:
    - `#app-state-landing` – initial upload/hero and 3-step overview.
    - `#app-state-progress` – analysis-in-progress card with spinner and step list.
    - `#app-state-results` – displays score donut, risk level, reasons, recommendations, and action buttons.
  - Uses `hidden` attributes (toggled by JS) to simulate navigation.
  - Loads Manrope font via Google Fonts and Font Awesome icons via CDN.

- **Client logic:** `web/main.js`
  - Uses a simple `state` object to track the current file.
  - Hard-codes `API_BASE_URL = "http://localhost:8000/api/v1"`.
  - Core flows:
    - `switchState(newState)` toggles the `hidden` attribute on state containers.
    - `handleFileUpload(file)` sets `state.file`, switches to `progress`, sends `FormData` with `file` to `POST /analyze`, then on success calls `renderResults` and switches to `results`.
    - `renderResults(data)`:
      - Renders donut chart via `drawDonut(score)` (SVG-based, with color coded by risk range).
      - Sets risk level and reasons.
      - Handles recommendations from the backend:
        - If `data.recommendations` is present, assumes an array of either `RecommendationItem`-like objects or strings and normalizes to messages.
        - Falls back to static placeholder recommendations only when talking to older backends that omit the `recommendations` field entirely.
    - `downloadPdfBtn` posts the stored `state.file` to `/report.pdf` and downloads the resulting blob as `GreenCheck_Report.pdf`.
    - `reanalyzeBtn` clears `state.file` and returns to `landing` state.
  - Drag-and-drop and click-to-upload for the main dropzone; file input is hidden.

- **Styling:** `web/styles.css`
  - Uses CSS custom properties (color, spacing, typography) and the Manrope font family.
  - Implements card UI for progress and results, donut score visualization container, and responsive-ish layout via grid and flex.

When extending the UI, follow the existing pattern: add new containers or elements in `index.html`, style via CSS variables in `styles.css`, and wire behavior in `main.js` without introducing a build system unless explicitly requested.

---

## Agent / Tooling Rules from `AGENTS.md`

Key project-specific rules for AI agents (including Warp) distilled from `AGENTS.md`:

- **Canonical modules & reuse**
  - For backend changes, prefer reusing `ocr_service`, `gpt_service`, `pdf_service`, and `RecommendationEngine` rather than duplicating logic.
  - For frontend changes, work in `web/` and keep `/web-legacy` and older frameworks (Next.js, Streamlit) untouched unless explicitly instructed.

- **Environment and secrets**
  - Never hard-code `OPENAI_API_KEY`, Supabase keys, or other secrets; always read from environment or `.env` and the devcontainer `remoteEnv` mapping.
  - Relevant environment variables: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE`, `APP_BASE_URL`.

- **Design system (web + any future UI)**
  - Use Manrope typography and the existing color tokens defined in `web/styles.css`; do not introduce arbitrary hex colors.
  - Maintain the clean, card-based aesthetic already in `web/`.

- **Performance & dependencies**
  - Do not add heavy frontend frameworks or CSS utilities (e.g., no Tailwind, no React rewrite) without explicit approval.

- **Safety / scope of operations**
  - Safe to do without extra confirmation: read/list files, lint/format/test single files, make small/scoped code edits.
  - Ask before: installing/removing packages, deleting/renaming directories, or performing large refactors/repo-wide automated changes, or running production builds/deployments.

- **Interop with other AI tools**
  - If creating or updating `CLAUDE.md`, `.cursor/rules/`, etc., ensure they simply point back to and follow `AGENTS.md` for consistency.

---

## Legacy & Historical Context (from `DEV_CHECKPOINT.md`)

- Earlier versions of GreenCheck used:
  - A Streamlit UI (`src/app.py` / `_legacy_app.py`) and a Next.js marketing site under `/web-legacy`.
  - A FastAPI app at `src/api.py` referenced by Docker/devcontainer.
- The project has since converged on:
  - **FastAPI backend** under `src/app/main.py` and its routers/services.
  - **Static SPA frontend** under `web/` that talks to `/api/v1`.
- When you encounter legacy files (e.g., `src/_legacy_app.py`, `src/analyzer.py`, `src/recommender.py`, `/web-legacy`):
  - Treat them as historical reference unless a task explicitly targets them.
  - Avoid mixing legacy and current patterns (e.g., don’t pull Next.js components into `web/`).

This file should be kept up to date as the FastAPI+SPA architecture evolves; prefer updating these guidelines over adding new, conflicting ones elsewhere.
