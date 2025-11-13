from src.app.services.ocr_service import extract_text_from_image
from src.app.services.gpt_service import analyze_text_with_gpt
from typing import Dict, Any

def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Orchestrates the analysis of an image by performing OCR and then GPT analysis.
    """
    extracted_text = extract_text_from_image(image_bytes)
    gpt_analysis = analyze_text_with_gpt(extracted_text)

    # Placeholder recommendations for this iteration. In a future version, this can
    # be driven by rule-based triggers and/or richer LLM output.
    recommendations = [
        "Clarify the environmental claim with scope and metrics.",
        "Provide external certifications or third-party verification.",
        "Avoid absolute expressions such as '100% sustainable'.",
    ]

    return {
        "text": extracted_text,
        "score": gpt_analysis.get("risk_score"),
        "level": gpt_analysis.get("level"),
        "reasons": gpt_analysis.get("reasons"),
        "recommendations": recommendations,
    }
