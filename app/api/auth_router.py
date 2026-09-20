from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.auth import TokenResponse
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

        user.last_login = datetime.now(timezone.utc)

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