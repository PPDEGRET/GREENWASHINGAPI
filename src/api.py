"""FastAPI application exposing OCR, GPT judging, and report generation endpoints."""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from judge_gpt import judge_with_gpt
from ocr import extract_text
from report import build_report

load_dotenv()

app = FastAPI(title="GreenCheck API", version="1.0.0")

# Define allowed origins for local development
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5500",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
]

# In a production environment, you would fetch this from an environment variable
# prod_origins = os.environ.get("PROD_ORIGINS", "").split(",")
# origins.extend([origin for origin in prod_origins if origin])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    """Basic health probe used by infrastructure and smoke tests."""
    return {"status": "ok"}


async def _read_upload(file: UploadFile) -> bytes:
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file was empty.")
    return payload


def _normalise_judge_output(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        data = {
            "risk_score": 0,
            "level": "Low",
            "reasons": ["LLM judge error."],
            "_error": True,
        }
    score = int(data.get("risk_score", 0) or 0)
    level = str(data.get("level", "Low") or "Low")
    reasons = data.get("reasons", []) or []
    if isinstance(reasons, str):
        reasons = [reasons]
    reasons = [str(reason) for reason in reasons if reason]
    return {"risk_score": score, "level": level, "reasons": reasons, **data}


@app.post("/analyze")
async def analyze_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """Perform OCR then GPT judging, returning the consolidated payload."""
    blob = await _read_upload(file)
    text = extract_text(blob) or ""
    judge_data = _normalise_judge_output(judge_with_gpt(text))
    response = {
        "score": int(judge_data.get("risk_score", 0) or 0),
        "level": str(judge_data.get("level", "Low") or "Low"),
        "reasons": judge_data.get("reasons", []) or [],
        "text": text,
    }
    return JSONResponse(content=response)


@app.post("/report.pdf")
async def report_endpoint(file: UploadFile = File(...)) -> StreamingResponse:
    """Generate a PDF report from the uploaded asset and GPT analysis."""
    blob = await _read_upload(file)
    text = extract_text(blob) or ""
    judge_data = _normalise_judge_output(judge_with_gpt(text))
    results = {
        "score": int(judge_data.get("risk_score", 0) or 0),
        "level": str(judge_data.get("level", "Low") or "Low"),
        "ai_label": "GPT Review",
        "ai_confidence": 100.0,
        "triggers": {},
        "reasons": judge_data.get("reasons", []) or [],
    }
    pdf_bytes, filename = build_report(blob, text, results)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
