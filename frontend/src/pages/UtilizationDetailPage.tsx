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

function UtilizationDetailPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [filters, setFilters] = useState<AnalyticsFilters>({
    ...DEFAULT_ANALYTICS_FILTERS,
  })
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
              : 'Unable to load utilization analytics.',
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
      return {
        departments: [],
        designations: [],
        projects: [],
        projectStatuses: [],
        projectPriorities: [],
        allocationStatuses: [],
      }
    }

    const departments = Array.from(
      new Set(
        data.employees
          .map((employee) => employee.department)
          .filter(
            (department): department is string =>
              Boolean(department?.trim()),
          ),
      ),
    ).sort((first, second) =>
      first.localeCompare(second),
    )

    const designations = Array.from(
      new Set(
        data.employees
          .map((employee) => employee.designation)
          .filter(
            (designation): designation is string =>
              Boolean(designation?.trim()),
          ),
      ),
    ).sort((first, second) =>
      first.localeCompare(second),
    )

    const projects = [...data.projects].sort(
      (first, second) =>
        first.project_name.localeCompare(
          second.project_name,
        ),
    )

    const projectStatuses = Array.from(
      new Set(
        data.projects
          .map((project) => project.status)
          .filter((status) => Boolean(status?.trim())),
      ),
    ).sort((first, second) =>
      first.localeCompare(second),
    )

    const projectPriorities = Array.from(
      new Set(
        data.projects
          .map((project) => project.priority)
          .filter((priority) =>
            Boolean(priority?.trim()),
          ),
      ),
    ).sort((first, second) =>
      first.localeCompare(second),
    )

    const allocationStatuses = Array.from(
      new Set(
        data.allocations
          .map((allocation) => allocation.status)
          .filter((status) => Boolean(status?.trim())),
      ),
    ).sort((first, second) =>
      first.localeCompare(second),
    )

    return {
      departments,
      designations,
      projects,
      projectStatuses,
      projectPriorities,
      allocationStatuses,
    }
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

  const updateFilter = (
    key: keyof AnalyticsFilters,
    value: string,
  ) => {
    setFilters((currentFilters) => ({
      ...currentFilters,
      [key]: value || null,
    }))
  }

  const resetFilters = () => {
    setFilters({
      ...DEFAULT_ANALYTICS_FILTERS,
    })
  }

  const hasActiveFilters = Object.values(filters).some(
    (value) => Boolean(value),
  )

  if (loading) {
    return (
      <section className="analytics-page">
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE UTILIZATION
            </span>

            <h2>Utilization Detail</h2>

            <p>
              Detailed workforce utilization and capacity analysis.
            </p>
          </div>
        </div>

        <div className="loading-message">
          Loading utilization analytics...
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="analytics-page">
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE UTILIZATION
            </span>

            <h2>Utilization Detail</h2>

            <p>
              Detailed workforce utilization and capacity analysis.
            </p>
          </div>
        </div>

        <div className="error-message">
          {error}
        </div>
      </section>
    )
  }

  if (!data || !filteredData) {
    return (
      <section className="analytics-page">
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE UTILIZATION
            </span>

            <h2>Utilization Detail</h2>

            <p>
              Detailed workforce utilization and capacity analysis.
            </p>
          </div>
        </div>

        <div className="empty-message">
          No utilization data is available.
        </div>
      </section>
    )
  }

  const {
    utilization,
    capacity,
    employeeUtilization,
  } = filteredData

  const totalEmployees = employeeUtilization.length

  const maxUtilization =
    Math.max(
      utilization.highestUtilization,
      1,
    )

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

  return (
    <section className="analytics-page">
      <div className="analytics-detail-back">
        <Link to="/analytics">
          ← Back to Executive Analytics
        </Link>
      </div>

      <div className="page-heading">
        <div>
          <span className="page-eyebrow">
            WORKFORCE UTILIZATION
          </span>

          <h2>Utilization Detail</h2>

          <p>
            Detailed workforce utilization and capacity analysis.
          </p>
        </div>

        <div className="home-heading-meta">
          <span>Current workforce snapshot</span>

          <strong>
            {totalEmployees} employees
          </strong>
        </div>
      </div>

      <div
        className="analytics-panel"
        style={{
          marginBottom: '24px',
        }}
      >
        <div className="analytics-panel-header">
          <div>
            <span className="card-eyebrow">
              FILTERS
            </span>

            <h3>Workforce Scope</h3>

            <p>
              Refine utilization and capacity analysis
              using workforce and allocation attributes.
            </p>
          </div>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={resetFilters}
              style={{
                border: '1px solid var(--border-color, #d9dee7)',
                background: 'transparent',
                borderRadius: '8px',
                padding: '8px 12px',
                cursor: 'pointer',
                fontWeight: 600,
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
              'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '14px',
            marginTop: '18px',
          }}
        >
          <label
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              Department
            </span>

            <select
              value={filters.department ?? ''}
              onChange={(event) =>
                updateFilter(
                  'department',
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                padding: '9px 10px',
                borderRadius: '8px',
                border:
                  '1px solid var(--border-color, #d9dee7)',
                background:
                  'var(--card-background, #ffffff)',
              }}
            >
              <option value="">All departments</option>

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
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              Designation
            </span>

            <select
              value={filters.designation ?? ''}
              onChange={(event) =>
                updateFilter(
                  'designation',
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                padding: '9px 10px',
                borderRadius: '8px',
                border:
                  '1px solid var(--border-color, #d9dee7)',
                background:
                  'var(--card-background, #ffffff)',
              }}
            >
              <option value="">All designations</option>

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
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              Project
            </span>

            <select
              value={filters.projectId ?? ''}
              onChange={(event) =>
                updateFilter(
                  'projectId',
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                padding: '9px 10px',
                borderRadius: '8px',
                border:
                  '1px solid var(--border-color, #d9dee7)',
                background:
                  'var(--card-background, #ffffff)',
              }}
            >
              <option value="">All projects</option>

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
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              Project Status
            </span>

            <select
              value={filters.projectStatus ?? ''}
              onChange={(event) =>
                updateFilter(
                  'projectStatus',
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                padding: '9px 10px',
                borderRadius: '8px',
                border:
                  '1px solid var(--border-color, #d9dee7)',
                background:
                  'var(--card-background, #ffffff)',
              }}
            >
              <option value="">All statuses</option>

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
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              Project Priority
            </span>

            <select
              value={filters.projectPriority ?? ''}
              onChange={(event) =>
                updateFilter(
                  'projectPriority',
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                padding: '9px 10px',
                borderRadius: '8px',
                border:
                  '1px solid var(--border-color, #d9dee7)',
                background:
                  'var(--card-background, #ffffff)',
              }}
            >
              <option value="">All priorities</option>

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
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}
          >
            <span
              style={{
                fontSize: '0.8rem',
                fontWeight: 600,
              }}
            >
              Allocation Status
            </span>

            <select
              value={filters.allocationStatus ?? ''}
              onChange={(event) =>
                updateFilter(
                  'allocationStatus',
                  event.target.value,
                )
              }
              style={{
                width: '100%',
                padding: '9px 10px',
                borderRadius: '8px',
                border:
                  '1px solid var(--border-color, #d9dee7)',
                background:
                  'var(--card-background, #ffffff)',
              }}
            >
              <option value="">All allocation statuses</option>

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
        </div>

        {hasActiveFilters && (
          <div
            style={{
              marginTop: '14px',
              fontSize: '0.8rem',
              opacity: 0.72,
            }}
          >
            Showing filtered utilization and capacity
            results.
          </div>
        )}
      </div>

      <div className="analytics-detail-kpi-grid">
        <div className="analytics-detail-card">
          <span>Average</span>

          <strong>
            {formatPercentage(
              utilization.averageUtilization,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Median</span>

          <strong>
            {formatPercentage(
              utilization.medianUtilization,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Highest</span>

          <strong>
            {formatPercentage(
              utilization.highestUtilization,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Lowest</span>

          <strong>
            {formatPercentage(
              utilization.lowestUtilization,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Bench Employees</span>

          <strong>
            {utilization.benchEmployees}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Bench Percentage</span>

          <strong>
            {formatPercentage(
              utilization.benchPercentage,
            )}
          </strong>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <span className="card-eyebrow">
                DISTRIBUTION
              </span>

              <h3>Utilization Bands</h3>

              <p>
                Workforce distribution across utilization ranges.
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

          <div className="analytics-panel-footer">
            <span>
              Average workforce utilization
            </span>

            <strong>
              {formatPercentage(
                utilization.averageUtilization,
              )}
            </strong>
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <span className="card-eyebrow">
                CAPACITY
              </span>

              <h3>Capacity Overview</h3>

              <p>
                Current capacity position across the workforce.
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
              {utilization.benchEmployees} bench employees
            </span>
          </div>

          <div className="analytics-capacity-note">
            <span>Available capacity</span>

            <strong>
              {capacity.availableCapacity.toFixed(0)}%
            </strong>
          </div>
        </div>
      </div>

      <div className="analytics-section">
        <div className="analytics-section-header">
          <div>
            <span className="page-eyebrow">
              EMPLOYEE ANALYSIS
            </span>

            <h3>Employee Utilization</h3>

            <p>
              Current allocation and available capacity by employee.
            </p>
          </div>
        </div>

        {employeeUtilization.length === 0 ? (
          <div className="analytics-panel">
            <div className="analytics-empty-chart">
              No employee utilization data is available.
            </div>
          </div>
        ) : (
          <div className="analytics-panel analytics-employee-panel">
            <div className="analytics-table-wrapper">
              <table className="analytics-table">
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Department</th>
                    <th>Designation</th>
                    <th>Utilization</th>
                    <th>Available</th>
                  </tr>
                </thead>

                <tbody>
                  {employeeUtilization.map((employee) => (
                    <tr key={employee.employeeId}>
                      <td>
                        <strong>
                          {employee.employeeName}
                        </strong>

                        <small>
                          {employee.employeeCode}
                        </small>
                      </td>

                      <td>
                        {employee.department ?? '—'}
                      </td>

                      <td>
                        {employee.designation ?? '—'}
                      </td>

                      <td>
                        <div className="analytics-table-percentage">
                          <span>
                            {formatPercentage(
                              employee.utilizationPercentage,
                            )}
                          </span>

                          <div className="analytics-table-track">
                            <div
                              className="analytics-table-fill"
                              style={{
                                width: `${
                                  (employee.utilizationPercentage /
                                    maxUtilization) *
                                  100
                                }%`,
                              }}
                            />
                          </div>
                        </div>
                      </td>

                      <td>
                        {formatPercentage(
                          employee.availablePercentage,
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}

export default UtilizationDetailPage