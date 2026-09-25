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

function ProjectAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [filters, setFilters] = useState<AnalyticsFilters>(
    DEFAULT_ANALYTICS_FILTERS,
  )

  const filterOptions = useMemo(() => {
    if (!data) {
      return {
        departments: [] as string[],
        designations: [] as string[],
        projects: [] as AnalyticsData['projects'],
        projectStatuses: [] as string[],
        projectPriorities: [] as string[],
        allocationStatuses: [] as string[],
      }
    }

    const departments = Array.from(
      new Set(
        data.employees
          .map((employee) => employee.department)
          .filter((value): value is string => Boolean(value)),
      ),
    ).sort()

    const designations = Array.from(
      new Set(
        data.employees
          .map((employee) => employee.designation)
          .filter((value): value is string => Boolean(value)),
      ),
    ).sort()

    const projects = [...data.projects].sort((first, second) =>
      first.project_name.localeCompare(second.project_name),
    )

    const projectStatuses = Array.from(
      new Set(data.projects.map((project) => project.status)),
    ).sort()

    const projectPriorities = Array.from(
      new Set(data.projects.map((project) => project.priority)),
    ).sort()

    const allocationStatuses = Array.from(
      new Set(data.allocations.map((allocation) => allocation.status)),
    ).sort()

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

    const filteredSources = filterAnalyticsSources(data, filters)

    return calculateAnalyticsData(filteredSources)
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
    setFilters({ ...DEFAULT_ANALYTICS_FILTERS })
  }

  const hasActiveFilters = Object.values(filters).some(
    (value) => Boolean(value),
  )

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
              : 'Unable to load project analytics.',
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

        <h2>Project Allocation Analytics</h2>
        <p>
          Detailed view of project-level workforce allocation.
        </p>

        <div className="loading-message">
          Loading project analytics...
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

        <h2>Project Allocation Analytics</h2>
        <p>
          Detailed view of project-level workforce allocation.
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

        <h2>Project Allocation Analytics</h2>
        <p>
          Detailed view of project-level workforce allocation.
        </p>

        <div className="empty-message">
          No project analytics data is available.
        </div>
      </section>
    )
  }

  const analyticsData = filteredData

  if (!analyticsData) {
    return null
  }

  const { projectAnalytics } = analyticsData

  const maxAllocationShare =
    projectAnalytics.projectAllocations[0]?.allocationShare ?? 1

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
          <span>Department</span>

          <select
            value={filters.department ?? ''}
            onChange={(event) =>
              updateFilter(
                'department',
                event.target.value,
              )
            }
          >
            <option value="">
              All Departments
            </option>

            {filterOptions.departments.map(
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
          <span>Designation</span>

          <select
            value={filters.designation ?? ''}
            onChange={(event) =>
              updateFilter(
                'designation',
                event.target.value,
              )
            }
          >
            <option value="">
              All Designations
            </option>

            {filterOptions.designations.map(
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
          <span>Allocation Status</span>

          <select
            value={filters.allocationStatus ?? ''}
            onChange={(event) =>
              updateFilter(
                'allocationStatus',
                event.target.value,
              )
            }
          >
            <option value="">
              All Allocation Statuses
            </option>

            {filterOptions.allocationStatuses.map(
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
          <h2>Project Allocation Analytics</h2>

          <p>
            Detailed view of project-level workforce
            allocation.
          </p>
        </div>
      </div>

      <div className="analytics-detail-kpi-grid">
        <div className="analytics-detail-card">
          <span>Active Projects</span>

          <strong>
            {projectAnalytics.activeProjects}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Allocated Projects</span>

          <strong>
            {projectAnalytics.allocatedProjects}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Allocated Capacity</span>

          <strong>
            {formatPercentage(
              analyticsData.capacity
                .allocatedCapacity,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Average / Project</span>

          <strong>
            {formatPercentage(
              projectAnalytics
                .averageAllocationPerProject,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Largest Allocation</span>

          <strong>
            {formatPercentage(
              projectAnalytics
                .largestProjectAllocation,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Available Capacity</span>

          <strong>
            {formatPercentage(
              analyticsData.capacity
                .availableCapacity,
            )}
          </strong>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>
                Project Allocation Mix
              </h3>

              <p>
                Share of active allocated capacity
                by project.
              </p>
            </div>
          </div>

          {projectAnalytics
            .projectAllocations.length === 0 ? (
            <div className="analytics-empty-chart">
              No active project allocations
              available.
            </div>
          ) : (
            <div className="analytics-band-list">
              {projectAnalytics
                .projectAllocations.map(
                  (project) => (
                    <div
                      className="analytics-band-row"
                      key={project.projectId}
                    >
                      <div className="analytics-band-info">
                        <span
                          title={
                            project.projectName
                          }
                        >
                          {project.projectName}
                        </span>

                        <strong>
                          {project.allocationShare.toFixed(
                            1,
                          )}
                          %
                        </strong>
                      </div>

                      <div className="analytics-band-track">
                        <div
                          className="analytics-band-fill"
                          style={{
                            width: `${
                              (project.allocationShare /
                                maxAllocationShare) *
                              100
                            }%`,
                          }}
                        />
                      </div>

                      <small>
                        {project.allocatedCapacity.toFixed(
                          0,
                        )}
                        %
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
                Project Capacity Overview
              </h3>

              <p>
                Current workforce allocation
                across active projects.
              </p>
            </div>
          </div>

          {projectAnalytics
            .projectAllocations.length === 0 ? (
            <div className="analytics-empty-chart">
              No project allocation data
              available.
            </div>
          ) : (
            <div className="project-capacity-list">
              {projectAnalytics
                .projectAllocations.map(
                  (project) => (
                    <div
                      className="project-capacity-card"
                      key={project.projectId}
                    >
                      <div className="project-capacity-header">
                        <div>
                          <strong>
                            {project.projectName}
                          </strong>

                          <span>
                            {project.projectCode}
                          </span>
                        </div>

                        <strong>
                          {project.allocatedCapacity.toFixed(
                            0,
                          )}
                          %
                        </strong>
                      </div>

                      <div className="project-capacity-meta">
                        <span>
                          Client:{' '}
                          {project.clientName ??
                            '—'}
                        </span>

                        <span>
                          Status: {project.status}
                        </span>

                        <span>
                          Priority:{' '}
                          {project.priority}
                        </span>
                      </div>

                      <div className="project-capacity-stats">
                        <div>
                          <span>
                            Allocation Share
                          </span>

                          <strong>
                            {project.allocationShare.toFixed(
                              1,
                            )}
                            %
                          </strong>
                        </div>

                        <div>
                          <span>
                            Employees
                          </span>

                          <strong>
                            {project.allocatedEmployees}
                          </strong>
                        </div>

                        <div>
                          <span>
                            Active Allocations
                          </span>

                          <strong>
                            {project.activeAllocations}
                          </strong>
                        </div>
                      </div>
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
              Project Allocation Table
            </h3>

            <p>
              Detailed project-level allocation
              distribution.
            </p>
          </div>

          <strong className="analytics-panel-value">
            {projectAnalytics.allocatedProjects}
          </strong>
        </div>

        {projectAnalytics
          .projectAllocations.length === 0 ? (
          <div className="analytics-empty-chart">
            No active project allocations
            available.
          </div>
        ) : (
          <div className="analytics-table-wrapper">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Client</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Allocated</th>
                  <th>Mix Share</th>
                  <th>Employees</th>
                  <th>Allocations</th>
                </tr>
              </thead>

              <tbody>
                {projectAnalytics
                  .projectAllocations.map(
                    (project) => (
                      <tr
                        key={project.projectId}
                      >
                        <td>
                          <strong>
                            {project.projectName}
                          </strong>

                          <small>
                            {project.projectCode}
                          </small>
                        </td>

                        <td>
                          {project.clientName ??
                            '—'}
                        </td>

                        <td>
                          {project.status}
                        </td>

                        <td>
                          {project.priority}
                        </td>

                        <td>
                          {project.allocatedCapacity.toFixed(
                            0,
                          )}
                          %
                        </td>

                        <td>
                          {project.allocationShare.toFixed(
                            1,
                          )}
                          %
                        </td>

                        <td>
                          {project.allocatedEmployees}
                        </td>

                        <td>
                          {project.activeAllocations}
                        </td>
                      </tr>
                    ),
                  )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  )
}

export default ProjectAnalyticsPage