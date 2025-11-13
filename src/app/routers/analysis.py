from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from src.app.schemas.analysis import AnalysisResponse
from src.app.services.analysis_service import analyze_image
from src.app.services.pdf_service import PDFService
import io

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Accepts an image file, performs analysis, and returns the results.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis_results = analyze_image(image_bytes)
    return JSONResponse(content=analysis_results)

@router.post("/report.pdf")
async def generate_report_endpoint(file: UploadFile = File(...)):
    """
    Accepts an image file, performs analysis, and returns a PDF report.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis_results = analyze_image(image_bytes)

    pdf_service = PDFService(image_bytes, analysis_results)
    pdf_bytes, filename = pdf_service.generate_report()

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
