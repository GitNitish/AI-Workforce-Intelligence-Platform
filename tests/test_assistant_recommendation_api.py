
"""Integration tests for the read-only assistant recommendation API."""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database.connection import Base
from app.database.dependencies import get_db
from app.main import app
from app.models.entities import (
    AssistantInquiryContext,
    Employee,
    Project,
    Recommendation,
    StaffingRequirement,
    User,
)
from app.services.auth_service import create_user_access_token


@pytest.fixture
def recommendation_api_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def recommendation_api_client(recommendation_api_engine):
    def override_get_db():
        with Session(recommendation_api_engine) as session:
            yield session

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def assistant_users(recommendation_api_engine):
    """Create two authenticated users for ownership checks."""
    with Session(recommendation_api_engine) as db:
        user_a = User(
            user_id="assistant-rec-user-a",
            username="assistant_rec_user_a",
            email="assistant-rec-user-a@example.com",
            password_hash=hash_password("test-password-a"),
            status="active",
        )
        user_b = User(
            user_id="assistant-rec-user-b",
            username="assistant_rec_user_b",
            email="assistant-rec-user-b@example.com",
            password_hash=hash_password("test-password-b"),
            status="active",
        )

        db.add_all([user_a, user_b])
        db.commit()

        return {
            "user_a": user_a.user_id,
            "user_b": user_b.user_id,
            "token_a": create_user_access_token(user_a),
            "token_b": create_user_access_token(user_b),
        }


@pytest.fixture
def recommendation_api_data(recommendation_api_engine):
    with Session(recommendation_api_engine) as db:
        project = Project(
            project_id="assistant-rec-project",
            project_code="ARP001",
            project_name="Assistant Recommendation Test",
            status="active",
        )
        requirement = StaffingRequirement(
            staffing_requirement_id="assistant-rec-requirement",
            project_id="assistant-rec-project",
            role_name="Data Analyst",
            required_quantity=1,
            required_experience=1,
            required_proficiency="beginner",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status="open",
        )
        employee = Employee(
            employee_id="assistant-rec-employee",
            employee_code="ARE001",
            name="Recommendation Test Employee",
            email="recommendation-test@example.com",
            designation="Data Analyst",
            department="Analytics",
            experience_years=5,
            availability_status="available",
            utilization_percentage=0,
            status="active",
        )

        db.add_all([project, requirement, employee])
        db.commit()

        return {
            "requirement_id": requirement.staffing_requirement_id,
            "employee_id": employee.employee_id,
        }


def create_recommendation_context(
    client,
    engine,
    question_id="view_recommendations",
):
    """Create an inquiry and prepare its persisted question state.

    Recommendation questions remain disabled in guided routing until the
    recommendation API safety tests have passed.
    """
    response = client.post("/api/v1/assistant/inquiries")
    assert response.status_code == 201

    context_id = response.json()["context_id"]

    with Session(engine) as db:
        context = db.get(AssistantInquiryContext, context_id)
        assert context is not None

        context.question_id = question_id
        context.context_data = {
            "current_step": "capability",
            "current_category": "recommendations",
            "selected_question_id": question_id,
        }
        db.commit()

    return context_id


def call_recommendation_evaluation(
    client,
    context_id,
    requirement_id="assistant-rec-requirement",
    limit=25,
):
    return client.post(
        f"/api/v1/assistant/inquiries/{context_id}/recommendation-evaluation",
        json={
            "staffing_requirement_id": requirement_id,
            "limit": limit,
        },
    )


def test_recommendation_evaluation_returns_ranked_candidates(
    recommendation_api_client,
    recommendation_api_engine,
    recommendation_api_data,
):
    context_id = create_recommendation_context(
        recommendation_api_client,
        recommendation_api_engine,
    )

    response = call_recommendation_evaluation(
        recommendation_api_client,
        context_id,
        recommendation_api_data["requirement_id"],
    )

    assert response.status_code == 200
    data = response.json()

    assert data["capability"] == "read_only_recommendation_evaluation"
    assert (
        data["staffing_requirement"]["staffing_requirement_id"]
        == recommendation_api_data["requirement_id"]
    )
    assert data["result_count"] >= 1
    assert data["eligible_candidate_count"] >= 1
    assert (
        data["candidates"][0]["employee_id"]
        == recommendation_api_data["employee_id"]
    )
    assert data["candidates"][0]["rank"] == 1
    assert "without saving recommendations" in data["notice"].lower()


