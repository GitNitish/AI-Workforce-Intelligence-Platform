"""Deterministic routing for the guided WorkForceIQ assistant."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AssistantOptionDefinition:
    """A predefined option shown to the user."""

    option_id: str
    label: str
    description: str
    enabled: bool = True


@dataclass(frozen=True)
class AssistantRoute:
    """The next step selected by deterministic routing."""

    current_step: str
    message: str
    options: tuple[AssistantOptionDefinition, ...]


CATEGORIES: tuple[AssistantOptionDefinition, ...] = (
    AssistantOptionDefinition(
        option_id="candidate_discovery",
        label="Candidate discovery",
        description="Explore employees who may match a staffing requirement.",
    ),
    AssistantOptionDefinition(
        option_id="recommendations",
        label="Recommendations",
        description=(
            "Evaluate eligible candidates, compare scores, "
            "and understand recommendation explanations."
        ),
    ),
    AssistantOptionDefinition(
        option_id="workforce_capacity_analysis",
        label="Workforce Capacity Analysis",
        description=(
            "Review employee utilization, allocated capacity, and available "
            "capacity together for a reporting date."
        ),
    ),
    AssistantOptionDefinition(
        option_id="staffing_demand_analysis",
        label="Staffing Demand Analysis",
        description=(
            "Review recorded staffing requirements, requested headcount, "
            "and demand breakdowns by status, role, project, priority, and skill."
        ),
    ),
    AssistantOptionDefinition(
        option_id="demand_forecasting",
        label="Demand and forecasting",
        description="Demand forecasting is not available in this assistant version.",
        enabled=False,
    ),
)


WORKFORCE_CAPACITY_QUESTION = AssistantOptionDefinition(
    option_id="view_workforce_capacity_analysis",
    label="View workforce capacity analysis",
    description=(
        "Review utilization, allocated capacity, and available capacity "
        "together for active employees on a reporting date."
    ),
)

STAFFING_DEMAND_QUESTION = AssistantOptionDefinition(
    option_id="view_staffing_demand_analysis",
    label="View staffing demand analysis",
    description=(
        "Review recorded staffing requirements and requested headcount, "
        "with breakdowns by status, role, project, priority, and required skill. "
        "This does not forecast demand or verify unfilled positions."
    ),
)


CATEGORY_QUESTIONS: dict[str, tuple[AssistantOptionDefinition, ...]] = {
    "candidate_discovery": (
        AssistantOptionDefinition(
            option_id="find_candidates_for_requirement",
            label="Find candidates for a requirement",
            description=(
                "Select a staffing requirement to explore matching employees."
            ),
        ),
        AssistantOptionDefinition(
            option_id="search_employees",
            label="Explore employees",
            description="Explore available employee information.",
        ),
    ),
    "recommendations": (
        AssistantOptionDefinition(
            option_id="view_recommendations",
            label="Staffing Recommendations & Score Analysis",
            description=(
                "Evaluate eligible candidates for a staffing requirement, "
                "review their ranking and overall scores, inspect all six "
                "scoring components and matched skills, and understand "
                "recommendation explanations. Results are read-only."
            ),
        ),
    ),
    "workforce_capacity_analysis": (WORKFORCE_CAPACITY_QUESTION,),
    "staffing_demand_analysis": (STAFFING_DEMAND_QUESTION,),
    "demand_forecasting": (),
}

# Accept legacy category/question IDs for existing clients and stored contexts,
# but do not expose the old separate categories in the guided category list.
LEGACY_CATEGORY_ALIASES = {
    "utilization": "workforce_capacity_analysis",
    "capacity": "workforce_capacity_analysis",
}
LEGACY_QUESTION_ALIASES = {
    "view_current_utilization": "view_workforce_capacity_analysis",
    "view_current_capacity": "view_workforce_capacity_analysis",
}


class AssistantRoutingError(Exception):
    """Base exception for assistant routing errors."""


class UnknownSelectionError(AssistantRoutingError):
    """Raised when a submitted selection is not recognized."""


class DisabledSelectionError(AssistantRoutingError):
    """Raised when a recognized selection is not currently available."""


def _canonical_category_id(category_id: str) -> str:
    """Map legacy category identifiers to the current category identifier."""
    return LEGACY_CATEGORY_ALIASES.get(category_id, category_id)


def get_categories() -> tuple[AssistantOptionDefinition, ...]:
    """Return the predefined assistant categories."""
    return CATEGORIES


def get_category(category_id: str) -> AssistantOptionDefinition:
    """Return one category or reject an unknown or disabled category ID."""
    canonical_id = _canonical_category_id(category_id)
    for category in CATEGORIES:
        if category.option_id == canonical_id:
            if not category.enabled:
                raise DisabledSelectionError(
                    f"Category '{category_id}' is not currently available."
                )
            return category

    raise UnknownSelectionError(
        f"Unknown assistant category '{category_id}'."
    )


def get_category_questions(
    category_id: str,
) -> tuple[AssistantOptionDefinition, ...]:
    """Return the predefined questions for an enabled category."""
    canonical_id = _canonical_category_id(category_id)
    get_category(category_id)
    return CATEGORY_QUESTIONS[canonical_id]


def route_selection(
    selection_id: str,
    *,
    current_category: str | None = None,
) -> AssistantRoute:
    """Validate a selection and determine the next guided workflow step."""
    if current_category is None:
        category = get_category(selection_id)
        questions = get_category_questions(category.option_id)

        return AssistantRoute(
            current_step="question",
            message=f"Choose what you want to explore under {category.label}.",
            options=questions,
        )

    canonical_category = _canonical_category_id(current_category)
    get_category(current_category)
    questions = CATEGORY_QUESTIONS[canonical_category]
    canonical_selection = LEGACY_QUESTION_ALIASES.get(
        selection_id,
        selection_id,
    )

    selected_question = next(
        (
            question
            for question in questions
            if question.option_id == canonical_selection
        ),
        None,
    )

    # Backward compatibility: accept the former score-analysis selection
    # without displaying it as a separate option in the guided workflow.
    if (
        selected_question is None
        and canonical_category == "recommendations"
        and selection_id == "understand_recommendation_scores"
    ):
        selected_question = next(
            (
                question
                for question in questions
                if question.option_id == "view_recommendations"
            ),
            None,
        )

    if selected_question is None:
        raise UnknownSelectionError(
            f"Selection '{selection_id}' is not valid for "
            f"category '{current_category}'."
        )

    if not selected_question.enabled:
        raise DisabledSelectionError(
            f"Selection '{selection_id}' is not currently available."
        )

    if canonical_category == "recommendations":
        message = (
            f"'{selected_question.label}' was selected. "
            "Provide a staffing requirement ID to evaluate candidates. "
            "The evaluation includes candidate rankings and score analysis. "
            "It is read-only and does not save recommendations."
        )
    elif canonical_category == "workforce_capacity_analysis":
        message = (
            f"'{selected_question.label}' was selected. "
            "The assistant can retrieve utilization, allocated capacity, "
            "and available capacity together for active employees on the "
            "reporting date. This is a read-only analysis and does not "
            "change employee or allocation records."
        )
    elif canonical_category == "staffing_demand_analysis":
        message = (
            f"'{selected_question.label}' was selected. "
            "The assistant can summarize recorded staffing requirements and "
            "requested headcount by status, role, project, priority, and skill. "
            "Requested headcount is not a verified vacancy count, and this "
            "analysis does not forecast future demand. Results are read-only."
        )
    else:
        message = (
            f"'{selected_question.label}' was selected. "
            "This capability must be integrated and validated "
            "before it can return results."
        )

    return AssistantRoute(
        current_step="capability",
        message=message,
        options=(),
    )
