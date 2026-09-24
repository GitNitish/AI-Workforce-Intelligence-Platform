from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.database.connection import Base
from app.database.dependencies import get_db
from app.main import app
from app.models.entities import (
    Permission,
    Role,
    RolePermission,
    User,
)


def create_test_database():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
        future=True,
    )

    Base.metadata.create_all(engine)

    return engine


def create_test_user(
    user_id="user-001",
    username="governance_admin",
    email="governance.admin@workforceiq.local",
    role_id=None,
    status="active",
):
    return User(
        user_id=user_id,
        username=username,
        email=email,
        password_hash="test-password-hash",
        role_id=role_id,
        status=status,
    )


def clear_dependency_overrides():
    app.dependency_overrides.clear()


def test_auth_me_requires_authentication():
    clear_dependency_overrides()

    client = TestClient(app)

    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401


def test_auth_me_returns_current_user_role_and_permissions():
    engine = create_test_database()

    role = Role(
        role_id="role-admin",
        role_name="Administrator",
        status="active",
    )

    permission_names = [
        "employee.read",
        "employee.write",
        "analytics.read",
        "user.manage",
    ]

    permissions = [
        Permission(
            permission_id=f"permission-{index}",
            permission_name=permission_name,
        )
        for index, permission_name in enumerate(
            permission_names,
            start=1,
        )
    ]

    role_permissions = [
        RolePermission(
            role_id=role.role_id,
            permission_id=permission.permission_id,
        )
        for permission in permissions
    ]

    user = create_test_user(
        role_id=role.role_id,
    )

    with Session(engine) as db:
        db.add(role)
        db.add_all(permissions)
        db.add_all(role_permissions)
        db.add(user)
        db.commit()

        def override_get_db():
            yield db

        def override_get_current_user():
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[
            get_current_user
        ] = override_get_current_user

        try:
            client = TestClient(app)

            response = client.get(
                "/api/v1/auth/me",
            )

            assert response.status_code == 200

            data = response.json()

            assert data["user_id"] == user.user_id
            assert data["username"] == user.username
            assert data["email"] == user.email
            assert data["role"] == "Administrator"
            assert data["status"] == "active"

            assert data["permissions"] == sorted(
                permission_names
            )

        finally:
            clear_dependency_overrides()


def test_auth_me_returns_empty_role_and_permissions_when_user_has_no_role():
    engine = create_test_database()

    user = create_test_user(
        user_id="user-no-role",
        username="no_role_user",
        email="no.role@workforceiq.local",
        role_id=None,
    )

    with Session(engine) as db:
        db.add(user)
        db.commit()

        def override_get_db():
            yield db

        def override_get_current_user():
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[
            get_current_user
        ] = override_get_current_user

        try:
            client = TestClient(app)

            response = client.get(
                "/api/v1/auth/me",
            )

            assert response.status_code == 200

            data = response.json()

            assert data["user_id"] == "user-no-role"
            assert data["username"] == "no_role_user"
            assert data["role"] is None
            assert data["permissions"] == []

        finally:
            clear_dependency_overrides()