
"""Read-only candidate evaluation for the guided WorkForceIQ assistant."""

from typing import Any

from sqlalchemy.orm import Session

from app.ai.eligibility import (
    _calculate_requirement_period_utilization,
    check_employee_eligibility,
)
from app.ai.scoring import (
    PROFICIENCY_LEVELS,
    calculate_availability_score,
    calculate_certification_score,
    calculate_experience_score,
    calculate_proficiency_score,
    calculate_skill_match_score,
    calculate_total_score,
    calculate_utilization_score,
)
from app.models.entities import Employee, StaffingRequirement
from app.services.assistant_capability_service import (
    AssistantEntityNotFoundError,
    InvalidAssistantFilterError,
)
from app.services.candidate_matching_service import (
    discover_candidate_employees,
)
from app.services.staffing_service import get_staffing_requirement


MAX_RECOMMENDATION_RESULTS = 25


def _get_employee_proficiency(
    employee: Employee,
    required_skill_ids: set[str],
) -> str | None:
    """Return the lowest recognized proficiency among matched skills."""
    matched_proficiencies: list[tuple[int, str]] = []

    for employee_skill in employee.skills:
        if employee_skill.skill_id not in required_skill_ids:
            continue

        proficiency = (
            employee_skill.proficiency_level or ""
        ).strip().lower()

        level = PROFICIENCY_LEVELS.get(proficiency, 0)

        if level > 0:
            matched_proficiencies.append((level, proficiency))

    if not matched_proficiencies:
        return None

    return min(matched_proficiencies, key=lambda item: item[0])[1]


def _get_matched_skill_ids(
    employee: Employee,
    required_skill_ids: set[str],
) -> set[str]:
    """Return required skill IDs held by the employee."""
    return {
        employee_skill.skill_id
        for employee_skill in employee.skills
        if employee_skill.skill_id in required_skill_ids
    }


def _get_matched_skill_names(
    employee: Employee,
    required_skill_ids: set[str],
) -> list[str]:
    """Return sorted, unique names of matched required skills."""
    names = {
        employee_skill.skill.skill_name
        for employee_skill in employee.skills
        if (
            employee_skill.skill_id in required_skill_ids
            and employee_skill.skill is not None
        )
    }

    return sorted(names, key=str.lower)


def _get_matched_certification_count(
    employee: Employee,
    required_certification_names: set[str],
) -> int:
    """Count distinct active certifications matching the requirement."""
    if not required_certification_names:
        return 0

    matched_certifications: set[str] = set()

    for certification in employee.certifications:
        if (certification.status or "").strip().lower() != "active":
            continue

        certification_name = (
            certification.certification_name or ""
        ).strip().lower()

        if certification_name in required_certification_names:
            matched_certifications.add(certification_name)

    return len(matched_certifications)


def _build_recommendation_reason(
    *,
    matched_skill_count: int,
    required_skill_count: int,
    employee_experience: float,
    required_experience: float,
    matched_certification_count: int,
    required_certification_count: int,
    availability_status: str | None,
    utilization_percentage: float,
) -> str:
    """Build a concise, deterministic explanation for a candidate score."""
    reasons: list[str] = []

    if required_skill_count == 0:
        reasons.append("No specific skill requirement")
    elif matched_skill_count == required_skill_count:
        reasons.append("All required skills matched")
    else:
        reasons.append(
            f"{matched_skill_count} of {required_skill_count} "
            "required skills matched"
        )

    if required_experience <= 0:
        reasons.append("No minimum experience requirement")
    elif employee_experience >= required_experience:
        reasons.append("Experience requirement met")
    else:
        reasons.append("Experience below requirement")

    if required_certification_count == 0:
        reasons.append("No certification requirement")
    elif matched_certification_count == required_certification_count:
        reasons.append("Certification requirements met")
    else:
        reasons.append("Certification requirements incomplete")

    if (
        availability_status
        and availability_status.strip().lower() == "available"
    ):
        reasons.append("Currently available")
    else:
        reasons.append("Availability requirement not met")

    remaining_capacity = max(
        0.0,
        100.0 - utilization_percentage,
    )
    reasons.append(f"{remaining_capacity:g}% remaining capacity")

    return "; ".join(reasons)


