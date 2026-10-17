import { useState } from 'react'
import type { ReactNode } from 'react'
import { apiRequest } from '../services/api'
import './AssistantPage.css'

interface AssistantOption {
  id: string
  label: string
  description: string
  enabled: boolean
}

interface AssistantInquiry {
  context_id: string
  status: string
  question_id?: string | null
  current_step?: string
  message?: string
  options?: AssistantOption[]
}

interface Employee {
  employee_id: string
  employee_code: string
  name: string
  designation?: string | null
  department?: string | null
  experience_years: number
  availability_status: string
  location?: string | null
  status: string
  utilization_percentage: number
}

interface EmployeeSearchResponse {
  capability: string
  filters: Record<string, unknown>
  result_count: number
  limit: number
  has_more_results: boolean
  employees: Employee[]
}

interface EmployeeDetailResponse {
  capability: string
  employee: Employee
}

interface StaffingRequirement {
  staffing_requirement_id: string
  project_id: string
  role_name: string
  required_quantity: number
  required_experience: number
  required_proficiency?: string | null
  status: string
}

interface CandidateDiscoveryResponse {
  capability: string
  staffing_requirement: StaffingRequirement
  result_count: number
  limit: number
  has_more_results: boolean
  employees: Employee[]
  notice: string
}

interface RecommendationScoreBreakdown {
  skill_match: number
  proficiency: number
  experience: number
  certification: number
  availability: number
  utilization: number
}

interface RecommendationCandidate {
  employee_id: string
  employee_code: string
  name: string
  designation: string
  department: string
  experience_years: number
  availability_status: string
  location?: string | null
  utilization_percentage: number
  remaining_capacity_percentage: number
  score: number
  score_breakdown: RecommendationScoreBreakdown
  matched_skills: string[]
  recommendation_reason: string
  rank: number
}

interface RecommendationEvaluationResponse {
  capability: 'read_only_recommendation_evaluation'
  staffing_requirement: StaffingRequirement
  result_count: number
  eligible_candidate_count: number
  limit: number
  has_more_results: boolean
  candidates: RecommendationCandidate[]
  notice: string
}

interface UtilizationEmployee {
  employee_id: string
  employee_code: string
  name: string
  designation?: string | null
  department?: string | null
  utilization_percentage: number
  available_capacity_percentage: number
}

interface UtilizationSummaryResponse {
  capability: 'utilization_summary'
  active_employee_count: number
  average_utilization_percentage: number
  average_available_capacity_percentage: number
  result_count: number
  limit: number
  has_more_results: boolean
  employees: UtilizationEmployee[]
}

interface CapacityEmployee {
  employee_id: string
  employee_code: string
  name: string
  designation?: string | null
  department?: string | null
  allocated_capacity_percentage: number
  available_capacity_percentage: number
}

interface CapacitySummaryResponse {
  capability: 'capacity_summary'
  reporting_date: string
  active_employee_count: number
  average_allocated_capacity_percentage: number
  average_available_capacity_percentage: number
  employees_with_no_available_capacity_count: number
  employees_with_partial_available_capacity_count: number
  employees_with_full_available_capacity_count: number
  result_count: number
  limit: number
  has_more_results: boolean
  employees: CapacityEmployee[]
}

interface WorkforceCapacityEmployee {
  employee_id: string
  employee_code: string
  name: string
  designation?: string | null
  department?: string | null
  utilization_percentage: number
  allocated_capacity_percentage: number
  available_capacity_percentage: number
}

interface WorkforceCapacityAnalysisResponse {
  capability: 'workforce_capacity_analysis'
  reporting_date: string
  active_employee_count: number
  average_utilization_percentage: number
  average_allocated_capacity_percentage: number
  average_available_capacity_percentage: number
  employees_with_no_available_capacity_count: number
  employees_with_partial_available_capacity_count: number
  employees_with_full_available_capacity_count: number
  result_count: number
  limit: number
  has_more_results: boolean
  employees: WorkforceCapacityEmployee[]
}

interface DemandStatusBreakdown {
  status: string
  requirement_count: number
  requested_headcount: number
}

interface DemandNamedBreakdown {
  name: string
  requirement_count: number
  requested_headcount: number
}

interface DemandProjectBreakdown {
  project_id: string
  project_name: string
  requirement_count: number
  requested_headcount: number
}

interface DemandRequirementDetail {
  staffing_requirement_id: string
  project_id: string
  project_name: string
  role_name: string
  required_quantity: number
  status: string
  priority: string
  required_experience: number
  required_proficiency?: string | null
  start_date?: string | null
  end_date?: string | null
  required_skills: string[]
}

interface StaffingDemandAnalysisResponse {
  capability: 'staffing_demand_analysis'
  total_requirement_count: number
  total_requested_headcount: number
  open_requirement_count: number
  open_requested_headcount: number
  requirements_by_status: DemandStatusBreakdown[]
  requirements_by_role: DemandNamedBreakdown[]
  requirements_by_project: DemandProjectBreakdown[]
  requirements_by_priority: DemandNamedBreakdown[]
  requirements_by_skill: DemandNamedBreakdown[]
  result_count: number
  limit: number
  has_more_results: boolean
  requirements: DemandRequirementDetail[]
  notice: string
}

type EmployeeListResult =
  | EmployeeSearchResponse
  | CandidateDiscoveryResponse

type AssistantResult =
  | EmployeeListResult
  | EmployeeDetailResponse
  | RecommendationEvaluationResponse
  | UtilizationSummaryResponse
  | CapacitySummaryResponse
  | WorkforceCapacityAnalysisResponse
  | StaffingDemandAnalysisResponse

