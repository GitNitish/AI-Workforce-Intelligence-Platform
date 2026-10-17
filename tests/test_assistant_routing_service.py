"""Tests for deterministic WorkForceIQ assistant routing."""

import pytest

from app.services.assistant_routing_service import (
    AssistantRoute,
    DisabledSelectionError,
    UnknownSelectionError,
    get_categories,
    get_category,
    get_category_questions,
    route_selection,
)


def test_get_categories_returns_predefined_categories():
    categories = get_categories()

    category_ids = {category.option_id for category in categories}

    assert category_ids == {
        "candidate_discovery",
        "recommendations",
        "workforce_capacity_analysis",
        "staffing_demand_analysis",
        "demand_forecasting",
    }


def test_workforce_capacity_analysis_category_is_available():
    category = get_category("workforce_capacity_analysis")

    assert category.enabled is True
    assert category.label == "Workforce Capacity Analysis"
    assert "utilization" in category.description.lower()
    assert "allocated capacity" in category.description.lower()
    assert "available capacity" in category.description.lower()


def test_workforce_capacity_analysis_question_is_enabled():
    questions = get_category_questions("workforce_capacity_analysis")

    assert len(questions) == 1
    assert questions[0].option_id == "view_workforce_capacity_analysis"
    assert questions[0].label == "View workforce capacity analysis"
    assert questions[0].enabled is True


def test_selecting_workforce_capacity_category_returns_question_step():
    route = route_selection("workforce_capacity_analysis")

    assert route.current_step == "question"
    assert len(route.options) == 1
    assert route.options[0].option_id == "view_workforce_capacity_analysis"


def test_selecting_workforce_capacity_question_returns_capability_step():
    route = route_selection(
        "view_workforce_capacity_analysis",
        current_category="workforce_capacity_analysis",
    )

    assert route.current_step == "capability"
    assert route.options == ()
    assert "utilization" in route.message.lower()
    assert "allocated capacity" in route.message.lower()
    assert "available capacity" in route.message.lower()
    assert "read-only" in route.message.lower()
    assert "does not change employee or allocation records" in route.message.lower()


@pytest.mark.parametrize("legacy_category", ["utilization", "capacity"])
def test_legacy_categories_resolve_to_workforce_capacity_analysis(
    legacy_category,
):
    category = get_category(legacy_category)
    questions = get_category_questions(legacy_category)
    route = route_selection(legacy_category)

    assert category.option_id == "workforce_capacity_analysis"
    assert len(questions) == 1
    assert questions[0].option_id == "view_workforce_capacity_analysis"
    assert route.current_step == "question"
    assert route.options == questions


@pytest.mark.parametrize(
    ("legacy_category", "legacy_question"),
    [
        ("utilization", "view_current_utilization"),
        ("capacity", "view_current_capacity"),
    ],
)
def test_legacy_questions_resolve_to_combined_capability(
    legacy_category,
    legacy_question,
):
    route = route_selection(
        legacy_question,
        current_category=legacy_category,
    )

    assert route.current_step == "capability"
    assert route.options == ()
    assert "utilization" in route.message.lower()
    assert "allocated capacity" in route.message.lower()
    assert "available capacity" in route.message.lower()
    assert "read-only" in route.message.lower()



def test_staffing_demand_analysis_category_is_available():
    category = get_category("staffing_demand_analysis")

    assert category.enabled is True
    assert category.label == "Staffing Demand Analysis"
    assert "staffing requirements" in category.description.lower()
    assert "requested headcount" in category.description.lower()


def test_staffing_demand_analysis_question_is_enabled():
    questions = get_category_questions("staffing_demand_analysis")

    assert len(questions) == 1
    assert questions[0].option_id == "view_staffing_demand_analysis"
    assert questions[0].enabled is True


def test_selecting_staffing_demand_category_returns_question_step():
    route = route_selection("staffing_demand_analysis")

    assert route.current_step == "question"
    assert len(route.options) == 1
    assert route.options[0].option_id == "view_staffing_demand_analysis"


def test_selecting_staffing_demand_question_returns_capability_step():
    route = route_selection(
        "view_staffing_demand_analysis",
        current_category="staffing_demand_analysis",
    )

    assert route.current_step == "capability"
    assert route.options == ()
    assert "staffing requirements" in route.message.lower()
    assert "requested headcount" in route.message.lower()
    assert "not a verified vacancy count" in route.message.lower()
    assert "forecast" in route.message.lower()
    assert "read-only" in route.message.lower()


def test_demand_forecasting_category_is_disabled():
    with pytest.raises(DisabledSelectionError):
        get_category("demand_forecasting")



def test_demand_forecasting_has_no_enabled_questions():
    with pytest.raises(DisabledSelectionError):
        get_category_questions("demand_forecasting")

    with pytest.raises(DisabledSelectionError):
        route_selection("demand_forecasting")

def test_unknown_category_is_rejected():
    with pytest.raises(UnknownSelectionError):
        get_category("unknown_category")


def test_candidate_discovery_category_is_available():
    category = get_category("candidate_discovery")

    assert category.enabled is True
    assert category.label == "Candidate discovery"


def test_candidate_discovery_questions_are_predefined():
    questions = get_category_questions("candidate_discovery")

    question_ids = {question.option_id for question in questions}

    assert question_ids == {
        "find_candidates_for_requirement",
        "search_employees",
    }


def test_selecting_category_returns_question_step():
    route = route_selection("candidate_discovery")

    assert isinstance(route, AssistantRoute)
    assert route.current_step == "question"
    assert route.options
    assert all(option.enabled for option in route.options)


def test_selecting_unknown_category_is_rejected():
    with pytest.raises(UnknownSelectionError):
        route_selection("not_a_real_category")


def test_selecting_question_without_category_is_rejected():
    with pytest.raises(UnknownSelectionError):
        route_selection("search_employees")


def test_recommendation_questions_are_enabled_and_consolidated():
    questions = get_category_questions("recommendations")

    assert len(questions) == 1
    assert questions[0].option_id == "view_recommendations"
    assert questions[0].label == "Staffing Recommendations & Score Analysis"
    assert questions[0].enabled is True


@pytest.mark.parametrize(
    "question_id",
    [
        "view_recommendations",
        "understand_recommendation_scores",
    ],
)
def test_selecting_recommendation_question_returns_capability_step(
    question_id,
):
    route = route_selection(
        question_id,
        current_category="recommendations",
    )

    assert route.current_step == "capability"
    assert route.options == ()
    assert "read-only" in route.message.lower()
    assert "does not save recommendations" in route.message.lower()


def test_selecting_candidate_question_returns_capability_step():
    route = route_selection(
        "search_employees",
        current_category="candidate_discovery",
    )

    assert route.current_step == "capability"
    assert route.options == ()
    assert "must be integrated and validated" in route.message


def test_question_from_another_category_is_rejected():
    with pytest.raises(UnknownSelectionError):
        route_selection(
            "search_employees",
            current_category="workforce_capacity_analysis",
        )
