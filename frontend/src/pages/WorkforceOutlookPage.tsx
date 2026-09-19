import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function WorkforceOutlookPage() {
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
              : 'Unable to load workforce outlook data.',
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

        <h2>Workforce Outlook</h2>
        <p>
          Current capacity and workforce demand across upcoming months.
        </p>

        <div className="loading-message">
          Loading workforce outlook...
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

        <h2>Workforce Outlook</h2>
        <p>
          Current capacity and workforce demand across upcoming months.
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

        <h2>Workforce Outlook</h2>
        <p>
          Current capacity and workforce demand across upcoming months.
        </p>

        <div className="empty-message">
          No workforce outlook data is available.
        </div>
      </section>
    )
  }

  const { workforceOutlook } = data
  const monthlyOutlook = workforceOutlook.monthlyOutlook
  const currentMonth = monthlyOutlook[0]

  return (
    <section className="analytics-page workforce-outlook-page">
      <style>
        {`
          .workforce-outlook-page .workforce-outlook-summary {
            margin-top: 28px;
          }

          .workforce-outlook-page .workforce-outlook-table-wrapper {
            width: 100%;
            overflow-x: auto;
          }

          .workforce-outlook-page .workforce-outlook-table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
          }

          .workforce-outlook-page .workforce-outlook-table th {
            padding: 13px 14px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            background: #f8fafc;
            color: #64748b;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
          }

          .workforce-outlook-page .workforce-outlook-table td {
            padding: 16px 14px;
            border-bottom: 1px solid #edf2f7;
            vertical-align: middle;
          }

          .workforce-outlook-page .workforce-outlook-table tbody tr:last-child td {
            border-bottom: none;
          }

          .workforce-outlook-page .workforce-outlook-table tbody tr:hover {
            background: #fafcff;
          }

          .workforce-outlook-page .outlook-month {
            font-weight: 700;
            color: #0f172a;
            white-space: nowrap;
          }

          .workforce-outlook-page .outlook-capacity-cell {
            min-width: 190px;
          }

          .workforce-outlook-page .outlook-capacity-value {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 7px;
          }

          .workforce-outlook-page .outlook-capacity-value strong {
            color: #0f172a;
            font-size: 14px;
          }

          .workforce-outlook-page .outlook-capacity-track {
            width: 100%;
            height: 7px;
            overflow: hidden;
            border-radius: 999px;
            background: #e9eef5;
          }

          .workforce-outlook-page .outlook-capacity-fill {
            height: 100%;
            border-radius: inherit;
          }

          .workforce-outlook-page .outlook-capacity-fill.committed {
            background: #2563eb;
          }

          .workforce-outlook-page .outlook-capacity-fill.available {
            background: #94a3b8;
          }

          .workforce-outlook-page .outlook-number {
            color: #0f172a;
            font-weight: 600;
          }

          .workforce-outlook-page .outlook-subtext {
            display: block;
            margin-top: 4px;
            color: #64748b;
            font-size: 12px;
          }

          .workforce-outlook-page .workforce-outlook-guide {
            margin-top: 20px;
          }

          .workforce-outlook-page .workforce-outlook-guide-intro {
            margin-bottom: 18px;
          }

          .workforce-outlook-page .workforce-outlook-guide-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
          }

          .workforce-outlook-page .workforce-outlook-guide-item {
            padding: 16px;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            background: #f8fafc;
          }

          .workforce-outlook-page .workforce-outlook-guide-item strong {
            display: block;
            margin-bottom: 7px;
            color: #0f172a;
            font-size: 13px;
          }

          .workforce-outlook-page .workforce-outlook-guide-item p {
            margin: 0;
            color: #64748b;
            font-size: 12px;
            line-height: 1.55;
          }

          .workforce-outlook-page .workforce-outlook-basis {
            margin-top: 16px;
            padding: 13px 15px;
            border-left: 3px solid #2563eb;
            border-radius: 6px;
            background: #f8fafc;
            color: #475569;
            font-size: 12px;
            line-height: 1.55;
          }

          .workforce-outlook-page .workforce-outlook-basis strong {
            color: #0f172a;
          }

          @media (max-width: 900px) {
            .workforce-outlook-page .workforce-outlook-guide-grid {
              grid-template-columns: repeat(2, minmax(0, 1fr));
            }
          }

          @media (max-width: 640px) {
            .workforce-outlook-page .workforce-outlook-guide-grid {
              grid-template-columns: 1fr;
            }

            .workforce-outlook-page .workforce-outlook-table {
              min-width: 760px;
            }
          }
        `}
      </style>

      <div className="analytics-detail-back">
        <Link to="/analytics">
          ← Back to Executive Analytics
        </Link>
      </div>

      <div className="analytics-header">
        <div>
          <h2>Workforce Outlook</h2>
          <p>
            Current capacity and workforce demand across upcoming months.
          </p>
        </div>
      </div>

      <div className="analytics-detail-kpi-grid">
        <div className="analytics-detail-card">
          <span>Outlook Horizon</span>
          <strong>
            {monthlyOutlook.length} months
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Total Capacity</span>
          <strong>
            {workforceOutlook.totalCapacity.toFixed(0)}%
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Current Committed</span>
          <strong>
            {currentMonth
              ? formatPercentage(
                  currentMonth.committedAllocation,
                )
              : '0.0%'}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Current Available</span>
          <strong>
            {currentMonth
              ? formatPercentage(
                  currentMonth.availableCapacity,
                )
              : '0.0%'}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Current Open Demand</span>
          <strong>
            {currentMonth?.openDemand ?? 0}
          </strong>
        </div>

        <div className="analytics-detail-card">
          <span>Open Requirements</span>
          <strong>
            {currentMonth?.openRequirements ?? 0}
          </strong>
        </div>
      </div>

      <div className="analytics-section workforce-outlook-summary">
        <div className="analytics-section-header">
          <h3>Monthly Workforce Outlook</h3>
          <p>
            Current committed capacity, remaining capacity, and open
            staffing demand for each month in the outlook period.
          </p>
        </div>

        {monthlyOutlook.length === 0 ? (
          <div className="analytics-panel">
            <div className="analytics-empty-chart">
              No workforce outlook data is available.
            </div>
          </div>
        ) : (
          <div className="analytics-panel">
            <div className="workforce-outlook-table-wrapper">
              <table className="workforce-outlook-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Committed Capacity</th>
                    <th>Available Capacity</th>
                    <th>Open Demand</th>
                    <th>Open Requirements</th>
                  </tr>
                </thead>

                <tbody>
                  {monthlyOutlook.map((month) => (
                    <tr key={month.month}>
                      <td>
                        <span className="outlook-month">
                          {month.monthLabel}
                        </span>
                      </td>

                      <td className="outlook-capacity-cell">
                        <div className="outlook-capacity-value">
                          <strong>
                            {formatPercentage(
                              month.committedAllocation,
                            )}
                          </strong>
                        </div>

                        <div className="outlook-capacity-track">
                          <div
                            className="outlook-capacity-fill committed"
                            style={{
                              width: `${Math.min(
                                month.committedAllocation,
                                100,
                              )}%`,
                            }}
                          />
                        </div>
                      </td>

                      <td className="outlook-capacity-cell">
                        <div className="outlook-capacity-value">
                          <strong>
                            {formatPercentage(
                              month.availableCapacity,
                            )}
                          </strong>
                        </div>

                        <div className="outlook-capacity-track">
                          <div
                            className="outlook-capacity-fill available"
                            style={{
                              width: `${Math.min(
                                month.availableCapacity,
                                100,
                              )}%`,
                            }}
                          />
                        </div>
                      </td>

                      <td>
                        <span className="outlook-number">
                          {month.openDemand}
                        </span>

                        <span className="outlook-subtext">
                          resource demand
                        </span>
                      </td>

                      <td>
                        <span className="outlook-number">
                          {month.openRequirements}
                        </span>

                        <span className="outlook-subtext">
                          open requirement
                          {month.openRequirements === 1
                            ? ''
                            : 's'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <div className="analytics-panel workforce-outlook-guide">
        <div className="analytics-panel-header workforce-outlook-guide-intro">
          <div>
            <h3>How to interpret this view</h3>
            <p>
              Use this page to understand how much workforce capacity is
              currently committed, how much remains available, and how
              much open staffing demand exists across the displayed
              months.
            </p>
          </div>
        </div>

        <div className="workforce-outlook-guide-grid">
          <div className="workforce-outlook-guide-item">
            <strong>Committed Capacity</strong>
            <p>
              Workforce capacity already assigned through active
              allocations. A higher percentage means more of the
              available workforce is already committed.
            </p>
          </div>

          <div className="workforce-outlook-guide-item">
            <strong>Available Capacity</strong>
            <p>
              Remaining workforce capacity after current active
              allocations. This represents capacity that is not
              currently committed.
            </p>
          </div>

          <div className="workforce-outlook-guide-item">
            <strong>Open Demand</strong>
            <p>
              The total number of workforce positions requested by
              staffing requirements that are currently open for that
              month.
            </p>
          </div>

          <div className="workforce-outlook-guide-item">
            <strong>Open Requirements</strong>
            <p>
              The number of open staffing requirements contributing to
              the demand shown for that month.
            </p>
          </div>
        </div>

        <div className="workforce-outlook-basis">
          <strong>Important:</strong>{' '}
          This is a descriptive workforce view, not a forecast. The
          displayed months are derived from current active allocations
          and open staffing requirements. It does not predict future
          utilization, hiring needs, or staffing outcomes.
        </div>
      </div>
    </section>
  )
}

export default WorkforceOutlookPage