interface EmployeeFilters {
  name: string
  employee_code: string
  department: string
  designation: string
  availability_status: string
  location: string
  min_experience: string
  max_utilization: string
  status: 'active' | 'inactive'
  limit: number
}

const INITIAL_FILTERS: EmployeeFilters = {
  name: '',
  employee_code: '',
  department: '',
  designation: '',
  availability_status: '',
  location: '',
  min_experience: '',
  max_utilization: '',
  status: 'active',
  limit: 25,
}

const RECOMMENDATION_QUESTIONS = new Set([
  'view_recommendations',
  'understand_recommendation_scores',
])

const SCORE_COMPONENTS: Array<{
  key: keyof RecommendationScoreBreakdown
  label: string
}> = [
  { key: 'skill_match', label: 'Skill match' },
  { key: 'proficiency', label: 'Proficiency' },
  { key: 'experience', label: 'Experience' },
  { key: 'certification', label: 'Certification' },
  { key: 'availability', label: 'Availability' },
  { key: 'utilization', label: 'Utilization' },
]

function isEmployeeSearchResult(
  result: AssistantResult,
): result is EmployeeSearchResponse {
  return (
    'employees' in result &&
    result.capability === 'search_employees'
  )
}

function isCandidateDiscoveryResult(
  result: AssistantResult,
): result is CandidateDiscoveryResponse {
  return (
    'employees' in result &&
    result.capability === 'candidate_discovery'
  )
}

function isEmployeeDetailResult(
  result: AssistantResult,
): result is EmployeeDetailResponse {
  return 'employee' in result
}

function isRecommendationResult(
  result: AssistantResult,
): result is RecommendationEvaluationResponse {
  return (
    'candidates' in result &&
    result.capability === 'read_only_recommendation_evaluation'
  )
}

function isUtilizationResult(
  result: AssistantResult,
): result is UtilizationSummaryResponse {
  return result.capability === 'utilization_summary'
}

function isCapacityResult(
  result: AssistantResult,
): result is CapacitySummaryResponse {
  return result.capability === 'capacity_summary'
}

function isWorkforceCapacityAnalysisResult(
  result: AssistantResult,
): result is WorkforceCapacityAnalysisResponse {
  return result.capability === 'workforce_capacity_analysis'
}

function isStaffingDemandAnalysisResult(
  result: AssistantResult,
): result is StaffingDemandAnalysisResponse {
  return result.capability === 'staffing_demand_analysis'
}

function formatAvailability(value: string): string {
  return value.replaceAll('_', ' ')
}

function formatScore(value: number): string {
  return `${value.toFixed(2)} / 100`
}

