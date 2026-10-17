"""Integration tests for the WorkForceIQ assistant API."""

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
    EmployeeSkill,
    Project,
    Skill,
    StaffingRequirement,
    StaffingRequirementSkill,
    User,
)
from app.services.auth_service import create_user_access_token

API_PREFIX = "/api/v1/assistant"


@pytest.fixture
def assistant_engine():
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
def assistant_client(assistant_engine):
    def override_get_db():
        with Session(assistant_engine) as session:
            yield session

    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def assistant_users(assistant_engine):
    with Session(assistant_engine) as db:
        user_a = User(
            user_id="assistant-user-a",
            username="assistant_user_a",
            email="assistant_user_a@example.com",
            password_hash=hash_password("test-password-a"),
            status="active",
        )
        user_b = User(
            user_id="assistant-user-b",
            username="assistant_user_b",
            email="assistant_user_b@example.com",
            password_hash=hash_password("test-password-b"),
            status="active",
        )
        db.add_all([user_a, user_b])
        db.commit()
        token_a = create_user_access_token(user_a)
        token_b = create_user_access_token(user_b)
        return {
            "user_a": user_a.user_id,
            "user_b": user_b.user_id,
            "token_a": token_a,
            "token_b": token_b,
        }


@pytest.fixture
def workforce_data(assistant_engine):
    """Create employees and a staffing requirement for API integration tests."""
    with Session(assistant_engine) as db:
        alice = Employee(
            employee_id="assistant-employee-alice",
            employee_code="EMP-A100",
            name="Alice Sharma",
            email="alice.assistant@example.com",
            designation="Data Analyst",
            department="Analytics",
            experience_years=5,
            availability_status="available",
            utilization_percentage=20,
            location="Delhi",
            status="active",
        )
        bob = Employee(
            employee_id="assistant-employee-bob",
            employee_code="EMP-B200",
            name="Bob Kumar",
            email="bob.assistant@example.com",
            designation="Backend Developer",
            department="Engineering",
            experience_years=3,
            availability_status="partially_available",
            utilization_percentage=70,
            location="Mumbai",
            status="active",
        )
        inactive = Employee(
            employee_id="assistant-employee-inactive",
            employee_code="EMP-C300",
            name="Charlie Das",
            email="charlie.assistant@example.com",
            designation="Data Analyst",
            department="Analytics",
            experience_years=8,
            availability_status="unavailable",
            utilization_percentage=100,
            location="Delhi",
            status="inactive",
        )
        project = Project(
            project_id="assistant-project-1",
            project_code="AST-PROJ-1",
            project_name="Assistant Integration Test",
            client_name="Test Client",
            status="active",
            priority="medium",
        )
        skill = Skill(
            skill_id="assistant-skill-python",
            skill_name="Python",
            category="Technical",
            status="active",
        )
        requirement = StaffingRequirement(
            staffing_requirement_id="assistant-requirement-1",
            project_id=project.project_id,
            role_name="Python Developer",
            required_quantity=1,
            required_experience=2,
            required_proficiency="intermediate",
            status="open",
            priority="medium",
        )
        db.add_all([alice, bob, inactive, project, skill, requirement])
        db.flush()
        db.add_all(
            [
                EmployeeSkill(
                    employee_id=alice.employee_id,
                    skill_id=skill.skill_id,
                    proficiency_level="advanced",
                    years_experience=5,
                ),
                EmployeeSkill(
                    employee_id=bob.employee_id,
                    skill_id=skill.skill_id,
                    proficiency_level="intermediate",
                    years_experience=3,
                ),
                StaffingRequirementSkill(
                    staffing_requirement_id=(
                        requirement.staffing_requirement_id
                    ),
                    skill_id=skill.skill_id,
                ),
            ]
        )
        db.commit()
        return {
            "alice_id": alice.employee_id,
            "bob_id": bob.employee_id,
            "inactive_id": inactive.employee_id,
            "requirement_id": requirement.staffing_requirement_id,
        }


def start_guest_inquiry(client):
    response = client.post(f"{API_PREFIX}/inquiries")
    assert response.status_code == 201
    return response.json()["context_id"]


def select_assistant_question(client, context_id, question_id):
    category_response = client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": "candidate_discovery"},
    )
    assert category_response.status_code == 200
    question_response = client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": question_id},
    )
    assert question_response.status_code == 200
    return question_response


