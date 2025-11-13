# src/analyzer.py
from typing import Any, Dict, List, Optional
import os

from config import AppConfig
from judge_gpt import judge_with_gpt
from ocr import extract_text
from recommender import get_recommendations
from risk_rules import evaluate_rules
import utils

config = AppConfig()

def analyze_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Full pipeline for analyzing an image for greenwashing risk.
    Orchestrates OCR, rule-based analysis, and LLM judging.
    """
    text = extract_text(image_bytes)
    rule_results = evaluate_rules(text)
    llm_results = judge_with_gpt(text)

    # Combine scores and recommendations
    final_score = combine_scores(rule_results.get("score", 0), llm_results.get("risk_score", 0))
    recommendations = get_recommendations(rule_results.get("triggers", []))

    return {
        "text": text,
        "score": final_score,
        "level": get_risk_level(final_score),
        "triggers": rule_results.get("triggers", []),
        "reasons": llm_results.get("reasons", []),
        "recommendations": recommendations,
    }

def combine_scores(rule_score: int, llm_score: Optional[int]) -> int:
    """Combine GreenCheck rule score with an LLM judge score."""
    if llm_score is None:
        return rule_score
    # Weighted average, giving more weight to the LLM
    return int(rule_score * 0.3 + llm_score * 0.7)

def get_risk_level(score: int) -> str:
    """Convert a numeric score to a risk level."""
    if score >= 75:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"
