"""Response schemas for read-only assistant recommendation evaluation."""

from pydantic import BaseModel, ConfigDict, Field


class AssistantRecommendationScoreBreakdown(BaseModel):
    """Individual scoring components returned by the scoring engine."""

    model_config = ConfigDict(extra="forbid")

    skill_match: float = Field(ge=0, le=100)
    proficiency: float = Field(ge=0, le=100)
    experience: float = Field(ge=0, le=100)
    certification: float = Field(ge=0, le=100)
    availability: float = Field(ge=0, le=100)
    utilization: float = Field(ge=0, le=100)


class AssistantRecommendationCandidate(BaseModel):
    """Safe, read-only candidate evaluation result."""

    model_config = ConfigDict(extra="forbid")

    employee_id: str
    employee_code: str
    name: str
    designation: str
    department: str
    experience_years: float = Field(ge=0)
    availability_status: str
    location: str | None = None
    utilization_percentage: float = Field(ge=0, le=100)
    remaining_capacity_percentage: float = Field(ge=0, le=100)
    score: float = Field(ge=0, le=100)
    score_breakdown: AssistantRecommendationScoreBreakdown
    matched_skills: list[str]
    recommendation_reason: str
    rank: int = Field(ge=1)


class AssistantRecommendationStaffingRequirement(BaseModel):
    """Staffing requirement summary used for candidate evaluation."""

    model_config = ConfigDict(extra="forbid")

    staffing_requirement_id: str
    project_id: str
    role_name: str
    required_quantity: int = Field(ge=1)
    required_experience: float = Field(ge=0)
    required_proficiency: str | None
    status: str


class AssistantRecommendationEvaluationResponse(BaseModel):
    """Response contract for non-persisting recommendation evaluation."""

    model_config = ConfigDict(extra="forbid")

    capability: str
    staffing_requirement: AssistantRecommendationStaffingRequirement
    result_count: int = Field(ge=0)
    eligible_candidate_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    candidates: list[AssistantRecommendationCandidate]
    notice: str
