# LeafCheck — AI Greenwashing Detector

LeafCheck reviews advertising creatives for potential greenwashing claims. The project now ships as a FastAPI backend with a static, responsive web frontend.

## Architecture Overview
- **Backend** — `src/api.py` (FastAPI) reuses the OCR, GPT judging, and PDF report helpers found in `src/ocr.py`, `src/judge_gpt.py`, and `src/report.py`.
- **Frontend** — `/web` is a single-page static site served with any static file host. It talks to the API via HTTP.
- **Legacy UI** — The original Streamlit dashboard lives in `src/_legacy_app.py` for reference but is no longer started by default.

## Prerequisites
- Python 3.11+
- An `.env` file that exposes the existing variables (`OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE`, `APP_BASE_URL`). See `.env.example` for placeholders.

## Local Development
Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the FastAPI backend
```bash
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Serve the static frontend
```bash
cd web
python -m http.server 5500
```

Open http://localhost:5500 in your browser. The page calls the API at `http://localhost:8000` for OCR, GPT judging, and PDF exports.

### Optional: Legacy Streamlit dashboard
```bash
streamlit run src/_legacy_app.py --server.address=0.0.0.0 --server.port=8501
```

## API Endpoints
- `GET /health` → `{"status": "ok"}`
- `POST /ocr` (multipart `file`) → `{"text": "..."}`
- `POST /judge` (`text` form field) → GPT risk assessment payload
- `POST /analyze` (multipart `file`) → `{ "score", "level", "reasons", "text" }`
- `POST /report.pdf` (multipart `file`) → Streams a generated PDF download

All endpoints share the existing environment configuration loaded via `python-dotenv`.

## Docker
Build and run the API with uvicorn:

```bash
docker build -t leafcheck .
docker run --rm -p 8000:8000 --env-file .env leafcheck
```

Then serve `/web` with any static host (e.g., `python -m http.server 5500`).

## Contributing
- Keep CSS tokens and typography consistent with the design system in `AGENTS.md`.
- Ensure OCR, GPT, and PDF flows continue to work end-to-end.
- Do not commit secrets; rely on environment variables and `.env` files for local development.
