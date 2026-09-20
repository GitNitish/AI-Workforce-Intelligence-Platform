from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    employee_code: str
    name: str
    email: str
    designation: str | None = None
    department: str | None = None
    experience_years: float = Field(
        default=0,
        ge=0,
    )
    availability_status: str = "available"
    location: str | None = None
    status: str = "active"


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_code: str | None = None
    name: str | None = None
    email: str | None = None
    designation: str | None = None
    department: str | None = None
    experience_years: float | None = Field(
        default=None,
        ge=0,
    )
    availability_status: str | None = None
    location: str | None = None
    status: str | None = None


class EmployeeResponse(EmployeeBase):
    employee_id: str
    utilization_percentage: float = Field(
        ge=0,
        le=100,
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)