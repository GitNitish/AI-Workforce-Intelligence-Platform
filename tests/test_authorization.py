from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.database.connection import Base
from app.models.entities import (
    Permission,
    Role,
    RolePermission,
    User,
)


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
    )

    Base.metadata.create_all(
        engine,
        tables=[
            Permission.__table__,
            Role.__table__,
            RolePermission.__table__,
            User.__table__,
        ],
    )

    return engine


def create_user(
    user_id: str,
    username: str,
    role_id: str | None,
    status: str = "active",
) -> User:
    return User(
        user_id=user_id,
        username=username,
        email=f"{username}@example.com",
        password_hash="test-hash",
        role_id=role_id,
        status=status,
    )


def test_require_permission_allows_user_with_permission():
    engine = create_test_database()

    with Session(engine) as db:
        role = Role(
            role_id="role-admin",
            role_name="Administrator",
            status="active",
        )

        permission = Permission(
            permission_id="permission-employee-write",
            permission_name="employee.write",
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
            user_id="user-admin",
            username="admin",
            role_id=role.role_id,
        )

        db.add(user)
        db.commit()

        dependency = require_permission(
            "employee.write"
        )

        result = dependency(
            current_user=user,
            db=db,
        )

        assert result.user_id == "user-admin"


def test_require_permission_rejects_user_without_permission():
    engine = create_test_database()

    with Session(engine) as db:
        role = Role(
            role_id="role-viewer",
            role_name="Viewer",
            status="active",
        )

        permission = Permission(
            permission_id="permission-employee-read",
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
            user_id="user-viewer",
            username="viewer",
            role_id=role.role_id,
        )

        db.add(user)
        db.commit()

        dependency = require_permission(
            "employee.write"
        )

        try:
            dependency(
                current_user=user,
                db=db,
            )
            assert False, "Expected permission denial"

        except Exception as exc:
            assert getattr(
                exc,
                "status_code",
                None,
            ) == 403

            assert exc.detail == (
                "Permission required: employee.write"
            )


def test_require_permission_rejects_user_without_role():
    engine = create_test_database()

    with Session(engine) as db:
        user = create_user(
            user_id="user-no-role",
            username="no-role",
            role_id=None,
        )

        db.add(user)
        db.commit()

        dependency = require_permission(
            "employee.write"
        )

        try:
            dependency(
                current_user=user,
                db=db,
            )
            assert False, "Expected role denial"

        except Exception as exc:
            assert getattr(
                exc,
                "status_code",
                None,
            ) == 403

            assert exc.detail == (
                "User does not have an assigned role"
            )


def test_require_permission_uses_exact_permission_name():
    engine = create_test_database()

    with Session(engine) as db:
        role = Role(
            role_id="role-manager",
            role_name="Resource Manager",
            status="active",
        )

        permission = Permission(
            permission_id="permission-project-write",
            permission_name="project.write",
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
            user_id="user-manager",
            username="manager",
            role_id=role.role_id,
        )

        db.add(user)
        db.commit()

        dependency = require_permission(
            "employee.write"
        )

        try:
            dependency(
                current_user=user,
                db=db,
            )
            assert False, "Expected permission denial"

        except Exception as exc:
            assert getattr(
                exc,
                "status_code",
                None,
            ) == 403

            assert exc.detail == (
                "Permission required: employee.write"
            )