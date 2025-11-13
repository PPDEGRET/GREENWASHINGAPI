# AGENTS.md — GreenCheck Project Guidelines

Project: GreenCheck — AI Greenwashing Detector
Purpose: Guide AI agents and contributors to make consistent, safe, and well-structured changes.

-------------------------------------------------------------------------------

## Architecture Overview

This project is a web application with a **static frontend** and a **Python FastAPI backend**.

- **/web**: Contains the static frontend (HTML, CSS, JS). It is a single-page application that communicates with the backend API. It has no build step.
- **/src/app**: Contains the FastAPI backend.
  - `main.py`: The FastAPI application entrypoint.
  - `routers/`: Defines the API endpoints (e.g., `/api/v1/analyze`).
  - `schemas/`: Pydantic schemas for API request and response models.
  - `services/`: Contains the core business logic.
    - `ocr_service.py`: Text extraction from images.
    - `gpt_service.py`: Provides a base risk score and identifies **subtle** greenwashing triggers.
    - `recommendation_engine.py`: A hybrid engine that uses rule-based detection and GPT input to generate structured, actionable recommendations.
    - `analysis_service.py`: Orchestrates the entire analysis pipeline.
- **/tests**: Contains `pytest` tests for the backend.

**Key Logic Flow:**
1.  The frontend uploads an image to `/api/v1/analyze`.
2.  `analysis_service` coordinates the workflow:
3.  `ocr_service` extracts text.
4.  `recommendation_engine` detects deterministic triggers (e.g., "100% green").
5.  `gpt_service` provides a risk score, reasons, and detects subtle triggers (e.g., omissions).
6.  `recommendation_engine` merges all triggers and generates a final list of structured recommendations.
7.  The structured response is sent to the frontend.

-------------------------------------------------------------------------------

## Development Environment

- **Environment Variables**: A `.env` file is required for local development, primarily for the `OPENAI_API_KEY`.
- **Dependencies**: Install Python dependencies from `requirements.txt` using `pip install -r requirements.txt`.
- **Running Locally**: Use the unified script `./run_dev.sh` to start both the backend and frontend servers.
  - Backend API will be available at `http://localhost:8000`.
  - Frontend will be available at `http://localhost:8888`.

-------------------------------------------------------------------------------

## Best Practices

### General
- **Code Style**: Follow Black for Python and Prettier for frontend code. Use `ruff` for linting.
- **Commits**: Keep commits atomic and write clear, descriptive messages.
- **Testing**: All new backend logic should be accompanied by `pytest` tests. Ensure the test suite passes before submitting changes.

### Backend
- **Modularity**: Keep services focused on a single responsibility.
- **Schemas**: All API responses should be strictly defined with Pydantic schemas.
- **Configuration**: Do not hard-code secrets or configuration values. Use environment variables.

### Frontend
- **Simplicity**: The frontend is a static site. Do not add complex build tools (e.g., Webpack, React) without explicit approval.
- **Styling**: Use the existing CSS variables in `web/styles.css` for consistency.
- **API Interaction**: All API calls should be centralized and handle potential errors gracefully.

-------------------------------------------------------------------------------

## File-Scoped Commands

- **Python Formatting**: `python -m black .`
- **Python Linting**: `python -m ruff check --fix .`
- **Running Tests**: `python -m pytest`
- **Frontend Formatting**: `npx prettier --write "web/**/*.html" "web/**/*.css" "web/**/*.js"`

-------------------------------------------------------------------------------
