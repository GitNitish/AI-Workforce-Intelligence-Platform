from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.database.dependencies import get_db
from app.main import app


def override_get_db():
    yield None


def override_recommendation_permission():
    return SimpleNamespace(
        user_id="recommendation-test-user",
        role_id="recommendation-test-role",
        status="active",
    )


def get_recommendation_permission_dependency():
    for included_router in app.routes:
        original_router = getattr(
            included_router,
            "original_router",
            None,
        )

        if original_router is None:
            continue

        for route in original_router.routes:
            if getattr(route, "path", None) != "/recommendations":
                continue

            for dependency in route.dependant.dependencies:
                dependency_name = getattr(
                    dependency.call,
                    "__name__",
                    "",
                )

                if dependency_name == "permission_dependency":
                    return dependency.call

    raise RuntimeError(
        "Recommendation permission dependency not found"
    )


@pytest.fixture(autouse=True)
def recommendation_test_dependencies():
    original_overrides = app.dependency_overrides.copy()

    recommendation_permission = (
        get_recommendation_permission_dependency()
    )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[
        recommendation_permission
    ] = override_recommendation_permission

    yield

    app.dependency_overrides.clear()
    app.dependency_overrides.update(
        original_overrides
    )


client = TestClient(app)


def test_generate_recommendations_returns_success_response(
    monkeypatch,
):
    generated_at = datetime.now(timezone.utc)

    employee = SimpleNamespace(
        employee_id="employee-001"
    )

    recommendation = SimpleNamespace(
        employee=employee,
        employee_id="employee-001",
        rank=1,
        score=87.5,
        eligibility_status="eligible",
        recommendation_reason=(
            "Matched skills: Python, SQL. "
            "All required skills matched; "
            "Experience requirement met; "
            "No certification requirement; "
            "Currently available; "
            "20% remaining capacity"
        ),
        generated_at=generated_at,
    )

    def fake_generate_recommendations(
        db,
        staffing_requirement_id,
    ):
        assert staffing_requirement_id == "staffing-001"
        return [recommendation]

    monkeypatch.setattr(
        "app.api.router.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/v1/recommendations",
        json={
            "staffing_requirement_id": "staffing-001"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["staffing_requirement_id"] == "staffing-001"
    assert data["message"] == (
        "Recommendations generated successfully."
    )

    assert len(data["recommendations"]) == 1

    item = data["recommendations"][0]

    assert item["employee_id"] == "employee-001"
    assert item["rank"] == 1
    assert item["score"] == 87.5
    assert item["eligibility_status"] == "eligible"
    assert item["matched_skills"] == [
        "Python",
        "SQL",
    ]
    assert "All required skills matched" in item["reason"]


def test_generate_recommendations_returns_404_when_requirement_not_found(
    monkeypatch,
):
    def fake_generate_recommendations(
        db,
        staffing_requirement_id,
    ):
        raise ValueError(
            "Staffing requirement not found"
        )

    monkeypatch.setattr(
        "app.api.router.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/v1/recommendations",
        json={
            "staffing_requirement_id": "missing-requirement",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Staffing requirement not found"
    )


def test_generate_recommendations_returns_422_for_business_rule_error(
    monkeypatch,
):
    def fake_generate_recommendations(
        db,
        staffing_requirement_id,
    ):
        raise ValueError(
            "Invalid recommendation criteria"
        )

    monkeypatch.setattr(
        "app.api.router.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/v1/recommendations",
        json={
            "staffing_requirement_id": "staffing-001"
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Invalid recommendation criteria"
    )


def test_generate_recommendations_returns_empty_result_when_no_candidates(
    monkeypatch,
):
    def fake_generate_recommendations(
        db,
        staffing_requirement_id,
    ):
        return []

    monkeypatch.setattr(
        "app.api.router.generate_recommendations",
        fake_generate_recommendations,
    )

    response = client.post(
        "/api/v1/recommendations",
        json={
            "staffing_requirement_id": "staffing-001"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["staffing_requirement_id"] == "staffing-001"
    assert data["recommendations"] == []
    assert data["message"] == (
        "No eligible employees found."
    )


def test_generate_recommendations_requires_staffing_requirement_id():
    response = client.post(
        "/api/v1/recommendations",
        json={},
    )

    assert response.status_code == 422