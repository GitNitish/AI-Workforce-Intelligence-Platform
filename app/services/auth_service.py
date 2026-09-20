from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.models.entities import User


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User:
    user = db.scalar(
        select(User).where(
            User.username == username
        )
    )

    if user is None:
        raise ValueError(
            "Invalid username or password"
        )

    if user.status != "active":
        raise ValueError(
            "User account is inactive"
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise ValueError(
            "Invalid username or password"
        )

    return user


def create_user_access_token(
    user: User,
) -> str:
    return create_access_token(
        user.user_id
    )