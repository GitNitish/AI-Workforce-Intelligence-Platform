from datetime import datetime, timezone

from sqlalchemy import delete, select
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
from app.models.entities import (
    Employee,
    Recommendation,
    StaffingRequirement,
)


def _get_employee_proficiency(
    employee: Employee,
    required_skill_ids: set[str],
) -> str | None:
    """
    Return the lowest proficiency among the employee's
    matched required skills.

    This provides a conservative proficiency score when
    multiple required skills are present.
    """

    matched_proficiencies: list[tuple[int, str]] = []

    for employee_skill in employee.skills:
        if employee_skill.skill_id not in required_skill_ids:
            continue

        proficiency = (
            employee_skill.proficiency_level or ""
        ).strip().lower()

        level = PROFICIENCY_LEVELS.get(
            proficiency,
            0,
        )

        if level > 0:
            matched_proficiencies.append(
                (level, proficiency)
            )

    if not matched_proficiencies:
        return None

    matched_proficiencies.sort(
        key=lambda item: item[0]
    )

    return matched_proficiencies[0][1]


def _get_matched_skill_ids(
    employee: Employee,
    required_skill_ids: set[str],
) -> set[str]:
    return {
        employee_skill.skill_id
        for employee_skill in employee.skills
        if employee_skill.skill_id in required_skill_ids
    }


def _get_matched_skill_names(
    employee: Employee,
    required_skill_ids: set[str],
) -> list[str]:
    matched_names: list[str] = []

    for employee_skill in employee.skills:
        if employee_skill.skill_id not in required_skill_ids:
            continue

        if employee_skill.skill is not None:
            matched_names.append(
                employee_skill.skill.skill_name
            )

    return sorted(set(matched_names))


def _get_matched_certification_count(
    employee: Employee,
    required_certification_names: set[str],
) -> int:
    if not required_certification_names:
        return 0

    matched_certifications: set[str] = set()

    for certification in employee.certifications:
        if certification.status != "active":
            continue

        certification_name = (
            certification.certification_name
            or ""
        ).strip().lower()

        if certification_name in required_certification_names:
            matched_certifications.add(
                certification_name
            )

    return len(matched_certifications)


def _build_recommendation_reason(
    matched_skill_count: int,
    required_skill_count: int,
    employee_experience: float,
    required_experience: float,
    matched_certification_count: int,
    required_certification_count: int,
    availability_status: str | None,
    utilization_percentage: float,
) -> str:
    reasons: list[str] = []

    if required_skill_count == 0:
        reasons.append("No specific skill requirement")
    elif matched_skill_count == required_skill_count:
        reasons.append("All required skills matched")
    else:
        reasons.append(
            f"{matched_skill_count} of "
            f"{required_skill_count} required skills matched"
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
        and availability_status.strip().lower()
        == "available"
    ):
        reasons.append("Currently available")
    else:
        reasons.append("Availability requirement not met")

    remaining_capacity = max(
        0.0,
        100.0 - utilization_percentage,
    )

    reasons.append(
        f"{remaining_capacity:g}% remaining capacity"
    )

    return "; ".join(reasons)


def generate_recommendations(
    db: Session,
    staffing_requirement_id: str,
) -> list[Recommendation]:
    """
    Generate and persist ranked recommendations for a
    staffing requirement.

    Only employees that pass mandatory eligibility checks
    are scored and ranked.

    Capacity and utilization are calculated from actual
    active allocations overlapping the staffing requirement
    period rather than relying on the employee's stored
    utilization_percentage field.

    Existing recommendations for the same staffing
    requirement are replaced so repeated generation does
    not create duplicate recommendation records.
    """

    requirement = db.get(
        StaffingRequirement,
        staffing_requirement_id,
    )

    if requirement is None:
        raise ValueError(
            "Staffing requirement not found"
        )

    # --------------------------------------------------------
    # Remove previous recommendations
    # --------------------------------------------------------

    db.execute(
        delete(Recommendation).where(
            Recommendation.staffing_requirement_id
            == staffing_requirement_id
        )
    )

    db.flush()

    # --------------------------------------------------------
    # Load employees deterministically
    # --------------------------------------------------------

    employees = list(
        db.scalars(
            select(Employee).order_by(
                Employee.name.asc()
            )
        ).all()
    )

    # --------------------------------------------------------
    # Build requirement criteria
    # --------------------------------------------------------

    required_skill_ids = {
        required_skill.skill_id
        for required_skill in requirement.required_skills
    }

    required_certification_names = {
        (
            required_certification.certification_name
            or ""
        ).strip().lower()
        for required_certification
        in requirement.required_certifications
    }

    # --------------------------------------------------------
    # Evaluate and score eligible employees
    # --------------------------------------------------------

    ranked_candidates: list[
        tuple[Employee, float, list[str], str]
    ] = []

    for employee in employees:

        eligibility_result = check_employee_eligibility(
            employee,
            requirement,
        )

        # Mandatory eligibility failures are excluded
        # before recommendation scoring.
        if not eligibility_result.eligible:
            continue

        # ----------------------------------------------------
        # Calculate authoritative utilization from allocations
        # ----------------------------------------------------

        utilization_percentage = (
            _calculate_requirement_period_utilization(
                employee,
                requirement,
            )
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

        matched_certification_count = (
            _get_matched_certification_count(
                employee,
                required_certification_names,
            )
        )

        # ----------------------------------------------------
        # Individual scoring components
        # ----------------------------------------------------

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

        utilization_score = calculate_utilization_score(
            utilization_percentage,
        )

        # ----------------------------------------------------
        # Weighted total score
        # ----------------------------------------------------

        total_score = calculate_total_score(
            skill_score,
            proficiency_score,
            experience_score,
            certification_score,
            availability_score,
            utilization_score,
        )

        # ----------------------------------------------------
        # Explainable recommendation reason
        # ----------------------------------------------------

        reason = _build_recommendation_reason(
            len(matched_skill_ids),
            len(required_skill_ids),
            employee.experience_years,
            requirement.required_experience,
            matched_certification_count,
            len(required_certification_names),
            employee.availability_status,
            utilization_percentage,
        )

        ranked_candidates.append(
            (
                employee,
                total_score,
                matched_skill_names,
                reason,
            )
        )

    # --------------------------------------------------------
    # Deterministic ranking
    # --------------------------------------------------------

    ranked_candidates.sort(
        key=lambda candidate: (
            -candidate[1],
            candidate[0].name.lower(),
            candidate[0].employee_id,
        )
    )

    generated_at = datetime.now(timezone.utc)

    recommendations: list[Recommendation] = []

    # --------------------------------------------------------
    # Persist current recommendation set
    # --------------------------------------------------------

    for rank, (
        employee,
        score,
        matched_skill_names,
        reason,
    ) in enumerate(
        ranked_candidates,
        start=1,
    ):
        recommendation = Recommendation(
            staffing_requirement_id=(
                requirement.staffing_requirement_id
            ),
            employee_id=employee.employee_id,
            score=score,
            rank=rank,
            eligibility_status="eligible",
            recommendation_reason=(
                f"Matched skills: "
                f"{', '.join(matched_skill_names)}. "
                f"{reason}"
            ),
            generated_at=generated_at,
            generated_by=None,
        )

        db.add(recommendation)
        recommendations.append(recommendation)

    db.commit()

    for recommendation in recommendations:
        db.refresh(recommendation)

    return recommendations