from app.ai.scoring_config import (
    AVAILABILITY_WEIGHT,
    CERTIFICATION_WEIGHT,
    EXPERIENCE_WEIGHT,
    PROFICIENCY_WEIGHT,
    SKILL_MATCH_WEIGHT,
    UTILIZATION_WEIGHT,
)


PROFICIENCY_LEVELS = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4,
}


def calculate_skill_match_score(
    matched_skills: int,
    required_skills: int,
) -> float:
    if required_skills == 0:
        return float(SKILL_MATCH_WEIGHT)

    if matched_skills <= 0:
        return 0.0

    matched_skills = min(
        matched_skills,
        required_skills,
    )

    return (
        matched_skills
        / required_skills
        * SKILL_MATCH_WEIGHT
    )


def calculate_proficiency_score(
    employee_proficiency: str | None,
    required_proficiency: str | None,
) -> float:
    if not required_proficiency:
        return float(PROFICIENCY_WEIGHT)

    employee_level = PROFICIENCY_LEVELS.get(
        (employee_proficiency or "").strip().lower(),
        0,
    )

    required_level = PROFICIENCY_LEVELS.get(
        required_proficiency.strip().lower(),
        0,
    )

    if required_level == 0:
        return 0.0

    if employee_level == 0:
        return 0.0

    return min(
        employee_level / required_level
        * PROFICIENCY_WEIGHT,
        float(PROFICIENCY_WEIGHT),
    )


def calculate_experience_score(
    employee_experience: float,
    required_experience: float,
) -> float:
    if required_experience <= 0:
        return float(EXPERIENCE_WEIGHT)

    if employee_experience <= 0:
        return 0.0

    return min(
        employee_experience
        / required_experience
        * EXPERIENCE_WEIGHT,
        float(EXPERIENCE_WEIGHT),
    )


def calculate_certification_score(
    required_certifications: int,
    matched_certifications: int,
) -> float:
    if required_certifications == 0:
        return float(CERTIFICATION_WEIGHT)

    if matched_certifications < required_certifications:
        return 0.0

    return float(CERTIFICATION_WEIGHT)


def calculate_availability_score(
    availability_status: str | None,
) -> float:
    if (
        availability_status
        and availability_status.strip().lower()
        == "available"
    ):
        return float(AVAILABILITY_WEIGHT)

    return 0.0


def calculate_utilization_score(
    utilization_percentage: float,
) -> float:
    utilization = min(
        max(utilization_percentage, 0.0),
        100.0,
    )

    return (
        (100.0 - utilization)
        / 100.0
        * UTILIZATION_WEIGHT
    )


def calculate_total_score(
    skill_match_score: float,
    proficiency_score: float,
    experience_score: float,
    certification_score: float,
    availability_score: float,
    utilization_score: float,
) -> float:
    total = (
        skill_match_score
        + proficiency_score
        + experience_score
        + certification_score
        + availability_score
        + utilization_score
    )

    return round(
        min(max(total, 0.0), 100.0),
        2,
    )