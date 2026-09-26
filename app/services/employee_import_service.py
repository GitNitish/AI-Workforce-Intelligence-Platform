import csv
import io
from dataclasses import dataclass, field
from typing import BinaryIO

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Employee
from app.schemas.employee import EmployeeCreate
from app.services.audit_service import create_audit_event


REQUIRED_COLUMNS = {
    "employee_code",
    "name",
    "email",
}

ALLOWED_COLUMNS = {
    "employee_code",
    "name",
    "email",
    "designation",
    "department",
    "experience_years",
    "availability_status",
    "location",
    "status",
}


@dataclass
class ImportRowError:
    row: int
    errors: list[str] = field(default_factory=list)


@dataclass
class EmployeeImportResult:
    total_rows: int
    imported: int
    failed: int
    errors: list[ImportRowError] = field(default_factory=list)


class EmployeeImportValidationError(Exception):
    """Raised when the import file itself is invalid."""


def _normalise_value(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    return cleaned if cleaned else None


def _normalise_row(
    row: dict[str, str | None],
) -> dict[str, str | None]:
    return {
        key.strip(): _normalise_value(value)
        for key, value in row.items()
        if key is not None
    }


def _validate_headers(
    fieldnames: list[str] | None,
) -> None:
    if not fieldnames:
        raise EmployeeImportValidationError(
            "The CSV file must contain a header row.",
        )

    headers = {
        header.strip()
        for header in fieldnames
        if header is not None and header.strip()
    }

    missing_columns = REQUIRED_COLUMNS - headers
    unknown_columns = headers - ALLOWED_COLUMNS

    errors: list[str] = []

    if missing_columns:
        errors.append(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns)),
        )

    if unknown_columns:
        errors.append(
            "Unknown columns: "
            + ", ".join(sorted(unknown_columns)),
        )

    if errors:
        raise EmployeeImportValidationError(
            " ".join(errors),
        )


def _build_employee_data(
    row: dict[str, str | None],
    row_number: int,
) -> EmployeeCreate:
    try:
        return EmployeeCreate(
            employee_code=row.get("employee_code"),
            name=row.get("name"),
            email=row.get("email"),
            designation=row.get("designation"),
            department=row.get("department"),
            experience_years=(
                float(row["experience_years"])
                if row.get("experience_years") is not None
                else 0
            ),
            availability_status=(
                row.get("availability_status")
                or "available"
            ),
            location=row.get("location"),
            status=row.get("status") or "active",
        )

    except ValidationError as exc:
        messages: list[str] = []

        for error in exc.errors():
            location = ".".join(
                str(item)
                for item in error["loc"]
            )

            message = str(error["msg"])

            if location:
                messages.append(
                    f"{location}: {message}"
                )
            else:
                messages.append(message)

        raise EmployeeImportValidationError(
            f"Row {row_number}: "
            + "; ".join(messages),
        ) from exc

    except (TypeError, ValueError) as exc:
        raise EmployeeImportValidationError(
            f"Row {row_number}: "
            f"invalid employee data: {exc}",
        ) from exc


def _check_duplicate_values(
    rows: list[tuple[int, EmployeeCreate]],
) -> list[ImportRowError]:
    errors_by_row: dict[int, list[str]] = {}

    employee_codes: dict[str, list[int]] = {}
    emails: dict[str, list[int]] = {}

    for row_number, employee_data in rows:
        employee_code = (
            employee_data.employee_code.strip().lower()
        )

        email = (
            employee_data.email.strip().lower()
        )

        employee_codes.setdefault(
            employee_code,
            [],
        ).append(row_number)

        emails.setdefault(
            email,
            [],
        ).append(row_number)

    for code, row_numbers in employee_codes.items():
        if len(row_numbers) > 1:
            for row_number in row_numbers:
                errors_by_row.setdefault(
                    row_number,
                    [],
                ).append(
                    f"Duplicate employee_code "
                    f"'{code}' in import file.",
                )

    for email, row_numbers in emails.items():
        if len(row_numbers) > 1:
            for row_number in row_numbers:
                errors_by_row.setdefault(
                    row_number,
                    [],
                ).append(
                    f"Duplicate email "
                    f"'{email}' in import file.",
                )

    return [
        ImportRowError(
            row=row_number,
            errors=row_errors,
        )
        for row_number, row_errors
        in sorted(errors_by_row.items())
    ]


