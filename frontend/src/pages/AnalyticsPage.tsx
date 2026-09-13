import { useEffect, useMemo, useState } from 'react'
import {
  getAnalyticsData,
  type AnalyticsData,
} from '../services/analytics'

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

  const metrics = useMemo(() => {
    if (!data) {
      return null
    }

    const activeAllocations = data.allocations.filter(
      (allocation) => allocation.status === 'active',
    )

    const activeAllocationByEmployee = new Map<string, number>()

    for (const allocation of activeAllocations) {
      const current =
        activeAllocationByEmployee.get(allocation.employee_id) ?? 0

      activeAllocationByEmployee.set(
        allocation.employee_id,
        current + allocation.allocation_percentage,
      )
    }

    const employeeUtilizations = data.employees.map((employee) =>
      Math.min(
        activeAllocationByEmployee.get(employee.employee_id) ?? 0,
        100,
      ),
    )

    const totalEmployees = data.employees.length

    const allocatedEmployees = employeeUtilizations.filter(
      (utilization) => utilization > 0,
    ).length

    const benchEmployees = employeeUtilizations.filter(
      (utilization) => utilization === 0,
    ).length

    const averageUtilization =
      totalEmployees > 0
        ? employeeUtilizations.reduce(
            (total, utilization) => total + utilization,
            0,
          ) / totalEmployees
        : 0

    const totalCapacity = totalEmployees * 100

    const allocatedCapacity = activeAllocations.reduce(
      (total, allocation) =>
        total + allocation.allocation_percentage,
      0,
    )

    const availableCapacity = Math.max(
      0,
      totalCapacity - allocatedCapacity,
    )

    const openRequirements = data.staffingRequirements.filter(
      (requirement) => requirement.status === 'open',
    )

    const openDemand = openRequirements.reduce(
      (total, requirement) =>
        total + requirement.required_quantity,
      0,
    )

    const highPriorityDemand = openRequirements
      .filter((requirement) => requirement.priority === 'high')
      .reduce(
        (total, requirement) =>
          total + requirement.required_quantity,
        0,
      )

    const mediumPriorityDemand = openRequirements
      .filter((requirement) => requirement.priority === 'medium')
      .reduce(
        (total, requirement) =>
          total + requirement.required_quantity,
        0,
      )

    const lowPriorityDemand = openRequirements
      .filter((requirement) => requirement.priority === 'low')
      .reduce(
        (total, requirement) =>
          total + requirement.required_quantity,
        0,
      )

    const allocationByProject = new Map<string, number>()

    for (const allocation of activeAllocations) {
      const current =
        allocationByProject.get(allocation.project_id) ?? 0

      allocationByProject.set(
        allocation.project_id,
        current + allocation.allocation_percentage,
      )
    }

    const totalAllocatedCapacity = Array.from(
      allocationByProject.values(),
    ).reduce(
      (total, percentage) => total + percentage,
      0,
    )

    const allocationMix = data.projects
      .map((project) => {
        const allocatedPercentage =
          allocationByProject.get(project.project_id) ?? 0

        return {
          projectId: project.project_id,
          projectName: project.project_name,
          percentage:
            totalAllocatedCapacity > 0
              ? (allocatedPercentage /
                  totalAllocatedCapacity) *
                100
              : 0,
        }
      })
      .filter((project) => project.percentage > 0)
      .sort((a, b) => b.percentage - a.percentage)

    const utilizationDistribution = {
      available: employeeUtilizations.filter(
        (utilization) => utilization === 0,
      ).length,
      partial: employeeUtilizations.filter(
        (utilization) =>
          utilization > 0 && utilization < 100,
      ).length,
      full: employeeUtilizations.filter(
        (utilization) => utilization >= 100,
      ).length,
    }

    return {
      totalEmployees,
      allocatedEmployees,
      benchEmployees,
      averageUtilization,
      totalCapacity,
      allocatedCapacity,
      availableCapacity,
      openRequirements: openRequirements.length,
      openDemand,
      highPriorityDemand,
      mediumPriorityDemand,
      lowPriorityDemand,
      allocationMix,
      utilizationDistribution,
    }
  }, [data])

  if (loading) {
    return (
      <section>
        <h2>Executive Analytics</h2>
        <p>Workforce utilization, capacity and staffing insights.</p>

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
        <p>Workforce utilization, capacity and staffing insights.</p>

        <div className="error-message">
          {error}
        </div>
      </section>
    )
  }

  if (!data || !metrics) {
    return (
      <section>
        <h2>Executive Analytics</h2>
        <p>Workforce utilization, capacity and staffing insights.</p>

        <div className="empty-message">
          No analytics data is available.
        </div>
      </section>
    )
  }

  const maxAllocationPercentage =
    metrics.allocationMix[0]?.percentage ?? 1

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

      <div className="analytics-kpi-grid">
        <div className="analytics-kpi-card">
          <span>Total Workforce</span>
          <strong>{metrics.totalEmployees}</strong>
          <small>
            {metrics.allocatedEmployees} currently allocated
          </small>
        </div>

        <div className="analytics-kpi-card">
          <span>Average Utilization</span>
          <strong>
            {metrics.averageUtilization.toFixed(1)}%
          </strong>
          <small>Across the current workforce</small>
        </div>

        <div className="analytics-kpi-card">
          <span>Bench</span>
          <strong>{metrics.benchEmployees}</strong>
          <small>
            {metrics.totalEmployees > 0
              ? `${(
                  (metrics.benchEmployees /
                    metrics.totalEmployees) *
                  100
                ).toFixed(1)}% of workforce`
              : '0.0% of workforce'}
          </small>
        </div>

        <div className="analytics-kpi-card">
          <span>Open Demand</span>
          <strong>{metrics.openDemand}</strong>
          <small>
            {metrics.openRequirements} open requirements
          </small>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Utilization Distribution</h3>
              <p>Current workforce allocation levels.</p>
            </div>
          </div>

          <div className="analytics-bars">
            <div className="analytics-bar-row">
              <div className="analytics-bar-label">
                <span>Available</span>
                <strong>
                  {metrics.utilizationDistribution.available}
                </strong>
              </div>

              <div className="analytics-bar-track">
                <div
                  className="analytics-bar-fill"
                  style={{
                    width:
                      metrics.totalEmployees > 0
                        ? `${
                            (metrics.utilizationDistribution
                              .available /
                              metrics.totalEmployees) *
                            100
                          }%`
                        : '0%',
                  }}
                />
              </div>
            </div>

            <div className="analytics-bar-row">
              <div className="analytics-bar-label">
                <span>Partially Utilized</span>
                <strong>
                  {metrics.utilizationDistribution.partial}
                </strong>
              </div>

              <div className="analytics-bar-track">
                <div
                  className="analytics-bar-fill"
                  style={{
                    width:
                      metrics.totalEmployees > 0
                        ? `${
                            (metrics.utilizationDistribution
                              .partial /
                              metrics.totalEmployees) *
                            100
                          }%`
                        : '0%',
                  }}
                />
              </div>
            </div>

            <div className="analytics-bar-row">
              <div className="analytics-bar-label">
                <span>Fully Utilized</span>
                <strong>
                  {metrics.utilizationDistribution.full}
                </strong>
              </div>

              <div className="analytics-bar-track">
                <div
                  className="analytics-bar-fill"
                  style={{
                    width:
                      metrics.totalEmployees > 0
                        ? `${
                            (metrics.utilizationDistribution
                              .full /
                              metrics.totalEmployees) *
                            100
                          }%`
                        : '0%',
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Capacity & Bench</h3>
              <p>Current workforce capacity allocation.</p>
            </div>
          </div>

          <div className="capacity-summary">
            <div>
              <span>Total Capacity</span>
              <strong>
                {metrics.totalCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Allocated</span>
              <strong>
                {metrics.allocatedCapacity.toFixed(0)}%
              </strong>
            </div>

            <div>
              <span>Available</span>
              <strong>
                {metrics.availableCapacity.toFixed(0)}%
              </strong>
            </div>
          </div>

          <div className="capacity-track">
            <div
              className="capacity-allocated"
              style={{
                width:
                  metrics.totalCapacity > 0
                    ? `${Math.min(
                        (metrics.allocatedCapacity /
                          metrics.totalCapacity) *
                          100,
                        100,
                      )}%`
                    : '0%',
              }}
            />
          </div>

          <div className="capacity-caption">
            <span>
              {metrics.allocatedEmployees} allocated employees
            </span>

            <span>
              {metrics.benchEmployees} bench employees
            </span>
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Staffing Demand</h3>
              <p>Open workforce demand by priority.</p>
            </div>

            <strong className="analytics-panel-value">
              {metrics.openDemand}
            </strong>
          </div>

          <div className="demand-list">
            <div className="demand-row">
              <span>High Priority</span>
              <strong>{metrics.highPriorityDemand}</strong>
            </div>

            <div className="demand-row">
              <span>Medium Priority</span>
              <strong>{metrics.mediumPriorityDemand}</strong>
            </div>

            <div className="demand-row">
              <span>Low Priority</span>
              <strong>{metrics.lowPriorityDemand}</strong>
            </div>
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h3>Allocation Mix</h3>
              <p>Share of active allocated capacity by project.</p>
            </div>
          </div>

          {metrics.allocationMix.length === 0 ? (
            <div className="analytics-empty-chart">
              No active allocations available.
            </div>
          ) : (
            <div className="allocation-list">
              {metrics.allocationMix.map((project) => (
                <div
                  className="allocation-row"
                  key={project.projectId}
                >
                  <div className="allocation-row-header">
                    <span>{project.projectName}</span>
                    <strong>
                      {project.percentage.toFixed(0)}%
                    </strong>
                  </div>

                  <div className="analytics-bar-track">
                    <div
                      className="analytics-bar-fill"
                      style={{
                        width: `${
                          (project.percentage /
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
    </section>
  )
}

export default AnalyticsPage