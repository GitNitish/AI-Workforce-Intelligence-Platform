from dataclasses import dataclass
from datetime import date

from app.ai.scoring import PROFICIENCY_LEVELS


@dataclass
class EligibilityResult:
    eligible: bool
    reasons: list[str]


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _meets_proficiency(
    employee_proficiency: str | None,
    required_proficiency: str | None,
) -> bool:
    if not required_proficiency:
        return True

    employee_level = PROFICIENCY_LEVELS.get(
        _normalize(employee_proficiency),
        0,
    )

    required_level = PROFICIENCY_LEVELS.get(
        _normalize(required_proficiency),
        0,
    )

    if required_level == 0:
        return False

    return employee_level >= required_level


def _has_required_skills(
    employee,
    required_skill_ids: set[str],
) -> tuple[bool, set[str]]:
    employee_skills = {
        employee_skill.skill_id: employee_skill
        for employee_skill in employee.skills
    }

    missing_skill_ids = (
        required_skill_ids - employee_skills.keys()
    )

    return (
        not missing_skill_ids,
        missing_skill_ids,
    )


def _has_valid_certifications(
    employee,
    required_certifications: set[str],
    today: date,
) -> tuple[bool, set[str]]:
    employee_certifications = {}

    for certification in employee.certifications:
        name = _normalize(
            certification.certification_name
        )

        employee_certifications.setdefault(
            name,
            [],
        ).append(certification)

    missing_or_invalid = set()

    for required_name in required_certifications:
        normalized_name = _normalize(required_name)

        matching_certifications = (
            employee_certifications.get(
                normalized_name,
                [],
            )
        )

        valid = False

        for certification in matching_certifications:
            status = _normalize(
                certification.status
            )

            expiry_date = certification.expiry_date

            if status != "active":
                continue

            if (
                expiry_date is not None
                and expiry_date < today
            ):
                continue

            valid = True
            break

        if not valid:
            missing_or_invalid.add(required_name)

    return (
        not missing_or_invalid,
        missing_or_invalid,
    )


def _calculate_requirement_period_utilization(
    employee,
    staffing_requirement,
) -> float:
    """
    Calculate utilization from active allocations that
    overlap the staffing requirement period.

    The employee's stored utilization_percentage is not
    used as the authoritative capacity value because
    allocation records are the source of truth for
    workforce capacity.
    """

    requirement_start = staffing_requirement.start_date
    requirement_end = staffing_requirement.end_date

    utilization = 0.0

    for allocation in employee.allocations:
        if _normalize(allocation.status) != "active":
            continue

        allocation_start = allocation.start_date
        allocation_end = allocation.end_date

        if allocation_start is None:
            continue

        if allocation_start > requirement_end:
            continue

        if (
            allocation_end is not None
            and allocation_end < requirement_start
        ):
            continue

        utilization += (
            allocation.allocation_percentage or 0.0
        )

    return min(utilization, 100.0)


def check_employee_eligibility(
    employee,
    staffing_requirement,
    today: date | None = None,
) -> EligibilityResult:
    evaluation_date = today or date.today()
    reasons: list[str] = []

    if _normalize(employee.status) != "active":
        reasons.append(
            "Employee status is not active."
        )

    required_skill_ids = {
        required_skill.skill_id
        for required_skill in staffing_requirement.required_skills
    }

    has_skills, missing_skill_ids = _has_required_skills(
        employee,
        required_skill_ids,
    )

    if not has_skills:
        reasons.append(
            "Employee is missing required skills: "
            + ", ".join(sorted(missing_skill_ids))
        )

    if staffing_requirement.required_proficiency:
        employee_skills = {
            employee_skill.skill_id: employee_skill
            for employee_skill in employee.skills
        }

        insufficient_skills = []

        for skill_id in required_skill_ids:
            employee_skill = employee_skills.get(skill_id)

            if employee_skill is None:
                continue

            if not _meets_proficiency(
                employee_skill.proficiency_level,
                staffing_requirement.required_proficiency,
            ):
                insufficient_skills.append(skill_id)

        if insufficient_skills:
            reasons.append(
                "Required proficiency is not met for skills: "
                + ", ".join(sorted(insufficient_skills))
            )

    if (
        employee.experience_years
        < staffing_requirement.required_experience
    ):
        reasons.append(
            "Employee experience is below the required experience."
        )

    required_certifications = {
        required_certification.certification_name
        for required_certification
        in staffing_requirement.required_certifications
    }

    has_certifications, invalid_certifications = (
        _has_valid_certifications(
            employee,
            required_certifications,
            evaluation_date,
        )
    )

    if not has_certifications:
        reasons.append(
            "Missing or invalid required certifications: "
            + ", ".join(
                sorted(invalid_certifications)
            )
        )

    if (
        _normalize(employee.availability_status)
        != "available"
    ):
        reasons.append(
            "Employee is not currently available."
        )

    # --------------------------------------------------------
    # Capacity is calculated from actual active allocations
    # overlapping the staffing requirement period.
    # --------------------------------------------------------

    utilization = _calculate_requirement_period_utilization(
        employee,
        staffing_requirement,
    )

    if utilization >= 100.0:
        reasons.append(
            "Employee has no remaining allocation capacity "
            "during the staffing requirement period."
        )

    return EligibilityResult(
        eligible=not reasons,
        reasons=reasons,
    )