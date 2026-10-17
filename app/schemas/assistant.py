
"""Pydantic contracts for the guided WorkForceIQ assistant API."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class AssistantOption(BaseModel):
    id: str
    label: str
    description: str
    enabled: bool = True


class AssistantInquiryCreateResponse(BaseModel):
    context_id: str
    status: Literal["active"]
    expires_at: datetime
    absolute_expires_at: datetime
    current_step: Literal["category"] = "category"
    message: str
    options: list[AssistantOption]


class AssistantSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selection_id: str = Field(min_length=1, max_length=100)


class AssistantInquiryResponse(BaseModel):
    context_id: str
    status: str
    question_id: str | None
    context_data: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    absolute_expires_at: datetime


class AssistantSelectionResponse(BaseModel):
    context_id: str
    status: Literal["active"]
    selected_id: str
    current_step: Literal["question", "capability", "filters", "results"]
    message: str
    options: list[AssistantOption]


class AssistantEmployeeResult(BaseModel):
    """Approved employee fields exposed by assistant queries."""

    employee_id: str
    employee_code: str
    name: str
    designation: str | None = None
    department: str | None = None
    experience_years: float
    availability_status: str
    location: str | None = None
    status: str
    utilization_percentage: float


class AssistantEmployeeSearchFilters(BaseModel):
    """Validated filters used by guided employee search."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=100)
    employee_code: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    designation: str | None = Field(default=None, max_length=100)
    availability_status: Literal[
        "available",
        "partially_available",
        "unavailable",
    ] | None = None
    location: str | None = Field(default=None, max_length=100)
    min_experience: float | None = Field(default=None, ge=0, le=60)
    max_utilization: float | None = Field(default=None, ge=0, le=100)
    status: Literal["active", "inactive"] | None = "active"
    limit: int = Field(default=25, ge=1, le=25)


class AssistantEmployeeSearchResult(BaseModel):
    """Structured response for employee search."""

    capability: Literal["search_employees"] = "search_employees"
    filters: AssistantEmployeeSearchFilters
    result_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    employees: list[AssistantEmployeeResult]


class AssistantEmployeeDetailResult(BaseModel):
    """Structured response for employee detail retrieval."""

    capability: Literal["employee_detail"] = "employee_detail"
    employee: AssistantEmployeeResult


class AssistantStaffingRequirementSummary(BaseModel):
    """Minimal staffing requirement fields used in candidate discovery."""

    staffing_requirement_id: str
    project_id: str
    role_name: str
    required_quantity: int
    required_experience: float
    required_proficiency: str | None = None
    status: str


class AssistantCandidateDiscoveryResult(BaseModel):
    """Structured candidate-discovery response, not a recommendation."""

    capability: Literal["candidate_discovery"] = "candidate_discovery"
    staffing_requirement: AssistantStaffingRequirementSummary
    result_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    employees: list[AssistantEmployeeResult]
    notice: str


class AssistantUtilizationEmployee(BaseModel):
    """Approved employee fields for utilization summaries."""

    employee_id: str
    employee_code: str
    name: str
    designation: str | None = None
    department: str | None = None
    utilization_percentage: float = Field(ge=0, le=100)
    available_capacity_percentage: float = Field(ge=0, le=100)


class AssistantUtilizationSummaryResponse(BaseModel):
    """Read-only workforce utilization summary."""

    capability: Literal["utilization_summary"] = "utilization_summary"
    active_employee_count: int = Field(ge=0)
    average_utilization_percentage: float = Field(ge=0, le=100)
    average_available_capacity_percentage: float = Field(ge=0, le=100)
    result_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    employees: list[AssistantUtilizationEmployee]


class AssistantCapacityEmployee(BaseModel):
    """Approved employee fields for capacity summaries."""

    employee_id: str
    employee_code: str
    name: str
    designation: str | None = None
    department: str | None = None
    allocated_capacity_percentage: float = Field(ge=0)
    available_capacity_percentage: float = Field(ge=0, le=100)


