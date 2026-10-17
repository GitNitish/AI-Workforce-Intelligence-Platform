
"""Read-only workforce capabilities for the guided WorkForceIQ assistant."""

from collections import defaultdict
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    Allocation,
    Employee,
    Project,
    StaffingRequirement,
)
from app.services.candidate_matching_service import (
    discover_candidate_employees,
)
from app.services.employee_service import (
    _calculate_employee_utilization_from_record,
    get_employee,
    search_employees,
)
from app.services.staffing_service import get_staffing_requirement


MAX_SEARCH_RESULTS = 25
MAX_FILTER_LENGTH = 100
MAX_EXPERIENCE_YEARS = 60.0
MAX_UTILIZATION_PERCENTAGE = 100.0

ALLOWED_AVAILABILITY_STATUSES = {
    "available",
    "partially_available",
    "unavailable",
}

ALLOWED_EMPLOYEE_STATUSES = {
    "active",
    "inactive",
}


class AssistantCapabilityError(Exception):
    """Base exception for assistant capability errors."""


class InvalidAssistantFilterError(AssistantCapabilityError):
    """Raised when an assistant search filter is invalid."""


class AssistantEntityNotFoundError(AssistantCapabilityError):
    """Raised when a requested workforce entity does not exist."""


def _validate_optional_text(
    value: str | None,
    field_name: str,
) -> str | None:
    """Validate and normalize an optional text filter."""
    if value is None:
        return None

    if not isinstance(value, str):
        raise InvalidAssistantFilterError(
            f"{field_name} must be text."
        )

    normalized = value.strip()

    if not normalized:
        return None

    if len(normalized) > MAX_FILTER_LENGTH:
        raise InvalidAssistantFilterError(
            f"{field_name} cannot exceed "
            f"{MAX_FILTER_LENGTH} characters."
        )

    return normalized


def _validate_optional_number(
    value: float | int | None,
    field_name: str,
    *,
    minimum: float,
    maximum: float,
) -> float | None:
    """Validate a bounded numeric filter."""
    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidAssistantFilterError(
            f"{field_name} must be a number."
        )

    normalized = float(value)

    if not minimum <= normalized <= maximum:
        raise InvalidAssistantFilterError(
            f"{field_name} must be between "
            f"{minimum:g} and {maximum:g}."
        )

    return normalized


def _validate_optional_choice(
    value: str | None,
    field_name: str,
    allowed_values: set[str],
) -> str | None:
    """Validate a case-insensitive value from an allowed set."""
    normalized = _validate_optional_text(value, field_name)

    if normalized is None:
        return None

    normalized = normalized.lower()

    if normalized not in allowed_values:
        allowed = ", ".join(sorted(allowed_values))
        raise InvalidAssistantFilterError(
            f"{field_name} must be one of: {allowed}."
        )

    return normalized


