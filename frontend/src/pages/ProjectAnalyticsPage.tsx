import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function ProjectAnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
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

  const { projectAnalytics } = data

  const maxAllocationShare =
    projectAnalytics.projectAllocations[0]?.allocationShare ?? 1

  return (
    <section className="analytics-page">
      <div className="analytics-detail-back">
        <Link to="/analytics">
          ← Back to Executive Analytics
        </Link>
      </div>

      <div className="analytics-header">
        <div>
          <h2>Project Allocation Analytics</h2>
          <p>
            Detailed view of project-level workforce allocation.
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
              data.capacity.allocatedCapacity,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Average / Project</span>
          <strong>
            {formatPercentage(
              projectAnalytics.averageAllocationPerProject,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Largest Allocation</span>
          <strong>
            {formatPercentage(
              projectAnalytics.largestProjectAllocation,
            )}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Available Capacity</span>
          <strong>
            {formatPercentage(
              data.capacity.availableCapacity,
            )}
          </strong>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Project Allocation Mix</h3>
              <p>
                Share of active allocated capacity by project.
              </p>
            </div>
          </div>

          {projectAnalytics.projectAllocations.length === 0 ? (
            <div className="analytics-empty-chart">
              No active project allocations available.
            </div>
          ) : (
            <div className="analytics-band-list">
              {projectAnalytics.projectAllocations.map(
                (project) => (
                  <div
                    className="analytics-band-row"
                    key={project.projectId}
                  >
                    <div className="analytics-band-info">
                      <span title={project.projectName}>
                        {project.projectName}
                      </span>

                      <strong>
                        {project.allocationShare.toFixed(1)}%
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
                      {project.allocatedCapacity.toFixed(0)}%
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
              <h3>Project Capacity Overview</h3>
              <p>
                Current workforce allocation across active projects.
              </p>
            </div>
          </div>

          {projectAnalytics.projectAllocations.length === 0 ? (
            <div className="analytics-empty-chart">
              No project allocation data available.
            </div>
          ) : (
            <div className="project-capacity-list">
              {projectAnalytics.projectAllocations.map(
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
                        {project.allocatedCapacity.toFixed(0)}%
                      </strong>
                    </div>

                    <div className="project-capacity-meta">
                      <span>
                        Client:{' '}
                        {project.clientName ?? '—'}
                      </span>

                      <span>
                        Status: {project.status}
                      </span>

                      <span>
                        Priority: {project.priority}
                      </span>
                    </div>

                    <div className="project-capacity-stats">
                      <div>
                        <span>Allocation Share</span>
                        <strong>
                          {project.allocationShare.toFixed(1)}%
                        </strong>
                      </div>

                      <div>
                        <span>Employees</span>
                        <strong>
                          {project.allocatedEmployees}
                        </strong>
                      </div>

                      <div>
                        <span>Active Allocations</span>
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
            <h3>Project Allocation Table</h3>
            <p>
              Detailed project-level allocation distribution.
            </p>
          </div>

          <strong className="analytics-panel-value">
            {projectAnalytics.allocatedProjects}
          </strong>
        </div>

        {projectAnalytics.projectAllocations.length === 0 ? (
          <div className="analytics-empty-chart">
            No active project allocations available.
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
                {projectAnalytics.projectAllocations.map(
                  (project) => (
                    <tr key={project.projectId}>
                      <td>
                        <strong>
                          {project.projectName}
                        </strong>

                        <small>
                          {project.projectCode}
                        </small>
                      </td>

                      <td>
                        {project.clientName ?? '—'}
                      </td>

                      <td>{project.status}</td>

                      <td>{project.priority}</td>

                      <td>
                        {project.allocatedCapacity.toFixed(0)}%
                      </td>

                      <td>
                        {project.allocationShare.toFixed(1)}%
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