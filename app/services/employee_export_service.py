import csv
from io import StringIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Employee


EXPORT_FIELDS = [
    "employee_code",
    "name",
    "email",
    "designation",
    "department",
    "experience_years",
    "availability_status",
    "location",
    "status",
]


VALID_DATASETS = {
    "all",
    "active",
    "inactive",
    "available",
    "partially_available",
}


def get_export_employees(
    db: Session,
    dataset: str,
) -> list[Employee]:
    normalized_dataset = dataset.strip().lower()

    if normalized_dataset not in VALID_DATASETS:
        raise ValueError(
            "Invalid export dataset. "
            "Choose one of: all, active, inactive, "
            "available, partially_available."
        )

    statement = select(Employee)

    if normalized_dataset == "active":
        statement = statement.where(
            Employee.status == "active"
        )

    elif normalized_dataset == "inactive":
        statement = statement.where(
            Employee.status == "inactive"
        )

    elif normalized_dataset == "available":
        statement = statement.where(
            Employee.availability_status == "available"
        )

    elif normalized_dataset == "partially_available":
        statement = statement.where(
            Employee.availability_status == "partially_available"
        )

    statement = statement.order_by(
        Employee.employee_code.asc()
    )

    result = db.execute(statement)

    return list(result.scalars().all())


def generate_employee_csv(
    db: Session,
    dataset: str = "all",
) -> tuple[str, int]:
    employees = get_export_employees(
        db=db,
        dataset=dataset,
    )

    output = StringIO(newline="")

    writer = csv.DictWriter(
        output,
        fieldnames=EXPORT_FIELDS,
        extrasaction="ignore",
    )

    writer.writeheader()

    for employee in employees:
        writer.writerow(
            {
                "employee_code": employee.employee_code,
                "name": employee.name,
                "email": employee.email,
                "designation": employee.designation,
                "department": employee.department,
                "experience_years": employee.experience_years,
                "availability_status": employee.availability_status,
                "location": employee.location,
                "status": employee.status,
            }
        )

    return output.getvalue(), len(employees)