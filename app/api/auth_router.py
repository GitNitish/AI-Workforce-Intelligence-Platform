from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.entities import (
    Permission,
    Role,
    RolePermission,
    User,
)
from app.schemas.auth import (
    CurrentUserResponse,
    TokenResponse,
)
from app.services.audit_service import create_audit_event
from app.services.auth_service import (
    authenticate_user,
    create_user_access_token,
)


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@auth_router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        user = authenticate_user(
            db=db,
            username=form_data.username,
            password=form_data.password,
        )

        access_token = create_user_access_token(user)

        user.last_login_at = datetime.now(timezone.utc)

        create_audit_event(
            db=db,
            action="LOGIN",
            entity_type="User",
            entity_id=user.user_id,
            result="success",
            user_id=user.user_id,
            metadata={
                "source": "api",
            },
        )

        db.commit()

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
        )

    except ValueError as exc:
        create_audit_event(
            db=db,
            action="LOGIN",
            entity_type="User",
            entity_id=None,
            result="failure",
            user_id=None,
            metadata={
                "source": "api",
                "reason": str(exc),
            },
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )


@auth_router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_authenticated_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    role_name = None
    permissions: list[str] = []

    if current_user.role_id is not None:
        role_name = db.scalar(
            select(Role.role_name).where(
                Role.role_id == current_user.role_id
            )
        )

        permissions = list(
            db.scalars(
                select(Permission.permission_name)
                .join(
                    RolePermission,
                    RolePermission.permission_id
                    == Permission.permission_id,
                )
                .where(
                    RolePermission.role_id
                    == current_user.role_id
                )
                .order_by(Permission.permission_name)
            ).all()
        )

    return CurrentUserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=role_name,
        status=current_user.status,
        permissions=permissions,
    )