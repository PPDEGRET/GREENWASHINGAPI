# GreenCheck — AI Greenwashing Detector

GreenCheck reviews advertising creatives for potential greenwashing claims. The project now ships as a FastAPI backend with a static, responsive web frontend.

This repository contains the full source for the GreenCheck application, including:
-   `/web`: A vanilla HTML/CSS/JS single-page application for the user interface.
-   `/src`: The Python-based backend, including a FastAPI server and the core analysis logic.

## Running Locally

To run GreenCheck locally, you'll need two separate terminal sessions.

**1. Start the Backend API:**
```bash
# From the root of the project
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

**2. Start the Frontend Server:**
```bash
# From the web directory
cd web
python -m http.server 5500
```

Once both servers are running, you can access the application at `http://localhost:5500`.

## About GreenCheck

GreenCheck is designed to help marketing, legal, and sustainability teams identify and mitigate greenwashing risks before campaigns go live. It uses a combination of Optical Character Recognition (OCR) and a Large Language Model (LLM) to analyze advertising materials and provide a risk score, detailed feedback, and recommendations for improvement.
