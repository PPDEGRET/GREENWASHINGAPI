"""FastAPI application exposing OCR, analysis, and reporting endpoints."""
from __future__ import annotations

import base64
from io import BytesIO
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

import ocr as ocr_module
from analyzer import analyze_text
from ocr import extract_text
from recommender import recommend
from report import build_report

app = FastAPI(
    title="LeafCheck API",
    description="Programmatic access to LeafCheck OCR, analysis, and reporting engines.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://0.0.0.0:3000",
    ],
    allow_origin_regex=r"https?://localhost(:\\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    risk_level: str
    score: int
    triggers: Dict[str, Any]
    rationale: str
    recommendations: list[str]
    raw: Dict[str, Any]


class ReportRequest(BaseModel):
    text: str
    analysis: Dict[str, Any]
    image_base64: Optional[str] = None


@app.post("/api/ocr")
async def run_ocr(image: UploadFile = File(...)) -> Dict[str, Any]:
    """Run OCR on an uploaded image and return extracted text."""
    if getattr(ocr_module, "RapidOCR", None) is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "OCR backend unavailable: install rapidocr-onnxruntime to enable OCR. "
                "Text can still be analyzed by pasting it manually."
            ),
        )

    payload = await image.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file was empty.")

    try:
        text = extract_text(payload)
    except Exception as exc:  # pragma: no cover - rely on existing Streamlit helpers.
        raise HTTPException(status_code=500, detail="OCR processing failed.") from exc

    return {"text": text, "spans": [], "confidences": []}


def _compose_rationale(analysis: Dict[str, Any]) -> str:
    """Build a concise rationale string from analyzer output."""
    label = str(analysis.get("ai_label", "—") or "—")
    try:
        confidence = float(analysis.get("ai_confidence", 0.0) or 0.0)
    except (TypeError, ValueError):
        confidence = 0.0
    breakdown = analysis.get("breakdown", {}) or {}
    risk_strength = breakdown.get("risk_strength")
    evidence_strength = breakdown.get("evidence_strength")
    parts = [
        f"Model highlight: {label} ({confidence:.1f}% confidence)."
    ]
    if isinstance(risk_strength, (int, float)):
        parts.append(f"Risk strength {float(risk_strength):.2f}.")
    if isinstance(evidence_strength, (int, float)):
        parts.append(f"Evidence strength {float(evidence_strength):.2f}.")
    return " ".join(parts)


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze supplied text and return a structured risk summary."""
    text = (request.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Provide text to analyze.")

    analysis = analyze_text(text)
    triggers = analysis.get("triggers", {}) or {}
    recs = recommend(triggers, text)
    rationale = _compose_rationale(analysis)

    return AnalyzeResponse(
        risk_level=str(analysis.get("level", "Unknown") or "Unknown"),
        score=int(analysis.get("score", 0) or 0),
        triggers=triggers,
        rationale=rationale,
        recommendations=recs,
        raw=analysis,
    )


def _resolve_image_bytes(image_base64: Optional[str]) -> bytes:
    if not image_base64:
        return b""
    try:
        return base64.b64decode(image_base64)
    except (ValueError, TypeError) as exc:  # pragma: no cover - defensive fallback.
        raise HTTPException(status_code=400, detail="Invalid base64 image payload.") from exc


@app.post("/api/report")
async def report(request: ReportRequest) -> StreamingResponse:
    """Generate a PDF report from text + prior analysis."""
    analysis = request.analysis or {}
    if not isinstance(analysis, dict):
        raise HTTPException(status_code=400, detail="Analysis payload must be an object.")

    image_bytes = _resolve_image_bytes(request.image_base64)
    pdf_bytes, filename = build_report(image_bytes, request.text or "", analysis)
    buffer = BytesIO(pdf_bytes)
    headers = {
        "Content-Disposition": f"attachment; filename={filename}",
        "X-LeafCheck-Filename": filename,
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)


@app.get("/healthz")
async def healthcheck() -> JSONResponse:
    """Lightweight health probe for infrastructure."""
    available = getattr(ocr_module, "RapidOCR", None) is not None
    return JSONResponse({"status": "ok", "ocr_available": available})
