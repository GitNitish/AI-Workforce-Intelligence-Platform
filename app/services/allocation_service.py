
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    Allocation,
    Employee,
    Project,
)
from app.schemas.allocation import (
    AllocationCreate,
    AllocationUpdate,
)
from app.services.staffing_service import (
    get_staffing_requirement,
)


ACTIVE_STATUS = "active"
DEALLOCATED_STATUS = "deallocated"
ALLOWED_STATUSES = {
    ACTIVE_STATUS,
    DEALLOCATED_STATUS,
}
ELIGIBLE_PROJECT_STATUSES = {
    "active",
    "in_progress",
}


def _validate_status(status: str) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError(
            "Allocation status must be 'active' or 'deallocated'"
        )


def _validate_project_eligibility(project: Project) -> None:
    if project.status not in ELIGIBLE_PROJECT_STATUSES:
        raise ValueError(
            "Project must have status 'active' or 'in_progress' "
            "to receive allocations"
        )


def _validate_date_range(
    start_date: date,
    end_date: date | None,
) -> None:
    if not isinstance(start_date, date):
        raise ValueError("start_date is required")

    if end_date is not None and end_date < start_date:
        raise ValueError(
            "end_date must be greater than or equal to start_date"
        )


def _validate_percentage(percentage: float) -> None:
    if percentage is None or not 0 < percentage <= 100:
        raise ValueError(
            "allocation_percentage must be greater than 0 and no more than 100"
        )


def _validate_capacity(
    existing_allocations: list[Allocation],
    new_start_date: date,
    new_end_date: date | None,
    new_percentage: float,
) -> None:
    """
    Validate that concurrent active allocations never exceed 100%.

    Each allocation is evaluated over its actual date interval.
    End dates are inclusive. An end date of None means no end date.
    """

    _validate_date_range(new_start_date, new_end_date)
    _validate_percentage(new_percentage)

    relevant_allocations = [
        allocation
        for allocation in existing_allocations
        if allocation.status == ACTIVE_STATUS
        and (
            allocation.end_date is None
            or allocation.end_date >= new_start_date
        )
        and (
            new_end_date is None
            or allocation.start_date <= new_end_date
        )
    ]

    boundaries = {new_start_date}

    if new_end_date is not None:
        boundaries.add(new_end_date + timedelta(days=1))

    for allocation in relevant_allocations:
        overlap_start = max(
            new_start_date,
            allocation.start_date,
        )

        boundaries.add(overlap_start)

        if allocation.end_date is not None:
            overlap_end = allocation.end_date

            if (
                new_end_date is not None
                and overlap_end > new_end_date
            ):
                overlap_end = new_end_date

            boundaries.add(
                overlap_end + timedelta(days=1)
            )

    for segment_start in sorted(boundaries):
        if (
            new_end_date is not None
            and segment_start > new_end_date
        ):
            continue

        existing_percentage = sum(
            allocation.allocation_percentage
            for allocation in relevant_allocations
            if allocation.start_date <= segment_start
            and (
                allocation.end_date is None
                or allocation.end_date >= segment_start
            )
        )

        if existing_percentage + new_percentage > 100:
            raise ValueError(
                "Employee allocation capacity exceeded"
            )