def test_start_inquiry_creates_guest_session(assistant_client):
    response = assistant_client.post(f"{API_PREFIX}/inquiries")
    assert response.status_code == 201
    data = response.json()
    assert data["context_id"]
    assert data["status"] == "active"
    assert data["current_step"] == "category"
    assert data["options"]
    cookie = response.headers.get("set-cookie", "")
    assert "workforceiq_guest_session=" in cookie
    assert "httponly" in cookie.lower()
    category_ids = {option["id"] for option in data["options"]}
    assert "candidate_discovery" in category_ids
    assert "recommendations" in category_ids
    assert "workforce_capacity_analysis" in category_ids
    assert "utilization" not in category_ids


def test_guest_can_retrieve_own_inquiry(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["context_id"] == context_id
    assert data["status"] == "active"
    assert data["context_data"]["current_step"] == "category"


def test_guest_can_select_candidate_discovery(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": "candidate_discovery"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["context_id"] == context_id
    assert data["selected_id"] == "candidate_discovery"
    assert data["current_step"] == "question"
    option_ids = {option["id"] for option in data["options"]}
    assert option_ids == {
        "find_candidates_for_requirement",
        "search_employees",
    }


def test_guest_can_select_candidate_question(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    assert response.json()["selected_id"] == "search_employees"
    assert response.json()["current_step"] == "capability"
    assert response.json()["options"] == []


def test_unknown_category_is_rejected(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": "unknown_category"},
    )
    assert response.status_code == 422


def test_legacy_capacity_category_routes_to_unified_analysis(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": "capacity"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["selected_id"] == "capacity"
    assert data["current_step"] == "question"
    assert data["options"]
    assert {option["id"] for option in data["options"]} == {
        "view_workforce_capacity_analysis"
    }


def test_recommendation_question_is_accepted(assistant_client):
    context_id = start_guest_inquiry(assistant_client)

    category_response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": "recommendations"},
    )

    assert category_response.status_code == 200

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={"selection_id": "view_recommendations"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["selected_id"] == "view_recommendations"
    assert payload["current_step"] == "capability"


def test_guest_cannot_access_another_guest_context(assistant_engine):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        with Session(assistant_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as first_client:
            context_id = start_guest_inquiry(first_client)
            with TestClient(app) as second_client:
                response = second_client.get(
                    f"{API_PREFIX}/inquiries/{context_id}"
                )
                assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def test_guest_can_reset_inquiry(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/reset"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["context_id"] == context_id
    assert data["status"] == "reset"
    assert data["context_data"] == {}
    assert data["question_id"] is None


def test_reset_inquiry_cannot_be_retrieved_as_active(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    reset_response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/reset"
    )
    assert reset_response.status_code == 200
    response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert response.status_code == 410


def test_selection_rejects_unexpected_fields(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/selections",
        json={
            "selection_id": "candidate_discovery",
            "execute_sql": "SELECT * FROM users",
        },
    )
    assert response.status_code == 422


def test_authenticated_user_can_access_own_inquiry(
    assistant_client,
    assistant_users,
):
    token = assistant_users["token_a"]
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    context_id = response.json()["context_id"]
    get_response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["context_id"] == context_id


def test_authenticated_user_cannot_access_another_users_context(
    assistant_client,
    assistant_users,
):
    token_a = assistant_users["token_a"]
    token_b = assistant_users["token_b"]
    create_response = assistant_client.post(
        f"{API_PREFIX}/inquiries",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert create_response.status_code == 201
    context_id = create_response.json()["context_id"]
    response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 403


def test_authenticated_user_cannot_access_guest_context(
    assistant_client,
    assistant_users,
):
    guest_client = TestClient(app)
    context_id = start_guest_inquiry(guest_client)
    token = assistant_users["token_a"]
    response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_guest_cannot_access_authenticated_users_context(
    assistant_client,
    assistant_users,
):
    token = assistant_users["token_a"]
    create_response = assistant_client.post(
        f"{API_PREFIX}/inquiries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    context_id = create_response.json()["context_id"]
    guest_client = TestClient(app)
    response = guest_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert response.status_code == 403


def test_employee_search_returns_filtered_results(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-search",
        json={
            "department": "Analytics",
            "min_experience": 4,
            "status": "active",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["capability"] == "search_employees"
    assert data["result_count"] == 1
    assert data["employees"][0]["employee_id"] == workforce_data["alice_id"]
    assert data["filters"]["department"] == "Analytics"
    assert data["filters"]["min_experience"] == 4
    assert "email" not in data["employees"][0]


def test_employee_search_requires_search_question(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-search",
        json={"department": "Analytics"},
    )
    assert response.status_code == 409


def test_employee_search_rejects_invalid_filters(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-search",
        json={"availability_status": "maybe"},
    )
    assert response.status_code == 422


def test_employee_search_rejects_unexpected_fields(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-search",
        json={
            "department": "Analytics",
            "delete_records": True,
        },
    )
    assert response.status_code == 422


def test_employee_detail_returns_approved_fields(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-detail",
        json={"employee_id": workforce_data["alice_id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["capability"] == "employee_detail"
    assert data["employee"]["name"] == "Alice Sharma"
    assert data["employee"]["employee_id"] == workforce_data["alice_id"]
    assert "email" not in data["employee"]


def test_employee_detail_returns_not_found_for_unknown_employee(
    assistant_client,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-detail",
        json={"employee_id": "does-not-exist"},
    )
    assert response.status_code == 404


def test_employee_detail_requires_employee_related_question(
    assistant_client,
):
    context_id = start_guest_inquiry(assistant_client)
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-detail",
        json={"employee_id": "does-not-exist"},
    )
    assert response.status_code == 409


def test_candidate_discovery_returns_discovery_notice(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "find_candidates_for_requirement",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/candidate-discovery",
        json={
            "staffing_requirement_id": workforce_data["requirement_id"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["capability"] == "candidate_discovery"
    assert data["staffing_requirement"]["staffing_requirement_id"] == (
        workforce_data["requirement_id"]
    )
    assert data["result_count"] == 2
    assert {item["employee_id"] for item in data["employees"]} == {
        workforce_data["alice_id"],
        workforce_data["bob_id"],
    }
    assert "not final eligibility" in data["notice"]
    assert "email" not in data["employees"][0]


def test_candidate_discovery_requires_candidate_question(
    assistant_client,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/candidate-discovery",
        json={
            "staffing_requirement_id": workforce_data["requirement_id"],
        },
    )
    assert response.status_code == 409


def test_candidate_discovery_returns_not_found_for_unknown_requirement(
    assistant_client,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "find_candidates_for_requirement",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/candidate-discovery",
        json={"staffing_requirement_id": "does-not-exist"},
    )
    assert response.status_code == 404


def test_employee_search_enforces_context_ownership(
    assistant_engine,
    workforce_data,
):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        with Session(assistant_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as owner_client:
            context_id = start_guest_inquiry(owner_client)
            select_assistant_question(
                owner_client,
                context_id,
                "search_employees",
            )
            with TestClient(app) as other_client:
                response = other_client.post(
                    f"{API_PREFIX}/inquiries/{context_id}/employee-search",
                    json={"department": "Analytics"},
                )
                assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def test_capability_queries_do_not_modify_employee_records(
    assistant_client,
    assistant_engine,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    with Session(assistant_engine) as db:
        before = db.scalar(
            select(Employee).where(
                Employee.employee_id == workforce_data["alice_id"]
            )
        )
        original_name = before.name
        original_department = before.department
        original_status = before.status
    search_response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-search",
        json={"department": "Analytics"},
    )
    assert search_response.status_code == 200
    detail_response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-detail",
        json={"employee_id": workforce_data["alice_id"]},
    )
    assert detail_response.status_code == 200
    with Session(assistant_engine) as db:
        after = db.scalar(
            select(Employee).where(
                Employee.employee_id == workforce_data["alice_id"]
            )
        )
        assert after.name == original_name
        assert after.department == original_department
        assert after.status == original_status


def test_assistant_context_stores_result_summary(
    assistant_client,
    assistant_engine,
    workforce_data,
):
    context_id = start_guest_inquiry(assistant_client)
    select_assistant_question(
        assistant_client,
        context_id,
        "search_employees",
    )
    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/employee-search",
        json={"department": "Analytics"},
    )
    assert response.status_code == 200
    context_response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert context_response.status_code == 200
    data = context_response.json()["context_data"]
    assert data["current_step"] == "results"
    assert data["last_result_summary"]["capability"] == "search_employees"
    assert data["last_result_summary"]["result_count"] == 1
    assert data["search_filters"]["department"] == "Analytics"


def prepare_utilization_context(assistant_client, assistant_engine):
    """Put an owned inquiry into the utilization question state for endpoint tests."""
    context_id = start_guest_inquiry(assistant_client)
    with Session(assistant_engine) as db:
        context = db.scalar(
            select(AssistantInquiryContext).where(
                AssistantInquiryContext.context_id == context_id
            )
        )
        assert context is not None
        context.context_data = {
            "current_step": "capability",
            "current_category": "utilization",
            "selected_question_id": "view_current_utilization",
        }
        context.question_id = "view_current_utilization"
        db.commit()
    return context_id


def test_utilization_returns_summary_and_persists_result_state(
    assistant_client,
    assistant_engine,
    workforce_data,
):
    context_id = prepare_utilization_context(
        assistant_client,
        assistant_engine,
    )

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/utilization"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["capability"] == "utilization_summary"
    assert data["active_employee_count"] == 2
    assert data["result_count"] == 2
    assert data["limit"] >= data["result_count"]
    assert data["has_more_results"] is False
    assert len(data["employees"]) == 2
    assert {employee["employee_id"] for employee in data["employees"]} == {
        workforce_data["alice_id"],
        workforce_data["bob_id"],
    }
    assert all("email" not in employee for employee in data["employees"])

    context_response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert context_response.status_code == 200
    context_data = context_response.json()["context_data"]
    assert context_data["current_step"] == "results"
    assert context_data["last_result_summary"]["capability"] == (
        "utilization_summary"
    )
    assert context_data["last_result_summary"]["active_employee_count"] == 2
    assert context_data["last_result_summary"]["result_count"] == 2


def test_utilization_requires_utilization_question(assistant_client):
    context_id = start_guest_inquiry(assistant_client)

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/utilization"
    )

    assert response.status_code == 409


def test_utilization_enforces_guest_context_ownership(assistant_engine):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        with Session(assistant_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as owner_client:
            context_id = prepare_utilization_context(
                owner_client,
                assistant_engine,
            )
            with TestClient(app) as other_client:
                response = other_client.post(
                    f"{API_PREFIX}/inquiries/{context_id}/utilization"
                )
                assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
def prepare_capacity_context(assistant_client, assistant_engine):
    """Put an owned inquiry into the capacity question state for endpoint tests."""
    context_id = start_guest_inquiry(assistant_client)
    with Session(assistant_engine) as db:
        context = db.scalar(
            select(AssistantInquiryContext).where(
                AssistantInquiryContext.context_id == context_id
            )
        )
        assert context is not None
        context.context_data = {
            "current_step": "capability",
            "current_category": "capacity",
            "selected_question_id": "view_current_capacity",
        }
        context.question_id = "view_current_capacity"
        db.commit()
    return context_id


def test_capacity_returns_summary_and_persists_result_state(
    assistant_client,
    assistant_engine,
    workforce_data,
):
    context_id = prepare_capacity_context(
        assistant_client,
        assistant_engine,
    )

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/capacity"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["capability"] == "capacity_summary"
    assert data["reporting_date"]
    assert data["active_employee_count"] == 2
    assert data["result_count"] == 2
    assert data["limit"] >= data["result_count"]
    assert data["has_more_results"] is False
    assert data["average_allocated_capacity_percentage"] == 0
    assert data["average_available_capacity_percentage"] == 100
    assert data["employees_with_no_available_capacity_count"] == 0
    assert data["employees_with_partial_available_capacity_count"] == 0
    assert data["employees_with_full_available_capacity_count"] == 2
    assert len(data["employees"]) == 2
    assert {
        employee["employee_id"] for employee in data["employees"]
    } == {
        workforce_data["alice_id"],
        workforce_data["bob_id"],
    }
    assert all(
        employee["allocated_capacity_percentage"] == 0
        and employee["available_capacity_percentage"] == 100
        for employee in data["employees"]
    )
    assert all("email" not in employee for employee in data["employees"])

    context_response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert context_response.status_code == 200
    context_data = context_response.json()["context_data"]
    assert context_data["current_step"] == "results"
    assert context_data["last_result_summary"]["capability"] == (
        "capacity_summary"
    )
    assert context_data["last_result_summary"]["reporting_date"] == (
        data["reporting_date"]
    )
    assert context_data["last_result_summary"]["active_employee_count"] == 2
    assert context_data["last_result_summary"]["result_count"] == 2
    assert context_data["last_result_summary"]["has_more_results"] is False


def test_capacity_requires_capacity_question(assistant_client):
    context_id = start_guest_inquiry(assistant_client)

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/capacity"
    )

    assert response.status_code == 409


def test_capacity_rejects_other_selected_question(
    assistant_client,
    assistant_engine,
):
    context_id = prepare_utilization_context(
        assistant_client,
        assistant_engine,
    )

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/capacity"
    )

    assert response.status_code == 409


def test_capacity_enforces_guest_context_ownership(assistant_engine):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        with Session(assistant_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as owner_client:
            context_id = prepare_capacity_context(
                owner_client,
                assistant_engine,
            )
            with TestClient(app) as other_client:
                response = other_client.post(
                    f"{API_PREFIX}/inquiries/{context_id}/capacity"
                )
                assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def test_capacity_rejects_reset_inquiry(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    reset_response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/reset"
    )
    assert reset_response.status_code == 200

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/capacity"
    )
    assert response.status_code == 410

def prepare_workforce_capacity_analysis_context(assistant_client, assistant_engine):
    """Put an owned inquiry into the unified workforce analysis question state."""
    context_id = start_guest_inquiry(assistant_client)
    with Session(assistant_engine) as db:
        context = db.scalar(
            select(AssistantInquiryContext).where(
                AssistantInquiryContext.context_id == context_id
            )
        )
        assert context is not None
        context.context_data = {
            "current_step": "capability",
            "current_category": "workforce_capacity_analysis",
            "selected_question_id": "view_workforce_capacity_analysis",
        }
        context.question_id = "view_workforce_capacity_analysis"
        db.commit()
    return context_id


def test_workforce_capacity_analysis_returns_combined_summary_and_persists_state(
    assistant_client,
    assistant_engine,
    workforce_data,
):
    context_id = prepare_workforce_capacity_analysis_context(
        assistant_client,
        assistant_engine,
    )

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/workforce-capacity-analysis"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["capability"] == "workforce_capacity_analysis"
    assert data["reporting_date"]
    assert data["active_employee_count"] == 2
    assert data["result_count"] == 2
    assert data["limit"] >= data["result_count"]
    assert data["has_more_results"] is False
    assert data["average_utilization_percentage"] >= 0
    assert data["average_allocated_capacity_percentage"] == 0
    assert data["average_available_capacity_percentage"] == 100
    assert data["employees_with_no_available_capacity_count"] == 0
    assert data["employees_with_partial_available_capacity_count"] == 0
    assert data["employees_with_full_available_capacity_count"] == 2
    assert {
        employee["employee_id"] for employee in data["employees"]
    } == {
        workforce_data["alice_id"],
        workforce_data["bob_id"],
    }
    assert all(
        0 <= employee["utilization_percentage"] <= 100
        and employee["allocated_capacity_percentage"] == 0
        and employee["available_capacity_percentage"] == 100
        for employee in data["employees"]
    )
    assert all("email" not in employee for employee in data["employees"])

    context_response = assistant_client.get(
        f"{API_PREFIX}/inquiries/{context_id}"
    )
    assert context_response.status_code == 200
    context_data = context_response.json()["context_data"]
    assert context_data["current_step"] == "results"
    assert context_data["last_result_summary"]["capability"] == (
        "workforce_capacity_analysis"
    )
    assert context_data["last_result_summary"]["reporting_date"] == (
        data["reporting_date"]
    )
    assert context_data["last_result_summary"]["active_employee_count"] == 2
    assert context_data["last_result_summary"]["result_count"] == 2
    assert context_data["last_result_summary"]["has_more_results"] is False


def test_workforce_capacity_analysis_requires_unified_question(assistant_client):
    context_id = start_guest_inquiry(assistant_client)

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/workforce-capacity-analysis"
    )

    assert response.status_code == 409


def test_workforce_capacity_analysis_enforces_guest_context_ownership(
    assistant_engine,
):
    original_overrides = app.dependency_overrides.copy()

    def override_get_db():
        with Session(assistant_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as owner_client:
            context_id = prepare_workforce_capacity_analysis_context(
                owner_client,
                assistant_engine,
            )
            with TestClient(app) as other_client:
                response = other_client.post(
                    f"{API_PREFIX}/inquiries/{context_id}/workforce-capacity-analysis"
                )
                assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


def test_workforce_capacity_analysis_rejects_reset_inquiry(assistant_client):
    context_id = start_guest_inquiry(assistant_client)
    reset_response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/reset"
    )
    assert reset_response.status_code == 200

    response = assistant_client.post(
        f"{API_PREFIX}/inquiries/{context_id}/workforce-capacity-analysis"
    )

    assert response.status_code == 410
