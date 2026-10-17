
"""Validated filter requests for guided assistant capabilities."""

from pydantic import BaseModel, ConfigDict, Field


class AssistantEmployeeFiltersRequest(BaseModel):
    """Filters submitted during guided employee search."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=100)
    employee_code: str | None = Field(default=None, max_length=100)
    department: str | None = Field(default=None, max_length=100)
    designation: str | None = Field(default=None, max_length=100)
    availability_status: str | None = Field(default=None, max_length=50)
    location: str | None = Field(default=None, max_length=100)
    min_experience: float | None = Field(default=None, ge=0, le=60)
    max_utilization: float | None = Field(default=None, ge=0, le=100)
    status: str | None = Field(default="active", max_length=50)
    limit: int = Field(default=25, ge=1, le=25)


class AssistantCandidateDiscoveryRequest(BaseModel):
    """Staffing requirement selected for candidate discovery."""

    model_config = ConfigDict(extra="forbid")

    staffing_requirement_id: str = Field(min_length=1, max_length=100)
    limit: int = Field(default=25, ge=1, le=25)


class AssistantEmployeeDetailRequest(BaseModel):
    """Employee selected for a detail inquiry."""

    model_config = ConfigDict(extra="forbid")

    employee_id: str = Field(min_length=1, max_length=100)
