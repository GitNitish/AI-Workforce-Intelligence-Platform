from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.database.dependencies import get_db

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

from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
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

from app.services.audit_service import (
    create_audit_event,
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

from app.services.recommendation_service import (
    generate_recommendations,
)

from app.services.staffing_service import (
    create_staffing_requirement,
    get_staffing_requirement,
    get_staffing_requirements,
    update_staffing_requirement,
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
    current_user=Depends(
        require_permission("employee.write")
    ),
):
    try:
        employee = create_employee(
            db,
            employee_data,
        )

        create_audit_event(
            db=db,
            action="CREATE",
            entity_type="Employee",
            entity_id=employee.employee_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return employee

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@api_router.put(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def update_existing_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("employee.write")
    ),
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

    try:
        updated_employee = update_employee(
            db,
            employee,
            employee_data,
        )

        create_audit_event(
            db=db,
            action="UPDATE",
            entity_type="Employee",
            entity_id=updated_employee.employee_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return updated_employee

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@api_router.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("employee.write")
    ),
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

    deleted_employee_id = employee.employee_id

    delete_employee(
        db,
        employee,
    )

    create_audit_event(
        db=db,
        action="DELETE",
        entity_type="Employee",
        entity_id=deleted_employee_id,
        result="success",
        user_id=current_user.user_id,
        metadata={
            "source": "api",
        },
    )

    db.commit()


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
    current_user=Depends(
        require_permission("project.write")
    ),
):
    try:
        project = create_project(
            db,
            project_data,
        )

        create_audit_event(
            db=db,
            action="CREATE",
            entity_type="Project",
            entity_id=project.project_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return project

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
    current_user=Depends(
        require_permission("project.write")
    ),
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
        updated_project = update_project(
            db,
            project,
            project_data,
        )

        create_audit_event(
            db=db,
            action="UPDATE",
            entity_type="Project",
            entity_id=updated_project.project_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return updated_project

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
    current_user=Depends(
        require_permission("staffing.write")
    ),
):
    try:
        requirement = create_staffing_requirement(
            db,
            project_id,
            requirement_data,
        )

        create_audit_event(
            db=db,
            action="CREATE",
            entity_type="StaffingRequirement",
            entity_id=requirement.staffing_requirement_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return requirement

    except ValueError as exc:
        if str(exc) == "Project not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
    current_user=Depends(
        require_permission("staffing.write")
    ),
):
    try:
        requirement = update_staffing_requirement(
            db,
            requirement_id,
            requirement_data,
        )

        create_audit_event(
            db=db,
            action="UPDATE",
            entity_type="StaffingRequirement",
            entity_id=requirement.staffing_requirement_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return requirement

    except ValueError as exc:
        if str(exc) == "Staffing requirement not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


# ============================================================
# Recommendation APIs
# ============================================================


@api_router.post(
    "/recommendations",
    response_model=RecommendationResponse,
)
def generate_staffing_recommendations(
    recommendation_request: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("recommendation.generate")
    ),
):
    try:
        recommendations = generate_recommendations(
            db,
            recommendation_request.staffing_requirement_id,
        )

    except ValueError as exc:
        if str(exc) == "Staffing requirement not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    generated_at = (
        recommendations[0].generated_at
        if recommendations
        else datetime.now(timezone.utc)
    )

    response_items = []

    for recommendation in recommendations:
        employee = recommendation.employee

        matched_skills = []

        if employee is not None:
            reason = recommendation.recommendation_reason or ""

            if reason.startswith("Matched skills: "):
                matched_section = reason.split(
                    ". ",
                    1,
                )[0]

                matched_text = matched_section[
                    len("Matched skills: "):
                ]

                if matched_text:
                    matched_skills = [
                        skill.strip()
                        for skill in matched_text.split(",")
                    ]

            response_items.append(
                RecommendationItem(
                    employee_id=(
                        recommendation.employee_id
                    ),
                    rank=recommendation.rank,
                    score=recommendation.score,
                    eligibility_status=(
                        recommendation.eligibility_status
                    ),
                    matched_skills=matched_skills,
                    reason=(
                        recommendation.recommendation_reason
                        or ""
                    ),
                )
            )

    return RecommendationResponse(
        staffing_requirement_id=(
            recommendation_request.staffing_requirement_id
        ),
        recommendations=response_items,
        generated_at=generated_at,
        message=(
            "Recommendations generated successfully."
            if response_items
            else "No eligible employees found."
        ),
    )


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
    current_user=Depends(
        require_permission("allocation.write")
    ),
):
    try:
        allocation = create_allocation(
            db,
            allocation_data,
        )

        create_audit_event(
            db=db,
            action="CREATE",
            entity_type="Allocation",
            entity_id=allocation.allocation_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return allocation

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
    current_user=Depends(
        require_permission("allocation.write")
    ),
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
        updated_allocation = update_allocation(
            db,
            allocation,
            allocation_data,
        )

        create_audit_event(
            db=db,
            action="UPDATE",
            entity_type="Allocation",
            entity_id=updated_allocation.allocation_id,
            result="success",
            user_id=current_user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return updated_allocation

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
    current_user=Depends(
        require_permission("allocation.write")
    ),
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

    deleted_allocation_id = allocation.allocation_id

    delete_allocation(
        db,
        allocation,
    )

    create_audit_event(
        db=db,
        action="DELETE",
        entity_type="Allocation",
        entity_id=deleted_allocation_id,
        result="success",
        user_id=current_user.user_id,
        metadata={
            "source": "api",
        },
    )

    db.commit()