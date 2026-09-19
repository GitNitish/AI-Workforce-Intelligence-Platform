import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function UtilizationDetailPage() {
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

  if (!data) {
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
  } = data

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