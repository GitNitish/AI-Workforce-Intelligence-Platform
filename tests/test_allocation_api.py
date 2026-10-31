
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException
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
    Project,
    Role,
    RolePermission,
    User,
)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def create_user_with_permission(
    db: Session,
    permission_name: str | None,
    user_id: str = "allocation-user-001",
) -> User:
    role = Role(
        role_id=f"role-{user_id}",
        role_name=f"Role {user_id}",
        status="active",
    )
    db.add(role)
    db.flush()

    if permission_name is not None:
        permission = Permission(
            permission_id=f"permission-{user_id}",
            permission_name=permission_name,
        )
        db.add(permission)
        db.flush()
        db.add(
            RolePermission(
                role_id=role.role_id,
                permission_id=permission.permission_id,
            )
        )

    user = User(
        user_id=user_id,
        username=user_id,
        email=f"{user_id}@example.com",
        password_hash="test-password-hash",
        role_id=role.role_id,
        status="active",
    )
    db.add(user)
    db.commit()
    return user


def authenticate_as(user: User):
    def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user


def require_unauthenticated():
    def override_get_current_user():
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    app.dependency_overrides[get_current_user] = override_get_current_user


def create_allocation_records(
    db: Session,
    user: User,
) -> Allocation:
    employee = Employee(
        employee_id="employee-api-001",
        employee_code="EMP-API-001",
        name="Allocation Test Employee",
        email="allocation.employee@example.com",
        experience_years=5,
        availability_status="available",
        utilization_percentage=0,
        status="active",
    )
    project = Project(
        project_id="project-api-001",
        project_code="PRJ-API-001",
        project_name="Allocation API Test Project",
        status="active",
        priority="medium",
    )
    db.add_all([employee, project])
    db.flush()

    allocation = Allocation(
        allocation_id="allocation-api-001",
        employee_id=employee.employee_id,
        project_id=project.project_id,
        allocation_percentage=50,
        start_date=date(2026, 9, 20),
        end_date=None,
        status="active",
        allocated_by=user.user_id,
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    return allocation


def audit_events_for(db: Session, entity_id: str):
    return list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.entity_id == entity_id)
            .order_by(AuditEvent.event_timestamp)
        )
    )


def test_list_allocations_requires_authentication(client):
    require_unauthenticated()

    response = client.get("/api/v1/allocations")

    assert response.status_code == 401


def test_get_allocation_requires_authentication(client):
    require_unauthenticated()

    response = client.get("/api/v1/allocations/allocation-api-001")

    assert response.status_code == 401


def test_authenticated_user_can_list_allocations(db, client):
    user = create_user_with_permission(db, None)
    create_allocation_records(db, user)
    authenticate_as(user)

    response = client.get("/api/v1/allocations")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["allocation_id"] == "allocation-api-001"


def test_authenticated_user_can_get_allocation(db, client):
    user = create_user_with_permission(db, None)
    create_allocation_records(db, user)
    authenticate_as(user)

    response = client.get(
        "/api/v1/allocations/allocation-api-001"
    )

    assert response.status_code == 200
    assert response.json()["allocation_id"] == "allocation-api-001"


def test_update_allocation_requires_allocation_write_permission(
    db,
    client,
):
    user = create_user_with_permission(
        db,
        "employee.read",
        user_id="allocation-viewer-001",
    )
    create_allocation_records(db, user)
    authenticate_as(user)

    response = client.put(
        "/api/v1/allocations/allocation-api-001",
        json={"allocation_percentage": 75},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Permission required: allocation.write"
    )

    allocation = db.get(Allocation, "allocation-api-001")
    assert allocation is not None
    assert allocation.allocation_percentage == 50
    assert allocation.status == "active"
    assert audit_events_for(db, allocation.allocation_id) == []


