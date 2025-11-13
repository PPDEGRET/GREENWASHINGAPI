from src.app.services.ocr_service import extract_text_from_image
from src.app.services.gpt_service import analyze_text_with_gpt
from src.app.services.recommendation_engine import RecommendationEngine
from src.app.schemas.analysis import AnalysisResponse

# Instantiate the engine once to be reused in all analyses
recommendation_engine = RecommendationEngine()

def analyze_image(image_bytes: bytes) -> AnalysisResponse:
    """
    Orchestrates the analysis of an image by performing OCR, rule-based analysis,
    GPT analysis, and recommendation generation.
    """
    # 1. Extract text from the image
    extracted_text = extract_text_from_image(image_bytes)

    # 2. Get GPT analysis (score, reasons, and subtle triggers)
    gpt_analysis = analyze_text_with_gpt(extracted_text)

    # 3. Detect deterministic triggers from the text
    rule_based_triggers = recommendation_engine.detect_rule_based_triggers(extracted_text)

    # 4. Combine all triggers (rule-based and GPT-based)
    all_triggers = list(set(rule_based_triggers + gpt_analysis.get("subtle_triggers", [])))

    # 5. Generate final recommendations based on the combined triggers
    recommendations = recommendation_engine.generate_recommendations(all_triggers)

    # 6. Construct the final response object
    return AnalysisResponse(
        text=extracted_text,
        score=gpt_analysis.get("risk_score"),
        level=gpt_analysis.get("level"),
        reasons=gpt_analysis.get("reasons"),
        recommendations=recommendations,
    )
