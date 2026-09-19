from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def _calculate_employee_utilization_from_record(
    employee: Employee,
) -> float:
    active_allocations = [
        allocation
        for allocation in employee.allocations
        if allocation.status == "active"
    ]

    utilization = sum(
        allocation.allocation_percentage
        for allocation in active_allocations
    )

    return min(utilization, 100.0)


def _apply_calculated_utilization(
    employee: Employee,
) -> Employee:
    employee.utilization_percentage = (
        _calculate_employee_utilization_from_record(
            employee
        )
    )

    return employee


def create_employee(
    db: Session,
    employee_data: EmployeeCreate,
) -> Employee:
    employee = Employee(**employee_data.model_dump())

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employees(
    db: Session,
) -> list[Employee]:
    result = db.execute(
        select(Employee)
    )

    employees = list(result.scalars().all())

    for employee in employees:
        _apply_calculated_utilization(employee)

    return employees


def search_employees(
    db: Session,
    name: str | None = None,
    employee_code: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    availability_status: str | None = None,
    location: str | None = None,
    min_experience: float | None = None,
    max_utilization: float | None = None,
    status: str | None = None,
) -> list[Employee]:

    statement = select(Employee)

    if name:
        statement = statement.where(
            Employee.name.ilike(f"%{name}%")
        )

    if employee_code:
        statement = statement.where(
            Employee.employee_code.ilike(
                f"%{employee_code}%"
            )
        )

    if department:
        statement = statement.where(
            Employee.department.ilike(
                f"%{department}%"
            )
        )

    if designation:
        statement = statement.where(
            Employee.designation.ilike(
                f"%{designation}%"
            )
        )

    if availability_status:
        statement = statement.where(
            Employee.availability_status
            == availability_status
        )

    if location:
        statement = statement.where(
            Employee.location.ilike(
                f"%{location}%"
            )
        )

    if min_experience is not None:
        statement = statement.where(
            Employee.experience_years
            >= min_experience
        )

    if status:
        statement = statement.where(
            Employee.status == status
        )

    statement = statement.order_by(
        Employee.name.asc()
    )

    result = db.execute(statement)

    employees = list(result.scalars().all())

    for employee in employees:
        calculated_utilization = (
            _calculate_employee_utilization_from_record(
                employee
            )
        )

        if (
            max_utilization is not None
            and calculated_utilization > max_utilization
        ):
            continue

        employee.utilization_percentage = (
            calculated_utilization
        )

    return employees


def get_employee(
    db: Session,
    employee_id: str,
) -> Employee | None:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        return None

    return _apply_calculated_utilization(employee)


def update_employee(
    db: Session,
    employee: Employee,
    employee_data: EmployeeUpdate,
) -> Employee:

    update_data = employee_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            employee,
            field,
            value,
        )

    db.commit()
    db.refresh(employee)

    return _apply_calculated_utilization(employee)


def delete_employee(
    db: Session,
    employee: Employee,
) -> None:
    db.delete(employee)
    db.commit()


def calculate_employee_utilization(
    db: Session,
    employee_id: str,
) -> float:
    employee = db.get(
        Employee,
        employee_id,
    )

    if employee is None:
        raise ValueError("Employee not found")

    return _calculate_employee_utilization_from_record(
        employee
    )