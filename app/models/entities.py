from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


def generate_id() -> str:
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    employee_code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    designation: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    experience_years: Mapped[float] = mapped_column(
        Float, nullable=False, default=0
    )
    availability_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="available"
    )
    utilization_percentage: Mapped[float] = mapped_column(
        Float, nullable=False, default=0
    )
    location: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    skills: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    allocations: Mapped[list["Allocation"]] = relationship(
        back_populates="employee"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="employee"
    )

    __table_args__ = (
        CheckConstraint(
            "experience_years >= 0",
            name="ck_employee_experience_nonnegative",
        ),
        CheckConstraint(
            "utilization_percentage >= 0 AND utilization_percentage <= 100",
            name="ck_employee_utilization_range",
        ),
    )


class Skill(Base):
    __tablename__ = "skills"

    skill_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    skill_name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    category: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    employees: Mapped[list["EmployeeSkill"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
    )


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    employee_skill_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_id
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True,
    )
    skill_id: Mapped[str] = mapped_column(
        ForeignKey("skills.skill_id"),
        nullable=False,
        index=True,
    )
    proficiency_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    years_experience: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )
    last_assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="skills"
    )
    skill: Mapped["Skill"] = relationship(
        back_populates="employees"
    )

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "skill_id",
            name="uq_employee_skill",
        ),
        CheckConstraint(
            "years_experience >= 0",
            name="ck_employee_skill_experience_nonnegative",
        ),
    )


class Certification(Base):
    __tablename__ = "certifications"

    certification_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True,
    )
    certification_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    issuing_authority: Mapped[str | None] = mapped_column(
        String(150)
    )
    certification_number: Mapped[str | None] = mapped_column(
        String(100)
    )
    issue_date: Mapped[Date | None] = mapped_column(Date)
    expiry_date: Mapped[Date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="certifications"
    )

    __table_args__ = (
        CheckConstraint(
            "expiry_date IS NULL OR issue_date IS NULL "
            "OR expiry_date >= issue_date",
            name="ck_certification_date_range",
        ),
    )


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    project_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    project_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    client_name: Mapped[str | None] = mapped_column(
        String(150)
    )
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[Date | None] = mapped_column(Date)
    end_date: Mapped[Date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planned",
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    staffing_requirements: Mapped[
        list["StaffingRequirement"]
    ] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    allocations: Mapped[list["Allocation"]] = relationship(
        back_populates="project"
    )

    __table_args__ = (
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL "
            "OR end_date >= start_date",
            name="ck_project_date_range",
        ),
    )


class StaffingRequirement(Base):
    __tablename__ = "staffing_requirements"

    staffing_requirement_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    role_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    required_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    required_experience: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0,
    )
    required_proficiency: Mapped[str | None] = mapped_column(
        String(50)
    )
    start_date: Mapped[Date | None] = mapped_column(Date)
    end_date: Mapped[Date | None] = mapped_column(Date)
    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    project: Mapped["Project"] = relationship(
        back_populates="staffing_requirements"
    )
    allocations: Mapped[list["Allocation"]] = relationship(
        back_populates="staffing_requirement"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="staffing_requirement"
    )

    __table_args__ = (
        CheckConstraint(
            "required_quantity > 0",
            name="ck_staffing_quantity_positive",
        ),
        CheckConstraint(
            "required_experience >= 0",
            name="ck_staffing_experience_nonnegative",
        ),
        CheckConstraint(
            "end_date IS NULL OR start_date IS NULL "
            "OR end_date >= start_date",
            name="ck_staffing_date_range",
        ),
    )


class Role(Base):
    __tablename__ = "roles"

    role_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    role_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="role"
    )
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )


class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    permission_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_permission_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.role_id"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[str] = mapped_column(
        ForeignKey("permissions.permission_id"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    role: Mapped["Role"] = relationship(
        back_populates="role_permissions"
    )
    permission: Mapped["Permission"] = relationship(
        back_populates="role_permissions"
    )

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission",
        ),
    )


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=True,
        index=True,
    )
    role_id: Mapped[str | None] = mapped_column(
        ForeignKey("roles.role_id"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    role: Mapped["Role | None"] = relationship(
        back_populates="users"
    )
    employee: Mapped["Employee | None"] = relationship()

    allocations_created: Mapped[list["Allocation"]] = relationship(
        back_populates="allocated_by_user",
        foreign_keys="Allocation.allocated_by",
    )

    recommendations_generated: Mapped[
        list["Recommendation"]
    ] = relationship(
        back_populates="generated_by_user",
        foreign_keys="Recommendation.generated_by",
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="user"
    )


class Allocation(Base):
    __tablename__ = "allocations"

    allocation_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.project_id"),
        nullable=False,
        index=True,
    )
    staffing_requirement_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "staffing_requirements.staffing_requirement_id"
        ),
        nullable=True,
        index=True,
    )
    allocation_percentage: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    start_date: Mapped[Date] = mapped_column(
        Date,
        nullable=False,
    )
    end_date: Mapped[Date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    allocated_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    employee: Mapped["Employee"] = relationship(
        back_populates="allocations"
    )
    project: Mapped["Project"] = relationship(
        back_populates="allocations"
    )
    staffing_requirement: Mapped[
        "StaffingRequirement | None"
    ] = relationship(
        back_populates="allocations"
    )
    allocated_by_user: Mapped["User | None"] = relationship(
        back_populates="allocations_created",
        foreign_keys=[allocated_by],
    )

    __table_args__ = (
        CheckConstraint(
            "allocation_percentage > 0 "
            "AND allocation_percentage <= 100",
            name="ck_allocation_percentage_range",
        ),
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="ck_allocation_date_range",
        ),
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    staffing_requirement_id: Mapped[str] = mapped_column(
        ForeignKey(
            "staffing_requirements.staffing_requirement_id"
        ),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.employee_id"),
        nullable=False,
        index=True,
    )
    score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    eligibility_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    recommendation_reason: Mapped[str | None] = mapped_column(
        Text
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    generated_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
        index=True,
    )

    staffing_requirement: Mapped[
        "StaffingRequirement"
    ] = relationship(
        back_populates="recommendations"
    )
    employee: Mapped["Employee"] = relationship(
        back_populates="recommendations"
    )
    generated_by_user: Mapped["User | None"] = relationship(
        back_populates="recommendations_generated",
        foreign_keys=[generated_by],
    )

    __table_args__ = (
        CheckConstraint(
            "rank > 0",
            name="ck_recommendation_rank_positive",
        ),
    )


class AuditEvent(Base):
    __tablename__ = "audit_events"

    audit_event_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    entity_id: Mapped[str | None] = mapped_column(
        String(36)
    )
    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    # "metadata" is the database column name.
    # "event_metadata" is the Python attribute because
    # SQLAlchemy reserves the name "metadata".
    event_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="audit_events"
    )