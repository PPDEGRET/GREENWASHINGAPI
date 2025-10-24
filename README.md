# LeafCheck — Ad Screenshot Analyzer

Run locally:
```bash
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
streamlit run src/app.py


## 3) Push to GitHub
- Create a new public or private repo, push the project.

## 4) Deploy on Streamlit Cloud
- Go to share.streamlit.io → “New app” → select your repo/branch → `src/app.py`.
- It will auto-install `apt.txt` and `requirements.txt`.
- Set **Secrets** later if you add API keys: in the app settings → “Secrets”.

**Notes**
- Streamlit Cloud sleeps on inactivity (free plan). Wakes in a few seconds.
- If OCR gives a “tesseract not found” error, double-check `apt.txt` exists at repo root.

---

# Option B — Hugging Face Spaces (simple + free tier + good for demos)

**Good for** easy public sharing, reproducible builds, Docker optional.

## 1) Use the same repo, add one file: `runtime.txt`


## 2) Create a Space
- Go to huggingface.co → Spaces → Create → **Streamlit** template
- Connect your GitHub (or upload zip).
- Set “App File” = `src/app.py`
- “Hardware” = CPU basic.

**If Tesseract missing**  
HF Spaces Streamlit runner doesn’t install apt packages by default. If OCR fails, switch the Space **type to Docker** and use the Dockerfile below from Option C.

---

# Option C — Docker + any host (Fly.io / Render / Railway / Google Cloud Run)

**Good for** robustness, custom OS deps (e.g., Tesseract), private apps, custom domains.

## 1) Add these files (root)

### `Dockerfile`
```dockerfile
FROM python:3.11-slim

# System deps (tesseract)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr libtesseract-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage docker layer cache
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src ./src
COPY assets ./assets

# Streamlit config (headless)
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PORT=8501

EXPOSE 8501
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
