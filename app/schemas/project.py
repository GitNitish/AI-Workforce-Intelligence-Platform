from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProjectBase(BaseModel):
    project_code: str = Field(
        min_length=1,
        max_length=50,
    )
    project_name: str = Field(
        min_length=1,
        max_length=150,
    )
    client_name: str | None = Field(
        default=None,
        max_length=150,
    )
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = Field(
        default="planned",
        max_length=50,
    )
    priority: str = Field(
        default="medium",
        max_length=50,
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


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    project_code: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    project_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    client_name: str | None = Field(
        default=None,
        max_length=150,
    )
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = Field(
        default=None,
        max_length=50,
    )
    priority: str | None = Field(
        default=None,
        max_length=50,
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


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    project_id: str
    created_at: datetime
    updated_at: datetime