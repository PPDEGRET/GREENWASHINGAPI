from pydantic import BaseModel, Field
from typing import List, Dict, Any

class RuleMatch(BaseModel):
    rule_id: str
    category: str
    severity: str
    matched_text: str
    recommendation: str

class GPTAnalysis(BaseModel):
    risk_score: int
    level: str
    reasons: List[str]
    subtle_triggers: List[str]
    recommendations: List[str]

class AnalysisResponse(BaseModel):
    score: int = Field(..., example=85)
    level: str = Field(..., example="High")
    reasons: List[str] = Field(..., example=["Vague language used.", "Lack of specific data."])
    recommendations: List[str] = Field(..., example=["Provide specific data to back up your claims."])
    rule_matches: List[RuleMatch] = Field(..., description="Matches from the rule-based engine.")
    gpt_analysis: GPTAnalysis = Field(..., description="Analysis from the GPT model.")
