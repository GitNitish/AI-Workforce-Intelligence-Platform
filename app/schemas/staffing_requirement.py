from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StaffingRequirementBase(BaseModel):
    role_name: str = Field(
        min_length=1,
        max_length=100,
    )
    required_quantity: int = Field(
        gt=0,
    )
    required_experience: float = Field(
        default=0,
        ge=0,
    )
    required_proficiency: str | None = Field(
        default=None,
        max_length=50,
    )
    start_date: date | None = None
    end_date: date | None = None
    priority: str = Field(
        default="medium",
        max_length=50,
    )
    status: str = Field(
        default="open",
        max_length=50,
    )
    required_skill_ids: list[str] = Field(
        default_factory=list,
    )
    required_certifications: list[str] = Field(
        default_factory=list,
    )

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


class StaffingRequirementCreate(StaffingRequirementBase):
    pass


class StaffingRequirementUpdate(BaseModel):
    role_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    required_quantity: int | None = Field(
        default=None,
        gt=0,
    )
    required_experience: float | None = Field(
        default=None,
        ge=0,
    )
    required_proficiency: str | None = Field(
        default=None,
        max_length=50,
    )
    start_date: date | None = None
    end_date: date | None = None
    priority: str | None = Field(
        default=None,
        max_length=50,
    )
    status: str | None = Field(
        default=None,
        max_length=50,
    )
    required_skill_ids: list[str] | None = None
    required_certifications: list[str] | None = None

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


class StaffingRequirementResponse(StaffingRequirementBase):
    model_config = ConfigDict(from_attributes=True)

    staffing_requirement_id: str
    project_id: str
    created_at: datetime
    updated_at: datetime