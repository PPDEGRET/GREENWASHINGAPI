from pydantic import BaseModel, Field
from typing import List

class AnalysisRequest(BaseModel):
    file: bytes

class AnalysisResponse(BaseModel):
    score: int = Field(..., example=85)
    level: str = Field(..., example="High")
    reasons: List[str] = Field(..., example=["Vague language used.", "Lack of specific data."])
    text: str = Field(..., example="This is the extracted text from the ad.")
    recommendations: List[str] = Field(default_factory=list)
