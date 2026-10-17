"""Tests for read-only assistant recommendation evaluation."""

from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database.connection import Base
from app.models.entities import (
    Employee,
    EmployeeSkill,
    Recommendation,
    Skill,
    StaffingRequirement,
    StaffingRequirementSkill,
)
from app.services.assistant_capability_service import (
    AssistantEntityNotFoundError,
    InvalidAssistantFilterError,
)
from app.services.assistant_recommendation_service import (
    evaluate_assistant_recommendations,
)


@pytest.fixture
def db():
    """Provide an isolated in-memory database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture
def recommendation_data(db):
    """Create a requirement and candidates for recommendation tests."""
    today = date.today()

    skill = Skill(
        skill_id="assistant-rec-skill-001",
        skill_name="Python",
        description="Python programming",
    )

    requirement = StaffingRequirement(
        staffing_requirement_id="assistant-rec-requirement-001",
        project_id="assistant-rec-project-001",
        role_name="Data Analyst",
        required_quantity=1,
        required_experience=3,
        required_proficiency="intermediate",
        start_date=today,
        end_date=today + timedelta(days=90),
        priority="high",
        status="open",
    )

    alice = Employee(
        employee_id="assistant-rec-employee-001",
        employee_code="REC001",
        name="Alice Sharma",
        email="alice.rec@example.com",
        designation="Data Analyst",
        department="Analytics",
        experience_years=5,
        availability_status="available",
        location="Delhi",
        status="active",
        utilization_percentage=99,
    )

    bob = Employee(
        employee_id="assistant-rec-employee-002",
        employee_code="REC002",
        name="Bob Kumar",
        email="bob.rec@example.com",
        designation="Data Analyst",
        department="Analytics",
        experience_years=4,
        availability_status="available",
        location="Delhi",
        status="active",
        utilization_percentage=0,
    )

    charlie = Employee(
        employee_id="assistant-rec-employee-003",
        employee_code="REC003",
        name="Charlie Singh",
        email="charlie.rec@example.com",
        designation="Data Analyst",
        department="Analytics",
        experience_years=8,
        availability_status="unavailable",
        location="Delhi",
        status="active",
        utilization_percentage=0,
    )

    inactive = Employee(
        employee_id="assistant-rec-employee-004",
        employee_code="REC004",
        name="Inactive Employee",
        email="inactive.rec@example.com",
        designation="Data Analyst",
        department="Analytics",
        experience_years=10,
        availability_status="available",
        location="Delhi",
        status="inactive",
        utilization_percentage=0,
    )

    db.add_all([skill, requirement, alice, bob, charlie, inactive])
    db.flush()

    db.add(
        StaffingRequirementSkill(
            staffing_requirement_id=requirement.staffing_requirement_id,
            skill_id=skill.skill_id,
        )
    )

    db.add_all(
        [
            EmployeeSkill(
                employee_id=alice.employee_id,
                skill_id=skill.skill_id,
                proficiency_level="advanced",
                years_experience=4,
            ),
            EmployeeSkill(
                employee_id=bob.employee_id,
                skill_id=skill.skill_id,
                proficiency_level="intermediate",
                years_experience=3,
            ),
            EmployeeSkill(
                employee_id=charlie.employee_id,
                skill_id=skill.skill_id,
                proficiency_level="expert",
                years_experience=5,
            ),
            EmployeeSkill(
                employee_id=inactive.employee_id,
                skill_id=skill.skill_id,
                proficiency_level="expert",
                years_experience=5,
            ),
        ]
    )

    db.commit()

    return {
        "requirement": requirement,
        "employees": [alice, bob, charlie, inactive],
        "skill": skill,
    }


def test_evaluation_returns_only_eligible_candidates(
    db,
    recommendation_data,
):
    result = evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )

    returned_ids = [
        candidate["employee_id"]
        for candidate in result["candidates"]
    ]

    assert result["capability"] == "read_only_recommendation_evaluation"
    assert returned_ids == [
        "assistant-rec-employee-001",
        "assistant-rec-employee-002",
    ]
    assert "assistant-rec-employee-003" not in returned_ids
    assert "assistant-rec-employee-004" not in returned_ids


def test_evaluation_returns_score_breakdown_and_explanation(
    db,
    recommendation_data,
):
    result = evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )

    candidate = result["candidates"][0]

    assert candidate["rank"] == 1
    assert 0 <= candidate["score"] <= 100
    assert set(candidate["score_breakdown"]) == {
        "skill_match",
        "proficiency",
        "experience",
        "certification",
        "availability",
        "utilization",
    }
    assert candidate["matched_skills"] == ["Python"]
    assert "All required skills matched" in (
        candidate["recommendation_reason"]
    )
    assert candidate["utilization_percentage"] == 0
    assert candidate["remaining_capacity_percentage"] == 100


def test_evaluation_uses_allocation_based_utilization_not_stored_value(
    db,
    recommendation_data,
):
    result = evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )

    alice = next(
        candidate
        for candidate in result["candidates"]
        if candidate["employee_id"] == "assistant-rec-employee-001"
    )

    # Alice's stored utilization is 99%, but she has no active
    # allocations overlapping the requirement period.
    assert alice["utilization_percentage"] == 0
    assert alice["remaining_capacity_percentage"] == 100


def test_evaluation_ranking_is_deterministic(
    db,
    recommendation_data,
):
    first = evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )
    second = evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )

    first_results = [
        (
            candidate["employee_id"],
            candidate["rank"],
            candidate["score"],
        )
        for candidate in first["candidates"]
    ]
    second_results = [
        (
            candidate["employee_id"],
            candidate["rank"],
            candidate["score"],
        )
        for candidate in second["candidates"]
    ]

    assert first_results == second_results


def test_evaluation_applies_result_limit(
    db,
    recommendation_data,
):
    result = evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
        limit=1,
    )

    assert result["result_count"] == 1
    assert result["eligible_candidate_count"] == 2
    assert result["limit"] == 1
    assert result["has_more_results"] is True


@pytest.mark.parametrize(
    ("requirement_id", "limit", "message"),
    [
        ("", 10, "staffing_requirement_id"),
        ("assistant-rec-requirement-001", 0, "limit"),
        ("assistant-rec-requirement-001", 26, "limit"),
        ("assistant-rec-requirement-001", True, "limit"),
        ("assistant-rec-requirement-001", 1.5, "limit"),
    ],
)
def test_evaluation_rejects_invalid_arguments(
    db,
    recommendation_data,
    requirement_id,
    limit,
    message,
):
    with pytest.raises(InvalidAssistantFilterError, match=message):
        evaluate_assistant_recommendations(
            db,
            requirement_id,
            limit=limit,
        )


def test_evaluation_rejects_unknown_requirement(db):
    with pytest.raises(
        AssistantEntityNotFoundError,
        match="Staffing requirement was not found",
    ):
        evaluate_assistant_recommendations(
            db,
            "assistant-rec-requirement-does-not-exist",
        )


def test_evaluation_does_not_create_recommendation_records(
    db,
    recommendation_data,
):
    before_count = db.scalar(
        select(func.count()).select_from(Recommendation)
    )

    evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )

    db.expire_all()

    after_count = db.scalar(
        select(func.count()).select_from(Recommendation)
    )

    assert after_count == before_count


def test_evaluation_does_not_delete_existing_recommendations(
    db,
    recommendation_data,
):
    existing = Recommendation(
        recommendation_id="assistant-rec-existing-001",
        staffing_requirement_id="assistant-rec-requirement-001",
        employee_id="assistant-rec-employee-001",
        score=42.5,
        rank=1,
        eligibility_status="eligible",
        recommendation_reason="Existing saved recommendation",
        generated_by=None,
    )
    db.add(existing)
    db.commit()

    before = (
        existing.recommendation_id,
        existing.employee_id,
        existing.score,
        existing.rank,
        existing.recommendation_reason,
    )

    evaluate_assistant_recommendations(
        db,
        "assistant-rec-requirement-001",
    )

    db.expire_all()

    after = db.get(
        Recommendation,
        "assistant-rec-existing-001",
    )

    assert after is not None
    assert (
        after.recommendation_id,
        after.employee_id,
        after.score,
        after.rank,
        after.recommendation_reason,
    ) == before
