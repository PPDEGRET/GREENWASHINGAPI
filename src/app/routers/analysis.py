from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from src.app.schemas.analysis import AnalysisResponse
from src.app.models.user import User
from src.app.auth.dependencies import get_optional_current_user
from src.app.services import usage_service
import time
from src.app.services.analysis_service import analysis_service  # Updated import
from src.app.services.pdf_service import PDFService
import io
from typing import Any

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image_endpoint(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_optional_current_user),
) -> AnalysisResponse:
    """Accept an image file, perform analysis, and return the results."""
    start_time = time.time()

    ip_address = request.client.host
    if not await usage_service.can_perform_analysis(user=user, ip_address=ip_address):
        summary = await usage_service.get_usage_summary(user=user, ip_address=ip_address)
        raise HTTPException(
            status_code=429,
            detail={
                "code": "USAGE_LIMIT_EXCEEDED",
                "message": "Usage limit exceeded. Please upgrade to premium or log in.",
                **summary,
            },
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis_results = analysis_service.analyze_image(image_bytes)  # Use the service instance

    duration_ms = int((time.time() * 1000) - (start_time * 1000))
    await usage_service.log_analysis(
        input_type="image",
        result_json=analysis_results,
        duration_ms=duration_ms,
        user=user,
        ip_address=ip_address,
    )

    return AnalysisResponse(**analysis_results)


@router.post("/report.pdf")
async def generate_report_endpoint(file: UploadFile = File(...)):
    """Accept an image file, perform analysis, and return a PDF report."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis_results = analysis_service.analyze_image(image_bytes)

    # PDFService expects a dict-like object
    analysis_data = analysis_results

    pdf_service = PDFService(image_bytes, analysis_data)
    pdf_bytes, filename = pdf_service.generate_report()

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