function AssistantPage() {
  const [inquiry, setInquiry] =
    useState<AssistantInquiry | null>(null)
  const [options, setOptions] = useState<AssistantOption[]>([])
  const [categoryId, setCategoryId] = useState('')
  const [questionId, setQuestionId] = useState('')
  const [message, setMessage] = useState(
    'Start an inquiry to explore workforce information.',
  )
  const [filters, setFilters] =
    useState<EmployeeFilters>(INITIAL_FILTERS)
  const [staffingRequirementId, setStaffingRequirementId] =
    useState('')
  const [result, setResult] =
    useState<AssistantResult | null>(null)

  // Keep the previous result set while employee details are open.
  // Recommendation evaluations are result sets too.
  const [previousResults, setPreviousResults] =
    useState<EmployeeListResult | RecommendationEvaluationResponse | null>(null)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const canSearchEmployees =
    questionId === 'search_employees' && inquiry !== null

  const canDiscoverCandidates =
    questionId === 'find_candidates_for_requirement' &&
    inquiry !== null

  const canEvaluateRecommendations =
    RECOMMENDATION_QUESTIONS.has(questionId) &&
    inquiry !== null

  const canViewWorkforceCapacityAnalysis =
    questionId === 'view_workforce_capacity_analysis' && inquiry !== null

  const canViewStaffingDemandAnalysis =
    questionId === 'view_staffing_demand_analysis' && inquiry !== null

  async function startInquiry(): Promise<void> {
    setLoading(true)
    setError('')

    try {
      const response = await apiRequest<AssistantInquiry>(
        '/assistant/inquiries',
        { method: 'POST' },
      )

      setInquiry(response)
      setOptions(response.options ?? [])
      setCategoryId('')
      setQuestionId('')
      setResult(null)
      setPreviousResults(null)
      setStaffingRequirementId('')
      setFilters(INITIAL_FILTERS)
      setMessage(
        response.message ?? 'Choose a workforce topic to explore.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to start an assistant inquiry.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function submitSelection(
    option: AssistantOption,
  ): Promise<void> {
    if (!inquiry || !option.enabled) {
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setPreviousResults(null)

    try {
      const response = await apiRequest<AssistantInquiry>(
        `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/selections`,
        {
          method: 'POST',
          body: JSON.stringify({
            selection_id: option.id,
          }),
        },
      )

      if (response.current_step === 'question') {
        setCategoryId(option.id)
        setQuestionId('')
      } else {
        setQuestionId(option.id)
      }

      setOptions(response.options ?? [])
      setMessage(
        response.message ?? 'Continue with the next step.',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to process that selection.',
      )
    } finally {
      setLoading(false)
    }
  }

  function updateFilter<K extends keyof EmployeeFilters>(
    key: K,
    value: EmployeeFilters[K],
  ): void {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }))
  }

  async function searchEmployees(): Promise<void> {
    if (!inquiry) {
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setPreviousResults(null)

    const payload: Record<string, unknown> = {
      status: filters.status,
      limit: filters.limit,
    }

    const textFields = [
      'name',
      'employee_code',
      'department',
      'designation',
      'availability_status',
      'location',
    ] as const

    for (const key of textFields) {
      const value = filters[key].trim()

      if (value) {
        payload[key] = value
      }
    }

    if (filters.min_experience !== '') {
      payload.min_experience = Number(filters.min_experience)
    }

    if (filters.max_utilization !== '') {
      payload.max_utilization = Number(filters.max_utilization)
    }

    try {
      const response = await apiRequest<EmployeeSearchResponse>(
        `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/employee-search`,
        {
          method: 'POST',
          body: JSON.stringify(payload),
        },
      )

      setResult(response)
      setMessage(
        `Employee search returned ${response.result_count} result(s).`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to search employees.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function discoverCandidates(): Promise<void> {
    if (!inquiry || !staffingRequirementId.trim()) {
      setError('Enter a staffing requirement ID to continue.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setPreviousResults(null)

    try {
      const response =
        await apiRequest<CandidateDiscoveryResponse>(
          `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/candidate-discovery`,
          {
            method: 'POST',
            body: JSON.stringify({
              staffing_requirement_id: staffingRequirementId.trim(),
              limit: 25,
            }),
          },
        )

      setResult(response)
      setMessage(
        `Candidate discovery returned ${response.result_count} employee(s).`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to discover candidates.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function evaluateRecommendations(): Promise<void> {
    if (!inquiry || !staffingRequirementId.trim()) {
      setError('Enter a staffing requirement ID to continue.')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setPreviousResults(null)

    try {
      const response =
        await apiRequest<RecommendationEvaluationResponse>(
          `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/recommendation-evaluation`,
          {
            method: 'POST',
            body: JSON.stringify({
              staffing_requirement_id: staffingRequirementId.trim(),
              limit: 25,
            }),
          },
        )

      setResult(response)
      setMessage(
        `Recommendation evaluation returned ${response.result_count} eligible candidate(s).`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to evaluate recommendations.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function loadWorkforceCapacityAnalysis(): Promise<void> {
    if (!inquiry || !canViewWorkforceCapacityAnalysis) {
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setPreviousResults(null)

    try {
      const response = await apiRequest<WorkforceCapacityAnalysisResponse>(
        `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/workforce-capacity-analysis`,
        { method: 'POST' },
      )

      setResult(response)
      setMessage(
        `Workforce capacity analysis returned for ${response.active_employee_count} active employee(s) as of ${response.reporting_date}.`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to retrieve the workforce capacity analysis.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function loadStaffingDemandAnalysis(): Promise<void> {
    if (!inquiry || !canViewStaffingDemandAnalysis) {
      return
    }

    setLoading(true)
    setError('')
    setResult(null)
    setPreviousResults(null)

    try {
      const response = await apiRequest<StaffingDemandAnalysisResponse>(
        `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/staffing-demand-analysis`,
        { method: 'POST' },
      )

      setResult(response)
      setMessage(
        `Staffing demand analysis returned ${response.total_requirement_count} recorded requirement(s), including ${response.open_requirement_count} open requirement(s).`,
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to retrieve staffing demand analysis.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function showEmployeeDetail(
    employeeId: string,
  ): Promise<void> {
    if (!inquiry) {
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await apiRequest<EmployeeDetailResponse>(
        `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/employee-detail`,
        {
          method: 'POST',
          body: JSON.stringify({
            employee_id: employeeId,
          }),
        },
      )

      // Save the currently displayed list before switching to employee details.
      // This includes recommendation evaluations.
      if (
        result &&
        (isEmployeeSearchResult(result) ||
          isCandidateDiscoveryResult(result) ||
          isRecommendationResult(result))
      ) {
        setPreviousResults(result)
      }

      setResult(response)
      setMessage(`Employee details for ${response.employee.name}.`)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to retrieve employee details.',
      )
    } finally {
      setLoading(false)
    }
  }

  function returnToResults(): void {
    if (previousResults) {
      setResult(previousResults)

      // Intentionally retain previousResults so repeated navigation works.
      // A new search, inquiry, or selection clears it when appropriate.

      if (isEmployeeSearchResult(previousResults)) {
        setMessage(
          `Employee search returned ${previousResults.result_count} result(s).`,
        )
      } else if (isCandidateDiscoveryResult(previousResults)) {
        setMessage(
          `Candidate discovery returned ${previousResults.result_count} employee(s).`,
        )
      } else {
        setMessage(
          `Recommendation evaluation returned ${previousResults.result_count} eligible candidate(s).`,
        )
      }
    } else {
      setResult(null)
    }
  }

  async function resetInquiry(): Promise<void> {
    if (!inquiry) {
      return
    }

    setLoading(true)
    setError('')

    try {
      await apiRequest(
        `/assistant/inquiries/${encodeURIComponent(inquiry.context_id)}/reset`,
        { method: 'POST' },
      )

      await startInquiry()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to reset the inquiry.',
      )
      setLoading(false)
    }
  }

  function renderEmployee(employee: Employee) {
    return (
      <tr key={employee.employee_id}>
        <td>
          <strong>{employee.name}</strong>
          <div className="assistant-muted">
            {employee.employee_code}
          </div>
        </td>
        <td>{employee.designation || '—'}</td>
        <td>{employee.department || '—'}</td>
        <td>{employee.experience_years}</td>
        <td>{formatAvailability(employee.availability_status)}</td>
        <td>{employee.utilization_percentage}%</td>
        <td>
          <button
            type="button"
            className="assistant-secondary-button"
            disabled={loading}
            onClick={() => void showEmployeeDetail(employee.employee_id)}
          >
            View details
          </button>
        </td>
      </tr>
    )
  }

  return (
    <section className="assistant-page">
      <header className="assistant-header">
        <div>
          <p className="assistant-eyebrow">WORKFORCE INTELLIGENCE</p>
          <h1>Workforce Assistant</h1>
          <p className="assistant-intro">
            Explore employee information, staffing candidates, current
            utilization, workforce capacity, and read-only recommendation
            evaluations through a guided workflow.
          </p>
        </div>

        {inquiry && (
          <button
            type="button"
            className="assistant-secondary-button"
            disabled={loading}
            onClick={() => void resetInquiry()}
          >
            Reset inquiry
          </button>
        )}
      </header>

      {error && (
        <div className="assistant-error" role="alert">
          <strong>Something went wrong</strong>
          <p>{error}</p>
        </div>
      )}

      <section className="assistant-panel">
        <div className="assistant-panel-heading">
          <span className="assistant-step">01</span>
          <div>
            <h2>Start an inquiry</h2>
            <p>
              Each inquiry has its own server-managed session and expiration.
            </p>
          </div>
        </div>

        {!inquiry ? (
          <button
            type="button"
            className="assistant-primary-button"
            disabled={loading}
            onClick={() => void startInquiry()}
          >
            {loading ? 'Starting…' : 'Start inquiry'}
          </button>
        ) : (
          <div className="assistant-session">
            <span className="assistant-session-dot" />
            <span>Inquiry active</span>
            <span className="assistant-muted">
              ID: {inquiry.context_id}
            </span>
          </div>
        )}
      </section>

      {inquiry && (
        <>
          <section className="assistant-panel">
            <div className="assistant-panel-heading">
              <span className="assistant-step">02</span>
              <div>
                <h2>{categoryId ? 'Choose a question' : 'Choose a topic'}</h2>
                <p>{message}</p>
              </div>
            </div>

            <div className="assistant-option-grid">
              {options.map((option) => (
                <button
                  type="button"
                  key={option.id}
                  className="assistant-option"
                  disabled={loading || !option.enabled}
                  onClick={() => void submitSelection(option)}
                >
                  <span className="assistant-option-title">
                    {option.label}
                  </span>
                  <span className="assistant-option-description">
                    {option.description}
                  </span>
                  {!option.enabled && (
                    <span className="assistant-unavailable">
                      Not available yet
                    </span>
                  )}
                </button>
              ))}
            </div>
          </section>

          {canSearchEmployees && (
            <section className="assistant-panel">
              <div className="assistant-panel-heading">
                <span className="assistant-step">03</span>
                <div>
                  <h2>Employee search</h2>
                  <p>Narrow the search using employee attributes.</p>
                </div>
              </div>

              <form
                className="assistant-filter-grid"
                onSubmit={(event) => {
                  event.preventDefault()
                  void searchEmployees()
                }}
              >
                <label>
                  Name
                  <input
                    value={filters.name}
                    maxLength={100}
                    onChange={(event) => updateFilter('name', event.target.value)}
                    placeholder="Employee name"
                  />
                </label>

                <label>
                  Employee code
                  <input
                    value={filters.employee_code}
                    maxLength={100}
                    onChange={(event) =>
                      updateFilter('employee_code', event.target.value)
                    }
                    placeholder="Employee code"
                  />
                </label>

                <label>
                  Department
                  <input
                    value={filters.department}
                    maxLength={100}
                    onChange={(event) =>
                      updateFilter('department', event.target.value)
                    }
                    placeholder="Department"
                  />
                </label>

                <label>
                  Designation
                  <input
                    value={filters.designation}
                    maxLength={100}
                    onChange={(event) =>
                      updateFilter('designation', event.target.value)
                    }
                    placeholder="Designation"
                  />
                </label>

                <label>
                  Availability
                  <select
                    value={filters.availability_status}
                    onChange={(event) =>
                      updateFilter('availability_status', event.target.value)
                    }
                  >
                    <option value="">Any availability</option>
                    <option value="available">Available</option>
                    <option value="partially_available">Partially available</option>
                    <option value="unavailable">Unavailable</option>
                  </select>
                </label>

                <label>
                  Location
                  <input
                    value={filters.location}
                    maxLength={100}
                    onChange={(event) =>
                      updateFilter('location', event.target.value)
                    }
                    placeholder="Location"
                  />
                </label>

                <label>
                  Minimum experience (years)
                  <input
                    type="number"
                    min="0"
                    max="60"
                    step="0.5"
                    value={filters.min_experience}
                    onChange={(event) =>
                      updateFilter('min_experience', event.target.value)
                    }
                  />
                </label>

                <label>
                  Maximum utilization (%)
                  <input
                    type="number"
                    min="0"
                    max="100"
                    step="1"
                    value={filters.max_utilization}
                    onChange={(event) =>
                      updateFilter('max_utilization', event.target.value)
                    }
                  />
                </label>

                <label>
                  Employee status
                  <select
                    value={filters.status}
                    onChange={(event) =>
                      updateFilter(
                        'status',
                        event.target.value as 'active' | 'inactive',
                      )
                    }
                  >
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </label>

                <label>
                  Result limit
                  <select
                    value={filters.limit}
                    onChange={(event) =>
                      updateFilter('limit', Number(event.target.value))
                    }
                  >
                    <option value={10}>10 results</option>
                    <option value={25}>25 results</option>
                  </select>
                </label>

                <div className="assistant-filter-actions">
                  <button
                    type="submit"
                    className="assistant-primary-button"
                    disabled={loading}
                  >
                    {loading ? 'Searching…' : 'Search employees'}
                  </button>
                </div>
              </form>
            </section>
          )}

          {canViewWorkforceCapacityAnalysis && (
            <section className="assistant-panel">
              <div className="assistant-panel-heading">
                <span className="assistant-step">03</span>
                <div>
                  <h2>Workforce capacity analysis</h2>
                  <p>
                    Review utilization, allocated capacity, and available capacity
                    together for active employees as of the reporting date. These
                    are separate measures. This read-only analysis does not create
                    or change allocations and does not forecast future demand.
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="assistant-primary-button"
                disabled={loading}
                onClick={() => void loadWorkforceCapacityAnalysis()}
              >
                {loading ? 'Loading analysis…' : 'View workforce capacity analysis'}
              </button>
            </section>
          )}

          {canViewStaffingDemandAnalysis && (
            <section className="assistant-panel">
              <div className="assistant-panel-heading">
                <span className="assistant-step">03</span>
                <div>
                  <h2>Staffing demand analysis</h2>
                  <p>
                    Review recorded staffing requirements by status, role, project,
                    priority, and required skill. Requested headcount is not a
                    verified vacancy count, and this analysis does not forecast
                    future demand.
                  </p>
                </div>
              </div>

              <button
                type="button"
                className="assistant-primary-button"
                disabled={loading}
                onClick={() => void loadStaffingDemandAnalysis()}
              >
                {loading ? 'Loading analysis…' : 'View staffing demand analysis'}
              </button>
            </section>
          )}

          {(canDiscoverCandidates || canEvaluateRecommendations) && (
            <section className="assistant-panel">
              <div className="assistant-panel-heading">
                <span className="assistant-step">03</span>
                <div>
                  <h2>
                    {canEvaluateRecommendations
                      ? 'Recommendation evaluation'
                      : 'Candidate discovery'}
                  </h2>
                  <p>
                    {canEvaluateRecommendations
                      ? 'Evaluate eligible candidates using the existing scoring engine. Results are read-only and are not saved as recommendations.'
                      : 'Find potential candidates for an existing staffing requirement. Discovery does not score or save recommendations.'}
                  </p>
                </div>
              </div>

              <form
                className="assistant-requirement-form"
                onSubmit={(event) => {
                  event.preventDefault()
                  if (canEvaluateRecommendations) {
                    void evaluateRecommendations()
                  } else {
                    void discoverCandidates()
                  }
                }}
              >
                <label>
                  Staffing requirement ID
                  <input
                    required
                    value={staffingRequirementId}
                    maxLength={100}
                    onChange={(event) =>
                      setStaffingRequirementId(event.target.value)
                    }
                    placeholder="Paste an existing requirement ID"
                  />
                </label>

                <button
                  type="submit"
                  className="assistant-primary-button"
                  disabled={loading}
                >
                  {loading
                    ? 'Processing…'
                    : canEvaluateRecommendations
                      ? 'Evaluate recommendations'
                      : 'Find candidates'}
                </button>
              </form>
            </section>
          )}

          {loading && (
            <div className="assistant-loading" role="status">
              Processing your inquiry…
            </div>
          )}

          {result && (
            <section className="assistant-panel">
              <div className="assistant-panel-heading">
                <span className="assistant-step">04</span>
                <div>
                  <h2>
                    {isRecommendationResult(result)
                      ? 'Ranked recommendation evaluation'
                      : isWorkforceCapacityAnalysisResult(result)
                        ? 'Workforce capacity analysis'
                        : isStaffingDemandAnalysisResult(result)
                          ? 'Staffing demand analysis'
                          : isUtilizationResult(result)
                            ? 'Current utilization summary'
                            : isCapacityResult(result)
                              ? 'Current workforce capacity summary'
                              : 'Results'}
                  </h2>
                  <p>{message}</p>
                </div>
              </div>

              {isEmployeeDetailResult(result) && (
                <div className="assistant-detail-card">
                  <h3>{result.employee.name}</h3>

                  <dl className="assistant-detail-grid">
                    <div>
                      <dt>Employee code</dt>
                      <dd>{result.employee.employee_code}</dd>
                    </div>
                    <div>
                      <dt>Designation</dt>
                      <dd>{result.employee.designation || '—'}</dd>
                    </div>
                    <div>
                      <dt>Department</dt>
                      <dd>{result.employee.department || '—'}</dd>
                    </div>
                    <div>
                      <dt>Experience</dt>
                      <dd>{result.employee.experience_years} years</dd>
                    </div>
                    <div>
                      <dt>Availability</dt>
                      <dd>
                        {formatAvailability(result.employee.availability_status)}
                      </dd>
                    </div>
                    <div>
                      <dt>Utilization</dt>
                      <dd>{result.employee.utilization_percentage}%</dd>
                    </div>
                    <div>
                      <dt>Location</dt>
                      <dd>{result.employee.location || '—'}</dd>
                    </div>
                    <div>
                      <dt>Status</dt>
                      <dd>{result.employee.status}</dd>
                    </div>
                  </dl>

                  <button
                    type="button"
                    className="assistant-secondary-button"
                    onClick={returnToResults}
                  >
                    Back to results
                  </button>
                </div>
              )}

              {isEmployeeSearchResult(result) && (
                <ResultTable
                  count={result.result_count}
                  hasMore={result.has_more_results}
                  employees={result.employees}
                  renderEmployee={renderEmployee}
                />
              )}

              {isCandidateDiscoveryResult(result) && (
                <>
                  <RequirementSummary requirement={result.staffing_requirement} />
                  <p className="assistant-notice">{result.notice}</p>
                  <ResultTable
                    count={result.result_count}
                    hasMore={result.has_more_results}
                    employees={result.employees}
                    renderEmployee={renderEmployee}
                  />
                </>
              )}

              {isWorkforceCapacityAnalysisResult(result) && (
                <>
                  <div className="assistant-result-summary">
                    <strong>
                      {result.active_employee_count} active employee(s)
                    </strong>
                    <span className="assistant-muted">
                      Reporting date: {result.reporting_date}
                    </span>
                    <span className="assistant-muted">
                      {result.result_count} employee record(s) displayed
                    </span>
                    {result.has_more_results && (
                      <span className="assistant-muted">
                        Additional employee records exist beyond this limit.
                      </span>
                    )}
                  </div>

                  <dl className="assistant-detail-grid">
                    <div>
                      <dt>Average utilization</dt>
                      <dd>{result.average_utilization_percentage.toFixed(2)}%</dd>
                    </div>
                    <div>
                      <dt>Average allocated capacity</dt>
                      <dd>{result.average_allocated_capacity_percentage.toFixed(2)}%</dd>
                    </div>
                    <div>
                      <dt>Average available capacity</dt>
                      <dd>{result.average_available_capacity_percentage.toFixed(2)}%</dd>
                    </div>
                    <div>
                      <dt>No available capacity</dt>
                      <dd>{result.employees_with_no_available_capacity_count}</dd>
                    </div>
                    <div>
                      <dt>Partial available capacity</dt>
                      <dd>{result.employees_with_partial_available_capacity_count}</dd>
                    </div>
                    <div>
                      <dt>Full available capacity</dt>
                      <dd>{result.employees_with_full_available_capacity_count}</dd>
                    </div>
                  </dl>

                  <p className="assistant-notice">
                    Utilization comes from the existing employee utilization
                    calculation. Allocated capacity is based on active allocations
                    covering the reporting date; available capacity is the remaining
                    percentage up to 100%, with a minimum of 0%. These measures are
                    related but not interchangeable. This analysis is read-only and
                    is not a staffing recommendation or a forecast.
                  </p>

                  {result.employees.length === 0 ? (
                    <div className="assistant-empty-state">
                      No active employee capacity records were returned.
                    </div>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead>
                          <tr>
                            <th>Employee</th>
                            <th>Designation</th>
                            <th>Department</th>
                            <th>Utilization</th>
                            <th>Allocated capacity</th>
                            <th>Available capacity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.employees.map((employee) => (
                            <tr key={employee.employee_id}>
                              <td>
                                <strong>{employee.name}</strong>
                                <div className="assistant-muted">
                                  {employee.employee_code}
                                </div>
                              </td>
                              <td>{employee.designation || '—'}</td>
                              <td>{employee.department || '—'}</td>
                              <td>{employee.utilization_percentage.toFixed(2)}%</td>
                              <td>{employee.allocated_capacity_percentage.toFixed(2)}%</td>
                              <td>{employee.available_capacity_percentage.toFixed(2)}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}

              {isStaffingDemandAnalysisResult(result) && (
                <>
                  <div className="assistant-result-summary">
                    <strong>{result.total_requirement_count} recorded requirement(s)</strong>
                    <span className="assistant-muted">
                      Total requested headcount: {result.total_requested_headcount}
                    </span>
                    <span className="assistant-muted">
                      Open requirements: {result.open_requirement_count}
                    </span>
                    <span className="assistant-muted">
                      Open requested headcount: {result.open_requested_headcount}
                    </span>
                    <span className="assistant-muted">
                      {result.result_count} requirement record(s) displayed (limit {result.limit})
                    </span>
                    {result.has_more_results && (
                      <span className="assistant-muted">
                        Additional requirement records exist beyond this limit.
                      </span>
                    )}
                  </div>

                  <p className="assistant-notice">{result.notice}</p>

                  <h3>Requirements by status</h3>
                  {result.requirements_by_status.length === 0 ? (
                    <p className="assistant-muted">No status breakdown is available.</p>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead><tr><th>Status</th><th>Requirements</th><th>Requested headcount</th></tr></thead>
                        <tbody>
                          {result.requirements_by_status.map((item) => (
                            <tr key={item.status}>
                              <td>{item.status}</td>
                              <td>{item.requirement_count}</td>
                              <td>{item.requested_headcount}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <h3>Requirements by role</h3>
                  {result.requirements_by_role.length === 0 ? (
                    <p className="assistant-muted">No role breakdown is available.</p>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead><tr><th>Role</th><th>Requirements</th><th>Requested headcount</th></tr></thead>
                        <tbody>
                          {result.requirements_by_role.map((item) => (
                            <tr key={item.name}>
                              <td>{item.name}</td>
                              <td>{item.requirement_count}</td>
                              <td>{item.requested_headcount}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <h3>Requirements by project</h3>
                  {result.requirements_by_project.length === 0 ? (
                    <p className="assistant-muted">No project breakdown is available.</p>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead><tr><th>Project</th><th>Requirements</th><th>Requested headcount</th></tr></thead>
                        <tbody>
                          {result.requirements_by_project.map((item) => (
                            <tr key={item.project_id}>
                              <td>
                                <strong>{item.project_name}</strong>
                                <div className="assistant-muted">{item.project_id}</div>
                              </td>
                              <td>{item.requirement_count}</td>
                              <td>{item.requested_headcount}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <h3>Requirements by priority</h3>
                  {result.requirements_by_priority.length === 0 ? (
                    <p className="assistant-muted">No priority breakdown is available.</p>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead><tr><th>Priority</th><th>Requirements</th><th>Requested headcount</th></tr></thead>
                        <tbody>
                          {result.requirements_by_priority.map((item) => (
                            <tr key={item.name}>
                              <td>{item.name}</td>
                              <td>{item.requirement_count}</td>
                              <td>{item.requested_headcount}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <h3>Requirements by required skill</h3>
                  {result.requirements_by_skill.length === 0 ? (
                    <p className="assistant-muted">No required-skill breakdown is available.</p>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead><tr><th>Skill</th><th>Requirements</th><th>Requested headcount</th></tr></thead>
                        <tbody>
                          {result.requirements_by_skill.map((item) => (
                            <tr key={item.name}>
                              <td>{item.name}</td>
                              <td>{item.requirement_count}</td>
                              <td>{item.requested_headcount}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  <h3>Recorded requirement details</h3>
                  {result.requirements.length === 0 ? (
                    <div className="assistant-empty-state">
                      No staffing requirements were found.
                    </div>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead>
                          <tr>
                            <th>Role / project</th>
                            <th>Requested headcount</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Experience</th>
                            <th>Required skills</th>
                            <th>Start date</th>
                            <th>End date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.requirements.map((requirement) => (
                            <tr key={requirement.staffing_requirement_id}>
                              <td>
                                <strong>{requirement.role_name}</strong>
                                <div className="assistant-muted">{requirement.project_name}</div>
                                <div className="assistant-muted">ID: {requirement.staffing_requirement_id}</div>
                              </td>
                              <td>{requirement.required_quantity}</td>
                              <td>{requirement.status}</td>
                              <td>{requirement.priority}</td>
                              <td>{requirement.required_experience} years</td>
                              <td>{requirement.required_skills.length > 0 ? requirement.required_skills.join(', ') : '—'}</td>
                              <td>{requirement.start_date || '—'}</td>
                              <td>{requirement.end_date || '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}

              {isUtilizationResult(result) && (
                <>
                  <div className="assistant-result-summary">
                    <strong>
                      {result.active_employee_count} active employee(s)
                    </strong>
                    <span className="assistant-muted">
                      {result.result_count} employee record(s) displayed
                    </span>
                    {result.has_more_results && (
                      <span className="assistant-muted">
                        Additional employee records exist beyond this limit.
                      </span>
                    )}
                  </div>

                  <dl className="assistant-detail-grid">
                    <div>
                      <dt>Average utilization</dt>
                      <dd>{result.average_utilization_percentage.toFixed(2)}%</dd>
                    </div>
                    <div>
                      <dt>Average available capacity</dt>
                      <dd>{result.average_available_capacity_percentage.toFixed(2)}%</dd>
                    </div>
                  </dl>

                  <p className="assistant-notice">
                    Utilization reflects the current allocation records used by
                    the backend calculation. Available capacity is calculated
                    as the remaining percentage up to 100%; it is not a staffing
                    recommendation or a forecast.
                  </p>

                  {result.employees.length === 0 ? (
                    <div className="assistant-empty-state">
                      No active employee utilization records were returned.
                    </div>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead>
                          <tr>
                            <th>Employee</th>
                            <th>Designation</th>
                            <th>Department</th>
                            <th>Utilization</th>
                            <th>Available capacity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.employees.map((employee) => (
                            <tr key={employee.employee_id}>
                              <td>
                                <strong>{employee.name}</strong>
                                <div className="assistant-muted">
                                  {employee.employee_code}
                                </div>
                              </td>
                              <td>{employee.designation || '—'}</td>
                              <td>{employee.department || '—'}</td>
                              <td>{employee.utilization_percentage.toFixed(2)}%</td>
                              <td>{employee.available_capacity_percentage.toFixed(2)}%</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}

              {isCapacityResult(result) && (
                <>
                  <div className="assistant-result-summary">
                    <strong>
                      {result.active_employee_count} active employee(s)
                    </strong>
                    <span className="assistant-muted">
                      Reporting date: {result.reporting_date}
                    </span>
                    <span className="assistant-muted">
                      {result.result_count} employee record(s) displayed
                    </span>
                    {result.has_more_results && (
                      <span className="assistant-muted">
                        Additional employee records exist beyond this limit.
                      </span>
                    )}
                  </div>

                  <dl className="assistant-detail-grid">
                    <div>
                      <dt>Average allocated capacity</dt>
                      <dd>
                        {result.average_allocated_capacity_percentage.toFixed(2)}%
                      </dd>
                    </div>
                    <div>
                      <dt>Average available capacity</dt>
                      <dd>
                        {result.average_available_capacity_percentage.toFixed(2)}%
                      </dd>
                    </div>
                    <div>
                      <dt>No available capacity</dt>
                      <dd>{result.employees_with_no_available_capacity_count}</dd>
                    </div>
                    <div>
                      <dt>Partial available capacity</dt>
                      <dd>{result.employees_with_partial_available_capacity_count}</dd>
                    </div>
                    <div>
                      <dt>Full available capacity</dt>
                      <dd>{result.employees_with_full_available_capacity_count}</dd>
                    </div>
                  </dl>

                  <p className="assistant-notice">
                    Capacity is calculated from active allocations that cover
                    the reporting date. Available capacity is limited to a
                    minimum of 0%; allocated capacity is shown as recorded.
                    This summary does not forecast future demand or change
                    allocation records.
                  </p>

                  {result.employees.length === 0 ? (
                    <div className="assistant-empty-state">
                      No active employee capacity records were returned.
                    </div>
                  ) : (
                    <div className="assistant-table-wrap">
                      <table className="assistant-table">
                        <thead>
                          <tr>
                            <th>Employee</th>
                            <th>Designation</th>
                            <th>Department</th>
                            <th>Allocated capacity</th>
                            <th>Available capacity</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.employees.map((employee) => (
                            <tr key={employee.employee_id}>
                              <td>
                                <strong>{employee.name}</strong>
                                <div className="assistant-muted">
                                  {employee.employee_code}
                                </div>
                              </td>
                              <td>{employee.designation || '—'}</td>
                              <td>{employee.department || '—'}</td>
                              <td>
                                {employee.allocated_capacity_percentage.toFixed(2)}%
                              </td>
                              <td>
                                {employee.available_capacity_percentage.toFixed(2)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </>
              )}

              {isRecommendationResult(result) && (
                <>
                  <RequirementSummary requirement={result.staffing_requirement} />

                  <div className="assistant-result-summary">
                    <strong>
                      {result.result_count} candidate(s) returned
                    </strong>
                    <span className="assistant-muted">
                      {result.eligible_candidate_count} eligible candidate(s) found
                    </span>
                    {result.has_more_results && (
                      <span className="assistant-muted">
                        More eligible candidates exist beyond this limit.
                      </span>
                    )}
                  </div>

                  <p className="assistant-notice">{result.notice}</p>

                  {result.candidates.length === 0 ? (
                    <div className="assistant-empty-state">
                      No eligible candidates were found for this requirement.
                      Check the requirement ID or review its criteria.
                    </div>
                  ) : (
                    <div className="assistant-recommendation-list">
                      {result.candidates.map((candidate) => (
                        <article
                          className="assistant-detail-card"
                          key={candidate.employee_id}
                        >
                          <div className="assistant-recommendation-heading">
                            <div>
                              <p className="assistant-eyebrow">
                                RANK #{candidate.rank}
                              </p>
                              <h3>{candidate.name}</h3>
                              <p className="assistant-muted">
                                {candidate.employee_code}
                                {' · '}
                                {candidate.designation || 'No designation'}
                                {' · '}
                                {candidate.department || 'No department'}
                              </p>
                            </div>
                            <div>
                              <strong>{formatScore(candidate.score)}</strong>
                              <p className="assistant-muted">Overall score</p>
                            </div>
                          </div>

                          <dl className="assistant-detail-grid">
                            <div>
                              <dt>Experience</dt>
                              <dd>{candidate.experience_years} years</dd>
                            </div>
                            <div>
                              <dt>Availability</dt>
                              <dd>
                                {formatAvailability(candidate.availability_status)}
                              </dd>
                            </div>
                            <div>
                              <dt>Utilization for requirement period</dt>
                              <dd>{candidate.utilization_percentage}%</dd>
                            </div>
                            <div>
                              <dt>Remaining capacity</dt>
                              <dd>{candidate.remaining_capacity_percentage}%</dd>
                            </div>
                            <div>
                              <dt>Location</dt>
                              <dd>{candidate.location || '—'}</dd>
                            </div>
                          </dl>

                          <h4>Score breakdown</h4>
                          <dl className="assistant-detail-grid">
                            {SCORE_COMPONENTS.map((component) => (
                              <div key={component.key}>
                                <dt>{component.label}</dt>
                                <dd>
                                  {formatScore(
                                    candidate.score_breakdown[component.key],
                                  )}
                                </dd>
                              </div>
                            ))}
                          </dl>

                          <h4>Matched skills</h4>
                          {candidate.matched_skills.length > 0 ? (
                            <p>
                              {candidate.matched_skills.join(', ')}
                            </p>
                          ) : (
                            <p className="assistant-muted">
                              No matched skills were returned.
                            </p>
                          )}

                          <h4>Recommendation explanation</h4>
                          <p>{candidate.recommendation_reason}</p>

                          <button
                            type="button"
                            className="assistant-secondary-button"
                            disabled={loading}
                            onClick={() =>
                              void showEmployeeDetail(candidate.employee_id)
                            }
                          >
                            View employee details
                          </button>
                        </article>
                      ))}
                    </div>
                  )}
                </>
              )}
            </section>
          )}
        </>
      )}
    </section>
  )
}

interface RequirementSummaryProps {
  requirement: StaffingRequirement
}

function RequirementSummary({ requirement }: RequirementSummaryProps) {
  return (
    <div className="assistant-requirement-summary">
      <h3>{requirement.role_name}</h3>
      <p>
        Requirement ID: {requirement.staffing_requirement_id}
      </p>
      <p>
        Required quantity: {requirement.required_quantity}
        {' · '}
        Required experience: {requirement.required_experience} years
      </p>
      <p>
        Required proficiency: {requirement.required_proficiency || 'Not specified'}
      </p>
      <p>Status: {requirement.status}</p>
    </div>
  )
}

interface ResultTableProps {
  count: number
  hasMore: boolean
  employees: Employee[]
  renderEmployee: (employee: Employee) => ReactNode
}

function ResultTable({
  count,
  hasMore,
  employees,
  renderEmployee,
}: ResultTableProps) {
  return (
    <>
      <div className="assistant-result-summary">
        <strong>{count} result(s)</strong>
        {hasMore && (
          <span className="assistant-muted">
            More results are available beyond this limit.
          </span>
        )}
      </div>

      {employees.length === 0 ? (
        <div className="assistant-empty-state">
          No employees matched this inquiry. Try changing the filters.
        </div>
      ) : (
        <div className="assistant-table-wrap">
          <table className="assistant-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Designation</th>
                <th>Department</th>
                <th>Experience</th>
                <th>Availability</th>
                <th>Utilization</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>{employees.map(renderEmployee)}</tbody>
          </table>
        </div>
      )}
    </>
  )
}

export default AssistantPage