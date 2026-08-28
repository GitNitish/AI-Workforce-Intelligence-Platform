from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.models.entities import StaffingRequirement

from app.schemas.allocation import (
    AllocationCreate,
    AllocationResponse,
    AllocationUpdate,
)

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)

from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

from app.schemas.staffing_requirement import (
    StaffingRequirementCreate,
    StaffingRequirementResponse,
    StaffingRequirementUpdate,
)

from app.services.allocation_service import (
    create_allocation,
    delete_allocation,
    get_allocation,
    get_allocations,
    update_allocation,
)

from app.services.employee_service import (
    calculate_employee_utilization,
    create_employee,
    delete_employee,
    get_employee,
    get_employees,
    search_employees,
    update_employee,
)

from app.services.project_service import (
    create_project,
    get_project,
    get_project_employees,
    get_projects,
    search_projects,
    update_project,
)

from app.services.staffing_service import (
    create_staffing_requirement,
    get_staffing_requirement,
    get_staffing_requirements,
)


api_router = APIRouter()


# ============================================================
# Employee APIs
# ============================================================


@api_router.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def list_employees(
    db: Session = Depends(get_db),
):
    return get_employees(db)


@api_router.get(
    "/employees/search",
    response_model=list[EmployeeResponse],
)
def search_employee_records(
    name: str | None = None,
    employee_code: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    availability_status: str | None = None,
    location: str | None = None,
    min_experience: float | None = None,
    max_utilization: float | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return search_employees(
        db=db,
        name=name,
        employee_code=employee_code,
        department=department,
        designation=designation,
        availability_status=availability_status,
        location=location,
        min_experience=min_experience,
        max_utilization=max_utilization,
        status=status,
    )


@api_router.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def read_employee(
    employee_id: str,
    db: Session = Depends(get_db),
):
    employee = get_employee(
        db,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@api_router.get(
    "/employees/{employee_id}/utilization",
)
def read_employee_utilization(
    employee_id: str,
    db: Session = Depends(get_db),
):
    try:
        utilization = calculate_employee_utilization(
            db,
            employee_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return {
        "employee_id": employee_id,
        "utilization_percentage": utilization,
        "available_percentage": max(
            0,
            100 - utilization,
        ),
    }


@api_router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    return create_employee(
        db,
        employee_data,
    )


@api_router.put(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def update_existing_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = get_employee(
        db,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return update_employee(
        db,
        employee,
        employee_data,
    )


@api_router.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_employee(
    employee_id: str,
    db: Session = Depends(get_db),
):
    employee = get_employee(
        db,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    delete_employee(
        db,
        employee,
    )


# ============================================================
# Project APIs
# ============================================================


@api_router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def list_projects(
    db: Session = Depends(get_db),
):
    return get_projects(db)


@api_router.get(
    "/projects/search",
    response_model=list[ProjectResponse],
)
def search_project_records(
    project_code: str | None = None,
    project_name: str | None = None,
    client_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
):
    return search_projects(
        db=db,
        project_code=project_code,
        project_name=project_name,
        client_name=client_name,
        status=status,
        priority=priority,
    )


@api_router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def read_project(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@api_router.get(
    "/projects/{project_id}/employees",
    response_model=list[EmployeeResponse],
)
def list_project_employees(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return get_project_employees(
        db,
        project_id,
    )


@api_router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_project(
            db,
            project_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@api_router.put(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def update_existing_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    try:
        return update_project(
            db,
            project,
            project_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ============================================================
# Staffing Requirement APIs
# ============================================================


@api_router.get(
    "/projects/{project_id}/requirements",
    response_model=list[StaffingRequirementResponse],
)
def list_project_requirements(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = get_project(
        db,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return get_staffing_requirements(
        db,
        project_id,
    )


@api_router.post(
    "/projects/{project_id}/requirements",
    response_model=StaffingRequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_requirement(
    project_id: str,
    requirement_data: StaffingRequirementCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_staffing_requirement(
            db,
            project_id,
            requirement_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@api_router.get(
    "/requirements/{requirement_id}",
    response_model=StaffingRequirementResponse,
)
def read_staffing_requirement(
    requirement_id: str,
    db: Session = Depends(get_db),
):
    requirement = get_staffing_requirement(
        db,
        requirement_id,
    )

    if requirement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staffing requirement not found",
        )

    return requirement


@api_router.put(
    "/requirements/{requirement_id}",
    response_model=StaffingRequirementResponse,
)
def update_existing_staffing_requirement(
    requirement_id: str,
    requirement_data: StaffingRequirementUpdate,
    db: Session = Depends(get_db),
):
    requirement = db.get(
        StaffingRequirement,
        requirement_id,
    )

    if requirement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staffing requirement not found",
        )

    update_data = requirement_data.model_dump(
        exclude_unset=True
    )

    new_start_date = update_data.get(
        "start_date",
        requirement.start_date,
    )

    new_end_date = update_data.get(
        "end_date",
        requirement.end_date,
    )

    if (
        new_start_date is not None
        and new_end_date is not None
        and new_end_date < new_start_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "end_date must be greater than "
                "or equal to start_date"
            ),
        )

    for field, value in update_data.items():
        setattr(
            requirement,
            field,
            value,
        )

    db.commit()
    db.refresh(requirement)

    return requirement


# ============================================================
# Allocation APIs
# ============================================================


@api_router.get(
    "/allocations",
    response_model=list[AllocationResponse],
)
def list_allocations(
    db: Session = Depends(get_db),
):
    return get_allocations(db)


@api_router.get(
    "/allocations/{allocation_id}",
    response_model=AllocationResponse,
)
def read_allocation(
    allocation_id: str,
    db: Session = Depends(get_db),
):
    allocation = get_allocation(
        db,
        allocation_id,
    )

    if allocation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found",
        )

    return allocation


@api_router.post(
    "/allocations",
    response_model=AllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_allocation(
    allocation_data: AllocationCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_allocation(
            db,
            allocation_data,
        )

    except ValueError as exc:

        if str(exc) == "Employee allocation capacity exceeded":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "ALLOCATION_CONFLICT: "
                    "Employee allocation capacity exceeded"
                ),
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@api_router.put(
    "/allocations/{allocation_id}",
    response_model=AllocationResponse,
)
def update_existing_allocation(
    allocation_id: str,
    allocation_data: AllocationUpdate,
    db: Session = Depends(get_db),
):
    allocation = get_allocation(
        db,
        allocation_id,
    )

    if allocation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found",
        )

    try:
        return update_allocation(
            db,
            allocation,
            allocation_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@api_router.delete(
    "/allocations/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_allocation(
    allocation_id: str,
    db: Session = Depends(get_db),
):
    allocation = get_allocation(
        db,
        allocation_id,
    )

    if allocation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allocation not found",
        )

    delete_allocation(
        db,
        allocation,
    )
