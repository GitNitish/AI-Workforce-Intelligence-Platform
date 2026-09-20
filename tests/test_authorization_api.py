from datetime import date, datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
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


def test_create_employee_requires_authentication():
    engine = create_test_database()

    with Session(engine) as db:

        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        client = TestClient(app)

        response = client.post(
            "/api/v1/employees",
            json={
                "employee_code": "AUTH001",
                "name": "Authorization Test",
                "email": "authorization-test@example.com",
            },
        )

        assert response.status_code == 401

    clear_dependency_overrides()


def test_create_employee_allows_user_with_employee_write_permission():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_with_permission(
            db,
            "employee.write",
            user_id="user-admin",
            username="admin",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        response = client.post(
            "/api/v1/employees",
            json={
                "employee_code": "AUTH002",
                "name": "Authorized Employee",
                "email": "authorized@example.com",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["employee_code"] == "AUTH002"
        assert data["name"] == "Authorized Employee"
        assert data["email"] == "authorized@example.com"

    clear_dependency_overrides()


def test_create_employee_rejects_user_without_employee_write_permission():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_without_permission(
            db,
            user_id="user-viewer",
            username="viewer",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        response = client.post(
            "/api/v1/employees",
            json={
                "employee_code": "AUTH003",
                "name": "Unauthorized Employee",
                "email": "unauthorized@example.com",
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Permission required: employee.write"
        )

    clear_dependency_overrides()


def test_generate_recommendations_requires_authentication():
    engine = create_test_database()

    with Session(engine) as db:

        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations",
            json={
                "staffing_requirement_id": "staffing-001",
            },
        )

        assert response.status_code == 401

    clear_dependency_overrides()


def test_generate_recommendations_allows_user_with_permission(
    monkeypatch,
):
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_with_permission(
            db,
            "recommendation.generate",
            user_id="user-recommendation",
            username="recommendation-user",
        )

        apply_user_overrides(
            db,
            user,
        )

        def fake_generate_recommendations(
            db,
            staffing_requirement_id,
        ):
            assert staffing_requirement_id == "staffing-001"
            return []

        monkeypatch.setattr(
            "app.api.router.generate_recommendations",
            fake_generate_recommendations,
        )

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations",
            json={
                "staffing_requirement_id": "staffing-001",
            },
        )

        assert response.status_code == 200
        assert response.json()["recommendations"] == []

    clear_dependency_overrides()


def test_generate_recommendations_rejects_user_without_permission():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_without_permission(
            db,
            user_id="user-no-recommendation",
            username="no-recommendation",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        response = client.post(
            "/api/v1/recommendations",
            json={
                "staffing_requirement_id": "staffing-001",
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Permission required: recommendation.generate"
        )

    clear_dependency_overrides()


def test_create_allocation_requires_authentication():
    engine = create_test_database()

    with Session(engine) as db:

        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        client = TestClient(app)

        response = client.post(
            "/api/v1/allocations",
            json={
                "employee_id": "employee-001",
                "project_id": "project-001",
                "allocation_percentage": 50,
                "start_date": "2026-09-20",
            },
        )

        assert response.status_code == 401

    clear_dependency_overrides()


def test_create_allocation_allows_user_with_allocation_write_permission(
    monkeypatch,
):
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_with_permission(
            db,
            "allocation.write",
            user_id="user-allocation",
            username="allocation-user",
        )

        apply_user_overrides(
            db,
            user,
        )

        created_at = datetime.now(timezone.utc)

        allocation = SimpleNamespace(
            allocation_id="allocation-auth-001",
            employee_id="employee-001",
            project_id="project-001",
            staffing_requirement_id=None,
            allocation_percentage=50,
            start_date=date(2026, 9, 20),
            end_date=None,
            status="active",
            allocated_by=user.user_id,
            created_at=created_at,
            updated_at=created_at,
        )

        def fake_create_allocation(
            db,
            allocation_data,
        ):
            assert allocation_data.employee_id == (
                "employee-001"
            )
            assert allocation_data.project_id == (
                "project-001"
            )
            return allocation

        monkeypatch.setattr(
            "app.api.router.create_allocation",
            fake_create_allocation,
        )

        client = TestClient(app)

        response = client.post(
            "/api/v1/allocations",
            json={
                "employee_id": "employee-001",
                "project_id": "project-001",
                "allocation_percentage": 50,
                "start_date": "2026-09-20",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["allocation_id"] == (
            "allocation-auth-001"
        )
        assert data["allocation_percentage"] == 50

    clear_dependency_overrides()


def test_create_allocation_rejects_user_without_allocation_write_permission():
    engine = create_test_database()

    with Session(engine) as db:
        user = configure_user_without_permission(
            db,
            user_id="user-no-allocation",
            username="no-allocation",
        )

        apply_user_overrides(
            db,
            user,
        )

        client = TestClient(app)

        response = client.post(
            "/api/v1/allocations",
            json={
                "employee_id": "employee-001",
                "project_id": "project-001",
                "allocation_percentage": 50,
                "start_date": "2026-09-20",
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Permission required: allocation.write"
        )

    clear_dependency_overrides()


def test_update_allocation_requires_authentication():
    engine = create_test_database()

    with Session(engine) as db:

        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        client = TestClient(app)

        response = client.put(
            "/api/v1/allocations/allocation-001",
            json={
                "allocation_percentage": 75,
            },
        )

        assert response.status_code == 401

    clear_dependency_overrides()


def test_delete_allocation_requires_authentication():
    engine = create_test_database()

    with Session(engine) as db:

        def override_get_db():
            yield db

        app.dependency_overrides[get_db] = override_get_db

        client = TestClient(app)

        response = client.delete(
            "/api/v1/allocations/allocation-001",
        )

        assert response.status_code == 401

    clear_dependency_overrides()