def _evaluate_candidate(
    employee: Employee,
    requirement: StaffingRequirement,
    required_skill_ids: set[str],
    required_certification_names: set[str],
) -> dict[str, Any] | None:
    """Score one eligible candidate without persisting any records."""
    eligibility = check_employee_eligibility(employee, requirement)

    if not eligibility.eligible:
        return None

    utilization = _calculate_requirement_period_utilization(
        employee,
        requirement,
    )

    matched_skill_ids = _get_matched_skill_ids(
        employee,
        required_skill_ids,
    )
    matched_skill_names = _get_matched_skill_names(
        employee,
        required_skill_ids,
    )
    employee_proficiency = _get_employee_proficiency(
        employee,
        required_skill_ids,
    )
    matched_certification_count = _get_matched_certification_count(
        employee,
        required_certification_names,
    )

    skill_score = calculate_skill_match_score(
        len(matched_skill_ids),
        len(required_skill_ids),
    )
    proficiency_score = calculate_proficiency_score(
        employee_proficiency,
        requirement.required_proficiency,
    )
    experience_score = calculate_experience_score(
        employee.experience_years,
        requirement.required_experience,
    )
    certification_score = calculate_certification_score(
        len(required_certification_names),
        matched_certification_count,
    )
    availability_score = calculate_availability_score(
        employee.availability_status,
    )
    utilization_score = calculate_utilization_score(utilization)

    score_breakdown = {
        "skill_match": round(skill_score, 2),
        "proficiency": round(proficiency_score, 2),
        "experience": round(experience_score, 2),
        "certification": round(certification_score, 2),
        "availability": round(availability_score, 2),
        "utilization": round(utilization_score, 2),
    }

    total_score = calculate_total_score(
        skill_score,
        proficiency_score,
        experience_score,
        certification_score,
        availability_score,
        utilization_score,
    )

    reason = _build_recommendation_reason(
        matched_skill_count=len(matched_skill_ids),
        required_skill_count=len(required_skill_ids),
        employee_experience=employee.experience_years,
        required_experience=requirement.required_experience,
        matched_certification_count=matched_certification_count,
        required_certification_count=len(required_certification_names),
        availability_status=employee.availability_status,
        utilization_percentage=utilization,
    )

    return {
        "employee_id": employee.employee_id,
        "employee_code": employee.employee_code,
        "name": employee.name,
        "designation": employee.designation,
        "department": employee.department,
        "experience_years": employee.experience_years,
        "availability_status": employee.availability_status,
        "location": employee.location,
        "utilization_percentage": round(utilization, 2),
        "remaining_capacity_percentage": round(
            max(0.0, 100.0 - utilization),
            2,
        ),
        "score": total_score,
        "score_breakdown": score_breakdown,
        "matched_skills": matched_skill_names,
        "recommendation_reason": (
            f"Matched skills: {', '.join(matched_skill_names)}. "
            f"{reason}"
        ),
    }


def evaluate_assistant_recommendations(
    db: Session,
    staffing_requirement_id: str,
    *,
    limit: int = MAX_RECOMMENDATION_RESULTS,
) -> dict[str, Any]:
    """Evaluate and rank candidates without writing to the database.

    This function intentionally does not call the persistence-based
    generate_recommendations() service. It does not add, delete, update,
    flush, commit, or refresh ORM records.
    """
    if not isinstance(staffing_requirement_id, str):
        raise InvalidAssistantFilterError(
            "staffing_requirement_id must be text."
        )

    normalized_id = staffing_requirement_id.strip()

    if not normalized_id:
        raise InvalidAssistantFilterError(
            "staffing_requirement_id is required."
        )

    if len(normalized_id) > 100:
        raise InvalidAssistantFilterError(
            "staffing_requirement_id cannot exceed 100 characters."
        )

    if isinstance(limit, bool) or not isinstance(limit, int):
        raise InvalidAssistantFilterError(
            "limit must be an integer."
        )

    if not 1 <= limit <= MAX_RECOMMENDATION_RESULTS:
        raise InvalidAssistantFilterError(
            f"limit must be between 1 and "
            f"{MAX_RECOMMENDATION_RESULTS}."
        )

    requirement = get_staffing_requirement(db, normalized_id)

    if requirement is None:
        raise AssistantEntityNotFoundError(
            "Staffing requirement was not found."
        )

    required_skill_ids = {
        required_skill.skill_id
        for required_skill in requirement.required_skills
    }
    required_certification_names = {
        (certification.certification_name or "").strip().lower()
        for certification in requirement.required_certifications
        if (certification.certification_name or "").strip()
    }

    discovered_employees = discover_candidate_employees(
        db,
        requirement,
    )

    ranked_candidates: list[dict[str, Any]] = []

    for employee in discovered_employees:
        result = _evaluate_candidate(
            employee,
            requirement,
            required_skill_ids,
            required_certification_names,
        )

        if result is not None:
            ranked_candidates.append(result)

    ranked_candidates.sort(
        key=lambda candidate: (
            -candidate["score"],
            candidate["name"].lower(),
            candidate["employee_id"],
        )
    )

    for rank, candidate in enumerate(ranked_candidates, start=1):
        candidate["rank"] = rank

    bounded_candidates = ranked_candidates[:limit]

    return {
        "capability": "read_only_recommendation_evaluation",
        "staffing_requirement": {
            "staffing_requirement_id": requirement.staffing_requirement_id,
            "project_id": requirement.project_id,
            "role_name": requirement.role_name,
            "required_quantity": requirement.required_quantity,
            "required_experience": requirement.required_experience,
            "required_proficiency": requirement.required_proficiency,
            "status": requirement.status,
        },
        "result_count": len(bounded_candidates),
        "eligible_candidate_count": len(ranked_candidates),
        "limit": limit,
        "has_more_results": len(ranked_candidates) > limit,
        "candidates": bounded_candidates,
        "notice": (
            "These candidates passed the current deterministic eligibility "
            "checks and are ranked using the existing scoring model. "
            "Scores support human review and are not an autonomous staffing "
            "decision. Results were evaluated without saving recommendations."
        ),
    }