def test_recommendation_evaluation_requires_selected_question(
    recommendation_api_client,
    recommendation_api_engine,
    recommendation_api_data,
):
    context_id = create_recommendation_context(
        recommendation_api_client,
        recommendation_api_engine,
        question_id=None,
    )

    response = call_recommendation_evaluation(
        recommendation_api_client,
        context_id,
        recommendation_api_data["requirement_id"],
    )

    assert response.status_code == 409


def test_recommendation_evaluation_rejects_unknown_requirement(
    recommendation_api_client,
    recommendation_api_engine,
):
    context_id = create_recommendation_context(
        recommendation_api_client,
        recommendation_api_engine,
    )

    response = call_recommendation_evaluation(
        recommendation_api_client,
        context_id,
        "unknown-staffing-requirement",
    )

    assert response.status_code == 404


@pytest.mark.parametrize("limit", [0, -1, 26])
def test_recommendation_evaluation_rejects_invalid_limit(
    recommendation_api_client,
    recommendation_api_engine,
    recommendation_api_data,
    limit,
):
    context_id = create_recommendation_context(
        recommendation_api_client,
        recommendation_api_engine,
    )

    response = call_recommendation_evaluation(
        recommendation_api_client,
        context_id,
        recommendation_api_data["requirement_id"],
        limit=limit,
    )

    assert response.status_code == 422


def test_recommendation_evaluation_rejects_another_users_inquiry(
    recommendation_api_client,
    recommendation_api_engine,
    recommendation_api_data,
    assistant_users,
):
    token_a = assistant_users["token_a"]
    token_b = assistant_users["token_b"]

    create_response = recommendation_api_client.post(
        "/api/v1/assistant/inquiries",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_response.status_code == 201

    context_id = create_response.json()["context_id"]

    with Session(recommendation_api_engine) as db:
        context = db.get(AssistantInquiryContext, context_id)
        assert context is not None

        context.question_id = "view_recommendations"
        context.context_data = {
            "current_step": "capability",
            "current_category": "recommendations",
            "selected_question_id": "view_recommendations",
        }
        db.commit()

    response = recommendation_api_client.post(
        f"/api/v1/assistant/inquiries/{context_id}/recommendation-evaluation",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "staffing_requirement_id": recommendation_api_data["requirement_id"],
            "limit": 25,
        },
    )

    assert response.status_code == 403


def test_recommendation_evaluation_does_not_create_saved_recommendations(
    recommendation_api_client,
    recommendation_api_engine,
    recommendation_api_data,
):
    context_id = create_recommendation_context(
        recommendation_api_client,
        recommendation_api_engine,
    )

    with Session(recommendation_api_engine) as db:
        before = db.scalars(select(Recommendation)).all()
        before_ids = {item.recommendation_id for item in before}

    response = call_recommendation_evaluation(
        recommendation_api_client,
        context_id,
        recommendation_api_data["requirement_id"],
    )
    assert response.status_code == 200

    with Session(recommendation_api_engine) as db:
        after = db.scalars(select(Recommendation)).all()
        after_ids = {item.recommendation_id for item in after}

    assert after_ids == before_ids
    assert after == []


def test_recommendation_evaluation_preserves_existing_saved_recommendation(
    recommendation_api_client,
    recommendation_api_engine,
    recommendation_api_data,
):
    context_id = create_recommendation_context(
        recommendation_api_client,
        recommendation_api_engine,
    )

    with Session(recommendation_api_engine) as db:
        saved = Recommendation(
            recommendation_id="assistant-rec-saved-row",
            staffing_requirement_id=recommendation_api_data["requirement_id"],
            employee_id=recommendation_api_data["employee_id"],
            score=73.5,
            rank=1,
            eligibility_status="eligible",
            recommendation_reason="Existing saved recommendation",
        )
        db.add(saved)
        db.commit()

        before = {
            "recommendation_id": saved.recommendation_id,
            "staffing_requirement_id": saved.staffing_requirement_id,
            "employee_id": saved.employee_id,
            "score": saved.score,
            "rank": saved.rank,
            "eligibility_status": saved.eligibility_status,
            "recommendation_reason": saved.recommendation_reason,
        }

    response = call_recommendation_evaluation(
        recommendation_api_client,
        context_id,
        recommendation_api_data["requirement_id"],
    )
    assert response.status_code == 200

    with Session(recommendation_api_engine) as db:
        persisted = db.get(
            Recommendation,
            "assistant-rec-saved-row",
        )
        assert persisted is not None

        after = {
            "recommendation_id": persisted.recommendation_id,
            "staffing_requirement_id": persisted.staffing_requirement_id,
            "employee_id": persisted.employee_id,
            "score": persisted.score,
            "rank": persisted.rank,
            "eligibility_status": persisted.eligibility_status,
            "recommendation_reason": persisted.recommendation_reason,
        }

    assert after == before
