from datetime import datetime

from pydantic import BaseModel


class RecommendationRequest(BaseModel):
    staffing_requirement_id: str


class RecommendationItem(BaseModel):
    employee_id: str
    rank: int
    score: float
    eligibility_status: str
    matched_skills: list[str]
    reason: str


class RecommendationResponse(BaseModel):
    staffing_requirement_id: str
    recommendations: list[RecommendationItem]
    generated_at: datetime
    message: str | None = None