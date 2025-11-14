from typing import List, Set

from src.app.services.ocr_service import extract_text_from_image
from src.app.services.gpt_service import analyze_text_with_gpt
from src.app.services.recommendation_engine import RecommendationEngine
from src.app.schemas.analysis import AnalysisResponse, RecommendationItem

# Instantiate the engine once to be reused in all analyses
recommendation_engine = RecommendationEngine()

def _deduplicate_recommendations(recommendations: List[RecommendationItem]) -> List[RecommendationItem]:
    """Deduplicate recommendations by their message text while preserving order."""
    seen: Set[str] = set()
    deduped: List[RecommendationItem] = []
    for rec in recommendations:
        if rec.message in seen:
            continue
        seen.add(rec.message)
        deduped.append(rec)
    return deduped

def analyze_image(image_bytes: bytes) -> AnalysisResponse:
    """Orchestrate OCR, GPT analysis, rule-based analysis, and recommendation generation."""
    # 1. Extract text from the image
    extracted_text = extract_text_from_image(image_bytes)

    # 2. Get GPT analysis (score, reasons, subtle triggers, and GPT recommendations)
    gpt_analysis = analyze_text_with_gpt(extracted_text)

    # 3. Detect deterministic triggers from the text
    rule_based_triggers = recommendation_engine.detect_rule_based_triggers(extracted_text)

    # 4. Combine all triggers (rule-based and GPT-based)
    all_triggers = list(set(rule_based_triggers + gpt_analysis.get("subtle_triggers", [])))

    # 5. Generate rule-based recommendations from combined triggers
    rule_based_recs = recommendation_engine.generate_recommendations(all_triggers)

    # 6. Convert GPT recommendations (plain strings) into RecommendationItem objects
    gpt_rec_messages = gpt_analysis.get("recommendations", []) or []
    gpt_triggers = gpt_analysis.get("subtle_triggers", []) or []
    gpt_recs: List[RecommendationItem] = []
    for msg in gpt_rec_messages:
        if not msg:
            continue
        gpt_recs.append(
            RecommendationItem(
                type="gpt_insight",
                message=str(msg),
                severity=2,
                triggered_by=gpt_triggers,
            )
        )

    # 7. Merge and deduplicate recommendations (rule-based + GPT)
    combined_recs = _deduplicate_recommendations(rule_based_recs + gpt_recs)

    # 8. Construct the final response object
    return AnalysisResponse(
        text=extracted_text,
        score=gpt_analysis.get("risk_score"),
        level=gpt_analysis.get("level"),
        reasons=gpt_analysis.get("reasons"),
        recommendations=combined_recs,
    )
