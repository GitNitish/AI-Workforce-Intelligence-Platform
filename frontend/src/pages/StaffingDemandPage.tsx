import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  calculateAnalyticsData,
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'
import {
  DEFAULT_ANALYTICS_FILTERS,
  filterAnalyticsSources,
  type AnalyticsFilters,
} from '../services/analyticsFilters'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function StaffingDemandPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [filters, setFilters] = useState<AnalyticsFilters>(
    DEFAULT_ANALYTICS_FILTERS,
  )

  const filterOptions = useMemo(() => {
    if (!data) {
      return {
        projects: [] as AnalyticsData['projects'],
        projectStatuses: [] as string[],
        projectPriorities: [] as string[],
        staffingPriorities: [] as string[],
        staffingStatuses: [] as string[],
      }
    }

    const projects = [...data.projects].sort(
      (first, second) =>
        first.project_name.localeCompare(
          second.project_name,
        ),
    )

    const projectStatuses = Array.from(
      new Set(
        data.projects.map(
          (project) => project.status,
        ),
      ),
    ).sort()

    const projectPriorities = Array.from(
      new Set(
        data.projects.map(
          (project) => project.priority,
        ),
      ),
    ).sort()

    const staffingPriorities = Array.from(
      new Set(
        data.staffingRequirements.map(
          (requirement) =>
            requirement.priority,
        ),
      ),
    ).sort()

    const staffingStatuses = Array.from(
      new Set(
        data.staffingRequirements.map(
          (requirement) =>
            requirement.status,
        ),
      ),
    ).sort()

    return {
      projects,
      projectStatuses,
      projectPriorities,
      staffingPriorities,
      staffingStatuses,
    }
  }, [data])

  const filteredData = useMemo(() => {
    if (!data) {
      return null
    }

    const filteredSources =
      filterAnalyticsSources(
        data,
        filters,
      )

    return calculateAnalyticsData(
      filteredSources,
    )
  }, [data, filters])

  const updateFilter = (
    key: keyof AnalyticsFilters,
    value: string,
  ) => {
    setFilters((current) => ({
      ...current,
      [key]: value || null,
    }))
  }

  const resetFilters = () => {
    setFilters({
      ...DEFAULT_ANALYTICS_FILTERS,
    })
  }

  const hasActiveFilters = Object.values(
    filters,
  ).some((value) => Boolean(value))

  useEffect(() => {
    let cancelled = false

    async function loadAnalytics() {
      try {
        setLoading(true)
        setError(null)

        const analyticsData =
          await getAnalyticsData()

        if (!cancelled) {
          setData(analyticsData)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load staffing analytics.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadAnalytics()

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <section>
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <h2>
          Staffing &amp; Demand Analytics
        </h2>

        <p>
          Detailed view of current staffing
          requirements and workforce demand.
        </p>

        <div className="loading-message">
          Loading staffing analytics...
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section>
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <h2>
          Staffing &amp; Demand Analytics
        </h2>

        <p>
          Detailed view of current staffing
          requirements and workforce demand.
        </p>

        <div className="error-message">
          {error}
        </div>
      </section>
    )
  }

  if (!data) {
    return (
      <section>
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <h2>
          Staffing &amp; Demand Analytics
        </h2>

        <p>
          Detailed view of current staffing
          requirements and workforce demand.
        </p>

        <div className="empty-message">
          No staffing analytics data is
          available.
        </div>
      </section>
    )
  }

  const analyticsData = filteredData

  if (!analyticsData) {
    return null
  }

  const { staffing } = analyticsData

  const maxPriorityDemand =
    staffing.priorityDemand[0]?.demand ?? 1

  const maxProjectDemand =
    staffing.projectDemand[0]?.demand ?? 1

  const maxRoleDemand =
    staffing.roleDemand[0]?.demand ?? 1

  const maxStatusDemand =
    staffing.statusDemand[0]?.demand ?? 1

  const openRequirements =
    analyticsData.staffingRequirements
      .filter(
        (requirement) =>
          requirement.status
            .trim()
            .toLowerCase() === 'open',
      )
      .sort(
        (first, second) =>
          second.required_quantity -
          first.required_quantity,
      )

  return (
    <section className="analytics-page">
      <div className="analytics-detail-back">
        <Link to="/analytics">
          ← Back to Executive Analytics
        </Link>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns:
            'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '12px',
          marginBottom: '24px',
          padding: '16px',
          borderRadius: '12px',
          background:
            'var(--surface-secondary, #f8fafc)',
          border:
            '1px solid var(--border-color, #e2e8f0)',
        }}
      >
        <label
          style={{
            display: 'grid',
            gap: '6px',
          }}
        >
          <span>Project</span>

          <select
            value={filters.projectId ?? ''}
            onChange={(event) =>
              updateFilter(
                'projectId',
                event.target.value,
              )
            }
          >
            <option value="">
              All Projects
            </option>

            {filterOptions.projects.map(
              (project) => (
                <option
                  key={project.project_id}
                  value={project.project_id}
                >
                  {project.project_name}
                </option>
              ),
            )}
          </select>
        </label>

        <label
          style={{
            display: 'grid',
            gap: '6px',
          }}
        >
          <span>Project Status</span>

          <select
            value={filters.projectStatus ?? ''}
            onChange={(event) =>
              updateFilter(
                'projectStatus',
                event.target.value,
              )
            }
          >
            <option value="">
              All Statuses
            </option>

            {filterOptions.projectStatuses.map(
              (value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ),
            )}
          </select>
        </label>

        <label
          style={{
            display: 'grid',
            gap: '6px',
          }}
        >
          <span>Project Priority</span>

          <select
            value={filters.projectPriority ?? ''}
            onChange={(event) =>
              updateFilter(
                'projectPriority',
                event.target.value,
              )
            }
          >
            <option value="">
              All Priorities
            </option>

            {filterOptions.projectPriorities.map(
              (value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ),
            )}
          </select>
        </label>

        <label
          style={{
            display: 'grid',
            gap: '6px',
          }}
        >
          <span>Staffing Priority</span>

          <select
            value={filters.staffingPriority ?? ''}
            onChange={(event) =>
              updateFilter(
                'staffingPriority',
                event.target.value,
              )
            }
          >
            <option value="">
              All Staffing Priorities
            </option>

            {filterOptions.staffingPriorities.map(
              (value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ),
            )}
          </select>
        </label>

        <label
          style={{
            display: 'grid',
            gap: '6px',
          }}
        >
          <span>Staffing Status</span>

          <select
            value={filters.staffingStatus ?? ''}
            onChange={(event) =>
              updateFilter(
                'staffingStatus',
                event.target.value,
              )
            }
          >
            <option value="">
              All Staffing Statuses
            </option>

            {filterOptions.staffingStatuses.map(
              (value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ),
            )}
          </select>
        </label>

        {hasActiveFilters && (
          <button
            type="button"
            onClick={resetFilters}
            style={{
              alignSelf: 'end',
              minHeight: '40px',
            }}
          >
            Reset Filters
          </button>
        )}
      </div>

      <div className="analytics-header">
        <div>
          <h2>
            Staffing &amp; Demand Analytics
          </h2>

          <p>
            Detailed view of current staffing
            requirements and workforce demand.
          </p>
        </div>
      </div>

      <div className="analytics-detail-kpi-grid">
        <div className="analytics-detail-card">
          <span>Open Requirements</span>

          <strong>
            {staffing.openRequirements}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Open Demand</span>

          <strong>
            {staffing.openDemand}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>High Priority</span>

          <strong>
            {staffing.priorityDemand.find(
              (item) =>
                item.label.toLowerCase() ===
                'high',
            )?.demand ?? 0}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Medium Priority</span>

          <strong>
            {staffing.priorityDemand.find(
              (item) =>
                item.label.toLowerCase() ===
                'medium',
            )?.demand ?? 0}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Low Priority</span>

          <strong>
            {staffing.priorityDemand.find(
              (item) =>
                item.label.toLowerCase() ===
                'low',
            )?.demand ?? 0}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Demand Categories</span>

          <strong>
            {staffing.roleDemand.length}
          </strong>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>
                Demand by Priority
              </h3>

              <p>
                Open demand distributed across
                requirement priorities.
              </p>
            </div>
          </div>

          {staffing.priorityDemand.length ===
          0 ? (
            <div className="analytics-empty-chart">
              No open staffing demand
              available.
            </div>
          ) : (
            <div className="analytics-band-list">
              {staffing.priorityDemand.map(
                (item) => (
                  <div
                    className="analytics-band-row"
                    key={item.label}
                  >
                    <div className="analytics-band-info">
                      <span>
                        {item.label}
                      </span>

                      <strong>
                        {item.demand}
                      </strong>
                    </div>

                    <div className="analytics-band-track">
                      <div
                        className="analytics-band-fill"
                        style={{
                          width: `${
                            (item.demand /
                              maxPriorityDemand) *
                            100
                          }%`,
                        }}
                      />
                    </div>

                    <small>
                      {formatPercentage(
                        item.percentage,
                      )}
                    </small>
                  </div>
                ),
              )}
            </div>
          )}
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>
                Demand by Project
              </h3>

              <p>
                Open staffing demand across
                projects.
              </p>
            </div>
          </div>

          {staffing.projectDemand.length ===
          0 ? (
            <div className="analytics-empty-chart">
              No project demand available.
            </div>
          ) : (
            <div className="analytics-band-list">
              {staffing.projectDemand.map(
                (item) => (
                  <div
                    className="analytics-band-row"
                    key={item.projectId}
                  >
                    <div className="analytics-band-info">
                      <span
                        title={item.projectName}
                      >
                        {item.projectName}
                      </span>

                      <strong>
                        {item.demand}
                      </strong>
                    </div>

                    <div className="analytics-band-track">
                      <div
                        className="analytics-band-fill"
                        style={{
                          width: `${
                            (item.demand /
                              maxProjectDemand) *
                            100
                          }%`,
                        }}
                      />
                    </div>

                    <small>
                      {formatPercentage(
                        item.percentage,
                      )}
                    </small>
                  </div>
                ),
              )}
            </div>
          )}
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>
                Demand by Role
              </h3>

              <p>
                Roles with current open
                staffing demand.
              </p>
            </div>
          </div>

          {staffing.roleDemand.length === 0 ? (
            <div className="analytics-empty-chart">
              No role demand available.
            </div>
          ) : (
            <div className="analytics-band-list">
              {staffing.roleDemand.map(
                (item) => (
                  <div
                    className="analytics-band-row"
                    key={item.roleName}
                  >
                    <div className="analytics-band-info">
                      <span
                        title={item.roleName}
                      >
                        {item.roleName}
                      </span>

                      <strong>
                        {item.demand}
                      </strong>
                    </div>

                    <div className="analytics-band-track">
                      <div
                        className="analytics-band-fill"
                        style={{
                          width: `${
                            (item.demand /
                              maxRoleDemand) *
                            100
                          }%`,
                        }}
                      />
                    </div>

                    <small>
                      {formatPercentage(
                        item.percentage,
                      )}
                    </small>
                  </div>
                ),
              )}
            </div>
          )}
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>
                Requirement Status
              </h3>

              <p>
                Requirement volume across
                current statuses.
              </p>
            </div>
          </div>

          {staffing.statusDemand.length ===
          0 ? (
            <div className="analytics-empty-chart">
              No staffing requirements
              available.
            </div>
          ) : (
            <div className="analytics-band-list">
              {staffing.statusDemand.map(
                (item) => (
                  <div
                    className="analytics-band-row"
                    key={item.status}
                  >
                    <div className="analytics-band-info">
                      <span
                        title={item.status}
                      >
                        {item.status}
                      </span>

                      <strong>
                        {item.demand}
                      </strong>
                    </div>

                    <div className="analytics-band-track">
                      <div
                        className="analytics-band-fill"
                        style={{
                          width: `${
                            (item.demand /
                              maxStatusDemand) *
                            100
                          }%`,
                        }}
                      />
                    </div>

                    <small>
                      {formatPercentage(
                        item.percentage,
                      )}
                    </small>
                  </div>
                ),
              )}
            </div>
          )}
        </div>
      </div>

      <div className="analytics-panel analytics-employee-panel">
        <div className="analytics-panel-header">
          <div>
            <h3>
              Open Staffing Requirements
            </h3>

            <p>
              Current requirements contributing
              to open workforce demand.
            </p>
          </div>

          <strong className="analytics-panel-value">
            {staffing.openRequirements}
          </strong>
        </div>

        {openRequirements.length === 0 ? (
          <div className="analytics-empty-chart">
            No open staffing requirements
            available.
          </div>
        ) : (
          <div className="analytics-table-wrapper">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Project</th>
                  <th>Demand</th>
                  <th>Priority</th>
                  <th>Experience</th>
                  <th>Start Date</th>
                </tr>
              </thead>

              <tbody>
                {openRequirements.map(
                  (requirement) => {
                    const project =
                      analyticsData.projects.find(
                        (item) =>
                          item.project_id ===
                          requirement.project_id,
                      )

                    return (
                      <tr
                        key={
                          requirement.staffing_requirement_id
                        }
                      >
                        <td>
                          <strong>
                            {
                              requirement.role_name
                            }
                          </strong>
                        </td>

                        <td>
                          {project?.project_name ??
                            'Unknown Project'}
                        </td>

                        <td>
                          {
                            requirement.required_quantity
                          }
                        </td>

                        <td>
                          {requirement.priority}
                        </td>

                        <td>
                          {
                            requirement.required_experience
                          }
                          {' years'}
                        </td>

                        <td>
                          {requirement.start_date ??
                            '—'}
                        </td>
                      </tr>
                    )
                  },
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}

export default StaffingDemandPage