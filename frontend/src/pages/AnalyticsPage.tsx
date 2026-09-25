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
  getAnalyticsFilterOptions,
  hasActiveAnalyticsFilters,
  type AnalyticsFilters,
} from '../services/analyticsFilters'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [filters, setFilters] = useState<AnalyticsFilters>(
    DEFAULT_ANALYTICS_FILTERS,
  )
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadAnalytics() {
      try {
        setLoading(true)
        setError(null)

        const analyticsData = await getAnalyticsData()

        if (!cancelled) {
          setData(analyticsData)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load analytics data.',
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

  const filterOptions = useMemo(() => {
    if (!data) {
      return null
    }

    return getAnalyticsFilterOptions(data)
  }, [data])

  const filteredData = useMemo(() => {
    if (!data) {
      return null
    }

    const filteredSources = filterAnalyticsSources(
      data,
      filters,
    )

    return calculateAnalyticsData(filteredSources)
  }, [data, filters])

  function updateFilter<K extends keyof AnalyticsFilters>(
    key: K,
    value: AnalyticsFilters[K],
  ) {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }))
  }

  function resetFilters() {
    setFilters({ ...DEFAULT_ANALYTICS_FILTERS })
  }

  if (loading) {
    return (
      <section>
        <h2>Executive Analytics</h2>
        <p>
          Workforce utilization, capacity and staffing insights.
        </p>

        <div className="loading-message">
          Loading analytics...
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section>
        <h2>Executive Analytics</h2>
        <p>
          Workforce utilization, capacity and staffing insights.
        </p>

        <div className="error-message">
          {error}
        </div>
      </section>
    )
  }

  if (!data || !filteredData || !filterOptions) {
    return (
      <section>
        <h2>Executive Analytics</h2>
        <p>
          Workforce utilization, capacity and staffing insights.
        </p>

        <div className="empty-message">
          No analytics data is available.
        </div>
      </section>
    )
  }

  const {
    utilization,
    capacity,
    staffing,
    projectAnalytics,
  } = filteredData

  const totalEmployees = filteredData.employees.length

  const allocatedEmployees =
    filteredData.employeeUtilization.filter(
      (employee) =>
        employee.utilizationPercentage > 0,
    ).length

  const allocationMix =
    projectAnalytics.projectAllocations

  const maxAllocationPercentage =
    allocationMix[0]?.allocationShare ?? 1

  const distributionItems = [
    {
      label: 'Bench',
      count: utilization.distribution.bench,
    },
    {
      label: 'Low',
      count: utilization.distribution.low,
    },
    {
      label: 'Moderate',
      count: utilization.distribution.moderate,
    },
    {
      label: 'High',
      count: utilization.distribution.high,
    },
    {
      label: 'Fully Utilized',
      count: utilization.distribution.fullyUtilized,
    },
  ]

  const filtersActive = hasActiveAnalyticsFilters(filters)

  return (
    <section className="analytics-page">
      <div className="analytics-header">
        <div>
          <h2>Executive Analytics</h2>
          <p>
            Workforce utilization, capacity and staffing insights.
          </p>
        </div>
      </div>

      <div
        className="analytics-panel"
        style={{
          marginBottom: '14px',
        }}
      >
        <div
          className="analytics-panel-header"
          style={{
            marginBottom: '14px',
          }}
        >
          <div>
            <h3>Analytics Filters</h3>
            <p>
              Filter the executive view by workforce,
              project and staffing dimensions.
            </p>
          </div>

          {filtersActive && (
            <button
              type="button"
              onClick={resetFilters}
              style={{
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#374151',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: 600,
                padding: '7px 11px',
              }}
            >
              Reset Filters
            </button>
          )}
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns:
              'repeat(4, minmax(0, 1fr))',
            gap: '10px',
          }}
        >
          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Department
            </span>

            <select
              value={filters.department ?? ''}
              onChange={(event) =>
                updateFilter(
                  'department',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Departments
              </option>

              {filterOptions.departments.map(
                (department) => (
                  <option
                    key={department}
                    value={department}
                  >
                    {department}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Designation
            </span>

            <select
              value={filters.designation ?? ''}
              onChange={(event) =>
                updateFilter(
                  'designation',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Designations
              </option>

              {filterOptions.designations.map(
                (designation) => (
                  <option
                    key={designation}
                    value={designation}
                  >
                    {designation}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Project
            </span>

            <select
              value={filters.projectId ?? ''}
              onChange={(event) =>
                updateFilter(
                  'projectId',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Projects
              </option>

              {filterOptions.projects.map(
                (project) => (
                  <option
                    key={project.id}
                    value={project.id}
                  >
                    {project.name}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Project Status
            </span>

            <select
              value={filters.projectStatus ?? ''}
              onChange={(event) =>
                updateFilter(
                  'projectStatus',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Project Statuses
              </option>

              {filterOptions.projectStatuses.map(
                (status) => (
                  <option
                    key={status}
                    value={status}
                  >
                    {status}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Project Priority
            </span>

            <select
              value={filters.projectPriority ?? ''}
              onChange={(event) =>
                updateFilter(
                  'projectPriority',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Project Priorities
              </option>

              {filterOptions.projectPriorities.map(
                (priority) => (
                  <option
                    key={priority}
                    value={priority}
                  >
                    {priority}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Allocation Status
            </span>

            <select
              value={filters.allocationStatus ?? ''}
              onChange={(event) =>
                updateFilter(
                  'allocationStatus',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Allocation Statuses
              </option>

              {filterOptions.allocationStatuses.map(
                (status) => (
                  <option
                    key={status}
                    value={status}
                  >
                    {status}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Staffing Priority
            </span>

            <select
              value={filters.staffingPriority ?? ''}
              onChange={(event) =>
                updateFilter(
                  'staffingPriority',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Staffing Priorities
              </option>

              {filterOptions.staffingPriorities.map(
                (priority) => (
                  <option
                    key={priority}
                    value={priority}
                  >
                    {priority}
                  </option>
                ),
              )}
            </select>
          </label>

          <label
            style={{
              display: 'grid',
              gap: '5px',
            }}
          >
            <span
              style={{
                color: '#6b7280',
                fontSize: '9px',
                fontWeight: 700,
                textTransform: 'uppercase',
              }}
            >
              Staffing Status
            </span>

            <select
              value={filters.staffingStatus ?? ''}
              onChange={(event) =>
                updateFilter(
                  'staffingStatus',
                  event.target.value || null,
                )
              }
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                background: '#ffffff',
                color: '#172033',
                fontSize: '11px',
                padding: '8px',
              }}
            >
              <option value="">
                All Staffing Statuses
              </option>

              {filterOptions.staffingStatuses.map(
                (status) => (
                  <option
                    key={status}
                    value={status}
                  >
                    {status}
                  </option>
                ),
              )}
            </select>
          </label>
        </div>

        <div
          style={{
            marginTop: '10px',
            color: '#9ca3af',
            fontSize: '9px',
          }}
        >
          {filtersActive
            ? 'Dashboard metrics are recalculated from the selected filters.'
            : 'Showing the complete workforce analytics dataset.'}
        </div>
      </div>

      <div className="analytics-kpi-grid">
        <div className="analytics-kpi-card">
          <span>Total Workforce</span>
          <strong>{totalEmployees}</strong>
          <small>
            {allocatedEmployees} currently allocated
          </small>
        </div>

        <div className="analytics-kpi-card">
          <span>Average Utilization</span>
          <strong>
            {formatPercentage(
              utilization.averageUtilization,
            )}
          </strong>
          <small>
            Across the filtered workforce
          </small>
        </div>

        <div className="analytics-kpi-card">
          <span>Bench</span>
          <strong>
            {utilization.benchEmployees}
          </strong>
          <small>
            {formatPercentage(
              utilization.benchPercentage,
            )}{' '}
            of filtered workforce
          </small>
        </div>

        <div className="analytics-kpi-card">
          <span>Open Demand</span>
          <strong>{staffing.openDemand}</strong>
          <small>
            {staffing.openRequirements}{' '}
            open requirements
          </small>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Utilization Distribution</h3>
              <p>
                Current workforce allocation levels.
              </p>
            </div>
          </div>

          <div className="analytics-bars">
            {distributionItems.map((item) => {
              const percentage =
                totalEmployees > 0
                  ? (item.count / totalEmployees) * 100
                  : 0

              return (
                <div
                  className="analytics-bar-row"
                  key={item.label}
                >
                  <div className="analytics-bar-label">
                    <span>{item.label}</span>
                    <strong>
                      {item.count} (
                      {percentage.toFixed(1)}%)
                    </strong>
                  </div>

                  <div className="analytics-bar-track">
                    <div
                      className="analytics-bar-fill"
                      style={{
                        width: `${percentage}%`,
                      }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Capacity &amp; Bench</h3>
              <p>
                Current workforce capacity allocation.
              </p>
            </div>
          </div>

          <div className="capacity-summary">
            <div>
              <span>Total Capacity</span>
              <strong>
                {capacity.totalCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Allocated</span>
              <strong>
                {capacity.allocatedCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Available</span>
              <strong>
                {capacity.availableCapacity.toFixed(0)}%
              </strong>
            </div>
          </div>

          <div className="capacity-track">
            <div
              className="capacity-allocated"
              style={{
                width: `${Math.min(
                  capacity.utilizationPercentage,
                  100,
                )}%`,
              }}
            />
          </div>

          <div className="capacity-caption">
            <span>
              {formatPercentage(
                capacity.utilizationPercentage,
              )}{' '}
              capacity utilized
            </span>

            <span>
              {utilization.benchEmployees}{' '}
              bench employees
            </span>
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Staffing Demand</h3>
              <p>
                Open workforce demand by priority.
              </p>
            </div>

            <strong className="analytics-panel-value">
              {staffing.openDemand}
            </strong>
          </div>

          <div className="demand-list">
            {staffing.priorityDemand.map((item) => (
              <div
                className="demand-row"
                key={item.label}
              >
                <span>
                  {item.label} Priority
                </span>
                <strong>{item.demand}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Allocation Mix</h3>
              <p>
                Share of active allocated capacity by project.
              </p>
            </div>
          </div>

          {allocationMix.length === 0 ? (
            <div className="analytics-empty-chart">
              No active allocations available.
            </div>
          ) : (
            <div className="allocation-list">
              {allocationMix.map((project) => (
                <div
                  className="allocation-row"
                  key={project.projectId}
                >
                  <div className="allocation-row-header">
                    <span>
                      {project.projectName}
                    </span>
                    <strong>
                      {project.allocationShare.toFixed(0)}%
                    </strong>
                  </div>

                  <div className="analytics-bar-track">
                    <div
                      className="analytics-bar-fill"
                      style={{
                        width: `${
                          (project.allocationShare /
                            maxAllocationPercentage) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="analytics-detail-action">
        <div>
          <strong>
            Need a deeper utilization view?
          </strong>
          <span>
            Review employee-level utilization and current capacity.
          </span>
        </div>

        <Link
          className="analytics-detail-link"
          to="/analytics/utilization"
        >
          View Utilization Detail
          <span aria-hidden="true">→</span>
        </Link>
      </div>

      <div className="analytics-detail-action">
        <div>
          <strong>
            Need a deeper staffing view?
          </strong>
          <span>
            Explore open demand, priorities, projects and roles.
          </span>
        </div>

        <Link
          className="analytics-detail-link"
          to="/analytics/staffing"
        >
          View Staffing &amp; Demand Detail
          <span aria-hidden="true">→</span>
        </Link>
      </div>

      <div className="analytics-detail-action">
        <div>
          <strong>
            Need a deeper project view?
          </strong>
          <span>
            Review allocation mix and project-level workforce distribution.
          </span>
        </div>

        <Link
          className="analytics-detail-link"
          to="/analytics/projects"
        >
          View Project Analytics
          <span aria-hidden="true">→</span>
        </Link>
      </div>

      <div className="analytics-detail-action">
        <div>
          <strong>
            Need a deeper outlook view?
          </strong>
          <span>
            Review current capacity and workforce demand across upcoming months.
          </span>
        </div>

        <Link
          className="analytics-detail-link"
          to="/analytics/outlook"
        >
          View Workforce Outlook
          <span aria-hidden="true">→</span>
        </Link>
      </div>
    </section>
  )
}

export default AnalyticsPage