
"""Persistence and lifecycle management for conversational assistant contexts."""

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AssistantInquiryContext


INACTIVITY_TIMEOUT = timedelta(minutes=30)
ABSOLUTE_LIFETIME = timedelta(hours=8)
MAX_CONTEXT_DATA_BYTES = 16_384
MAX_QUESTION_ID_LENGTH = 100
MIN_GUEST_SECRET_LENGTH = 32

ALLOWED_STATUSES = {"active", "completed", "expired", "reset"}


class AssistantContextError(Exception):
    """Base exception for assistant context operations."""


class InvalidContextOwnerError(AssistantContextError):
    """Raised when an owner identity is missing or invalid."""


class ContextOwnershipError(AssistantContextError):
    """Raised when a context does not belong to the requesting owner."""


class ContextNotFoundError(AssistantContextError):
    """Raised when a context does not exist."""


class ContextExpiredError(AssistantContextError):
    """Raised when a context is expired or no longer active."""


class InvalidContextStateError(AssistantContextError):
    """Raised when context data or workflow state is invalid."""


def _utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


def _normalize_datetime(value: datetime) -> datetime:
    """Normalize SQLite's potentially timezone-naive datetime values to UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _resolve_now(now: datetime | None = None) -> datetime:
    """Resolve an optional testable clock value to UTC."""
    if now is None:
        return _utc_now()
    return _normalize_datetime(now)


def generate_guest_session_secret() -> str:
    """Generate a high-entropy secret for an anonymous guest session.

    The caller must retain the returned secret securely for subsequent
    requests. The raw secret must not be stored in the database.
    """
    return secrets.token_urlsafe(32)


def _hash_guest_secret(secret: str) -> str:
    """Validate and hash a guest session secret."""
    if not isinstance(secret, str) or len(secret) < MIN_GUEST_SECRET_LENGTH:
        raise InvalidContextOwnerError(
            "Guest session secrets must contain at least 32 characters."
        )

    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _resolve_owner(
    owner_user_id: str | None,
    guest_session_secret: str | None,
) -> tuple[str | None, str | None]:
    """Require exactly one owner identity and hash guest secrets."""
    has_user = owner_user_id is not None
    has_guest = guest_session_secret is not None

    if has_user == has_guest:
        raise InvalidContextOwnerError(
            "Provide exactly one of owner_user_id or guest_session_secret."
        )

    if has_user:
        if not isinstance(owner_user_id, str) or not owner_user_id.strip():
            raise InvalidContextOwnerError(
                "owner_user_id must be a non-empty string."
            )
        return owner_user_id, None

    return None, _hash_guest_secret(guest_session_secret)


def _validate_question_id(question_id: str | None) -> None:
    if question_id is None:
        return

    if (
        not isinstance(question_id, str)
        or not question_id.strip()
        or len(question_id) > MAX_QUESTION_ID_LENGTH
    ):
        raise InvalidContextStateError(
            f"question_id must be a non-empty string of at most "
            f"{MAX_QUESTION_ID_LENGTH} characters."
        )


def _validate_context_data(context_data: dict[str, Any]) -> dict[str, Any]:
    """Validate JSON-compatible, bounded workflow state."""
    if not isinstance(context_data, dict):
        raise InvalidContextStateError("Context data must be a dictionary.")

    try:
        serialized = json.dumps(
            context_data,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise InvalidContextStateError(
            "Context data must contain only valid JSON values."
        ) from exc

    if len(serialized.encode("utf-8")) > MAX_CONTEXT_DATA_BYTES:
        raise InvalidContextStateError(
            f"Context data cannot exceed {MAX_CONTEXT_DATA_BYTES} bytes."
        )

    prohibited_keys = {
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "guest_session_secret",
    }

    def inspect_value(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested_value in value.items():
                if isinstance(key, str) and key.lower() in prohibited_keys:
                    raise InvalidContextStateError(
                        f"Sensitive field '{key}' cannot be stored in context."
                    )
                inspect_value(nested_value)
        elif isinstance(value, list):
            for nested_value in value:
                inspect_value(nested_value)

    inspect_value(context_data)
    return context_data


def _is_expired(
    context: AssistantInquiryContext,
    now: datetime,
) -> bool:
    inactivity_expiry = _normalize_datetime(context.expires_at)
    absolute_expiry = _normalize_datetime(context.absolute_expires_at)

    return now >= inactivity_expiry or now >= absolute_expiry


def _require_active_context(
    db: Session,
    context: AssistantInquiryContext,
    now: datetime,
) -> None:
    if context.status != "active":
        raise ContextExpiredError(
            f"Context is not active; current status is '{context.status}'."
        )

    if _is_expired(context, now):
        context.status = "expired"
        db.commit()
        raise ContextExpiredError("Assistant context has expired.")


def create_context(
    db: Session,
    *,
    owner_user_id: str | None = None,
    guest_session_secret: str | None = None,
    question_id: str | None = None,
    context_data: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> AssistantInquiryContext:
    """Create a context owned by exactly one user or guest session."""
    resolved_user_id, guest_hash = _resolve_owner(
        owner_user_id,
        guest_session_secret,
    )
    _validate_question_id(question_id)

    state = _validate_context_data(
        {} if context_data is None else context_data
    )
    current_time = _resolve_now(now)
    absolute_expiry = current_time + ABSOLUTE_LIFETIME
    inactivity_expiry = min(
        current_time + INACTIVITY_TIMEOUT,
        absolute_expiry,
    )

    context = AssistantInquiryContext(
        owner_user_id=resolved_user_id,
        guest_session_hash=guest_hash,
        question_id=question_id,
        context_data=state,
        status="active",
        created_at=current_time,
        updated_at=current_time,
        last_activity_at=current_time,
        expires_at=inactivity_expiry,
        absolute_expires_at=absolute_expiry,
    )

    db.add(context)
    db.commit()
    db.refresh(context)
    return context


def get_context(
    db: Session,
    context_id: str,
    *,
    owner_user_id: str | None = None,
    guest_session_secret: str | None = None,
    now: datetime | None = None,
) -> AssistantInquiryContext:
    """Retrieve a context only when the caller owns it and it is active."""
    resolved_user_id, guest_hash = _resolve_owner(
        owner_user_id,
        guest_session_secret,
    )

    context = db.scalar(
        select(AssistantInquiryContext).where(
            AssistantInquiryContext.context_id == context_id
        )
    )

    if context is None:
        raise ContextNotFoundError("Assistant context was not found.")

    owner_matches = (
        context.owner_user_id == resolved_user_id
        and context.guest_session_hash is None
        if resolved_user_id is not None
        else context.owner_user_id is None
        and context.guest_session_hash == guest_hash
    )

    if not owner_matches:
        raise ContextOwnershipError(
            "Assistant context does not belong to this owner."
        )

    _require_active_context(db, context, _resolve_now(now))
    return context


def update_context_state(
    db: Session,
    context_id: str,
    *,
    owner_user_id: str | None = None,
    guest_session_secret: str | None = None,
    context_data: dict[str, Any],
    question_id: str | None = None,
    now: datetime | None = None,
) -> AssistantInquiryContext:
    """Replace bounded workflow state and refresh inactivity expiry."""
    current_time = _resolve_now(now)

    context = get_context(
        db,
        context_id,
        owner_user_id=owner_user_id,
        guest_session_secret=guest_session_secret,
        now=current_time,
    )

    state = _validate_context_data(context_data)
    _validate_question_id(question_id)

    if question_id is not None:
        context.question_id = question_id

    context.context_data = state
    context.last_activity_at = current_time
    context.updated_at = current_time
    context.expires_at = min(
        current_time + INACTIVITY_TIMEOUT,
        _normalize_datetime(context.absolute_expires_at),
    )

    db.commit()
    db.refresh(context)
    return context


def complete_context(
    db: Session,
    context_id: str,
    *,
    owner_user_id: str | None = None,
    guest_session_secret: str | None = None,
    now: datetime | None = None,
) -> AssistantInquiryContext:
    """Mark an active context as completed after verifying ownership."""
    context = get_context(
        db,
        context_id,
        owner_user_id=owner_user_id,
        guest_session_secret=guest_session_secret,
        now=now,
    )
    context.status = "completed"
    context.updated_at = _resolve_now(now)
    db.commit()
    db.refresh(context)
    return context


def reset_context(
    db: Session,
    context_id: str,
    *,
    owner_user_id: str | None = None,
    guest_session_secret: str | None = None,
    now: datetime | None = None,
) -> AssistantInquiryContext:
    """Clear workflow state and mark the context as reset."""
    context = get_context(
        db,
        context_id,
        owner_user_id=owner_user_id,
        guest_session_secret=guest_session_secret,
        now=now,
    )
    current_time = _resolve_now(now)

    context.question_id = None
    context.context_data = {}
    context.status = "reset"
    context.updated_at = current_time
    context.last_activity_at = current_time

    db.commit()
    db.refresh(context)
    return context


def cleanup_expired_contexts(
    db: Session,
    *,
    now: datetime | None = None,
) -> int:
    """Mark active contexts expired when either lifetime limit has elapsed.

    Cleanup is an operational convenience, not an access-control mechanism:
    get_context independently checks expiry on every access.
    """
    current_time = _resolve_now(now)
    contexts = db.scalars(
        select(AssistantInquiryContext).where(
            AssistantInquiryContext.status == "active"
        )
    ).all()

    expired_count = 0
    for context in contexts:
        if _is_expired(context, current_time):
            context.status = "expired"
            context.updated_at = current_time
            expired_count += 1

    if expired_count:
        db.commit()

    return expired_count
