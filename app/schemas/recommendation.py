from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecommendationRequest(BaseModel):
    staffing_requirement_id: str


class RecommendationItem(BaseModel):
    employee_id: str
    employee_code: str
    employee_name: str
    designation: str | None = None
    department: str | None = None
    experience_years: float
    availability_status: str
    utilization_percentage: float
    location: str | None = None
    status: str
    rank: int
    score: float
    eligibility_status: str
    matched_skills: list[str]
    reason: str

    model_config = ConfigDict(from_attributes=True)


class RecommendationResponse(BaseModel):
    staffing_requirement_id: str
    recommendations: list[RecommendationItem]
    generated_at: datetime
    message: str