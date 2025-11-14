# src/app/services/analysis_service.py
from typing import Any, Dict, List
from .rules_engine import rules_engine
from .ocr_service import extract_text_from_image
from .gpt_service import analyze_text_with_gpt

class AnalysisService:
    def __init__(self, rules_engine):
        self.rules_engine = rules_engine

    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Refactored analysis pipeline with distinct stages.
        """
        # Stage 1: OCR
        ocr_text = extract_text_from_image(image_bytes)

        # Stage 2: Claim Extraction (for now, we'll treat the whole text as a single claim)
        claims = self._extract_claims(ocr_text)

        # Stage 3: Scoring (Rule-based and GPT)
        rule_matches = self._score_with_rules(claims)
        gpt_analysis = self._score_with_gpt(claims)

        # Stage 4: Aggregation
        final_result = self._aggregate_results(rule_matches, gpt_analysis)

        return final_result

    def _extract_claims(self, text: str) -> List[str]:
        # Placeholder for a more sophisticated claim extraction logic.
        # For now, we'll just split the text into sentences.
        return [sentence.strip() for sentence in text.split('.') if sentence.strip()]

    def _score_with_rules(self, claims: List[str]) -> List[Dict[str, Any]]:
        all_matches = []
        for claim in claims:
            all_matches.extend(self.rules_engine.apply(claim))
        return all_matches

    def _score_with_gpt(self, claims: List[str]) -> Dict[str, Any]:
        # Placeholder for GPT-based scoring of each claim.
        # For now, we'll just send the whole text to the GPT service.
        full_text = " ".join(claims)
        return analyze_text_with_gpt(full_text)

    def _aggregate_results(self, rule_matches: List[Dict[str, Any]], gpt_analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for a more sophisticated aggregation logic.

        # Combine reasons and recommendations
        reasons = list(set([match["category"] for match in rule_matches] + gpt_analysis.get("reasons", [])))
        recommendations = list(set([match["recommendation"] for match in rule_matches] + gpt_analysis.get("recommendations", [])))

        # Simple score aggregation
        rule_score = sum(10 for match in rule_matches) # simplified scoring
        final_score = self._combine_scores(rule_score, gpt_analysis.get("risk_score"))

        return {
            "score": final_score,
            "level": self._get_risk_level(final_score),
            "reasons": reasons,
            "recommendations": recommendations,
            "rule_matches": rule_matches,
            "gpt_analysis": gpt_analysis,
        }

    def _combine_scores(self, rule_score: int, llm_score: int) -> int:
        """Combine GreenCheck rule score with an LLM judge score."""
        if llm_score is None:
            return rule_score
        # Weighted average, giving more weight to the LLM
        return int(rule_score * 0.3 + llm_score * 0.7)

    def _get_risk_level(self, score: int) -> str:
        """Convert a numeric score to a risk level."""
        if score >= 75:
            return "High"
        if score >= 40:
            return "Medium"
        return "Low"

# Singleton instance
analysis_service = AnalysisService(rules_engine)
