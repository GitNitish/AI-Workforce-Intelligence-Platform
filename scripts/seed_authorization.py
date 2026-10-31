
import secrets

from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.entities import (
    Permission,
    Role,
    RolePermission,
    User,
)


PERMISSIONS = {
    "employee.read": "View and search workforce employees",
    "employee.write": "Create, update, and delete workforce employees",
    "project.read": "View workforce projects",
    "project.write": "Create and update workforce projects",
    "staffing.read": "View staffing requirements",
    "staffing.write": "Create and update staffing requirements",
    "recommendation.generate": "Generate workforce recommendations",
    "allocation.read": "View workforce allocations",
    "allocation.write": "Create, update, and delete workforce allocations",
    "analytics.read": "View workforce analytics",
    "audit.read": "View audit history",
    "user.manage": "Manage users and access",
}


ROLE_PERMISSIONS = {
    "Administrator": list(PERMISSIONS.keys()),
    "Resource Manager": [
        "employee.read",
        "employee.write",
        "project.read",
        "project.write",
        "staffing.read",
        "staffing.write",
        "recommendation.generate",
        "allocation.read",
        "allocation.write",
        "analytics.read",
        "audit.read",
    ],
    "Workforce Analyst": [
        "employee.read",
        "project.read",
        "staffing.read",
        "recommendation.generate",
        "allocation.read",
        "analytics.read",
    ],
    "Viewer": [
        "employee.read",
        "project.read",
        "staffing.read",
        "allocation.read",
        "analytics.read",
    ],
    "Guest": [
        "employee.read",
        "project.read",
        "staffing.read",
        "allocation.read",
        "analytics.read",
    ],
}


ROLE_DESCRIPTIONS = {
    "Administrator": "Full access to workforce management and governance capabilities",
    "Resource Manager": "Manage workforce operations, staffing, recommendations, allocations, analytics, and audit visibility",
    "Workforce Analyst": "Analyze workforce data and generate staffing recommendations",
    "Viewer": "Read-only access to workforce operational data and analytics",
    "Guest": "Anonymous, shared, read-only access to workforce data and analytics",
}


ADMIN_EMAIL = "governance.admin@workforceiq.local"

GUEST_USERNAME = "workforceiq_guest"
GUEST_EMAIL = "guest@workforceiq.local"


def get_or_create_permission(
    db,
    permission_name: str,
    description: str,
) -> Permission:
    permission = db.scalar(
        select(Permission).where(
            Permission.permission_name == permission_name
        )
    )

    if permission is None:
        permission = Permission(
            permission_name=permission_name,
            description=description,
        )
        db.add(permission)
        db.flush()

    return permission


def get_or_create_role(
    db,
    role_name: str,
    description: str,
) -> Role:
    role = db.scalar(
        select(Role).where(
            Role.role_name == role_name
        )
    )

    if role is None:
        role = Role(
            role_name=role_name,
            description=description,
            status="active",
        )
        db.add(role)
        db.flush()

    return role


def ensure_role_permission(
    db,
    role: Role,
    permission: Permission,
) -> None:
    existing_mapping = db.scalar(
        select(RolePermission).where(
            RolePermission.role_id == role.role_id,
            RolePermission.permission_id == permission.permission_id,
        )
    )

    if existing_mapping is None:
        db.add(
            RolePermission(
                role_id=role.role_id,
                permission_id=permission.permission_id,
            )
        )


def synchronize_guest_permissions(
    db,
    guest_role: Role,
    expected_permissions: list[Permission],
) -> None:
    expected_permission_ids = {
        permission.permission_id
        for permission in expected_permissions
    }

    existing_mappings = db.scalars(
        select(RolePermission).where(
            RolePermission.role_id == guest_role.role_id
        )
    ).all()

    for mapping in existing_mappings:
        if mapping.permission_id not in expected_permission_ids:
            db.delete(mapping)


def get_or_create_guest_user(
    db,
    guest_role: Role,
) -> User:
    guest_user = db.scalar(
        select(User).where(
            User.username == GUEST_USERNAME
        )
    )

    guest_email_user = db.scalar(
        select(User).where(
            User.email == GUEST_EMAIL
        )
    )

    if (
        guest_user is not None
        and guest_email_user is not None
        and guest_user.user_id != guest_email_user.user_id
    ):
        raise ValueError(
            "Guest username and email belong to different users."
        )

    if guest_user is None and guest_email_user is not None:
        raise ValueError(
            "Guest email is already assigned to another user."
        )

    if guest_user is not None and guest_user.email != GUEST_EMAIL:
        raise ValueError(
            "Guest username is already assigned to another email."
        )

    if guest_user is None:
        guest_user = User(
            username=GUEST_USERNAME,
            email=GUEST_EMAIL,
            password_hash=hash_password(
                secrets.token_urlsafe(48)
            ),
            role_id=guest_role.role_id,
            status="active",
            employee_id=None,
        )
        db.add(guest_user)
    else:
        # Rotate to a newly generated, undisclosed password.
        # The account is intended to be accessed only through
        # the dedicated Guest authentication endpoint.
        guest_user.password_hash = hash_password(
            secrets.token_urlsafe(48)
        )
        guest_user.role_id = guest_role.role_id
        guest_user.status = "active"
        guest_user.employee_id = None

    return guest_user


def seed_authorization() -> None:
    with SessionLocal() as db:
        try:
            permissions = {}

            for permission_name, description in PERMISSIONS.items():
                permissions[permission_name] = get_or_create_permission(
                    db=db,
                    permission_name=permission_name,
                    description=description,
                )

            roles = {}

            for role_name, permission_names in ROLE_PERMISSIONS.items():
                role = get_or_create_role(
                    db=db,
                    role_name=role_name,
                    description=ROLE_DESCRIPTIONS[role_name],
                )

                roles[role_name] = role

                for permission_name in permission_names:
                    ensure_role_permission(
                        db=db,
                        role=role,
                        permission=permissions[permission_name],
                    )

            guest_role = roles["Guest"]
            guest_role.description = ROLE_DESCRIPTIONS["Guest"]
            guest_role.status = "active"

            synchronize_guest_permissions(
                db=db,
                guest_role=guest_role,
                expected_permissions=[
                    permissions[name]
                    for name in ROLE_PERMISSIONS["Guest"]
                ],
            )

            admin_user = db.scalar(
                select(User).where(
                    User.email == ADMIN_EMAIL
                )
            )

            if admin_user is None:
                raise ValueError(
                    f"Required Administrator account "
                    f"with email '{ADMIN_EMAIL}' was not found."
                )

            if admin_user.status != "active":
                raise ValueError(
                    "The existing Administrator account is not active."
                )

            if admin_user.role_id != roles["Administrator"].role_id:
                raise ValueError(
                    "The existing account does not currently have "
                    "the Administrator role. Refusing to change "
                    "its role automatically."
                )

            get_or_create_guest_user(
                db=db,
                guest_role=guest_role,
            )

            db.commit()

            print("Authorization seed completed successfully.")
            print(f"Permissions: {len(permissions)}")
            print(f"Roles: {len(roles)}")
            print(
                f"Existing Administrator verified: {ADMIN_EMAIL}"
            )
            print("Guest role and shared Guest identity provisioned.")
            print(
                "Guest permissions: "
                + ", ".join(ROLE_PERMISSIONS["Guest"])
            )

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed_authorization()
