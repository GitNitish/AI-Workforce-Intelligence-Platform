from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AllocationBase(BaseModel):
    employee_id: str
    project_id: str
    staffing_requirement_id: str | None = None

    allocation_percentage: float = Field(
        gt=0,
        le=100,
    )

    start_date: date
    end_date: date | None = None

    status: str = "active"

    allocated_by: str | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "end_date must be greater than or equal to start_date"
            )

        return self


class AllocationCreate(AllocationBase):
    pass


class AllocationUpdate(BaseModel):
    allocation_percentage: float | None = Field(
        default=None,
        gt=0,
        le=100,
    )

    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValueError(
                "end_date must be greater than or equal to start_date"
            )

        return self


class AllocationResponse(AllocationBase):
    model_config = ConfigDict(from_attributes=True)

    allocation_id: str
    created_at: datetime
    updated_at: datetime