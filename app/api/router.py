from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate,
)
from app.services.employee_service import (
    create_employee,
    delete_employee,
    get_employee,
    get_employees,
    update_employee,
)

api_router = APIRouter()


@api_router.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def list_employees(
    db: Session = Depends(get_db),
):
    return get_employees(db)


@api_router.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def read_employee(
    employee_id: str,
    db: Session = Depends(get_db),
):
    employee = get_employee(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return employee


@api_router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
):
    return create_employee(db, employee_data)


@api_router.put(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def update_existing_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = get_employee(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    return update_employee(db, employee, employee_data)


@api_router.delete(
    "/employees/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_existing_employee(
    employee_id: str,
    db: Session = Depends(get_db),
):
    employee = get_employee(db, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )

    delete_employee(db, employee)