def test_user_with_allocation_write_can_update_and_audit_is_created(
    db,
    client,
    monkeypatch,
):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-editor-001",
    )
    allocation = create_allocation_records(db, user)

    def fake_update_allocation(
        session,
        existing_allocation,
        allocation_data,
    ):
        assert existing_allocation.allocation_id == allocation.allocation_id
        existing_allocation.allocation_percentage = (
            allocation_data.allocation_percentage
        )
        session.flush()
        return existing_allocation

    monkeypatch.setattr(
        "app.api.router.update_allocation",
        fake_update_allocation,
    )
    authenticate_as(user)

    response = client.put(
        "/api/v1/allocations/allocation-api-001",
        json={"allocation_percentage": 75},
    )

    assert response.status_code == 200
    assert response.json()["allocation_percentage"] == 75

    events = audit_events_for(db, allocation.allocation_id)
    assert len(events) == 1
    assert events[0].action == "UPDATE"
    assert events[0].entity_type == "Allocation"
    assert events[0].result == "success"
    assert events[0].user_id == user.user_id
    assert events[0].event_metadata == {"source": "api"}


def test_deallocate_allocation_requires_allocation_write_permission(
    db,
    client,
):
    user = create_user_with_permission(
        db,
        "employee.read",
        user_id="allocation-deallocator-viewer",
    )
    create_allocation_records(db, user)
    authenticate_as(user)

    response = client.delete(
        "/api/v1/allocations/allocation-api-001"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Permission required: allocation.write"
    )

    allocation = db.get(Allocation, "allocation-api-001")
    assert allocation is not None
    assert allocation.status == "active"
    assert allocation.allocation_percentage == 50
    assert audit_events_for(db, allocation.allocation_id) == []


def test_user_with_allocation_write_can_deallocate_and_audit_is_created(
    db,
    client,
    monkeypatch,
):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-deallocator-001",
    )
    allocation = create_allocation_records(db, user)

    def fake_deallocate_allocation(session, existing_allocation):
        existing_allocation.status = "deallocated"
        session.flush()
        return existing_allocation

    monkeypatch.setattr(
        "app.api.router.deallocate_allocation",
        fake_deallocate_allocation,
    )
    authenticate_as(user)

    response = client.delete(
        "/api/v1/allocations/allocation-api-001"
    )

    assert response.status_code == 204
    assert response.content == b""

    db.refresh(allocation)
    assert allocation.status == "deallocated"

    events = audit_events_for(db, allocation.allocation_id)
    assert len(events) == 1
    assert events[0].action == "DEALLOCATE"
    assert events[0].entity_type == "Allocation"
    assert events[0].result == "success"
    assert events[0].user_id == user.user_id
    assert events[0].event_metadata == {"source": "api"}


def test_create_allocation_records_audit_event_and_uses_authenticated_user(
    db,
    client,
    monkeypatch,
):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-creator-001",
    )
    employee = Employee(
        employee_id="employee-create-001",
        employee_code="EMP-CREATE-001",
        name="Create Test Employee",
        email="create.employee@example.com",
        experience_years=4,
        availability_status="available",
        utilization_percentage=0,
        status="active",
    )
    project = Project(
        project_id="project-create-001",
        project_code="PRJ-CREATE-001",
        project_name="Allocation Create Test Project",
        status="active",
        priority="medium",
    )
    db.add_all([employee, project])
    db.commit()

    def fake_create_allocation(session, allocation_data):
        assert allocation_data.allocated_by == user.user_id
        allocation = Allocation(
            allocation_id="allocation-created-api-001",
            employee_id=allocation_data.employee_id,
            project_id=allocation_data.project_id,
            staffing_requirement_id=allocation_data.staffing_requirement_id,
            allocation_percentage=allocation_data.allocation_percentage,
            start_date=allocation_data.start_date,
            end_date=allocation_data.end_date,
            status=allocation_data.status,
            allocated_by=allocation_data.allocated_by,
        )
        session.add(allocation)
        session.flush()
        return allocation

    monkeypatch.setattr(
        "app.api.router.create_allocation",
        fake_create_allocation,
    )
    authenticate_as(user)

    response = client.post(
        "/api/v1/allocations",
        json={
            "employee_id": employee.employee_id,
            "project_id": project.project_id,
            "allocation_percentage": 50,
            "start_date": "2026-09-20",
        },
    )

    assert response.status_code == 201
    assert response.json()["allocation_id"] == (
        "allocation-created-api-001"
    )

    events = audit_events_for(db, "allocation-created-api-001")
    assert len(events) == 1
    assert events[0].action == "CREATE"
    assert events[0].entity_type == "Allocation"
    assert events[0].result == "success"
    assert events[0].user_id == user.user_id
    assert events[0].event_metadata == {"source": "api"}


