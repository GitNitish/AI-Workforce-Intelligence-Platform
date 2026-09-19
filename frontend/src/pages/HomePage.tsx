import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function HomePage() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadDashboard() {
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
              : 'Unable to load workforce dashboard.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadDashboard()

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return (
      <section className="home-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE OVERVIEW
            </span>

            <h2 className="home-welcome-title">
              Welcome back, Nitish 👋
            </h2>

            <p>
              A live view of your workforce, capacity and
              staffing position.
            </p>
          </div>
        </div>

        <div className="loading-message">
          Loading workforce dashboard...
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="home-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE OVERVIEW
            </span>

            <h2 className="home-welcome-title">
              Welcome back, Nitish 👋
            </h2>

            <p>
              A live view of your workforce, capacity and
              staffing position.
            </p>
          </div>
        </div>

        <div className="error-message">
          {error}
        </div>
      </section>
    )
  }

  if (!data) {
    return (
      <section className="home-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE OVERVIEW
            </span>

            <h2 className="home-welcome-title">
              Welcome back, Nitish 👋
            </h2>

            <p>
              A live view of your workforce, capacity and
              staffing position.
            </p>
          </div>
        </div>

        <div className="empty-message">
          No workforce data is currently available.
        </div>
      </section>
    )
  }

  const totalEmployees = data.employees.length

  const allocatedEmployees =
    data.employeeUtilization.filter(
      (employee) =>
        employee.utilizationPercentage > 0,
    ).length

  const topProjects =
    data.projectAnalytics.projectAllocations.slice(0, 5)

  const priorityDemand =
    data.staffing.priorityDemand.slice(0, 4)

  const utilizationItems = [
    {
      label: 'Bench',
      count: data.utilization.distribution.bench,
      percentage:
        totalEmployees > 0
          ? (data.utilization.distribution.bench /
              totalEmployees) *
            100
          : 0,
    },
    {
      label: 'Low',
      count: data.utilization.distribution.low,
      percentage:
        totalEmployees > 0
          ? (data.utilization.distribution.low /
              totalEmployees) *
            100
          : 0,
    },
    {
      label: 'Moderate',
      count: data.utilization.distribution.moderate,
      percentage:
        totalEmployees > 0
          ? (data.utilization.distribution.moderate /
              totalEmployees) *
            100
          : 0,
    },
    {
      label: 'High',
      count: data.utilization.distribution.high,
      percentage:
        totalEmployees > 0
          ? (data.utilization.distribution.high /
              totalEmployees) *
            100
          : 0,
    },
    {
      label: 'Fully Utilized',
      count: data.utilization.distribution.fullyUtilized,
      percentage:
        totalEmployees > 0
          ? (data.utilization.distribution.fullyUtilized /
              totalEmployees) *
            100
          : 0,
    },
  ]

  const maxProjectAllocation =
    topProjects[0]?.allocatedCapacity ?? 1

  return (
    <section className="home-page">
      <div className="page-heading home-heading">
        <div>
          <span className="page-eyebrow">
            WORKFORCE OVERVIEW
          </span>

          <h2 className="home-welcome-title">
            Welcome back, Nitish 👋
          </h2>

          <p>
            A live view of your workforce, capacity and
            staffing position.
          </p>
        </div>

        <div className="home-heading-meta">
          <span>Current workforce snapshot</span>

          <strong>
            {totalEmployees} employees
          </strong>
        </div>
      </div>

      <div className="home-kpi-grid">
        <div className="home-kpi-card">
          <div className="home-kpi-icon blue">
            👥
          </div>

          <div>
            <span>Total Employees</span>
            <strong>{totalEmployees}</strong>
            <small>
              {allocatedEmployees} currently allocated
            </small>
          </div>
        </div>

        <div className="home-kpi-card">
          <div className="home-kpi-icon purple">
            ◈
          </div>

          <div>
            <span>Active Projects</span>
            <strong>
              {data.projectAnalytics.activeProjects}
            </strong>
            <small>
              {data.projectAnalytics.allocatedProjects}{' '}
              currently allocated
            </small>
          </div>
        </div>

        <div className="home-kpi-card">
          <div className="home-kpi-icon green">
            ▤
          </div>

          <div>
            <span>Open Demand</span>
            <strong>{data.staffing.openDemand}</strong>
            <small>
              {data.staffing.openRequirements}{' '}
              open requirements
            </small>
          </div>
        </div>

        <div className="home-kpi-card">
          <div className="home-kpi-icon orange">
            ◌
          </div>

          <div>
            <span>Average Utilization</span>
            <strong>
              {formatPercentage(
                data.utilization.averageUtilization,
              )}
            </strong>
            <small>
              Across current workforce
            </small>
          </div>
        </div>

        <div className="home-kpi-card">
          <div className="home-kpi-icon indigo">
            ◫
          </div>

          <div>
            <span>Allocated Capacity</span>
            <strong>
              {data.capacity.allocatedCapacity.toFixed(
                0,
              )}
              %
            </strong>
            <small>
              {formatPercentage(
                data.capacity.utilizationPercentage,
              )}{' '}
              of total capacity
            </small>
          </div>
        </div>

        <div className="home-kpi-card">
          <div className="home-kpi-icon teal">
            ◐
          </div>

          <div>
            <span>Available Capacity</span>
            <strong>
              {data.capacity.availableCapacity.toFixed(
                0,
              )}
              %
            </strong>
            <small>
              {data.utilization.benchEmployees} bench
              employees
            </small>
          </div>
        </div>
      </div>

      <div className="home-main-grid">
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <span className="card-eyebrow">
                UTILIZATION
              </span>

              <h3>Workforce Utilization</h3>

              <p>
                Current distribution across the workforce.
              </p>
            </div>

            <Link to="/analytics/utilization">
              Details →
            </Link>
          </div>

          <div className="utilization-overview">
            <div className="utilization-primary">
              <strong>
                {formatPercentage(
                  data.utilization.averageUtilization,
                )}
              </strong>

              <span>
                Average utilization
              </span>
            </div>

            <div className="utilization-bar">
              <div
                className="utilization-bar-fill"
                style={{
                  width: `${Math.min(
                    data.utilization.averageUtilization,
                    100,
                  )}%`,
                }}
              />
            </div>

            <div className="utilization-caption">
              <span>
                {allocatedEmployees} allocated
              </span>

              <span>
                {data.utilization.benchEmployees} bench
              </span>
            </div>
          </div>

          <div className="utilization-distribution">
            {utilizationItems.map((item) => (
              <div
                className="utilization-distribution-row"
                key={item.label}
              >
                <div className="distribution-label">
                  <span>{item.label}</span>

                  <strong>
                    {item.count}
                  </strong>
                </div>

                <div className="distribution-track">
                  <div
                    className="distribution-fill"
                    style={{
                      width: `${item.percentage}%`,
                    }}
                  />
                </div>

                <small>
                  {item.percentage.toFixed(0)}%
                </small>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <span className="card-eyebrow">
                PROJECTS
              </span>

              <h3>Project Allocation</h3>

              <p>
                Active capacity distribution by project.
              </p>
            </div>

            <Link to="/analytics/projects">
              Details →
            </Link>
          </div>

          {topProjects.length === 0 ? (
            <div className="dashboard-empty">
              No active project allocations available.
            </div>
          ) : (
            <div className="project-allocation-list">
              {topProjects.map((project) => (
                <div
                  className="project-allocation-row"
                  key={project.projectId}
                >
                  <div className="project-allocation-name">
                    <strong>
                      {project.projectName}
                    </strong>

                    <span>
                      {project.allocatedEmployees}{' '}
                      employees ·{' '}
                      {project.activeAllocations}{' '}
                      allocations
                    </span>
                  </div>

                  <div className="project-allocation-value">
                    <strong>
                      {project.allocatedCapacity.toFixed(
                        0,
                      )}
                      %
                    </strong>

                    <div className="project-allocation-track">
                      <div
                        className="project-allocation-fill"
                        style={{
                          width: `${
                            (project.allocatedCapacity /
                              maxProjectAllocation) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <span className="card-eyebrow">
                STAFFING
              </span>

              <h3>Open Demand</h3>

              <p>
                Current workforce demand by priority.
              </p>
            </div>

            <Link to="/analytics/staffing">
              Details →
            </Link>
          </div>

          {priorityDemand.length === 0 ? (
            <div className="dashboard-empty">
              No open staffing demand.
            </div>
          ) : (
            <div className="demand-summary-list">
              {priorityDemand.map((item) => (
                <div
                  className="demand-summary-row"
                  key={item.label}
                >
                  <div>
                    <span
                      className={`priority-dot ${item.label.toLowerCase()}`}
                    />

                    <strong>
                      {item.label} Priority
                    </strong>
                  </div>

                  <div>
                    <strong>{item.demand}</strong>

                    <span>
                      {item.requirementCount}{' '}
                      requirements
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="demand-total">
            <span>Total open demand</span>

            <strong>
              {data.staffing.openDemand}
            </strong>
          </div>
        </div>
      </div>

      <div className="quick-actions">
        <Link
          className="quick-action blue"
          to="/employees"
        >
          <span className="quick-action-icon">
            👥
          </span>

          <span>
            <strong>Manage Employees</strong>
            <small>
              View workforce information
            </small>
          </span>

          <span className="quick-action-arrow">
            →
          </span>
        </Link>

        <Link
          className="quick-action purple"
          to="/analytics"
        >
          <span className="quick-action-icon">
            ▥
          </span>

          <span>
            <strong>View Analytics</strong>
            <small>
              Explore workforce insights
            </small>
          </span>

          <span className="quick-action-arrow">
            →
          </span>
        </Link>

        <Link
          className="quick-action orange"
          to="/recommendations"
        >
          <span className="quick-action-icon">
            ✦
          </span>

          <span>
            <strong>Find Candidates</strong>
            <small>
              Explore candidate recommendations
            </small>
          </span>

          <span className="quick-action-arrow">
            →
          </span>
        </Link>

        <div className="quick-action green disabled">
          <span className="quick-action-icon">
            ▣
          </span>

          <span>
            <strong>Manage Data</strong>
            <small>
              Available with Sprint 7.7
            </small>
          </span>

          <span className="quick-action-arrow">
            →
          </span>
        </div>
      </div>

      <div className="home-bottom-grid">
        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <span className="card-eyebrow">
                PROJECT PORTFOLIO
              </span>

              <h3>Projects</h3>

              <p>
                Current projects in the workforce system.
              </p>
            </div>

            <Link to="/projects">
              View all →
            </Link>
          </div>

          {data.projects.length === 0 ? (
            <div className="dashboard-empty">
              No projects are currently available.
            </div>
          ) : (
            <div className="home-table-wrapper">
              <table className="home-table">
                <thead>
                  <tr>
                    <th>Project</th>
                    <th>Client</th>
                    <th>Status</th>
                    <th>Priority</th>
                  </tr>
                </thead>

                <tbody>
                  {data.projects.slice(0, 5).map((project) => (
                    <tr key={project.project_id}>
                      <td>
                        <strong>
                          {project.project_name}
                        </strong>

                        <small>
                          {project.project_code}
                        </small>
                      </td>

                      <td>
                        {project.client_name ??
                          '—'}
                      </td>

                      <td>
                        <span className="status-badge">
                          {project.status}
                        </span>
                      </td>

                      <td>
                        {project.priority}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="dashboard-card home-insight-card">
          <div className="dashboard-card-header">
            <div>
              <span className="card-eyebrow">
                WORKFORCE OUTLOOK
              </span>

              <h3>Upcoming Capacity</h3>

              <p>
                Current and upcoming workforce position.
              </p>
            </div>

            <Link to="/analytics/outlook">
              Details →
            </Link>
          </div>

          {data.workforceOutlook.monthlyOutlook.length ===
          0 ? (
            <div className="dashboard-empty">
              No outlook data is available.
            </div>
          ) : (
            <div className="outlook-preview-list">
              {data.workforceOutlook.monthlyOutlook
                .slice(0, 4)
                .map((item) => (
                  <div
                    className="outlook-preview-row"
                    key={item.month}
                  >
                    <div>
                      <strong>
                        {item.monthLabel}
                      </strong>

                      <span>
                        {item.openRequirements}{' '}
                        open requirements
                      </span>
                    </div>

                    <div>
                      <strong>
                        {item.availableCapacity.toFixed(
                          0,
                        )}
                        %
                      </strong>

                      <span>
                        available capacity
                      </span>
                    </div>

                    <div>
                      <strong>
                        {item.openDemand}
                      </strong>

                      <span>
                        open demand
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default HomePage