
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.connection import Base
from app.models import AssistantInquiryContext, User


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


def test_context_model_persists_expected_fields(db):
    now = datetime.now(timezone.utc)

    context = AssistantInquiryContext(
        owner_user_id="user-model-test",
        context_data={"step": "start"},
        status="active",
        created_at=now,
        updated_at=now,
        last_activity_at=now,
        expires_at=now + timedelta(minutes=30),
        absolute_expires_at=now + timedelta(hours=8),
    )

    db.add(context)
    db.commit()
    db.refresh(context)

    assert context.context_id
    assert context.context_data == {"step": "start"}
    assert context.status == "active"


def test_context_requires_exactly_one_owner(db):
    context = AssistantInquiryContext(
        context_data={},
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_activity_at=datetime.now(timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        absolute_expires_at=datetime.now(timezone.utc) + timedelta(hours=8),
    )

    db.add(context)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_context_rejects_invalid_status(db):
    now = datetime.now(timezone.utc)
    context = AssistantInquiryContext(
        owner_user_id="user-model-test",
        context_data={},
        status="invalid",
        created_at=now,
        updated_at=now,
        last_activity_at=now,
        expires_at=now + timedelta(minutes=30),
        absolute_expires_at=now + timedelta(hours=8),
    )

    db.add(context)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


def test_context_rejects_expiry_after_absolute_expiry(db):
    now = datetime.now(timezone.utc)
    context = AssistantInquiryContext(
        owner_user_id="user-model-test",
        context_data={},
        status="active",
        created_at=now,
        updated_at=now,
        last_activity_at=now,
        expires_at=now + timedelta(hours=9),
        absolute_expires_at=now + timedelta(hours=8),
    )

    db.add(context)

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