def test_create_allocation_without_permission_does_not_mutate_data_or_audit(
    db,
    client,
):
    user = create_user_with_permission(
        db,
        "employee.read",
        user_id="allocation-create-viewer-001",
    )
    employee = Employee(
        employee_id="employee-unauthorized-create-001",
        employee_code="EMP-UNAUTH-CREATE-001",
        name="Unauthorized Create Employee",
        email="unauthorized.create@example.com",
        experience_years=3,
        availability_status="available",
        utilization_percentage=0,
        status="active",
    )
    project = Project(
        project_id="project-unauthorized-create-001",
        project_code="PRJ-UNAUTH-CREATE-001",
        project_name="Unauthorized Create Project",
        status="active",
        priority="medium",
    )
    db.add_all([employee, project])
    db.commit()
    authenticate_as(user)

    response = client.post(
        "/api/v1/allocations",
        json={
            "employee_id": employee.employee_id,
            "project_id": project.project_id,
            "allocation_percentage": 50,
            "start_date": "2026-09-20",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Permission required: allocation.write"
    )
    assert db.scalars(select(Allocation)).all() == []
    assert db.scalars(select(AuditEvent)).all() == []


def test_update_allocation_returns_404_when_allocation_does_not_exist(
    db,
    client,
):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-missing-update",
    )
    authenticate_as(user)

    response = client.put(
        "/api/v1/allocations/does-not-exist",
        json={"allocation_percentage": 75},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Allocation not found"


def test_deallocate_allocation_returns_404_when_allocation_does_not_exist(
    db,
    client,
):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-missing-delete",
    )
    authenticate_as(user)

    response = client.delete(
        "/api/v1/allocations/does-not-exist"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Allocation not found"


def test_failed_update_does_not_persist_audit_event(
    db,
    client,
    monkeypatch,
):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-failed-update",
    )
    allocation = create_allocation_records(db, user)

    def fake_update_allocation(
        session,
        existing_allocation,
        allocation_data,
    ):
        raise ValueError("Invalid allocation update")

    monkeypatch.setattr(
        "app.api.router.update_allocation",
        fake_update_allocation,
    )
    authenticate_as(user)

    response = client.put(
        "/api/v1/allocations/allocation-api-001",
        json={"allocation_percentage": 75},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid allocation update"
    assert audit_events_for(db, allocation.allocation_id) == []


def test_create_allocation_rejects_deallocated_status(db, client):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-create-deallocated",
    )
    authenticate_as(user)

    response = client.post(
        "/api/v1/allocations",
        json={
            "employee_id": "employee-create-001",
            "project_id": "project-create-001",
            "allocation_percentage": 50,
            "start_date": "2026-09-20",
            "status": "deallocated",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]
    assert db.scalar(select(Allocation)) is None
    assert db.scalars(select(AuditEvent)).all() == []


def test_update_cannot_deallocate_allocation_through_put(db, client):
    user = create_user_with_permission(
        db,
        "allocation.write",
        user_id="allocation-put-deallocate",
    )
    allocation = create_allocation_records(db, user)
    authenticate_as(user)

    response = client.put(
        f"/api/v1/allocations/{allocation.allocation_id}",
        json={"status": "deallocated"},
    )

    assert response.status_code == 422
    db.refresh(allocation)
    assert allocation.status == "active"
    assert audit_events_for(db, allocation.allocation_id) == []
