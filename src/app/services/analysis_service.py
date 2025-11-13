from src.app.services.ocr_service import extract_text_from_image
from src.app.services.gpt_service import analyze_text_with_gpt
from typing import Dict, Any

def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Orchestrates the analysis of an image by performing OCR and then GPT analysis.
    """
    extracted_text = extract_text_from_image(image_bytes)
    gpt_analysis = analyze_text_with_gpt(extracted_text)

    # Use recommendations coming from the GPT analysis when available. If the
    # model did not return any, expose an empty list rather than static
    # placeholders so the frontend can decide how to handle it.
    recommendations = gpt_analysis.get("recommendations")
    if not isinstance(recommendations, list):
        recommendations = []

    return {
        "text": extracted_text,
        "score": gpt_analysis.get("risk_score"),
        "level": gpt_analysis.get("level"),
        "reasons": gpt_analysis.get("reasons"),
        "recommendations": recommendations,
    }
