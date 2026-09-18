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
      <section>
        <div className="analytics-detail-back">
          <Link to="/analytics">
            ← Back to Executive Analytics
          </Link>
        </div>

        <h2>Utilization Detail</h2>
        <p>
          Detailed workforce utilization and capacity analysis.
        </p>

        <div className="loading-message">
          Loading utilization details...
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

        <h2>Utilization Detail</h2>
        <p>
          Detailed workforce utilization and capacity analysis.
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

        <h2>Utilization Detail</h2>
        <p>
          Detailed workforce utilization and capacity analysis.
        </p>

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

  const allocatedEmployees = employeeUtilization.filter(
    (employee) => employee.utilizationPercentage > 0,
  ).length

  const benchCapacity = utilization.benchEmployees * 100

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

      <div className="analytics-header">
        <div>
          <h2>Utilization Detail</h2>
          <p>
            Detailed workforce utilization and capacity analysis.
          </p>
        </div>
      </div>

      <div className="analytics-section">
        <div className="analytics-section-header">
          <div>
            <h3>Utilization Statistics</h3>
            <p>
              Current utilization statistics across the workforce.
            </p>
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
      </div>

      <div className="analytics-grid analytics-detail-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Utilization Bands</h3>
              <p>
                Workforce distribution across utilization ranges.
              </p>
            </div>
          </div>

          <div className="analytics-band-list">
            {distributionItems.map((item) => {
              const percentage =
                totalEmployees > 0
                  ? (item.count / totalEmployees) * 100
                  : 0

              return (
                <div
                  className="analytics-band-row"
                  key={item.label}
                >
                  <div className="analytics-band-info">
                    <span>{item.label}</span>
                    <strong>{item.count}</strong>
                  </div>

                  <div className="analytics-band-track">
                    <div
                      className="analytics-band-fill"
                      style={{
                        width: `${percentage}%`,
                      }}
                    />
                  </div>

                  <small>
                    {percentage.toFixed(1)}%
                  </small>
                </div>
              )
            })}
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Capacity Overview</h3>
              <p>
                Current capacity position across the workforce.
              </p>
            </div>
          </div>

          <div className="capacity-detail-grid">
            <div>
              <span>Total Capacity</span>
              <strong>
                {capacity.totalCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Allocated Capacity</span>
              <strong>
                {capacity.allocatedCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Available Capacity</span>
              <strong>
                {capacity.availableCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Capacity Utilization</span>
              <strong>
                {formatPercentage(
                  capacity.utilizationPercentage,
                )}
              </strong>
            </div>

            <div>
              <span>Bench Capacity</span>
              <strong>
                {benchCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Allocated Employees</span>
              <strong>{allocatedEmployees}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="analytics-panel analytics-employee-panel">
        <div className="analytics-panel-header">
          <div>
            <h3>Employee Utilization</h3>
            <p>
              Current utilization and available capacity by employee.
            </p>
          </div>

          <strong className="analytics-panel-value">
            {employeeUtilization.length}
          </strong>
        </div>

        {employeeUtilization.length === 0 ? (
          <div className="analytics-empty-chart">
            No employee utilization data available.
          </div>
        ) : (
          <div className="analytics-table-wrapper">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Code</th>
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
                    </td>

                    <td>{employee.employeeCode}</td>

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
                              width: `${Math.min(
                                employee.utilizationPercentage,
                                100,
                              )}%`,
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
        )}
      </div>
    </section>
  )
}

export default UtilizationDetailPage