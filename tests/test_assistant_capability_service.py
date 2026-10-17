"""Tests for read-only WorkForceIQ assistant capabilities."""

from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.connection import Base
from app.models.entities import (
    Allocation,
    Employee,
    Project,
    Skill,
    StaffingRequirement,
    StaffingRequirementSkill,
)
from app.services.assistant_capability_service import (
    AssistantEntityNotFoundError,
    InvalidAssistantFilterError,
    get_assistant_capacity_summary,
    get_assistant_employee_detail,
    get_assistant_staffing_demand_analysis,
    get_assistant_utilization_summary,
    search_assistant_employees,
)


@pytest.fixture
def db():
    """Provide an isolated in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def employees(db):
    """Create employees, projects, and allocations for capability tests."""
    records = [
        Employee(
            employee_id="assistant-employee-001",
            employee_code="AST001",
            name="Alice Sharma",
            email="alice.assistant@example.com",
            designation="Data Analyst",
            department="Analytics",
            experience_years=5,
            availability_status="available",
            location="Delhi",
            status="active",
            utilization_percentage=20,
        ),
        Employee(
            employee_id="assistant-employee-002",
            employee_code="AST002",
            name="Bob Kumar",
            email="bob.assistant@example.com",
            designation="Backend Developer",
            department="Engineering",
            experience_years=3,
            availability_status="partially_available",
            location="Mumbai",
            status="active",
            utilization_percentage=70,
        ),
        Employee(
            employee_id="assistant-employee-003",
            employee_code="AST003",
            name="Charlie Singh",
            email="charlie.assistant@example.com",
            designation="Senior Data Analyst",
            department="Analytics",
            experience_years=8,
            availability_status="unavailable",
            location="Delhi",
            status="inactive",
            utilization_percentage=100,
        ),
    ]

    projects = [
        Project(
            project_id="assistant-project-001",
            project_code="AST-PROJ-001",
            project_name="Analytics Project",
            status="active",
        ),
        Project(
            project_id="assistant-project-002",
            project_code="AST-PROJ-002",
            project_name="Engineering Project",
            status="active",
        ),
        Project(
            project_id="assistant-project-003",
            project_code="AST-PROJ-003",
            project_name="Legacy Project",
            status="active",
        ),
    ]

    db.add_all(projects)
    db.add_all(records)
    db.flush()

    allocations = [
        Allocation(
            allocation_id="assistant-allocation-001",
            employee_id="assistant-employee-001",
            project_id="assistant-project-001",
            allocation_percentage=20,
            start_date=date(2026, 1, 1),
            status="active",
        ),
        Allocation(
            allocation_id="assistant-allocation-002",
            employee_id="assistant-employee-002",
            project_id="assistant-project-002",
            allocation_percentage=70,
            start_date=date(2026, 1, 1),
            status="active",
        ),
        Allocation(
            allocation_id="assistant-allocation-003",
            employee_id="assistant-employee-003",
            project_id="assistant-project-003",
            allocation_percentage=100,
            start_date=date(2026, 1, 1),
            status="active",
        ),
    ]

    db.add_all(allocations)
    db.commit()

    return records


def test_search_employees_returns_only_active_employees_by_default(
    db,
    employees,
):
    result = search_assistant_employees(db)

    assert result["capability"] == "search_employees"
    assert result["result_count"] == 2
    assert [
        employee["employee_id"]
        for employee in result["employees"]
    ] == [
        "assistant-employee-001",
        "assistant-employee-002",
    ]
    assert result["has_more_results"] is False


def test_search_employees_applies_guided_filters(db, employees):
    result = search_assistant_employees(
        db,
        department="Analytics",
        location="Delhi",
        min_experience=4,
    )

    assert result["result_count"] == 1

    employee = result["employees"][0]
    assert employee["employee_id"] == "assistant-employee-001"
    assert employee["department"] == "Analytics"
    assert employee["location"] == "Delhi"
    assert result["filters"]["min_experience"] == 4.0


def test_search_employees_supports_employee_code_filter(db, employees):
    result = search_assistant_employees(
        db,
        employee_code="AST002",
    )

    assert result["result_count"] == 1
    assert result["employees"][0]["employee_code"] == "AST002"


def test_search_employees_can_filter_inactive_employees(db, employees):
    result = search_assistant_employees(
        db,
        status="inactive",
    )

    assert result["result_count"] == 1
    assert result["employees"][0]["employee_id"] == (
        "assistant-employee-003"
    )


def test_search_employees_limits_result_count(db, employees):
    result = search_assistant_employees(
        db,
        status=None,
        limit=2,
    )

    assert result["result_count"] == 2
    assert result["limit"] == 2
    assert result["has_more_results"] is True


@pytest.mark.parametrize(
    ("filters", "message"),
    [
        ({"min_experience": -1}, "min_experience"),
        ({"min_experience": 61}, "min_experience"),
        ({"max_utilization": 101}, "max_utilization"),
        (
            {"availability_status": "sometimes"},
            "availability_status",
        ),
        ({"status": "deleted"}, "status"),
        ({"department": "A" * 101}, "department"),
        ({"limit": 0}, "limit"),
        ({"limit": 26}, "limit"),
    ],
)
def test_search_employees_rejects_invalid_filters(
    db,
    filters,
    message,
):
    with pytest.raises(InvalidAssistantFilterError, match=message):
        search_assistant_employees(db, **filters)


def test_employee_detail_returns_approved_fields(db, employees):
    result = get_assistant_employee_detail(
        db,
        "assistant-employee-001",
    )

    assert result["capability"] == "employee_detail"
    assert result["employee"]["name"] == "Alice Sharma"
    assert result["employee"]["department"] == "Analytics"

    assert "email" not in result["employee"]
    assert "password" not in result["employee"]


def test_employee_detail_raises_for_unknown_employee(db):
    with pytest.raises(
        AssistantEntityNotFoundError,
        match="Employee was not found",
    ):
        get_assistant_employee_detail(
            db,
            "assistant-employee-does-not-exist",
        )


def test_utilization_summary_includes_active_employees_only(
    db,
    employees,
):
    result = get_assistant_utilization_summary(db)

    assert result["capability"] == "utilization_summary"
    assert result["active_employee_count"] == 2
    assert result["result_count"] == 2

    assert {
        employee["employee_id"]
        for employee in result["employees"]
    } == {
        "assistant-employee-001",
        "assistant-employee-002",
    }


def test_utilization_summary_calculates_average_utilization_and_capacity(
    db,
    employees,
):
    result = get_assistant_utilization_summary(db)

    assert result["average_utilization_percentage"] == 45.0
    assert result["average_available_capacity_percentage"] == 55.0


def test_utilization_summary_orders_employees_by_utilization(
    db,
    employees,
):
    result = get_assistant_utilization_summary(db)

    assert [
        employee["employee_id"]
        for employee in result["employees"]
    ] == [
        "assistant-employee-002",
        "assistant-employee-001",
    ]

    assert result["employees"][0]["utilization_percentage"] == 70.0
    assert result["employees"][0]["available_capacity_percentage"] == 30.0
    assert result["employees"][1]["utilization_percentage"] == 20.0
    assert result["employees"][1]["available_capacity_percentage"] == 80.0


def test_utilization_summary_respects_limit_and_reports_more_results(
    db,
    employees,
):
    result = get_assistant_utilization_summary(db, limit=1)

    assert result["active_employee_count"] == 2
    assert result["result_count"] == 1
    assert result["limit"] == 1
    assert result["has_more_results"] is True
    assert result["employees"][0]["employee_id"] == (
        "assistant-employee-002"
    )


def test_utilization_summary_reports_no_more_results_when_within_limit(
    db,
    employees,
):
    result = get_assistant_utilization_summary(db, limit=2)

    assert result["result_count"] == 2
    assert result["has_more_results"] is False


def test_utilization_summary_returns_zeroes_for_empty_workforce(db):
    result = get_assistant_utilization_summary(db)

    assert result["active_employee_count"] == 0
    assert result["average_utilization_percentage"] == 0.0
    assert result["average_available_capacity_percentage"] == 0.0
    assert result["result_count"] == 0
    assert result["employees"] == []
    assert result["has_more_results"] is False


@pytest.mark.parametrize(
    "limit",
    [0, -1, 26, True, False, 1.5, "2"],
)
def test_utilization_summary_rejects_invalid_limits(db, limit):
    with pytest.raises(InvalidAssistantFilterError, match="limit"):
        get_assistant_utilization_summary(db, limit=limit)


def test_utilization_summary_does_not_modify_employee_records(
    db,
    employees,
):
    before = db.scalars(
        select(Employee).order_by(Employee.employee_id)
    ).all()

    before_snapshot = [
        (
            employee.employee_id,
            employee.employee_code,
            employee.name,
            employee.status,
            employee.utilization_percentage,
        )
        for employee in before
    ]

    get_assistant_utilization_summary(db)

    db.expire_all()

    after = db.scalars(
        select(Employee).order_by(Employee.employee_id)
    ).all()

    after_snapshot = [
        (
            employee.employee_id,
            employee.employee_code,
            employee.name,
            employee.status,
            employee.utilization_percentage,
        )
        for employee in after
    ]

    assert after_snapshot == before_snapshot


def test_read_only_capabilities_do_not_change_employee_records(
    db,
    employees,
):
    before = db.scalars(
        select(Employee).order_by(Employee.employee_id)
    ).all()

    before_snapshot = [
        (
            employee.employee_id,
            employee.employee_code,
            employee.name,
            employee.department,
            employee.status,
        )
        for employee in before
    ]

    search_assistant_employees(
        db,
        department="Analytics",
    )
    get_assistant_employee_detail(
        db,
        "assistant-employee-001",
    )

    db.expire_all()

    after = db.scalars(
        select(Employee).order_by(Employee.employee_id)
    ).all()

    after_snapshot = [
        (
            employee.employee_id,
            employee.employee_code,
            employee.name,
            employee.department,
            employee.status,
        )
        for employee in after
    ]

    assert after_snapshot == before_snapshot


# Capacity summary tests


def test_capacity_summary_includes_only_active_employees(
    db,
    employees,
):
    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    assert result["capability"] == "capacity_summary"
    assert result["reporting_date"] == "2026-06-01"
    assert result["active_employee_count"] == 2
    assert {
        employee["employee_id"]
        for employee in result["employees"]
    } == {
        "assistant-employee-001",
        "assistant-employee-002",
    }


def test_capacity_summary_calculates_averages_and_distribution(
    db,
    employees,
):
    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    assert result["average_allocated_capacity_percentage"] == 45.0
    assert result["average_available_capacity_percentage"] == 55.0
    assert result["employees_with_no_available_capacity_count"] == 0
    assert result["employees_with_partial_available_capacity_count"] == 2
    assert result["employees_with_full_available_capacity_count"] == 0


def test_capacity_summary_orders_employees_by_allocated_capacity(
    db,
    employees,
):
    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    assert [
        employee["employee_id"]
        for employee in result["employees"]
    ] == [
        "assistant-employee-002",
        "assistant-employee-001",
    ]

    assert result["employees"][0]["allocated_capacity_percentage"] == 70.0
    assert result["employees"][0]["available_capacity_percentage"] == 30.0
    assert result["employees"][1]["allocated_capacity_percentage"] == 20.0
    assert result["employees"][1]["available_capacity_percentage"] == 80.0


def test_capacity_summary_includes_allocation_start_and_end_dates(
    db,
    employees,
):
    db.add_all(
        [
            Allocation(
                allocation_id="capacity-before-start",
                employee_id="assistant-employee-001",
                project_id="assistant-project-002",
                allocation_percentage=10,
                start_date=date(2026, 6, 2),
                end_date=date(2026, 6, 10),
                status="active",
            ),
            Allocation(
                allocation_id="capacity-ending-today",
                employee_id="assistant-employee-001",
                project_id="assistant-project-003",
                allocation_percentage=15,
                start_date=date(2026, 5, 1),
                end_date=date(2026, 6, 1),
                status="active",
            ),
            Allocation(
                allocation_id="capacity-already-ended",
                employee_id="assistant-employee-002",
                project_id="assistant-project-001",
                allocation_percentage=10,
                start_date=date(2026, 4, 1),
                end_date=date(2026, 5, 31),
                status="active",
            ),
        ]
    )
    db.commit()

    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )
    by_id = {
        employee["employee_id"]: employee
        for employee in result["employees"]
    }

    assert by_id["assistant-employee-001"]["allocated_capacity_percentage"] == 35.0
    assert by_id["assistant-employee-001"]["available_capacity_percentage"] == 65.0
    assert by_id["assistant-employee-002"]["allocated_capacity_percentage"] == 70.0


def test_capacity_summary_ignores_inactive_allocations(
    db,
    employees,
):
    db.add(
        Allocation(
            allocation_id="capacity-inactive-allocation",
            employee_id="assistant-employee-001",
            project_id="assistant-project-002",
            allocation_percentage=40,
            start_date=date(2026, 1, 1),
            status="inactive",
        )
    )
    db.commit()

    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )
    alice = next(
        employee
        for employee in result["employees"]
        if employee["employee_id"] == "assistant-employee-001"
    )

    assert alice["allocated_capacity_percentage"] == 20.0
    assert alice["available_capacity_percentage"] == 80.0


def test_capacity_summary_reports_full_and_zero_available_capacity(
    db,
    employees,
):
    # Bob has 70% allocated. Add 30% to make his available capacity zero.
    db.add(
        Allocation(
            allocation_id="capacity-bob-full",
            employee_id="assistant-employee-002",
            project_id="assistant-project-001",
            allocation_percentage=30,
            start_date=date(2026, 1, 1),
            status="active",
        )
    )
    db.commit()

    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    assert result["employees_with_no_available_capacity_count"] == 1
    assert result["employees_with_partial_available_capacity_count"] == 1
    assert result["employees_with_full_available_capacity_count"] == 0


def test_capacity_summary_reports_full_availability_for_unallocated_employee(
    db,
):
    employee = Employee(
        employee_id="capacity-unallocated-001",
        employee_code="CAP001",
        name="Unallocated Employee",
        email="unallocated@example.com",
        designation="Analyst",
        department="Analytics",
        experience_years=2,
        availability_status="available",
        location="Delhi",
        status="active",
        utilization_percentage=0,
    )
    db.add(employee)
    db.commit()

    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    assert result["active_employee_count"] == 1
    assert result["average_allocated_capacity_percentage"] == 0.0
    assert result["average_available_capacity_percentage"] == 100.0
    assert result["employees_with_no_available_capacity_count"] == 0
    assert result["employees_with_partial_available_capacity_count"] == 0
    assert result["employees_with_full_available_capacity_count"] == 1
    assert result["employees"][0]["available_capacity_percentage"] == 100.0


def test_capacity_summary_returns_zeroes_for_empty_workforce(db):
    result = get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    assert result["active_employee_count"] == 0
    assert result["average_allocated_capacity_percentage"] == 0.0
    assert result["average_available_capacity_percentage"] == 0.0
    assert result["employees_with_no_available_capacity_count"] == 0
    assert result["employees_with_partial_available_capacity_count"] == 0
    assert result["employees_with_full_available_capacity_count"] == 0
    assert result["result_count"] == 0
    assert result["employees"] == []
    assert result["has_more_results"] is False


def test_capacity_summary_respects_limit_but_aggregates_full_workforce(
    db,
    employees,
):
    result = get_assistant_capacity_summary(
        db,
        limit=1,
        as_of=date(2026, 6, 1),
    )

    assert result["active_employee_count"] == 2
    assert result["average_allocated_capacity_percentage"] == 45.0
    assert result["average_available_capacity_percentage"] == 55.0
    assert result["result_count"] == 1
    assert result["limit"] == 1
    assert result["has_more_results"] is True
    assert result["employees"][0]["employee_id"] == "assistant-employee-002"


@pytest.mark.parametrize(
    "limit",
    [0, -1, 26, True, False, 1.5, "2"],
)
def test_capacity_summary_rejects_invalid_limits(db, limit):
    with pytest.raises(InvalidAssistantFilterError, match="limit"):
        get_assistant_capacity_summary(db, limit=limit)


def test_capacity_summary_rejects_non_date_reporting_value(db):
    with pytest.raises(InvalidAssistantFilterError, match="as_of"):
        get_assistant_capacity_summary(
            db,
            as_of="2026-06-01",
        )


def test_capacity_summary_does_not_modify_employee_or_allocation_records(
    db,
    employees,
):
    employee_snapshot_before = [
        (
            employee.employee_id,
            employee.status,
            employee.utilization_percentage,
        )
        for employee in db.scalars(
            select(Employee).order_by(Employee.employee_id)
        ).all()
    ]
    allocation_snapshot_before = [
        (
            allocation.allocation_id,
            allocation.employee_id,
            allocation.allocation_percentage,
            allocation.start_date,
            allocation.end_date,
            allocation.status,
        )
        for allocation in db.scalars(
            select(Allocation).order_by(Allocation.allocation_id)
        ).all()
    ]

    get_assistant_capacity_summary(
        db,
        as_of=date(2026, 6, 1),
    )

    db.expire_all()

    employee_snapshot_after = [
        (
            employee.employee_id,
            employee.status,
            employee.utilization_percentage,
        )
        for employee in db.scalars(
            select(Employee).order_by(Employee.employee_id)
        ).all()
    ]
    allocation_snapshot_after = [
        (
            allocation.allocation_id,
            allocation.employee_id,
            allocation.allocation_percentage,
            allocation.start_date,
            allocation.end_date,
            allocation.status,
        )
        for allocation in db.scalars(
            select(Allocation).order_by(Allocation.allocation_id)
        ).all()
    ]

    assert employee_snapshot_after == employee_snapshot_before
    assert allocation_snapshot_after == allocation_snapshot_before


# Combined workforce capacity analysis tests

def test_workforce_capacity_analysis_combines_utilization_and_capacity(
    db,
    employees,
):
    from app.services.assistant_capability_service import (
        get_assistant_workforce_capacity_analysis,
    )

    result = get_assistant_workforce_capacity_analysis(
        db,
        as_of=date(2026, 6, 1),
    )

    assert result["capability"] == "workforce_capacity_analysis"
    assert result["reporting_date"] == "2026-06-01"
    assert result["active_employee_count"] == 2
    assert result["average_utilization_percentage"] == 45.0
    assert result["average_allocated_capacity_percentage"] == 45.0
    assert result["average_available_capacity_percentage"] == 55.0
    assert result["result_count"] == 2
    assert result["has_more_results"] is False

    by_id = {
        employee["employee_id"]: employee
        for employee in result["employees"]
    }
    assert by_id["assistant-employee-001"]["utilization_percentage"] == 20.0
    assert by_id["assistant-employee-001"]["allocated_capacity_percentage"] == 20.0
    assert by_id["assistant-employee-001"]["available_capacity_percentage"] == 80.0
    assert by_id["assistant-employee-002"]["utilization_percentage"] == 70.0
    assert by_id["assistant-employee-002"]["allocated_capacity_percentage"] == 70.0
    assert by_id["assistant-employee-002"]["available_capacity_percentage"] == 30.0


def test_workforce_capacity_analysis_respects_reporting_date(
    db,
    employees,
):
    from app.services.assistant_capability_service import (
        get_assistant_workforce_capacity_analysis,
    )

    result = get_assistant_workforce_capacity_analysis(
        db,
        as_of=date(2026, 6, 1),
    )
    alice = next(
        employee
        for employee in result["employees"]
        if employee["employee_id"] == "assistant-employee-001"
    )
    assert alice["allocated_capacity_percentage"] == 20.0
    assert alice["available_capacity_percentage"] == 80.0


def test_workforce_capacity_analysis_respects_limit(db, employees):
    from app.services.assistant_capability_service import (
        get_assistant_workforce_capacity_analysis,
    )

    result = get_assistant_workforce_capacity_analysis(
        db, limit=1, as_of=date(2026, 6, 1)
    )
    assert result["active_employee_count"] == 2
    assert result["result_count"] == 1
    assert result["limit"] == 1
    assert result["has_more_results"] is True
    assert len(result["employees"]) == 1


def test_workforce_capacity_analysis_returns_zeroes_for_empty_workforce(db):
    from app.services.assistant_capability_service import (
        get_assistant_workforce_capacity_analysis,
    )

    result = get_assistant_workforce_capacity_analysis(
        db, as_of=date(2026, 6, 1)
    )
    assert result["active_employee_count"] == 0
    assert result["average_utilization_percentage"] == 0.0
    assert result["average_allocated_capacity_percentage"] == 0.0
    assert result["average_available_capacity_percentage"] == 0.0
    assert result["result_count"] == 0
    assert result["employees"] == []
    assert result["has_more_results"] is False


def test_workforce_capacity_analysis_does_not_modify_workforce_records(
    db,
    employees,
):
    from app.services.assistant_capability_service import (
        get_assistant_workforce_capacity_analysis,
    )

    employee_snapshot_before = [
        (employee.employee_id, employee.status, employee.utilization_percentage)
        for employee in db.scalars(
            select(Employee).order_by(Employee.employee_id)
        ).all()
    ]
    allocation_snapshot_before = [
        (allocation.allocation_id, allocation.allocation_percentage, allocation.status)
        for allocation in db.scalars(
            select(Allocation).order_by(Allocation.allocation_id)
        ).all()
    ]

    get_assistant_workforce_capacity_analysis(db, as_of=date(2026, 6, 1))
    db.expire_all()

    employee_snapshot_after = [
        (employee.employee_id, employee.status, employee.utilization_percentage)
        for employee in db.scalars(
            select(Employee).order_by(Employee.employee_id)
        ).all()
    ]
    allocation_snapshot_after = [
        (allocation.allocation_id, allocation.allocation_percentage, allocation.status)
        for allocation in db.scalars(
            select(Allocation).order_by(Allocation.allocation_id)
        ).all()
    ]
    assert employee_snapshot_after == employee_snapshot_before
    assert allocation_snapshot_after == allocation_snapshot_before

# Staffing demand analysis tests


def _create_staffing_demand_fixtures(db):
    """Create requirements and skills with deliberately mixed statuses."""
    projects = [
        Project(
            project_id="demand-project-001",
            project_code="DEM-PROJ-001",
            project_name="Analytics Modernization",
            status="active",
        ),
        Project(
            project_id="demand-project-002",
            project_code="DEM-PROJ-002",
            project_name="Platform Renewal",
            status="active",
        ),
    ]
    skills = [
        Skill(
            skill_id="demand-skill-001",
            skill_name="Python",
            category="Engineering",
            status="active",
        ),
        Skill(
            skill_id="demand-skill-002",
            skill_name="SQL",
            category="Analytics",
            status="active",
        ),
    ]
    db.add_all(projects + skills)
    db.flush()

    requirements = [
        StaffingRequirement(
            staffing_requirement_id="demand-requirement-001",
            project_id="demand-project-001",
            role_name="Data Analyst",
            required_quantity=3,
            required_experience=2,
            required_proficiency="intermediate",
            start_date=date(2026, 11, 1),
            end_date=date(2027, 3, 31),
            priority="high",
            status="open",
        ),
        StaffingRequirement(
            staffing_requirement_id="demand-requirement-002",
            project_id="demand-project-001",
            role_name="Data Analyst",
            required_quantity=2,
            required_experience=4,
            required_proficiency="advanced",
            start_date=date(2026, 12, 1),
            end_date=None,
            priority="medium",
            status="open",
        ),
        StaffingRequirement(
            staffing_requirement_id="demand-requirement-003",
            project_id="demand-project-002",
            role_name="Backend Developer",
            required_quantity=4,
            required_experience=3,
            required_proficiency="intermediate",
            start_date=None,
            end_date=None,
            priority="high",
            status="in_progress",
        ),
    ]
    db.add_all(requirements)
    db.flush()
    db.add_all(
        [
            StaffingRequirementSkill(
                staffing_requirement_skill_id="demand-req-skill-001",
                staffing_requirement_id="demand-requirement-001",
                skill_id="demand-skill-001",
            ),
            StaffingRequirementSkill(
                staffing_requirement_skill_id="demand-req-skill-002",
                staffing_requirement_id="demand-requirement-001",
                skill_id="demand-skill-002",
            ),
            StaffingRequirementSkill(
                staffing_requirement_skill_id="demand-req-skill-003",
                staffing_requirement_id="demand-requirement-002",
                skill_id="demand-skill-002",
            ),
            StaffingRequirementSkill(
                staffing_requirement_skill_id="demand-req-skill-004",
                staffing_requirement_id="demand-requirement-003",
                skill_id="demand-skill-001",
            ),
        ]
    )
    db.commit()


def test_staffing_demand_analysis_aggregates_requirements_and_headcount(db):
    _create_staffing_demand_fixtures(db)

    result = get_assistant_staffing_demand_analysis(db)

    assert result["capability"] == "staffing_demand_analysis"
    assert result["total_requirement_count"] == 3
    assert result["total_requested_headcount"] == 9
    assert result["open_requirement_count"] == 2
    assert result["open_requested_headcount"] == 5
    assert result["result_count"] == 3
    assert result["has_more_results"] is False

    status_breakdown = {
        item["status"]: item for item in result["requirements_by_status"]
    }
    assert status_breakdown["open"]["requirement_count"] == 2
    assert status_breakdown["open"]["requested_headcount"] == 5
    assert status_breakdown["in_progress"]["requirement_count"] == 1
    assert status_breakdown["in_progress"]["requested_headcount"] == 4


def test_staffing_demand_analysis_breaks_down_roles_projects_priorities_and_skills(
    db,
):
    _create_staffing_demand_fixtures(db)

    result = get_assistant_staffing_demand_analysis(db)

    roles = {item["name"]: item for item in result["requirements_by_role"]}
    assert roles["Data Analyst"]["requirement_count"] == 2
    assert roles["Data Analyst"]["requested_headcount"] == 5
    assert roles["Backend Developer"]["requested_headcount"] == 4

    projects = {
        item["project_id"]: item for item in result["requirements_by_project"]
    }
    assert projects["demand-project-001"]["project_name"] == (
        "Analytics Modernization"
    )
    assert projects["demand-project-001"]["requirement_count"] == 2
    assert projects["demand-project-001"]["requested_headcount"] == 5
    assert projects["demand-project-002"]["requested_headcount"] == 4

    priorities = {
        item["name"]: item for item in result["requirements_by_priority"]
    }
    assert priorities["high"]["requirement_count"] == 2
    assert priorities["high"]["requested_headcount"] == 7
    assert priorities["medium"]["requested_headcount"] == 2

    skills = {item["name"]: item for item in result["requirements_by_skill"]}
    assert skills["Python"]["requirement_count"] == 2
    assert skills["Python"]["requested_headcount"] == 7
    assert skills["SQL"]["requirement_count"] == 2
    assert skills["SQL"]["requested_headcount"] == 5


def test_staffing_demand_analysis_returns_bounded_requirement_details(db):
    _create_staffing_demand_fixtures(db)

    result = get_assistant_staffing_demand_analysis(db, limit=2)

    assert result["total_requirement_count"] == 3
    assert result["total_requested_headcount"] == 9
    assert result["result_count"] == 2
    assert result["limit"] == 2
    assert result["has_more_results"] is True
    assert len(result["requirements"]) == 2

    first = result["requirements"][0]
    assert first["staffing_requirement_id"] == "demand-requirement-003" or (
        first["staffing_requirement_id"] == "demand-requirement-001"
    )
    assert "required_skills" in first
    assert "start_date" in first
    assert "end_date" in first


def test_staffing_demand_analysis_handles_empty_dataset(db):
    result = get_assistant_staffing_demand_analysis(db)

    assert result["total_requirement_count"] == 0
    assert result["total_requested_headcount"] == 0
    assert result["open_requirement_count"] == 0
    assert result["open_requested_headcount"] == 0
    assert result["requirements_by_status"] == []
    assert result["requirements_by_role"] == []
    assert result["requirements_by_project"] == []
    assert result["requirements_by_priority"] == []
    assert result["requirements_by_skill"] == []
    assert result["requirements"] == []
    assert result["result_count"] == 0
    assert result["has_more_results"] is False


def test_staffing_demand_analysis_rejects_invalid_limits(db):
    for limit in (0, -1, 26, True, False, 1.5, "2"):
        with pytest.raises(InvalidAssistantFilterError, match="limit"):
            get_assistant_staffing_demand_analysis(db, limit=limit)


def test_staffing_demand_analysis_explains_requested_headcount_is_not_vacancies(
    db,
):
    _create_staffing_demand_fixtures(db)

    result = get_assistant_staffing_demand_analysis(db)

    assert "not a verified vacancy count" in result["notice"]
    assert "forecasted demand are not calculated" in result["notice"]


def test_staffing_demand_analysis_does_not_modify_requirement_records(db):
    _create_staffing_demand_fixtures(db)
    before = [
        (
            requirement.staffing_requirement_id,
            requirement.project_id,
            requirement.role_name,
            requirement.required_quantity,
            requirement.status,
            requirement.priority,
        )
        for requirement in db.scalars(
            select(StaffingRequirement).order_by(
                StaffingRequirement.staffing_requirement_id
            )
        ).all()
    ]

    get_assistant_staffing_demand_analysis(db)
    db.expire_all()

    after = [
        (
            requirement.staffing_requirement_id,
            requirement.project_id,
            requirement.role_name,
            requirement.required_quantity,
            requirement.status,
            requirement.priority,
        )
        for requirement in db.scalars(
            select(StaffingRequirement).order_by(
                StaffingRequirement.staffing_requirement_id
            )
        ).all()
    ]

    assert after == before

