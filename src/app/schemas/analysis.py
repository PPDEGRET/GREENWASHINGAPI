from pydantic import BaseModel, Field
from typing import List

class AnalysisRequest(BaseModel):
    file: bytes

class RecommendationItem(BaseModel):
    type: str = Field(..., example="clarity")
    message: str = Field(..., example="Avoid vague terms like 'eco-friendly'.")
    severity: int = Field(..., ge=1, le=3, example=2)
    triggered_by: List[str] = Field(..., example=["superlatives"])


class AnalysisResponse(BaseModel):
    score: int = Field(..., example=85)
    level: str = Field(..., example="High")
    reasons: List[str] = Field(..., example=["Vague language used.", "Lack of specific data."])
    text: str = Field(..., example="This is the extracted text from the ad.")
    recommendations: List[RecommendationItem] = Field(default_factory=list)
