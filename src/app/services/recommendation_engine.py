from typing import List, Dict, Set
import re
from src.app.schemas.analysis import RecommendationItem

class RecommendationEngine:
    """
    A hybrid engine that generates recommendations based on rule-based triggers
    and GPT-assisted analysis.
    """

    def __init__(self):
        # This maps deterministic triggers to specific recommendation templates.
        self._rule_trigger_map = {
            "superlatives": {
                "type": "avoid_absolute",
                "message": "Avoid absolute environmental claims (e.g., 'carbon neutral', '100% sustainable') unless the scope is narrow, current, and backed by independent verification.",
                "severity": 3,
            },
            "future_claims": {
                "type": "future_claims",
                "message": "For future targets (e.g., 'net-zero by 2030'), provide the baseline, scope, assumptions, and a clear, verifiable action plan.",
                "severity": 2,
            },
            "offsets": {
                "type": "offsets",
                "message": "If mentioning carbon offsets, clearly state what is being offset, the standard used (e.g., Verra, Gold Standard), and avoid implying overall climate neutrality without full lifecycle analysis.",
                "severity": 2,
            },
        }

    def detect_rule_based_triggers(self, text: str) -> List[str]:
        """
        Detects deterministic triggers in the text using regular expressions.
        """
        triggers = []

        # Rule for superlatives and absolute claims
        superlative_pattern = r"\b(100%|eco-friendly|green|sustainable|carbon neutral|zero impact|climate positive)\b"
        if re.search(superlative_pattern, text, re.IGNORECASE):
            triggers.append("superlatives")

        # Rule for future claims
        future_claim_pattern = r"\b(net-zero|carbon neutral by|sustainable by|goal is to|by 20[3-9][0-9])\b"
        if re.search(future_claim_pattern, text, re.IGNORECASE):
            triggers.append("future_claims")

        # Rule for offsets
        offset_pattern = r"\b(offset|compensation|carbon credit)\b"
        if re.search(offset_pattern, text, re.IGNORECASE):
            triggers.append("offsets")

        return list(set(triggers)) # Return unique triggers

    def generate_recommendations(self, triggers: List[str]) -> List[RecommendationItem]:
        """
        Generates a list of RecommendationItem objects from a list of triggers.
        This method will later be expanded to merge triggers from GPT analysis.
        """
        recommendations = []

        for trigger in triggers:
            if trigger in self._rule_trigger_map:
                rec_data = self._rule_trigger_map[trigger]
                recommendations.append(
                    RecommendationItem(
                        type=rec_data["type"],
                        message=rec_data["message"],
                        severity=rec_data["severity"],
                        triggered_by=[trigger],
                    )
                )

        # In the future, this is where we will merge and deduplicate
        # recommendations from both rule-based and GPT-based triggers.

        return recommendations
