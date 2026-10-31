
from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.models.entities import Allocation, Employee, Project
from app.schemas.allocation import AllocationCreate, AllocationUpdate
from app.services.allocation_service import (
    create_allocation,
    deallocate_allocation,
    get_allocation,
    get_allocations,
    update_allocation,
)


@pytest.fixture
def db_session():
    """Provide an isolated in-memory database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        employee = Employee(
            employee_id="employee-allocation-test",
            employee_code="ALLOC-TEST-001",
            name="Allocation Test Employee",
            email="allocation-test@example.com",
            experience_years=5,
            availability_status="available",
            utilization_percentage=0,
            status="active",
        )
        project = Project(
            project_id="project-allocation-test",
            project_code="ALLOC-PROJECT-001",
            project_name="Allocation Test Project",
            status="active",
            priority="medium",
        )
        session.add_all([employee, project])
        session.commit()

        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def make_allocation_data(
    *,
    percentage=50,
    start_date=date(2026, 10, 1),
    end_date=date(2026, 10, 31),
    status="active",
):
    return AllocationCreate(
        employee_id="employee-allocation-test",
        project_id="project-allocation-test",
        allocation_percentage=percentage,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )


def test_create_allocation_persists_and_can_be_retrieved(db_session):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=60),
    )
    db_session.commit()

    retrieved = get_allocation(
        db_session,
        allocation.allocation_id,
    )

    assert retrieved is not None
    assert retrieved.allocation_id == allocation.allocation_id
    assert retrieved.employee_id == "employee-allocation-test"
    assert retrieved.project_id == "project-allocation-test"
    assert retrieved.allocation_percentage == 60
    assert retrieved.status == "active"


@pytest.mark.parametrize("project_status", ["active", "in_progress"])
def test_create_allocation_allows_eligible_project_statuses(
    db_session,
    project_status,
):
    project = db_session.get(Project, "project-allocation-test")
    project.status = project_status
    db_session.commit()

    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )

    assert allocation.status == "active"


@pytest.mark.parametrize(
    "project_status",
    ["planned", "completed", "cancelled", "unknown_status"],
)
def test_create_allocation_rejects_ineligible_project_statuses(
    db_session,
    project_status,
):
    project = db_session.get(Project, "project-allocation-test")
    project.status = project_status
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Project must have status 'active' or 'in_progress'",
    ):
        create_allocation(
            db_session,
            make_allocation_data(percentage=50),
        )


@pytest.mark.parametrize("project_status", ["active", "in_progress"])
def test_reactivation_allows_eligible_project_statuses(
    db_session,
    project_status,
):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )
    db_session.commit()

    deallocate_allocation(db_session, allocation)
    db_session.commit()

    project = db_session.get(Project, "project-allocation-test")
    project.status = project_status
    db_session.commit()

    reactivated = update_allocation(
        db_session,
        allocation,
        AllocationUpdate(status="active"),
    )

    assert reactivated.status == "active"


@pytest.mark.parametrize(
    "project_status",
    ["planned", "completed", "cancelled", "unknown_status"],
)
def test_reactivation_rejects_ineligible_project_statuses(
    db_session,
    project_status,
):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )
    db_session.commit()

    deallocate_allocation(db_session, allocation)
    db_session.commit()

    project = db_session.get(Project, "project-allocation-test")
    project.status = project_status
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Project must have status 'active' or 'in_progress'",
    ):
        update_allocation(
            db_session,
            allocation,
            AllocationUpdate(status="active"),
        )

    db_session.refresh(allocation)
    assert allocation.status == "deallocated"


def test_create_allocation_rejects_concurrent_capacity_over_100_percent(
    db_session,
):
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=70,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 20),
        ),
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Employee allocation capacity exceeded",
    ):
        create_allocation(
            db_session,
            make_allocation_data(
                percentage=40,
                start_date=date(2026, 10, 10),
                end_date=date(2026, 10, 30),
            ),
        )


def test_create_allocation_allows_non_overlapping_date_periods(
    db_session,
):
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=100,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15),
        ),
    )
    db_session.commit()

    second_allocation = create_allocation(
        db_session,
        make_allocation_data(
            percentage=100,
            start_date=date(2026, 10, 16),
            end_date=date(2026, 10, 31),
        ),
    )

    assert second_allocation.status == "active"
    assert second_allocation.allocation_percentage == 100


def test_update_allocation_revalidates_employee_capacity(db_session):
    first = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )
    second = create_allocation(
        db_session,
        make_allocation_data(
            percentage=30,
            start_date=date(2026, 11, 1),
            end_date=date(2026, 11, 30),
        ),
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Employee allocation capacity exceeded",
    ):
        update_allocation(
            db_session,
            second,
            AllocationUpdate(
                start_date=date(2026, 10, 15),
                end_date=date(2026, 10, 31),
                allocation_percentage=60,
            ),
        )

    db_session.refresh(first)
    db_session.refresh(second)
    assert first.allocation_percentage == 50
    assert second.allocation_percentage == 30
    assert second.start_date == date(2026, 11, 1)


def test_deallocation_preserves_record_and_releases_capacity(db_session):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=100),
    )
    db_session.commit()
    allocation_id = allocation.allocation_id

    deallocated = deallocate_allocation(
        db_session,
        allocation,
    )
    db_session.commit()

    assert deallocated.allocation_id == allocation_id
    assert deallocated.status == "deallocated"
    assert db_session.scalar(
        select(Allocation).where(
            Allocation.allocation_id == allocation_id
        )
    ) is not None

    replacement = create_allocation(
        db_session,
        make_allocation_data(percentage=100),
    )

    assert replacement.status == "active"
    assert len(get_allocations(db_session)) == 2


def test_deallocation_rejects_an_already_deallocated_record(db_session):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )
    db_session.commit()

    deallocate_allocation(db_session, allocation)
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Allocation is already deallocated",
    ):
        deallocate_allocation(db_session, allocation)


def test_create_allocation_rejects_deallocated_status():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AllocationCreate(
            employee_id="employee-allocation-test",
            project_id="project-allocation-test",
            allocation_percentage=50,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 31),
            status="deallocated",
        )


def test_update_rejects_deallocation_but_allows_reactivation_with_capacity_validation(
    db_session,
):
    from pydantic import ValidationError

    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=60),
    )
    db_session.commit()

    deallocate_allocation(db_session, allocation)
    db_session.commit()

    with pytest.raises(ValidationError):
        AllocationUpdate(status="deallocated")

    reactivated = update_allocation(
        db_session,
        allocation,
        AllocationUpdate(status="active"),
    )
    db_session.commit()

    assert reactivated.status == "active"
    assert reactivated.allocation_percentage == 60


def test_reactivation_revalidates_capacity(db_session):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=60),
    )
    db_session.commit()
    deallocate_allocation(db_session, allocation)
    db_session.commit()

    create_allocation(
        db_session,
        make_allocation_data(
            percentage=50,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 31),
        ),
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Employee allocation capacity exceeded",
    ):
        update_allocation(
            db_session,
            allocation,
            AllocationUpdate(status="active"),
        )

    db_session.refresh(allocation)
    assert allocation.status == "deallocated"


def test_reactivation_does_not_apply_project_status_rule_to_active_edits(
    db_session,
):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )
    db_session.commit()

    project = db_session.get(Project, "project-allocation-test")
    project.status = "completed"
    db_session.commit()

    updated = update_allocation(
        db_session,
        allocation,
        AllocationUpdate(allocation_percentage=40),
    )

    assert updated.status == "active"
    assert updated.allocation_percentage == 40


def test_deallocated_record_can_be_edited_without_reactivation(db_session):
    allocation = create_allocation(
        db_session,
        make_allocation_data(percentage=50),
    )
    db_session.commit()

    deallocate_allocation(db_session, allocation)
    db_session.commit()

    project = db_session.get(Project, "project-allocation-test")
    project.status = "completed"
    db_session.commit()

    updated = update_allocation(
        db_session,
        allocation,
        AllocationUpdate(
            allocation_percentage=40,
            start_date=date(2026, 10, 5),
        ),
    )

    assert updated.status == "deallocated"
    assert updated.allocation_percentage == 40
    assert updated.start_date == date(2026, 10, 5)


def test_create_service_rejects_non_active_status_even_if_schema_is_bypassed(
    db_session,
):
    allocation_data = AllocationCreate.model_construct(
        employee_id="employee-allocation-test",
        project_id="project-allocation-test",
        staffing_requirement_id=None,
        allocation_percentage=50,
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 31),
        status="deallocated",
        allocated_by=None,
    )

    with pytest.raises(
        ValueError,
        match="New allocations must have status 'active'",
    ):
        create_allocation(db_session, allocation_data)


def test_open_ended_allocation_consumes_capacity_for_later_dates(
    db_session,
):
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=60,
            start_date=date(2026, 10, 1),
            end_date=None,
        ),
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Employee allocation capacity exceeded",
    ):
        create_allocation(
            db_session,
            make_allocation_data(
                percentage=50,
                start_date=date(2026, 11, 1),
                end_date=date(2026, 11, 30),
            ),
        )


def test_multiple_date_segments_validate_combined_capacity(
    db_session,
):
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=40,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15),
        ),
    )
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=35,
            start_date=date(2026, 10, 10),
            end_date=date(2026, 10, 20),
        ),
    )
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=30,
            start_date=date(2026, 10, 16),
            end_date=date(2026, 10, 31),
        ),
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Employee allocation capacity exceeded",
    ):
        create_allocation(
            db_session,
            make_allocation_data(
                percentage=30,
                start_date=date(2026, 10, 1),
                end_date=date(2026, 10, 31),
            ),
        )


def test_allocations_sharing_end_and_start_date_are_overlapping(
    db_session,
):
    create_allocation(
        db_session,
        make_allocation_data(
            percentage=60,
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15),
        ),
    )
    db_session.commit()

    with pytest.raises(
        ValueError,
        match="Employee allocation capacity exceeded",
    ):
        create_allocation(
            db_session,
            make_allocation_data(
                percentage=50,
                start_date=date(2026, 10, 15),
                end_date=date(2026, 10, 31),
            ),
        )
