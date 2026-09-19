import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function AnalyticsPage() {
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

  if (loading) {
    return (
      <section className="analytics-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE INTELLIGENCE
            </span>

            <h2>Executive Analytics</h2>

            <p>
              Workforce utilization, capacity and staffing insights.
            </p>
          </div>
        </div>

        <div className="loading-message">
          Loading analytics...
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="analytics-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE INTELLIGENCE
            </span>

            <h2>Executive Analytics</h2>

            <p>
              Workforce utilization, capacity and staffing insights.
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
      <section className="analytics-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE INTELLIGENCE
            </span>

            <h2>Executive Analytics</h2>

            <p>
              Workforce utilization, capacity and staffing insights.
            </p>
          </div>
        </div>

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
  } = data

  const totalEmployees = data.employees.length

  const allocatedEmployees =
    data.employeeUtilization.filter(
      (employee) => employee.utilizationPercentage > 0,
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

  return (
    <section className="analytics-page">
      <div className="page-heading analytics-heading">
        <div>
          <span className="page-eyebrow">
            WORKFORCE INTELLIGENCE
          </span>

          <h2>Executive Analytics</h2>

          <p>
            Workforce utilization, capacity and staffing insights.
          </p>
        </div>

        <div className="home-heading-meta">
          <span>Current workforce snapshot</span>

          <strong>
            {totalEmployees} employees
          </strong>
        </div>
      </div>

      <div className="analytics-kpi-grid">
        <div className="analytics-kpi-card">
          <div className="analytics-kpi-topline">
            <span>Total Workforce</span>

            <span className="analytics-kpi-icon blue">
              👥
            </span>
          </div>

          <strong>{totalEmployees}</strong>

          <small>
            {allocatedEmployees} currently allocated
          </small>
        </div>

        <div className="analytics-kpi-card">
          <div className="analytics-kpi-topline">
            <span>Average Utilization</span>

            <span className="analytics-kpi-icon orange">
              ◌
            </span>
          </div>

          <strong>
            {formatPercentage(
              utilization.averageUtilization,
            )}
          </strong>

          <small>
            Across the current workforce
          </small>
        </div>

        <div className="analytics-kpi-card">
          <div className="analytics-kpi-topline">
            <span>Bench</span>

            <span className="analytics-kpi-icon teal">
              ◐
            </span>
          </div>

          <strong>
            {utilization.benchEmployees}
          </strong>

          <small>
            {formatPercentage(
              utilization.benchPercentage,
            )}{' '}
            of workforce
          </small>
        </div>

        <div className="analytics-kpi-card">
          <div className="analytics-kpi-topline">
            <span>Open Demand</span>

            <span className="analytics-kpi-icon green">
              ▤
            </span>
          </div>

          <strong>{staffing.openDemand}</strong>

          <small>
            {staffing.openRequirements} open requirements
          </small>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <span className="card-eyebrow">
                UTILIZATION
              </span>

              <h3>Utilization Distribution</h3>

              <p>
                Current workforce allocation levels.
              </p>
            </div>

            <Link
              className="analytics-panel-link"
              to="/analytics/utilization"
            >
              Details →
            </Link>
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
              Average utilization
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

              <h3>Capacity &amp; Bench</h3>

              <p>
                Current workforce capacity allocation.
              </p>
            </div>

            <Link
              className="analytics-panel-link"
              to="/analytics/utilization"
            >
              Details →
            </Link>
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

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <span className="card-eyebrow">
                STAFFING
              </span>

              <h3>Staffing Demand</h3>

              <p>
                Open workforce demand by priority.
              </p>
            </div>

            <div className="analytics-panel-value">
              {staffing.openDemand}
            </div>
          </div>

          {staffing.priorityDemand.length === 0 ? (
            <div className="analytics-empty-chart">
              No open staffing demand available.
            </div>
          ) : (
            <div className="demand-list">
              {staffing.priorityDemand.map((item) => (
                <div
                  className="demand-row"
                  key={item.label}
                >
                  <span>
                    <span
                      className={`priority-dot ${item.label.toLowerCase()}`}
                    />

                    {item.label} Priority
                  </span>

                  <strong>{item.demand}</strong>
                </div>
              ))}
            </div>
          )}

          <Link
            className="analytics-panel-action"
            to="/analytics/staffing"
          >
            Explore staffing demand
            <span aria-hidden="true">→</span>
          </Link>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <span className="card-eyebrow">
                PROJECTS
              </span>

              <h3>Allocation Mix</h3>

              <p>
                Share of active allocated capacity by project.
              </p>
            </div>

            <Link
              className="analytics-panel-link"
              to="/analytics/projects"
            >
              Details →
            </Link>
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

          <Link
            className="analytics-panel-action"
            to="/analytics/projects"
          >
            Explore project analytics
            <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>

      <div className="analytics-detail-grid">
        <div className="analytics-detail-action">
          <div>
            <span className="card-eyebrow">
              UTILIZATION
            </span>

            <strong>
              Employee-level utilization
            </strong>

            <span>
              Review employee allocation and current capacity.
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
            <span className="card-eyebrow">
              STAFFING
            </span>

            <strong>
              Staffing &amp; demand analysis
            </strong>

            <span>
              Explore open demand, priorities, projects and roles.
            </span>
          </div>

          <Link
            className="analytics-detail-link"
            to="/analytics/staffing"
          >
            View Staffing Detail
            <span aria-hidden="true">→</span>
          </Link>
        </div>

        <div className="analytics-detail-action">
          <div>
            <span className="card-eyebrow">
              PROJECTS
            </span>

            <strong>
              Project allocation analysis
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
            <span className="card-eyebrow">
              OUTLOOK
            </span>

            <strong>
              Workforce outlook
            </strong>

            <span>
              Review capacity and workforce demand across upcoming months.
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
      </div>
    </section>
  )
}

export default AnalyticsPage