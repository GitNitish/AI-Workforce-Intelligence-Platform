"""API endpoints for the guided WorkForceIQ assistant."""

from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.dependencies import get_db
from app.models.entities import User
from app.schemas.assistant import (
    AssistantCandidateDiscoveryResult,
    AssistantCapacitySummaryResponse,
    AssistantStaffingDemandAnalysisResponse,
    AssistantEmployeeDetailResult,
    AssistantEmployeeSearchResult,
    AssistantInquiryCreateResponse,
    AssistantInquiryResponse,
    AssistantOption,
    AssistantSelectionRequest,
    AssistantSelectionResponse,
    AssistantUtilizationSummaryResponse,
    AssistantWorkforceCapacityAnalysisResponse,
)
from app.schemas.assistant_filters import (
    AssistantCandidateDiscoveryRequest,
    AssistantEmployeeDetailRequest,
    AssistantEmployeeFiltersRequest,
)
from app.schemas.assistant_recommendations import (
    AssistantRecommendationEvaluationResponse,
)
from app.services.assistant_capability_service import (
    AssistantCapabilityError,
    AssistantEntityNotFoundError,
    InvalidAssistantFilterError,
    discover_assistant_candidates,
    get_assistant_capacity_summary,
    get_assistant_staffing_demand_analysis,
    get_assistant_employee_detail,
    get_assistant_utilization_summary,
    get_assistant_workforce_capacity_analysis,
    search_assistant_employees,
)
from app.services.assistant_context_service import (
    AssistantContextError,
    ContextExpiredError,
    ContextNotFoundError,
    ContextOwnershipError,
    InvalidContextOwnerError,
    InvalidContextStateError,
    create_context,
    generate_guest_session_secret,
    get_context,
    reset_context,
    update_context_state,
)
from app.services.assistant_recommendation_service import (
    evaluate_assistant_recommendations,
)
from app.services.assistant_routing_service import (
    AssistantRoutingError,
    DisabledSelectionError,
    UnknownSelectionError,
    get_categories,
    route_selection,
)


assistant_router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"],
)

optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)

GUEST_COOKIE_NAME = "workforceiq_guest_session"
GUEST_COOKIE_MAX_AGE_SECONDS = 8 * 60 * 60


