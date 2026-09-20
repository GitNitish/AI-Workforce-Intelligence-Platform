from sqlalchemy import select

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
}


ROLE_DESCRIPTIONS = {
    "Administrator": "Full access to workforce management and governance capabilities",
    "Resource Manager": "Manage workforce operations, staffing, recommendations, allocations, analytics, and audit visibility",
    "Workforce Analyst": "Analyze workforce data and generate staffing recommendations",
    "Viewer": "Read-only access to workforce operational data and analytics",
}


ADMIN_USERNAME = "governance_admin"


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

            admin_user = db.scalar(
                select(User).where(
                    User.username == ADMIN_USERNAME
                )
            )

            if admin_user is None:
                raise ValueError(
                    f"Required user '{ADMIN_USERNAME}' was not found."
                )

            admin_user.role_id = roles["Administrator"].role_id

            db.commit()

            print("Authorization seed completed successfully.")
            print(f"Permissions: {len(permissions)}")
            print(f"Roles: {len(roles)}")
            print("Administrator role assigned to governance_admin.")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed_authorization()