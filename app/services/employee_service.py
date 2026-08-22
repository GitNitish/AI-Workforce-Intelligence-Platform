from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, employee_data: EmployeeCreate) -> Employee:
    employee = Employee(**employee_data.model_dump())

    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def get_employees(db: Session) -> list[Employee]:
    result = db.execute(select(Employee))
    return list(result.scalars().all())


def get_employee(
    db: Session,
    employee_id: str,
) -> Employee | None:
    return db.get(Employee, employee_id)


def update_employee(
    db: Session,
    employee: Employee,
    employee_data: EmployeeUpdate,
) -> Employee:
    update_data = employee_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)

    return employee


def delete_employee(
    db: Session,
    employee: Employee,
) -> None:
    db.delete(employee)
    db.commit()