def _get_optional_user(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User | None:
    """Resolve an authenticated user when a bearer token is supplied."""
    if token is None:
        return None

    try:
        payload = decode_access_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.scalar(select(User).where(User.user_id == user_id))

    if user is None or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is unavailable or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def _resolve_owner(
    request: Request,
    response: Response,
    current_user: User | None,
) -> tuple[str | None, str | None]:
    """Resolve a user owner or issue/reuse a guest session secret."""
    if current_user is not None:
        return current_user.user_id, None

    guest_secret = request.cookies.get(GUEST_COOKIE_NAME)

    if guest_secret is None:
        guest_secret = generate_guest_session_secret()

    is_https = request.url.scheme.lower() == "https"

    response.set_cookie(
        key=GUEST_COOKIE_NAME,
        value=guest_secret,
        max_age=GUEST_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=is_https,
        samesite="lax",
        path="/api/v1/assistant",
    )

    return None, guest_secret


def _context_response(context) -> AssistantInquiryResponse:
    """Convert a persisted context into a safe API response."""
    return AssistantInquiryResponse(
        context_id=context.context_id,
        status=context.status,
        question_id=context.question_id,
        context_data=context.context_data,
        created_at=context.created_at,
        updated_at=context.updated_at,
        last_activity_at=context.last_activity_at,
        expires_at=context.expires_at,
        absolute_expires_at=context.absolute_expires_at,
    )


def _raise_context_http_error(exc: AssistantContextError) -> None:
    """Translate context-service errors into HTTP responses."""
    if isinstance(exc, ContextNotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ContextOwnershipError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ContextExpiredError):
        code = status.HTTP_410_GONE
    elif isinstance(
        exc,
        (InvalidContextOwnerError, InvalidContextStateError),
    ):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
    else:
        code = status.HTTP_400_BAD_REQUEST

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


def _raise_routing_http_error(exc: AssistantRoutingError) -> None:
    """Translate routing errors into HTTP responses."""
    if isinstance(exc, DisabledSelectionError):
        code = status.HTTP_409_CONFLICT
    elif isinstance(exc, UnknownSelectionError):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
    else:
        code = status.HTTP_400_BAD_REQUEST

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


def _raise_capability_http_error(exc: AssistantCapabilityError) -> None:
    """Translate read-only capability errors into HTTP responses."""
    if isinstance(exc, AssistantEntityNotFoundError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, InvalidAssistantFilterError):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
    else:
        code = status.HTTP_400_BAD_REQUEST

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


def _get_owned_context(
    context_id: str,
    request: Request,
    response: Response,
    db: Session,
    current_user: User | None,
):
    """Retrieve an active inquiry after checking its owner."""
    owner_user_id, guest_secret = _resolve_owner(
        request,
        response,
        current_user,
    )

    try:
        return get_context(
            db,
            context_id,
            owner_user_id=owner_user_id,
            guest_session_secret=guest_secret,
        )
    except AssistantContextError as exc:
        _raise_context_http_error(exc)


def _persist_context_state(
    context_id: str,
    request: Request,
    response: Response,
    db: Session,
    current_user: User | None,
    context_data: dict[str, Any],
    question_id: str | None,
):
    """Persist bounded workflow state for the verified context owner."""
    owner_user_id, guest_secret = _resolve_owner(
        request,
        response,
        current_user,
    )

    try:
        return update_context_state(
            db,
            context_id,
            owner_user_id=owner_user_id,
            guest_session_secret=guest_secret,
            context_data=context_data,
            question_id=question_id,
        )
    except AssistantContextError as exc:
        _raise_context_http_error(exc)


@assistant_router.post(
    "/inquiries",
    response_model=AssistantInquiryCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_inquiry(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Create an inquiry and return the available categories."""
    owner_user_id, guest_secret = _resolve_owner(
        request,
        response,
        current_user,
    )

    try:
        context = create_context(
            db,
            owner_user_id=owner_user_id,
            guest_session_secret=guest_secret,
            context_data={"current_step": "category"},
        )
    except AssistantContextError as exc:
        _raise_context_http_error(exc)

    options = [
        AssistantOption(
            id=option.option_id,
            label=option.label,
            description=option.description,
            enabled=option.enabled,
        )
        for option in get_categories()
    ]

    return AssistantInquiryCreateResponse(
        context_id=context.context_id,
        status="active",
        expires_at=context.expires_at,
        absolute_expires_at=context.absolute_expires_at,
        current_step="category",
        message="Choose a workforce topic to explore.",
        options=options,
    )


@assistant_router.get(
    "/inquiries/{context_id}",
    response_model=AssistantInquiryResponse,
)
def retrieve_inquiry(
    context_id: str,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Retrieve an inquiry only for its verified owner."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )
    return _context_response(context)


@assistant_router.post(
    "/inquiries/{context_id}/selections",
    response_model=AssistantSelectionResponse,
)
def submit_selection(
    context_id: str,
    selection: AssistantSelectionRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Validate a curated selection and persist the next workflow step."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    context_data = context.context_data or {}
    current_category = context_data.get("current_category")

    try:
        route = route_selection(
            selection.selection_id,
            current_category=current_category,
        )
    except AssistantRoutingError as exc:
        _raise_routing_http_error(exc)

    if route.current_step == "question":
        next_category = selection.selection_id
        question_id = None
    else:
        next_category = current_category
        question_id = selection.selection_id

    updated_data = {
        "current_step": route.current_step,
        "current_category": next_category,
        "selected_question_id": question_id,
    }

    context = _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        question_id,
    )

    options = [
        AssistantOption(
            id=option.option_id,
            label=option.label,
            description=option.description,
            enabled=option.enabled,
        )
        for option in route.options
    ]

    return AssistantSelectionResponse(
        context_id=context.context_id,
        status="active",
        selected_id=selection.selection_id,
        current_step=route.current_step,
        message=route.message,
        options=options,
    )


@assistant_router.post(
    "/inquiries/{context_id}/employee-search",
    response_model=AssistantEmployeeSearchResult,
)
def run_employee_search(
    context_id: str,
    filters: AssistantEmployeeFiltersRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Run a validated employee search within an owned inquiry."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    if context.question_id != "search_employees":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select the employee search question before "
                "submitting filters."
            ),
        )

    try:
        result = search_assistant_employees(
            db,
            **filters.model_dump(),
        )
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **(context.context_data or {}),
        "current_step": "results",
        "selected_question_id": "search_employees",
        "search_filters": filters.model_dump(),
        "last_result_summary": {
            "capability": "search_employees",
            "result_count": result["result_count"],
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        "search_employees",
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/employee-detail",
    response_model=AssistantEmployeeDetailResult,
)
def run_employee_detail(
    context_id: str,
    employee_request: AssistantEmployeeDetailRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Retrieve approved detail fields for a selected employee."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    # Recommendation evaluations are a valid source for employee details.
    # Ownership and context lifecycle checks have already been performed.
    context_data = context.context_data or {}
    last_result_summary = context_data.get("last_result_summary")
    is_recommendation_result = (
        isinstance(last_result_summary, dict)
        and last_result_summary.get("capability")
        == "read_only_recommendation_evaluation"
    )

    if (
        context.question_id
        not in {
            "search_employees",
            "find_candidates_for_requirement",
        }
        and not is_recommendation_result
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select an employee-related question or evaluate "
                "recommendations before requesting details."
            ),
        )

    try:
        result = get_assistant_employee_detail(
            db,
            employee_request.employee_id,
        )
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    # Preserve the original result summary so another employee detail
    # request remains authorized after returning to the results list.
    # Store the selected employee separately instead of replacing the
    # recommendation/search/discovery capability marker.
    updated_data = {
        **context_data,
        "current_step": "results",
        "last_result_summary": last_result_summary,
        "selected_employee_detail": {
            "employee_id": result["employee"]["employee_id"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        context.question_id,
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/candidate-discovery",
    response_model=AssistantCandidateDiscoveryResult,
)
def run_candidate_discovery(
    context_id: str,
    discovery_request: AssistantCandidateDiscoveryRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Discover candidates without generating persisted recommendations."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    if context.question_id != "find_candidates_for_requirement":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select candidate discovery before submitting "
                "a staffing requirement."
            ),
        )

    try:
        result = discover_assistant_candidates(
            db,
            discovery_request.staffing_requirement_id,
            limit=discovery_request.limit,
        )
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **(context.context_data or {}),
        "current_step": "results",
        "selected_question_id": "find_candidates_for_requirement",
        "staffing_requirement_id": (
            discovery_request.staffing_requirement_id
        ),
        "last_result_summary": {
            "capability": "candidate_discovery",
            "staffing_requirement_id": (
                discovery_request.staffing_requirement_id
            ),
            "result_count": result["result_count"],
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        "find_candidates_for_requirement",
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/recommendation-evaluation",
    response_model=AssistantRecommendationEvaluationResponse,
)
def run_recommendation_evaluation(
    context_id: str,
    evaluation_request: AssistantCandidateDiscoveryRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Evaluate candidates without modifying saved recommendations."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    allowed_question_ids = {
        "view_recommendations",
        "understand_recommendation_scores",
    }

    if context.question_id not in allowed_question_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select a recommendation question before requesting "
                "a read-only evaluation."
            ),
        )

    try:
        result = evaluate_assistant_recommendations(
            db,
            evaluation_request.staffing_requirement_id,
            limit=evaluation_request.limit,
        )
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **(context.context_data or {}),
        "current_step": "results",
        "selected_question_id": context.question_id,
        "staffing_requirement_id": (
            evaluation_request.staffing_requirement_id
        ),
        "last_result_summary": {
            "capability": "read_only_recommendation_evaluation",
            "staffing_requirement_id": (
                evaluation_request.staffing_requirement_id
            ),
            "result_count": result["result_count"],
            "eligible_candidate_count": (
                result["eligible_candidate_count"]
            ),
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        context.question_id,
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/utilization",
    response_model=AssistantUtilizationSummaryResponse,
)
def run_utilization_summary(
    context_id: str,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Return a read-only utilization summary for an owned inquiry."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    context_data = context.context_data or {}

    if (
        context_data.get("current_category") != "utilization"
        or context.question_id != "view_current_utilization"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select the current utilization question before "
                "requesting a utilization summary."
            ),
        )

    try:
        result = get_assistant_utilization_summary(db)
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **context_data,
        "current_step": "results",
        "selected_question_id": "view_current_utilization",
        "last_result_summary": {
            "capability": "utilization_summary",
            "active_employee_count": result["active_employee_count"],
            "result_count": result["result_count"],
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        "view_current_utilization",
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/capacity",
    response_model=AssistantCapacitySummaryResponse,
)
def run_capacity_summary(
    context_id: str,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Return a read-only capacity summary for an owned inquiry."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    context_data = context.context_data or {}

    if (
        context_data.get("current_category") != "capacity"
        or context.question_id != "view_current_capacity"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select the current capacity question before "
                "requesting a capacity summary."
            ),
        )

    try:
        result = get_assistant_capacity_summary(db)
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **context_data,
        "current_step": "results",
        "selected_question_id": "view_current_capacity",
        "last_result_summary": {
            "capability": "capacity_summary",
            "reporting_date": result["reporting_date"],
            "active_employee_count": result["active_employee_count"],
            "result_count": result["result_count"],
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        "view_current_capacity",
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/workforce-capacity-analysis",
    response_model=AssistantWorkforceCapacityAnalysisResponse,
)
def run_workforce_capacity_analysis(
    context_id: str,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Return a read-only combined utilization and capacity analysis."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    context_data = context.context_data or {}

    if (
        context_data.get("current_category") != "workforce_capacity_analysis"
        or context.question_id != "view_workforce_capacity_analysis"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select the workforce capacity analysis question before "
                "requesting a combined utilization and capacity analysis."
            ),
        )

    try:
        result = get_assistant_workforce_capacity_analysis(db)
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **context_data,
        "current_step": "results",
        "selected_question_id": "view_workforce_capacity_analysis",
        "last_result_summary": {
            "capability": "workforce_capacity_analysis",
            "reporting_date": result["reporting_date"],
            "active_employee_count": result["active_employee_count"],
            "result_count": result["result_count"],
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        "view_workforce_capacity_analysis",
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/staffing-demand-analysis",
    response_model=AssistantStaffingDemandAnalysisResponse,
)
def run_staffing_demand_analysis(
    context_id: str,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Return a read-only summary of recorded staffing demand."""
    context = _get_owned_context(
        context_id,
        request,
        response,
        db,
        current_user,
    )

    context_data = context.context_data or {}

    if (
        context_data.get("current_category") != "staffing_demand_analysis"
        or context.question_id != "view_staffing_demand_analysis"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Select the staffing demand analysis question before "
                "requesting a staffing demand summary."
            ),
        )

    try:
        result = get_assistant_staffing_demand_analysis(db)
    except AssistantCapabilityError as exc:
        _raise_capability_http_error(exc)

    updated_data = {
        **context_data,
        "current_step": "results",
        "selected_question_id": "view_staffing_demand_analysis",
        "last_result_summary": {
            "capability": "staffing_demand_analysis",
            "total_requirement_count": result["total_requirement_count"],
            "open_requirement_count": result["open_requirement_count"],
            "total_requested_headcount": result["total_requested_headcount"],
            "open_requested_headcount": result["open_requested_headcount"],
            "result_count": result["result_count"],
            "has_more_results": result["has_more_results"],
        },
    }

    _persist_context_state(
        context_id,
        request,
        response,
        db,
        current_user,
        updated_data,
        "view_staffing_demand_analysis",
    )

    return result


@assistant_router.post(
    "/inquiries/{context_id}/reset",
    response_model=AssistantInquiryResponse,
)
def reset_inquiry(
    context_id: str,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(_get_optional_user)],
):
    """Reset an inquiry while preserving ownership and lifecycle rules."""
    owner_user_id, guest_secret = _resolve_owner(
        request,
        response,
        current_user,
    )

    try:
        context = reset_context(
            db,
            context_id,
            owner_user_id=owner_user_id,
            guest_session_secret=guest_secret,
        )
    except AssistantContextError as exc:
        _raise_context_http_error(exc)

    return _context_response(context)