def _check_existing_employees(
    db: Session,
    rows: list[tuple[int, EmployeeCreate]],
) -> list[ImportRowError]:
    errors_by_row: dict[int, list[str]] = {}

    for row_number, employee_data in rows:
        existing_code = db.scalar(
            select(Employee).where(
                Employee.employee_code
                == employee_data.employee_code
            )
        )

        if existing_code is not None:
            errors_by_row.setdefault(
                row_number,
                [],
            ).append(
                f"Employee code "
                f"'{employee_data.employee_code}' "
                "already exists.",
            )

        existing_email = db.scalar(
            select(Employee).where(
                Employee.email
                == employee_data.email
            )
        )

        if existing_email is not None:
            errors_by_row.setdefault(
                row_number,
                [],
            ).append(
                f"Email "
                f"'{employee_data.email}' "
                "already exists.",
            )

    return [
        ImportRowError(
            row=row_number,
            errors=row_errors,
        )
        for row_number, row_errors
        in sorted(errors_by_row.items())
    ]


def import_employees_from_csv(
    db: Session,
    file: BinaryIO,
    user_id: str | None = None,
) -> EmployeeImportResult:
    raw_content = file.read()

    if isinstance(raw_content, bytes):
        try:
            content = raw_content.decode(
                "utf-8-sig"
            )
        except UnicodeDecodeError as exc:
            raise EmployeeImportValidationError(
                "The CSV file must be encoded as UTF-8.",
            ) from exc
    else:
        content = raw_content

    if not content.strip():
        raise EmployeeImportValidationError(
            "The CSV file is empty.",
        )

    reader = csv.DictReader(
        io.StringIO(content)
    )

    _validate_headers(
        reader.fieldnames
    )

    parsed_rows: list[
        tuple[int, EmployeeCreate]
    ] = []

    row_errors: list[ImportRowError] = []

    for row_number, raw_row in enumerate(
        reader,
        start=2,
    ):
        row = _normalise_row(raw_row)

        if not any(
            value is not None
            for value in row.values()
        ):
            continue

        try:
            employee_data = _build_employee_data(
                row,
                row_number,
            )

            parsed_rows.append(
                (
                    row_number,
                    employee_data,
                )
            )

        except EmployeeImportValidationError as exc:
            row_errors.append(
                ImportRowError(
                    row=row_number,
                    errors=[str(exc)],
                )
            )

    total_rows = (
        len(parsed_rows)
        + len(row_errors)
    )

    # --------------------------------------------------------
    # Validation phase
    # --------------------------------------------------------

    if row_errors:
        return EmployeeImportResult(
            total_rows=total_rows,
            imported=0,
            failed=len(row_errors),
            errors=row_errors,
        )

    duplicate_errors = (
        _check_duplicate_values(
            parsed_rows,
        )
    )

    existing_errors = (
        _check_existing_employees(
            db,
            parsed_rows,
        )
    )

    all_errors = (
        duplicate_errors
        + existing_errors
    )

    if all_errors:
        return EmployeeImportResult(
            total_rows=len(parsed_rows),
            imported=0,
            failed=len(all_errors),
            errors=all_errors,
        )

    # --------------------------------------------------------
    # Transaction phase
    # --------------------------------------------------------

    created_employees: list[Employee] = []

    try:
        for _, employee_data in parsed_rows:
            employee = Employee(
                **employee_data.model_dump()
            )

            db.add(employee)
            created_employees.append(employee)

        # Flush validates the pending database writes
        # without permanently committing them.
        db.flush()

        create_audit_event(
            db=db,
            action="employee.import",
            entity_type="Employee",
            entity_id=None,
            result="success",
            user_id=user_id,
            metadata={
                "total_rows": len(parsed_rows),
                "imported": len(
                    created_employees
                ),
                "failed": 0,
            },
        )

        # One and only one commit for the entire import.
        db.commit()

    except IntegrityError as exc:
        db.rollback()

        create_audit_event(
            db=db,
            action="employee.import",
            entity_type="Employee",
            entity_id=None,
            result="failure",
            user_id=user_id,
            metadata={
                "total_rows": len(parsed_rows),
                "imported": 0,
                "failed": len(parsed_rows),
                "error": (
                    "Database integrity error "
                    "during employee import."
                ),
            },
        )

        db.commit()

        return EmployeeImportResult(
            total_rows=len(parsed_rows),
            imported=0,
            failed=len(parsed_rows),
            errors=[
                ImportRowError(
                    row=0,
                    errors=[
                        "Import failed because of "
                        "a database integrity error."
                    ],
                )
            ],
        )

    except Exception:
        db.rollback()

        create_audit_event(
            db=db,
            action="employee.import",
            entity_type="Employee",
            entity_id=None,
            result="failure",
            user_id=user_id,
            metadata={
                "total_rows": len(parsed_rows),
                "imported": 0,
                "failed": len(parsed_rows),
                "error": (
                    "Unexpected error "
                    "during employee import."
                ),
            },
        )

        db.commit()

        raise

    return EmployeeImportResult(
        total_rows=len(parsed_rows),
        imported=len(created_employees),
        failed=0,
        errors=[],
    )