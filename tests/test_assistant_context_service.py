
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database.connection import Base
from app.models import AssistantInquiryContext
from app.services.assistant_context_service import (
    ABSOLUTE_LIFETIME,
    INACTIVITY_TIMEOUT,
    ContextExpiredError,
    ContextOwnershipError,
    InvalidContextOwnerError,
    InvalidContextStateError,
    cleanup_expired_contexts,
    create_context,
    generate_guest_session_secret,
    get_context,
    reset_context,
    update_context_state,
)


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def now():
    return datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)


def as_utc(value: datetime) -> datetime:
    """Normalize SQLite's timezone-naive datetime values for comparisons."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def test_create_user_context(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        question_id="employee_search",
        context_data={"filters": {"department": "Analytics"}},
        now=now,
    )

    assert context.context_id
    assert context.owner_user_id == "user-123"
    assert context.guest_session_hash is None
    assert context.question_id == "employee_search"
    assert context.context_data == {
        "filters": {"department": "Analytics"}
    }
    assert context.status == "active"
    assert as_utc(context.expires_at) == now + INACTIVITY_TIMEOUT
    assert as_utc(context.absolute_expires_at) == now + ABSOLUTE_LIFETIME


def test_create_guest_context_stores_only_hash(db, now):
    secret = generate_guest_session_secret()

    context = create_context(
        db,
        guest_session_secret=secret,
        now=now,
    )

    assert context.owner_user_id is None
    assert context.guest_session_hash
    assert context.guest_session_hash != secret
    assert len(context.guest_session_hash) == 64

    stored = db.scalar(
        select(AssistantInquiryContext).where(
            AssistantInquiryContext.context_id == context.context_id
        )
    )
    assert stored.guest_session_hash != secret


def test_owner_identity_must_be_exactly_one(db):
    with pytest.raises(InvalidContextOwnerError):
        create_context(db)

    with pytest.raises(InvalidContextOwnerError):
        create_context(
            db,
            owner_user_id="user-123",
            guest_session_secret=generate_guest_session_secret(),
        )


def test_guest_secret_must_be_long_enough(db):
    with pytest.raises(InvalidContextOwnerError):
        create_context(db, guest_session_secret="short-secret")


def test_context_cannot_be_read_by_another_user(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )

    with pytest.raises(ContextOwnershipError):
        get_context(
            db,
            context.context_id,
            owner_user_id="user-456",
            now=now + timedelta(minutes=1),
        )


def test_guest_context_requires_matching_secret(db, now):
    secret = generate_guest_session_secret()
    context = create_context(
        db,
        guest_session_secret=secret,
        now=now,
    )

    with pytest.raises(ContextOwnershipError):
        get_context(
            db,
            context.context_id,
            guest_session_secret=generate_guest_session_secret(),
            now=now + timedelta(minutes=1),
        )


def test_get_context_rejects_inactivity_expiry(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )

    with pytest.raises(ContextExpiredError):
        get_context(
            db,
            context.context_id,
            owner_user_id="user-123",
            now=now + INACTIVITY_TIMEOUT,
        )

    db.refresh(context)
    assert context.status == "expired"


def test_update_refreshes_inactivity_but_not_absolute_expiry(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )
    original_absolute_expiry = as_utc(context.absolute_expires_at)
    update_time = now + timedelta(minutes=20)

    updated = update_context_state(
        db,
        context.context_id,
        owner_user_id="user-123",
        context_data={"step": "select_department"},
        now=update_time,
    )

    assert updated.context_data == {"step": "select_department"}
    assert as_utc(updated.last_activity_at) == update_time
    assert as_utc(updated.expires_at) == update_time + INACTIVITY_TIMEOUT
    assert as_utc(updated.absolute_expires_at) == original_absolute_expiry


def test_update_cannot_extend_beyond_absolute_expiry(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )

    # Simulate ongoing activity, keeping each update within the
    # 30-minute inactivity window until close to the 8-hour limit.
    for minutes in range(20, 461, 20):
        update_time = now + timedelta(minutes=minutes)
        context = update_context_state(
            db,
            context.context_id,
            owner_user_id="user-123",
            context_data={"last_activity_minute": minutes},
            now=update_time,
        )

    update_time = now + timedelta(hours=7, minutes=50)
    updated = update_context_state(
        db,
        context.context_id,
        owner_user_id="user-123",
        context_data={"step": "final"},
        now=update_time,
    )

    absolute_expiry = now + ABSOLUTE_LIFETIME
    assert as_utc(updated.expires_at) == absolute_expiry
    assert as_utc(updated.absolute_expires_at) == absolute_expiry


def test_absolute_expiry_is_enforced(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )

    with pytest.raises(ContextExpiredError):
        get_context(
            db,
            context.context_id,
            owner_user_id="user-123",
            now=now + ABSOLUTE_LIFETIME,
        )


def test_state_size_is_bounded(db):
    with pytest.raises(InvalidContextStateError):
        create_context(
            db,
            owner_user_id="user-123",
            context_data={"payload": "x" * 20_000},
        )


def test_sensitive_state_keys_are_rejected(db):
    with pytest.raises(InvalidContextStateError):
        create_context(
            db,
            owner_user_id="user-123",
            context_data={"access_token": "do-not-store"},
        )


def test_non_json_state_is_rejected(db):
    with pytest.raises(InvalidContextStateError):
        create_context(
            db,
            owner_user_id="user-123",
            context_data={"unsupported": object()},
        )


def test_reset_clears_state_and_ends_context(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        question_id="employee_search",
        context_data={"step": "results"},
        now=now,
    )

    reset = reset_context(
        db,
        context.context_id,
        owner_user_id="user-123",
        now=now + timedelta(minutes=1),
    )

    assert reset.status == "reset"
    assert reset.question_id is None
    assert reset.context_data == {}

    with pytest.raises(ContextExpiredError):
        get_context(
            db,
            context.context_id,
            owner_user_id="user-123",
            now=now + timedelta(minutes=1),
        )


def test_cleanup_marks_expired_contexts(db, now):
    create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )
    create_context(
        db,
        owner_user_id="user-456",
        now=now,
    )

    count = cleanup_expired_contexts(
        db,
        now=now + INACTIVITY_TIMEOUT,
    )

    assert count == 2

    contexts = db.scalars(
        select(AssistantInquiryContext)
    ).all()
    assert all(context.status == "expired" for context in contexts)


def test_cleanup_does_not_expire_active_contexts(db, now):
    context = create_context(
        db,
        owner_user_id="user-123",
        now=now,
    )

    count = cleanup_expired_contexts(
        db,
        now=now + timedelta(minutes=10),
    )

    db.refresh(context)
    assert count == 0
    assert context.status == "active"