def create_allocation(
    db: Session,
    allocation_data: AllocationCreate,
) -> Allocation:

    if allocation_data.status != ACTIVE_STATUS:
        raise ValueError("New allocations must have status 'active'")

    _validate_status(allocation_data.status)

    _validate_date_range(
        allocation_data.start_date,
        allocation_data.end_date,
    )

    _validate_percentage(
        allocation_data.allocation_percentage,
    )

    employee = db.get(
        Employee,
        allocation_data.employee_id,
    )

    if employee is None:
        raise ValueError("Employee not found")

    project = db.get(
        Project,
        allocation_data.project_id,
    )

    if project is None:
        raise ValueError("Project not found")

    _validate_project_eligibility(project)

    if allocation_data.staffing_requirement_id is not None:
        requirement = get_staffing_requirement(
            db,
            allocation_data.staffing_requirement_id,
        )

        if requirement is None:
            raise ValueError("Staffing requirement not found")

        if requirement.project_id != allocation_data.project_id:
            raise ValueError(
                "Staffing requirement does not belong to the project"
            )

    if allocation_data.status == ACTIVE_STATUS:
        existing_allocations = db.scalars(
            select(Allocation).where(
                Allocation.employee_id == allocation_data.employee_id,
                Allocation.status == ACTIVE_STATUS,
            )
        ).all()

        _validate_capacity(
            existing_allocations=list(existing_allocations),
            new_start_date=allocation_data.start_date,
            new_end_date=allocation_data.end_date,
            new_percentage=allocation_data.allocation_percentage,
        )

    allocation = Allocation(
        employee_id=allocation_data.employee_id,
        project_id=allocation_data.project_id,
        staffing_requirement_id=(
            allocation_data.staffing_requirement_id
        ),
        allocation_percentage=allocation_data.allocation_percentage,
        start_date=allocation_data.start_date,
        end_date=allocation_data.end_date,
        status=allocation_data.status,
        allocated_by=allocation_data.allocated_by,
    )

    db.add(allocation)
    db.flush()
    db.refresh(allocation)

    return allocation


def get_allocations(
    db: Session,
) -> list[Allocation]:

    statement = (
        select(Allocation)
        .order_by(Allocation.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_allocation(
    db: Session,
    allocation_id: str,
) -> Allocation | None:

    statement = select(Allocation).where(
        Allocation.allocation_id == allocation_id
    )

    return db.scalar(statement)


def update_allocation(
    db: Session,
    allocation: Allocation,
    allocation_data: AllocationUpdate,
) -> Allocation:

    update_data = allocation_data.model_dump(
        exclude_unset=True
    )

    new_start_date = update_data.get(
        "start_date",
        allocation.start_date,
    )

    new_end_date = update_data.get(
        "end_date",
        allocation.end_date,
    )

    new_percentage = update_data.get(
        "allocation_percentage",
        allocation.allocation_percentage,
    )

    new_status = update_data.get(
        "status",
        allocation.status,
    )

    if new_start_date is None:
        raise ValueError("start_date is required")

    if new_percentage is None:
        raise ValueError("allocation_percentage is required")

    if new_status is None:
        raise ValueError("Allocation status is required")

    if new_status == DEALLOCATED_STATUS and "status" in update_data:
        raise ValueError(
            "Use the dedicated deallocation operation to deallocate an allocation"
        )

    _validate_status(new_status)

    _validate_date_range(
        new_start_date,
        new_end_date,
    )

    _validate_percentage(new_percentage)

    is_reactivation = (
        allocation.status == DEALLOCATED_STATUS
        and new_status == ACTIVE_STATUS
    )

    if is_reactivation:
        project = db.get(Project, allocation.project_id)

        if project is None:
            raise ValueError("Project not found")

        _validate_project_eligibility(project)

    if new_status == ACTIVE_STATUS:
        existing_allocations = db.scalars(
            select(Allocation).where(
                Allocation.employee_id == allocation.employee_id,
                Allocation.status == ACTIVE_STATUS,
                Allocation.allocation_id != allocation.allocation_id,
            )
        ).all()

        _validate_capacity(
            existing_allocations=list(existing_allocations),
            new_start_date=new_start_date,
            new_end_date=new_end_date,
            new_percentage=new_percentage,
        )

    for field, value in update_data.items():
        setattr(allocation, field, value)

    db.flush()
    db.refresh(allocation)

    return allocation


def deallocate_allocation(
    db: Session,
    allocation: Allocation,
) -> Allocation:

    if allocation.status == DEALLOCATED_STATUS:
        raise ValueError(
            "Allocation is already deallocated"
        )

    allocation.status = DEALLOCATED_STATUS

    db.flush()
    db.refresh(allocation)

    return allocation
