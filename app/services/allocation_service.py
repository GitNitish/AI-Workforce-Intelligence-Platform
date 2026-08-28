from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    Allocation,
    Employee,
    Project,
    StaffingRequirement,
)
from app.schemas.allocation import (
    AllocationCreate,
    AllocationUpdate,
)
from app.services.staffing_service import (
    get_staffing_requirement,
)


def create_allocation(
    db: Session,
    allocation_data: AllocationCreate,
) -> Allocation:

    # --------------------------------------------------------
    # Verify employee
    # --------------------------------------------------------

    employee = db.get(
        Employee,
        allocation_data.employee_id,
    )

    if employee is None:
        raise ValueError("Employee not found")

    # --------------------------------------------------------
    # Verify project
    # --------------------------------------------------------

    project = db.get(
        Project,
        allocation_data.project_id,
    )

    if project is None:
        raise ValueError("Project not found")

    # --------------------------------------------------------
    # Verify staffing requirement
    # --------------------------------------------------------

    requirement = None

    if allocation_data.staffing_requirement_id is not None:

        requirement = get_staffing_requirement(
            db,
            allocation_data.staffing_requirement_id,
        )

        if requirement is None:
            raise ValueError(
                "Staffing requirement not found"
            )

        # Requirement must belong to the same project
        if requirement.project_id != allocation_data.project_id:
            raise ValueError(
                "Staffing requirement does not belong to the project"
            )

    # --------------------------------------------------------
    # Validate employee allocation capacity
    # --------------------------------------------------------

    existing_allocations = db.scalars(
        select(Allocation).where(
            Allocation.employee_id
            == allocation_data.employee_id,
            Allocation.status == "active",
        )
    ).all()

    total_allocation = 0

    for existing in existing_allocations:

        # Check whether the allocation periods overlap
        existing_end = existing.end_date

        dates_overlap = (
            existing_end is None
            or allocation_data.start_date
            <= existing_end
        ) and (
            allocation_data.end_date is None
            or existing.start_date
            <= allocation_data.end_date
        )

        if dates_overlap:
            total_allocation += (
                existing.allocation_percentage
            )

    # New allocation must not push employee above 100%
    if (
        total_allocation
        + allocation_data.allocation_percentage
        > 100
    ):
        raise ValueError(
            "Employee allocation capacity exceeded"
        )

    # --------------------------------------------------------
    # Create allocation
    # --------------------------------------------------------

    allocation = Allocation(
        employee_id=allocation_data.employee_id,
        project_id=allocation_data.project_id,
        staffing_requirement_id=(
            allocation_data.staffing_requirement_id
        ),
        allocation_percentage=(
            allocation_data.allocation_percentage
        ),
        start_date=allocation_data.start_date,
        end_date=allocation_data.end_date,
        status=allocation_data.status,
        allocated_by=allocation_data.allocated_by,
    )

    db.add(allocation)
    db.commit()
    db.refresh(allocation)

    return allocation


def get_allocations(
    db: Session,
) -> list[Allocation]:

    statement = (
        select(Allocation)
        .order_by(
            Allocation.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


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

    if (
        new_start_date is not None
        and new_end_date is not None
        and new_end_date < new_start_date
    ):
        raise ValueError(
            "end_date must be greater than "
            "or equal to start_date"
        )

    # --------------------------------------------------------
    # Validate employee allocation capacity on update
    # --------------------------------------------------------

    if new_status == "active":

        existing_allocations = db.scalars(
            select(Allocation).where(
                Allocation.employee_id
                == allocation.employee_id,
                Allocation.status == "active",
                Allocation.allocation_id
                != allocation.allocation_id,
            )
        ).all()

        total_allocation = 0

        for existing in existing_allocations:

            existing_end = existing.end_date

            dates_overlap = (
                existing_end is None
                or new_start_date <= existing_end
            ) and (
                new_end_date is None
                or existing.start_date <= new_end_date
            )

            if dates_overlap:
                total_allocation += (
                    existing.allocation_percentage
                )

        if (
            total_allocation
            + new_percentage
            > 100
        ):
            raise ValueError(
                "Employee allocation capacity exceeded"
            )

    # --------------------------------------------------------
    # Apply update
    # --------------------------------------------------------

    for field, value in update_data.items():
        setattr(
            allocation,
            field,
            value,
        )

    db.commit()
    db.refresh(allocation)

    return allocation


def delete_allocation(
    db: Session,
    allocation: Allocation,
) -> None:

    db.delete(allocation)
    db.commit()