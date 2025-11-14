from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import StreamingResponse
from src.app.schemas.analysis import AnalysisResponse
from src.app.models.user import User
from src.app.routers.auth import current_user
from src.app.services import usage_service
import time
from src.app.services.analysis_service import analyze_image
from src.app.services.pdf_service import PDFService
import io
from typing import Any

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image_endpoint(
    file: UploadFile = File(...), user: User = Depends(current_user)
) -> AnalysisResponse:
    """Accept an image file, perform analysis, and return the results."""
    start_time = time.time()

    if not await usage_service.can_user_perform_analysis(user):
        raise HTTPException(
            status_code=429, detail="Usage limit exceeded. Please upgrade to premium."
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis_results = analyze_image(image_bytes, user)

    duration_ms = int((time.time() - start_time) * 1000)
    await usage_service.log_analysis(
        user=user,
        input_type="image",
        result_json=analysis_results.model_dump(),
        duration_ms=duration_ms,
    )

    return analysis_results


@router.post("/report.pdf")
async def generate_report_endpoint(file: UploadFile = File(...)):
    """Accept an image file, perform analysis, and return a PDF report."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis_results = analyze_image(image_bytes)

    # PDFService expects a dict-like object (uses `.get`); normalize here.
    analysis_data: Any
    if hasattr(analysis_results, "model_dump"):
        analysis_data = analysis_results.model_dump()
    elif hasattr(analysis_results, "dict"):
        analysis_data = analysis_results.dict()
    else:
        analysis_data = analysis_results

    pdf_service = PDFService(image_bytes, analysis_data)
    pdf_bytes, filename = pdf_service.generate_report()

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
