import pytest

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
from app.ai.scoring_config import (
    AVAILABILITY_WEIGHT,
    CERTIFICATION_WEIGHT,
    EXPERIENCE_WEIGHT,
    PROFICIENCY_WEIGHT,
    SKILL_MATCH_WEIGHT,
    UTILIZATION_WEIGHT,
)


def test_skill_match_full_score_when_all_skills_match():
    result = calculate_skill_match_score(3, 3)

    assert result == SKILL_MATCH_WEIGHT


def test_skill_match_partial_score():
    result = calculate_skill_match_score(2, 4)

    assert result == pytest.approx(
        SKILL_MATCH_WEIGHT * 0.5
    )


def test_skill_match_zero_when_no_skills_match():
    result = calculate_skill_match_score(0, 3)

    assert result == 0.0


def test_skill_match_caps_matched_skills_at_required_count():
    result = calculate_skill_match_score(10, 3)

    assert result == SKILL_MATCH_WEIGHT


def test_skill_match_full_weight_when_no_skills_required():
    result = calculate_skill_match_score(0, 0)

    assert result == SKILL_MATCH_WEIGHT


def test_proficiency_full_score_when_employee_meets_requirement():
    result = calculate_proficiency_score(
        "expert",
        "advanced",
    )

    assert result == PROFICIENCY_WEIGHT


def test_proficiency_partial_score():
    result = calculate_proficiency_score(
        "intermediate",
        "expert",
    )

    assert result == pytest.approx(
        PROFICIENCY_WEIGHT * 0.5
    )


def test_proficiency_returns_zero_for_unknown_employee_level():
    result = calculate_proficiency_score(
        "unknown",
        "expert",
    )

    assert result == 0.0


def test_proficiency_returns_zero_for_unknown_required_level():
    result = calculate_proficiency_score(
        "expert",
        "unknown",
    )

    assert result == 0.0


def test_proficiency_full_weight_when_requirement_is_missing():
    result = calculate_proficiency_score(
        "beginner",
        None,
    )

    assert result == PROFICIENCY_WEIGHT


def test_experience_full_score_when_requirement_is_met():
    result = calculate_experience_score(
        5.0,
        3.0,
    )

    assert result == EXPERIENCE_WEIGHT


def test_experience_partial_score():
    result = calculate_experience_score(
        2.0,
        4.0,
    )

    assert result == pytest.approx(
        EXPERIENCE_WEIGHT * 0.5
    )


def test_experience_zero_when_employee_has_no_experience():
    result = calculate_experience_score(
        0.0,
        3.0,
    )

    assert result == 0.0


def test_experience_full_weight_when_requirement_is_zero():
    result = calculate_experience_score(
        0.0,
        0.0,
    )

    assert result == EXPERIENCE_WEIGHT


def test_certification_full_score_when_all_required_certifications_match():
    result = calculate_certification_score(
        2,
        2,
    )

    assert result == CERTIFICATION_WEIGHT


def test_certification_zero_when_requirements_are_incomplete():
    result = calculate_certification_score(
        2,
        1,
    )

    assert result == 0.0


def test_certification_full_weight_when_no_certification_is_required():
    result = calculate_certification_score(
        0,
        0,
    )

    assert result == CERTIFICATION_WEIGHT


def test_availability_full_score_for_available_employee():
    result = calculate_availability_score("available")

    assert result == AVAILABILITY_WEIGHT


def test_availability_is_case_insensitive_and_trims_whitespace():
    result = calculate_availability_score("  AVAILABLE  ")

    assert result == AVAILABILITY_WEIGHT


def test_availability_zero_for_unavailable_employee():
    result = calculate_availability_score("unavailable")

    assert result == 0.0


def test_availability_zero_when_status_is_missing():
    result = calculate_availability_score(None)

    assert result == 0.0


def test_utilization_score_is_high_when_utilization_is_low():
    result = calculate_utilization_score(20.0)

    assert result == pytest.approx(
        UTILIZATION_WEIGHT * 0.8
    )


def test_utilization_score_is_zero_at_full_utilization():
    result = calculate_utilization_score(100.0)

    assert result == 0.0


def test_utilization_score_caps_utilization_above_100():
    result = calculate_utilization_score(150.0)

    assert result == 0.0


def test_utilization_score_clamps_negative_utilization():
    result = calculate_utilization_score(-20.0)

    assert result == UTILIZATION_WEIGHT


def test_total_score_adds_all_components():
    result = calculate_total_score(
        10.0,
        20.0,
        15.0,
        10.0,
        20.0,
        15.0,
    )

    assert result == 90.0


def test_total_score_rounds_to_two_decimal_places():
    result = calculate_total_score(
        10.123,
        10.456,
        10.789,
        10.111,
        10.222,
        10.333,
    )

    assert result == 62.03


def test_total_score_cannot_exceed_100():
    result = calculate_total_score(
        100.0,
        100.0,
        100.0,
        100.0,
        100.0,
        100.0,
    )

    assert result == 100.0


def test_total_score_cannot_go_below_zero():
    result = calculate_total_score(
        -10.0,
        -10.0,
        -10.0,
        -10.0,
        -10.0,
        -10.0,
    )

    assert result == 0.0


def test_proficiency_levels_have_expected_order():
    assert PROFICIENCY_LEVELS["beginner"] < PROFICIENCY_LEVELS["intermediate"]
    assert PROFICIENCY_LEVELS["intermediate"] < PROFICIENCY_LEVELS["advanced"]
    assert PROFICIENCY_LEVELS["advanced"] < PROFICIENCY_LEVELS["expert"]