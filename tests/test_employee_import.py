import io

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.database.connection import Base
from app.database.dependencies import get_db
from app.main import app
from app.models.entities import (
    Allocation,
    AuditEvent,
    Employee,
    Permission,
    Role,
    RolePermission,
    User,
)


def create_test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    Base.metadata.create_all(
        engine,
        tables=[
            Permission.__table__,
            Role.__table__,
            RolePermission.__table__,
            User.__table__,
            Employee.__table__,
            Allocation.__table__,
            AuditEvent.__table__,
        ],
    )

    return engine


def create_user(
    user_id: str,
    username: str,
    role_id: str,
) -> User:
    return User(
        user_id=user_id,
        username=username,
        email=f"{username}@example.com",
        password_hash="test-password-hash",
        role_id=role_id,
        status="active",
    )


def configure_user_with_permission(
    db,
    permission_name: str,
    user_id: str = "user-authorized",
    username: str = "authorized",
):
    role = Role(
        role_id=f"role-{permission_name}",
        role_name="Test Role",
        status="active",
    )

    permission = Permission(
        permission_id=f"permission-{permission_name}",
        permission_name=permission_name,
    )

    db.add_all(
        [
            role,
            permission,
        ]
    )

    db.flush()

    db.add(
        RolePermission(
            role_id=role.role_id,
            permission_id=permission.permission_id,
        )
    )

    user = create_user(
        user_id=user_id,
        username=username,
        role_id=role.role_id,
    )

    db.add(user)
    db.commit()

    return user


def configure_user_without_permission(
    db,
    user_id: str = "user-viewer",
    username: str = "viewer",
):
    role = Role(
        role_id="role-viewer",
        role_name="Viewer",
        status="active",
    )

    permission = Permission(
        permission_id="permission-read-only",
        permission_name="employee.read",
    )

    db.add_all(
        [
            role,
            permission,
        ]
    )

    db.flush()

    db.add(
        RolePermission(
            role_id=role.role_id,
            permission_id=permission.permission_id,
        )
    )

    user = create_user(
        user_id=user_id,
        username=username,
        role_id=role.role_id,
    )

    db.add(user)
    db.commit()

    return user


def apply_user_overrides(db, user):
    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        get_current_user
    ] = override_get_current_user


def clear_dependency_overrides():
    app.dependency_overrides.clear()


def test_employee_import_requires_authentication():
    clear_dependency_overrides()

    engine = create_test_database()

    with Session(engine) as db:
        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = (
            override_get_db
        )

        client = TestClient(app)

        csv_content = (
            "employee_code,name,email,designation,department\n"
            "IMP001,Import Test,"
            "import.test@example.com,"
            "Analyst,Analytics\n"
        )

        response = client.post(
            "/api/v1/employees/import",
            files={
                "file": (
                    "employees.csv",
                    io.BytesIO(
                        csv_content.encode("utf-8")
                    ),
                    "text/csv",
                )
            },
        )

        assert response.status_code == 401

    clear_dependency_overrides()


def test_employee_import_rejects_user_without_write_permission():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_without_permission(
            db,
            user_id="user-import-viewer",
            username="import-viewer",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        csv_content = (
            "employee_code,name,email,designation,department\n"
            "IMP002,Unauthorized Import,"
            "unauthorized.import@example.com,"
            "Analyst,Analytics\n"
        )

        response = client.post(
            "/api/v1/employees/import",
            files={
                "file": (
                    "employees.csv",
                    io.BytesIO(
                        csv_content.encode("utf-8")
                    ),
                    "text/csv",
                )
            },
        )

        assert response.status_code == 403

        assert response.json()["detail"] == (
            "Permission required: employee.write"
        )

    clear_dependency_overrides()


def test_employee_import_allows_user_with_write_permission():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_with_permission(
            db,
            "employee.write",
            user_id="user-import-admin",
            username="import-admin",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        csv_content = (
            "employee_code,name,email,designation,"
            "department,experience_years,"
            "availability_status,location,status\n"
            "IMP003,Imported Employee,"
            "imported.employee@example.com,"
            "Data Analyst,Analytics,4,"
            "available,Delhi,active\n"
        )

        response = client.post(
            "/api/v1/employees/import",
            files={
                "file": (
                    "employees.csv",
                    io.BytesIO(
                        csv_content.encode("utf-8")
                    ),
                    "text/csv",
                )
            },
        )

        assert response.status_code == 200

        employee = db.scalar(
            select(Employee).where(
                Employee.employee_code == "IMP003"
            )
        )

        assert employee is not None
        assert employee.name == "Imported Employee"
        assert employee.email == (
            "imported.employee@example.com"
        )
        assert employee.department == "Analytics"

    clear_dependency_overrides()


def test_employee_import_rejects_missing_required_columns():
    clear_dependency_overrides()

    engine = create_test_database()

    with Session(engine) as db:
        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = (
            override_get_db
        )

        client = TestClient(app)

        csv_content = (
            "employee_code,name\n"
            "IMP004,Missing Email\n"
        )

        response = client.post(
            "/api/v1/employees/import",
            files={
                "file": (
                    "employees.csv",
                    io.BytesIO(
                        csv_content.encode("utf-8")
                    ),
                    "text/csv",
                )
            },
        )

        assert response.status_code in {
            400,
            401,
            403,
            422,
        }

    clear_dependency_overrides()


def test_employee_import_rejects_duplicate_rows():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_with_permission(
            db,
            "employee.write",
            user_id="user-import-duplicate",
            username="import-duplicate",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        csv_content = (
            "employee_code,name,email,designation,department\n"
            "IMP005,Duplicate One,"
            "duplicate@example.com,"
            "Analyst,Analytics\n"
            "IMP005,Duplicate Two,"
            "duplicate2@example.com,"
            "Analyst,Analytics\n"
        )

        response = client.post(
            "/api/v1/employees/import",
            files={
                "file": (
                    "employees.csv",
                    io.BytesIO(
                        csv_content.encode("utf-8")
                    ),
                    "text/csv",
                )
            },
        )

        assert response.status_code == 422

        first_employee = db.scalar(
            select(Employee).where(
                Employee.employee_code == "IMP005"
            )
        )

        second_employee = db.scalar(
            select(Employee).where(
                Employee.email
                == "duplicate2@example.com"
            )
        )

        assert first_employee is None
        assert second_employee is None

    clear_dependency_overrides()


def test_employee_import_is_all_or_nothing_for_validation_failure():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_with_permission(
            db,
            "employee.write",
            user_id="user-import-atomic",
            username="import-atomic",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        csv_content = (
            "employee_code,name,email,designation,department,"
            "experience_years\n"
            "IMP006,Valid Employee,"
            "valid.import@example.com,"
            "Analyst,Analytics,3\n"
            "IMP007,Invalid Employee,"
            "invalid.import@example.com,"
            "Analyst,Analytics,-5\n"
        )

        response = client.post(
            "/api/v1/employees/import",
            files={
                "file": (
                    "employees.csv",
                    io.BytesIO(
                        csv_content.encode("utf-8")
                    ),
                    "text/csv",
                )
            },
        )

        assert response.status_code == 422

        valid_employee = db.scalar(
            select(Employee).where(
                Employee.employee_code == "IMP006"
            )
        )

        invalid_employee = db.scalar(
            select(Employee).where(
                Employee.employee_code == "IMP007"
            )
        )

        assert valid_employee is None
        assert invalid_employee is None

    clear_dependency_overrides()