def _validate_result_limit(limit: int) -> None:
    """Validate a bounded result limit shared by assistant capabilities."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise InvalidAssistantFilterError(
            "limit must be an integer."
        )

    if not 1 <= limit <= MAX_SEARCH_RESULTS:
        raise InvalidAssistantFilterError(
            f"limit must be between 1 and {MAX_SEARCH_RESULTS}."
        )


def _employee_to_result(employee: Employee) -> dict[str, Any]:
    """Return only approved, non-sensitive employee information."""
    return {
        "employee_id": employee.employee_id,
        "employee_code": employee.employee_code,
        "name": employee.name,
        "designation": employee.designation,
        "department": employee.department,
        "experience_years": employee.experience_years,
        "availability_status": employee.availability_status,
        "location": employee.location,
        "status": employee.status,
        "utilization_percentage": employee.utilization_percentage,
    }


def get_assistant_utilization_summary(
    db: Session,
    *,
    limit: int = MAX_SEARCH_RESULTS,
) -> dict[str, Any]:
    """Return a read-only summary of active workforce utilization."""
    _validate_result_limit(limit)

    employees = db.scalars(
        select(Employee).where(Employee.status == "active")
    ).all()

    employee_utilization = [
        (
            employee,
            _calculate_employee_utilization_from_record(employee),
        )
        for employee in employees
    ]

    employee_utilization.sort(
        key=lambda item: (
            -item[1],
            item[0].name.lower(),
            item[0].employee_id,
        )
    )

    employee_count = len(employee_utilization)

    total_utilization = sum(
        utilization
        for _, utilization in employee_utilization
    )

    average_utilization = (
        total_utilization / employee_count
        if employee_count
        else 0.0
    )

    average_available_capacity = (
        100.0 - average_utilization
        if employee_count
        else 0.0
    )

    bounded_employees = employee_utilization[:limit]

    return {
        "capability": "utilization_summary",
        "active_employee_count": employee_count,
        "average_utilization_percentage": round(
            average_utilization, 2
        ),
        "average_available_capacity_percentage": round(
            average_available_capacity, 2
        ),
        "result_count": len(bounded_employees),
        "limit": limit,
        "has_more_results": employee_count > limit,
        "employees": [
            {
                "employee_id": employee.employee_id,
                "employee_code": employee.employee_code,
                "name": employee.name,
                "designation": employee.designation,
                "department": employee.department,
                "utilization_percentage": round(
                    utilization, 2
                ),
                "available_capacity_percentage": round(
                    max(0.0, 100.0 - utilization),
                    2,
                ),
            }
            for employee, utilization in bounded_employees
        ],
    }


def get_assistant_capacity_summary(
    db: Session,
    *,
    limit: int = MAX_SEARCH_RESULTS,
    as_of: date | None = None,
) -> dict[str, Any]:
    """Return read-only workforce capacity as of a reporting date.

    Only active employees are included. An allocation contributes to
    capacity usage when its status is active and its date range includes
    the reporting date. Allocation start and end dates are inclusive.

    Aggregate statistics cover the full active workforce. The employee
    list is bounded by ``limit``. This function does not modify workforce
    records or commit database changes.
    """
    _validate_result_limit(limit)

    if as_of is not None and not isinstance(as_of, date):
        raise InvalidAssistantFilterError(
            "as_of must be a date."
        )

    reporting_date = as_of or date.today()

    employees = db.scalars(
        select(Employee).where(Employee.status == "active")
    ).all()

    employee_capacity: list[tuple[Employee, float, float]] = []

    for employee in employees:
        allocated_percentage = sum(
            allocation.allocation_percentage
            for allocation in employee.allocations
            if (
                allocation.status == "active"
                and allocation.start_date <= reporting_date
                and (
                    allocation.end_date is None
                    or allocation.end_date >= reporting_date
                )
            )
        )

        available_percentage = max(
            0.0,
            100.0 - allocated_percentage,
        )

        employee_capacity.append(
            (
                employee,
                allocated_percentage,
                available_percentage,
            )
        )

    employee_capacity.sort(
        key=lambda item: (
            -item[1],
            item[0].name.lower(),
            item[0].employee_id,
        )
    )

    employee_count = len(employee_capacity)

    total_allocated = sum(
        allocated
        for _, allocated, _ in employee_capacity
    )
    total_available = sum(
        available
        for _, _, available in employee_capacity
    )

    average_allocated = (
        total_allocated / employee_count
        if employee_count
        else 0.0
    )
    average_available = (
        total_available / employee_count
        if employee_count
        else 0.0
    )

    no_available_capacity_count = sum(
        1
        for _, _, available in employee_capacity
        if available == 0.0
    )
    partial_available_capacity_count = sum(
        1
        for _, _, available in employee_capacity
        if 0.0 < available < 100.0
    )
    full_available_capacity_count = sum(
        1
        for _, _, available in employee_capacity
        if available == 100.0
    )

    bounded_employees = employee_capacity[:limit]

    return {
        "capability": "capacity_summary",
        "reporting_date": reporting_date.isoformat(),
        "active_employee_count": employee_count,
        "average_allocated_capacity_percentage": round(
            average_allocated, 2
        ),
        "average_available_capacity_percentage": round(
            average_available, 2
        ),
        "employees_with_no_available_capacity_count": (
            no_available_capacity_count
        ),
        "employees_with_partial_available_capacity_count": (
            partial_available_capacity_count
        ),
        "employees_with_full_available_capacity_count": (
            full_available_capacity_count
        ),
        "result_count": len(bounded_employees),
        "limit": limit,
        "has_more_results": employee_count > limit,
        "employees": [
            {
                "employee_id": employee.employee_id,
                "employee_code": employee.employee_code,
                "name": employee.name,
                "designation": employee.designation,
                "department": employee.department,
                "allocated_capacity_percentage": round(
                    allocated, 2
                ),
                "available_capacity_percentage": round(
                    available, 2
                ),
            }
            for employee, allocated, available in bounded_employees
        ],
    }


def get_assistant_workforce_capacity_analysis(
    db: Session,
    *,
    limit: int = MAX_SEARCH_RESULTS,
    as_of: date | None = None,
) -> dict[str, Any]:
    """Return a unified, read-only utilization and capacity analysis.

    Utilization uses the existing employee utilization calculation. Allocated
    and available capacity use active allocations whose inclusive date range
    covers the reporting date. The employee list is bounded, while aggregate
    statistics cover the full active workforce.
    """
    _validate_result_limit(limit)

    if as_of is not None and not isinstance(as_of, date):
        raise InvalidAssistantFilterError("as_of must be a date.")

    reporting_date = as_of or date.today()
    employees = db.scalars(
        select(Employee).where(Employee.status == "active")
    ).all()

    workforce: list[dict[str, Any]] = []
    for employee in employees:
        utilization = float(
            _calculate_employee_utilization_from_record(employee)
        )
        allocated = float(
            sum(
                allocation.allocation_percentage
                for allocation in employee.allocations
                if (
                    allocation.status == "active"
                    and allocation.start_date <= reporting_date
                    and (
                        allocation.end_date is None
                        or allocation.end_date >= reporting_date
                    )
                )
            )
        )
        available = max(0.0, 100.0 - allocated)
        workforce.append(
            {
                "employee_id": employee.employee_id,
                "employee_code": employee.employee_code,
                "name": employee.name,
                "designation": employee.designation,
                "department": employee.department,
                "utilization_percentage": round(utilization, 2),
                "allocated_capacity_percentage": round(allocated, 2),
                "available_capacity_percentage": round(available, 2),
            }
        )

    workforce.sort(
        key=lambda item: (
            -item["utilization_percentage"],
            item["name"].lower(),
            item["employee_id"],
        )
    )

    employee_count = len(workforce)
    average_utilization = (
        sum(item["utilization_percentage"] for item in workforce)
        / employee_count
        if employee_count
        else 0.0
    )
    average_allocated = (
        sum(item["allocated_capacity_percentage"] for item in workforce)
        / employee_count
        if employee_count
        else 0.0
    )
    average_available = (
        sum(item["available_capacity_percentage"] for item in workforce)
        / employee_count
        if employee_count
        else 0.0
    )

    bounded_workforce = workforce[:limit]
    return {
        "capability": "workforce_capacity_analysis",
        "reporting_date": reporting_date.isoformat(),
        "active_employee_count": employee_count,
        "average_utilization_percentage": round(average_utilization, 2),
        "average_allocated_capacity_percentage": round(average_allocated, 2),
        "average_available_capacity_percentage": round(average_available, 2),
        "employees_with_no_available_capacity_count": sum(
            item["available_capacity_percentage"] == 0.0
            for item in workforce
        ),
        "employees_with_partial_available_capacity_count": sum(
            0.0 < item["available_capacity_percentage"] < 100.0
            for item in workforce
        ),
        "employees_with_full_available_capacity_count": sum(
            item["available_capacity_percentage"] == 100.0
            for item in workforce
        ),
        "result_count": len(bounded_workforce),
        "limit": limit,
        "has_more_results": employee_count > limit,
        "employees": bounded_workforce,
    }


def get_assistant_staffing_demand_analysis(
    db: Session,
    *,
    limit: int = MAX_SEARCH_RESULTS,
) -> dict[str, Any]:
    """Return a read-only summary of recorded staffing demand.

    Required quantities represent requested headcount, not verified vacancies.
    This capability does not infer requirement fulfillment or forecast demand.
    Aggregate counts cover all staffing requirements; the detail list is
    bounded by ``limit``.
    """
    _validate_result_limit(limit)

    requirements = db.scalars(
        select(StaffingRequirement)
        .order_by(
            StaffingRequirement.role_name.asc(),
            StaffingRequirement.created_at.desc(),
            StaffingRequirement.staffing_requirement_id.asc(),
        )
    ).all()

    project_names = {
        project.project_id: project.project_name
        for project in db.scalars(select(Project)).all()
    }

    total_requirements = len(requirements)
    total_requested_headcount = sum(
        requirement.required_quantity
        for requirement in requirements
    )

    status_counts: dict[str, int] = defaultdict(int)
    status_headcount: dict[str, int] = defaultdict(int)
    role_summary: dict[str, dict[str, int]] = {}
    project_summary: dict[str, dict[str, Any]] = {}
    priority_summary: dict[str, dict[str, int]] = {}
    skill_summary: dict[str, dict[str, int]] = {}
    detail_rows: list[dict[str, Any]] = []

    for requirement in requirements:
        status = (requirement.status or "unknown").strip().lower()
        role = requirement.role_name.strip() or "Unspecified role"
        priority = (requirement.priority or "unknown").strip().lower()
        project_id = requirement.project_id
        project_name = project_names.get(project_id, "Unknown project")
        quantity = requirement.required_quantity

        status_counts[status] += 1
        status_headcount[status] += quantity

        if role not in role_summary:
            role_summary[role] = {
                "requirement_count": 0,
                "requested_headcount": 0,
            }
        role_summary[role]["requirement_count"] += 1
        role_summary[role]["requested_headcount"] += quantity

        if project_id not in project_summary:
            project_summary[project_id] = {
                "project_id": project_id,
                "project_name": project_name,
                "requirement_count": 0,
                "requested_headcount": 0,
            }
        project_summary[project_id]["requirement_count"] += 1
        project_summary[project_id]["requested_headcount"] += quantity

        if priority not in priority_summary:
            priority_summary[priority] = {
                "requirement_count": 0,
                "requested_headcount": 0,
            }
        priority_summary[priority]["requirement_count"] += 1
        priority_summary[priority]["requested_headcount"] += quantity

        requirement_skills: list[str] = []
        for required_skill in requirement.required_skills:
            if required_skill.skill is not None:
                skill_name = required_skill.skill.skill_name.strip()
                if skill_name:
                    requirement_skills.append(skill_name)

        for skill_name in sorted(set(requirement_skills), key=str.lower):
            if skill_name not in skill_summary:
                skill_summary[skill_name] = {
                    "requirement_count": 0,
                    "requested_headcount": 0,
                }
            skill_summary[skill_name]["requirement_count"] += 1
            skill_summary[skill_name]["requested_headcount"] += quantity

        detail_rows.append(
            {
                "staffing_requirement_id": (
                    requirement.staffing_requirement_id
                ),
                "project_id": project_id,
                "project_name": project_name,
                "role_name": role,
                "required_quantity": quantity,
                "status": status,
                "priority": priority,
                "required_experience": requirement.required_experience,
                "required_proficiency": requirement.required_proficiency,
                "start_date": (
                    requirement.start_date.isoformat()
                    if requirement.start_date
                    else None
                ),
                "end_date": (
                    requirement.end_date.isoformat()
                    if requirement.end_date
                    else None
                ),
                "required_skills": sorted(
                    set(requirement_skills),
                    key=str.lower,
                ),
            }
        )

    detail_rows.sort(
        key=lambda item: (
            item["role_name"].lower(),
            item["project_name"].lower(),
            item["staffing_requirement_id"],
        )
    )
    bounded_requirements = detail_rows[:limit]

    def _sorted_breakdown(
        values: dict[str, dict[str, int]],
    ) -> list[dict[str, Any]]:
        return [
            {"name": name, **values[name]}
            for name in sorted(values, key=str.lower)
        ]

    return {
        "capability": "staffing_demand_analysis",
        "total_requirement_count": total_requirements,
        "total_requested_headcount": total_requested_headcount,
        "open_requirement_count": status_counts.get("open", 0),
        "open_requested_headcount": status_headcount.get("open", 0),
        "requirements_by_status": [
            {
                "status": status,
                "requirement_count": status_counts[status],
                "requested_headcount": status_headcount[status],
            }
            for status in sorted(status_counts)
        ],
        "requirements_by_role": _sorted_breakdown(role_summary),
        "requirements_by_project": [
            project_summary[project_id]
            for project_id in sorted(
                project_summary,
                key=lambda key: (
                    project_summary[key]["project_name"].lower(),
                    key,
                ),
            )
        ],
        "requirements_by_priority": _sorted_breakdown(priority_summary),
        "requirements_by_skill": _sorted_breakdown(skill_summary),
        "result_count": len(bounded_requirements),
        "limit": limit,
        "has_more_results": total_requirements > limit,
        "requirements": bounded_requirements,
        "notice": (
            "Requested headcount reflects recorded staffing requirements. "
            "It is not a verified vacancy count. Fulfillment gaps and "
            "forecasted demand are not calculated by this capability."
        ),
    }


def _require_employee(
    db: Session,
    employee_id: str,
) -> Employee:
    """Retrieve an employee or raise a controlled not-found error."""
    normalized_id = _validate_optional_text(
        employee_id,
        "employee_id",
    )

    if normalized_id is None:
        raise InvalidAssistantFilterError(
            "employee_id is required."
        )

    employee = get_employee(db, normalized_id)

    if employee is None:
        raise AssistantEntityNotFoundError(
            "Employee was not found."
        )

    return employee


def search_assistant_employees(
    db: Session,
    *,
    name: str | None = None,
    employee_code: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    availability_status: str | None = None,
    location: str | None = None,
    min_experience: float | None = None,
    max_utilization: float | None = None,
    status: str | None = "active",
    limit: int = MAX_SEARCH_RESULTS,
) -> dict[str, Any]:
    """Search employees with validated filters and bounded results.

    Reuses the existing employee search service. Does not create, update,
    or delete workforce records.
    """
    validated_name = _validate_optional_text(name, "name")
    validated_code = _validate_optional_text(
        employee_code,
        "employee_code",
    )
    validated_department = _validate_optional_text(
        department,
        "department",
    )
    validated_designation = _validate_optional_text(
        designation,
        "designation",
    )
    validated_location = _validate_optional_text(
        location,
        "location",
    )
    validated_availability = _validate_optional_choice(
        availability_status,
        "availability_status",
        ALLOWED_AVAILABILITY_STATUSES,
    )
    validated_status = _validate_optional_choice(
        status,
        "status",
        ALLOWED_EMPLOYEE_STATUSES,
    )
    validated_min_experience = _validate_optional_number(
        min_experience,
        "min_experience",
        minimum=0,
        maximum=MAX_EXPERIENCE_YEARS,
    )
    validated_max_utilization = _validate_optional_number(
        max_utilization,
        "max_utilization",
        minimum=0,
        maximum=MAX_UTILIZATION_PERCENTAGE,
    )

    _validate_result_limit(limit)

    employees = search_employees(
        db,
        name=validated_name,
        employee_code=validated_code,
        department=validated_department,
        designation=validated_designation,
        availability_status=validated_availability,
        location=validated_location,
        min_experience=validated_min_experience,
        max_utilization=validated_max_utilization,
        status=validated_status,
    )

    bounded_employees = employees[:limit]

    return {
        "capability": "search_employees",
        "filters": {
            "name": validated_name,
            "employee_code": validated_code,
            "department": validated_department,
            "designation": validated_designation,
            "availability_status": validated_availability,
            "location": validated_location,
            "min_experience": validated_min_experience,
            "max_utilization": validated_max_utilization,
            "status": validated_status,
        },
        "result_count": len(bounded_employees),
        "limit": limit,
        "has_more_results": len(employees) > limit,
        "employees": [
            _employee_to_result(employee)
            for employee in bounded_employees
        ],
    }


def get_assistant_employee_detail(
    db: Session,
    employee_id: str,
) -> dict[str, Any]:
    """Retrieve an employee detail result using the existing service."""
    employee = _require_employee(db, employee_id)

    return {
        "capability": "employee_detail",
        "employee": _employee_to_result(employee),
    }


def discover_assistant_candidates(
    db: Session,
    staffing_requirement_id: str,
    *,
    limit: int = MAX_SEARCH_RESULTS,
) -> dict[str, Any]:
    """Discover candidates without generating recommendations.

    Reuses the existing candidate-matching service. Results represent
    discovery matches, not final eligibility decisions or scored
    staffing recommendations.
    """
    normalized_id = _validate_optional_text(
        staffing_requirement_id,
        "staffing_requirement_id",
    )

    if normalized_id is None:
        raise InvalidAssistantFilterError(
            "staffing_requirement_id is required."
        )

    _validate_result_limit(limit)

    requirement: StaffingRequirement | None = get_staffing_requirement(
        db,
        normalized_id,
    )

    if requirement is None:
        raise AssistantEntityNotFoundError(
            "Staffing requirement was not found."
        )

    candidates = discover_candidate_employees(
        db,
        requirement,
    )
    bounded_candidates = candidates[:limit]

    return {
        "capability": "candidate_discovery",
        "staffing_requirement": {
            "staffing_requirement_id": (
                requirement.staffing_requirement_id
            ),
            "project_id": requirement.project_id,
            "role_name": requirement.role_name,
            "required_quantity": requirement.required_quantity,
            "required_experience": requirement.required_experience,
            "required_proficiency": requirement.required_proficiency,
            "status": requirement.status,
        },
        "result_count": len(bounded_candidates),
        "limit": limit,
        "has_more_results": len(candidates) > limit,
        "employees": [
            _employee_to_result(employee)
            for employee in bounded_candidates
        ],
        "notice": (
            "These are discovery results, not final eligibility "
            "decisions or scored staffing recommendations."
        ),
    }