class AssistantCapacitySummaryResponse(BaseModel):
    """Read-only workforce capacity summary for a reporting date."""

    capability: Literal["capacity_summary"] = "capacity_summary"
    reporting_date: str
    active_employee_count: int = Field(ge=0)
    average_allocated_capacity_percentage: float = Field(ge=0)
    average_available_capacity_percentage: float = Field(ge=0, le=100)
    employees_with_no_available_capacity_count: int = Field(ge=0)
    employees_with_partial_available_capacity_count: int = Field(ge=0)
    employees_with_full_available_capacity_count: int = Field(ge=0)
    result_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    employees: list[AssistantCapacityEmployee]


class AssistantWorkforceCapacityEmployee(BaseModel):
    """Approved employee fields for the combined utilization and capacity analysis."""

    employee_id: str
    employee_code: str
    name: str
    designation: str | None = None
    department: str | None = None
    utilization_percentage: float = Field(ge=0, le=100)
    allocated_capacity_percentage: float = Field(ge=0)
    available_capacity_percentage: float = Field(ge=0, le=100)


class AssistantWorkforceCapacityAnalysisResponse(BaseModel):
    """Read-only combined workforce utilization and capacity analysis."""

    capability: Literal["workforce_capacity_analysis"] = "workforce_capacity_analysis"
    reporting_date: str
    active_employee_count: int = Field(ge=0)
    average_utilization_percentage: float = Field(ge=0, le=100)
    average_allocated_capacity_percentage: float = Field(ge=0)
    average_available_capacity_percentage: float = Field(ge=0, le=100)
    employees_with_no_available_capacity_count: int = Field(ge=0)
    employees_with_partial_available_capacity_count: int = Field(ge=0)
    employees_with_full_available_capacity_count: int = Field(ge=0)
    result_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    employees: list[AssistantWorkforceCapacityEmployee]


class AssistantDemandStatusBreakdown(BaseModel):
    """Staffing requirement totals grouped by status."""

    status: str
    requirement_count: int = Field(ge=0)
    requested_headcount: int = Field(ge=0)


class AssistantDemandNamedBreakdown(BaseModel):
    """Staffing requirement totals grouped by a named attribute."""

    name: str
    requirement_count: int = Field(ge=0)
    requested_headcount: int = Field(ge=0)


class AssistantDemandProjectBreakdown(BaseModel):
    """Staffing requirement totals grouped by project."""

    project_id: str
    project_name: str
    requirement_count: int = Field(ge=0)
    requested_headcount: int = Field(ge=0)


class AssistantDemandRequirementDetail(BaseModel):
    """Bounded detail for a recorded staffing requirement."""

    staffing_requirement_id: str
    project_id: str
    project_name: str
    role_name: str
    required_quantity: int = Field(ge=0)
    status: str
    priority: str
    required_experience: float = Field(ge=0)
    required_proficiency: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    required_skills: list[str]


class AssistantStaffingDemandAnalysisResponse(BaseModel):
    """Read-only summary of recorded staffing demand, not a forecast."""

    capability: Literal["staffing_demand_analysis"] = "staffing_demand_analysis"
    total_requirement_count: int = Field(ge=0)
    total_requested_headcount: int = Field(ge=0)
    open_requirement_count: int = Field(ge=0)
    open_requested_headcount: int = Field(ge=0)
    requirements_by_status: list[AssistantDemandStatusBreakdown]
    requirements_by_role: list[AssistantDemandNamedBreakdown]
    requirements_by_project: list[AssistantDemandProjectBreakdown]
    requirements_by_priority: list[AssistantDemandNamedBreakdown]
    requirements_by_skill: list[AssistantDemandNamedBreakdown]
    result_count: int = Field(ge=0)
    limit: int = Field(ge=1, le=25)
    has_more_results: bool
    requirements: list[AssistantDemandRequirementDetail]
    notice: str
