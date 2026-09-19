import { useEffect, useMemo, useState } from 'react'
import type { Employee } from '../types/employee'
import type { EmployeeUtilization } from '../types/utilization'
import {
  getEmployee,
  getEmployeeUtilization,
} from '../services/employeeDetails'
import { getEmployees } from '../services/employees'

function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`
}

function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('')
  const [selectedEmployee, setSelectedEmployee] =
    useState<Employee | null>(null)
  const [utilization, setUtilization] =
    useState<EmployeeUtilization | null>(null)
  const [loadingEmployees, setLoadingEmployees] = useState(true)
  const [loadingDetails, setLoadingDetails] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadEmployees() {
      try {
        setLoadingEmployees(true)
        setError(null)

        const data = await getEmployees()

        setEmployees(data)

        if (data.length > 0) {
          setSelectedEmployeeId(data[0].employee_id)
        }
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load employees.'

        setError(message)
      } finally {
        setLoadingEmployees(false)
      }
    }

    void loadEmployees()
  }, [])

  useEffect(() => {
    if (!selectedEmployeeId) {
      return
    }

    async function loadEmployeeDetails() {
      try {
        setLoadingDetails(true)
        setError(null)

        const [employee, employeeUtilization] =
          await Promise.all([
            getEmployee(selectedEmployeeId),
            getEmployeeUtilization(selectedEmployeeId),
          ])

        setSelectedEmployee(employee)
        setUtilization(employeeUtilization)
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load employee details.'

        setError(message)
        setSelectedEmployee(null)
        setUtilization(null)
      } finally {
        setLoadingDetails(false)
      }
    }

    void loadEmployeeDetails()
  }, [selectedEmployeeId])

  const workforceSummary = useMemo(() => {
    const total = employees.length

    const available = employees.filter(
      (employee) =>
        employee.availability_status === 'available',
    ).length

    const allocated = employees.filter(
      (employee) =>
        employee.utilization_percentage > 0,
    ).length

    const averageUtilization =
      total > 0
        ? employees.reduce(
            (sum, employee) =>
              sum + employee.utilization_percentage,
            0,
          ) / total
        : 0

    return {
      total,
      available,
      allocated,
      averageUtilization,
    }
  }, [employees])

  if (loadingEmployees) {
    return (
      <section className="employees-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE MANAGEMENT
            </span>

            <h2>Employees</h2>

            <p>
              View the current workforce and employee
              availability.
            </p>
          </div>
        </div>

        <div className="loading-message">
          Loading employees...
        </div>
      </section>
    )
  }

  if (error && employees.length === 0) {
    return (
      <section className="employees-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE MANAGEMENT
            </span>

            <h2>Employees</h2>

            <p>
              View the current workforce and employee
              availability.
            </p>
          </div>
        </div>

        <div className="error-message" role="alert">
          {error}
        </div>
      </section>
    )
  }

  if (employees.length === 0) {
    return (
      <section className="employees-page">
        <div className="page-heading">
          <div>
            <span className="page-eyebrow">
              WORKFORCE MANAGEMENT
            </span>

            <h2>Employees</h2>

            <p>
              View the current workforce and employee
              availability.
            </p>
          </div>
        </div>

        <div className="empty-message">
          No employees found.
        </div>
      </section>
    )
  }

  return (
    <section className="employees-page">
      <div className="page-heading employees-heading">
        <div>
          <span className="page-eyebrow">
            WORKFORCE MANAGEMENT
          </span>

          <h2>Employees</h2>

          <p>
            View the current workforce and employee
            availability.
          </p>
        </div>

        <div className="employees-heading-meta">
          <span>Current workforce snapshot</span>

          <strong>
            {workforceSummary.total} employees
          </strong>
        </div>
      </div>

      <div className="employee-kpi-grid">
        <div className="employee-kpi-card">
          <div className="employee-kpi-icon blue">
            👥
          </div>

          <div>
            <span>Total Employees</span>

            <strong>
              {workforceSummary.total}
            </strong>

            <small>Current workforce</small>
          </div>
        </div>

        <div className="employee-kpi-card">
          <div className="employee-kpi-icon green">
            ◉
          </div>

          <div>
            <span>Available</span>

            <strong>
              {workforceSummary.available}
            </strong>

            <small>Marked available</small>
          </div>
        </div>

        <div className="employee-kpi-card">
          <div className="employee-kpi-icon purple">
            ▣
          </div>

          <div>
            <span>Allocated</span>

            <strong>
              {workforceSummary.allocated}
            </strong>

            <small>Currently utilized</small>
          </div>
        </div>

        <div className="employee-kpi-card">
          <div className="employee-kpi-icon orange">
            ◌
          </div>

          <div>
            <span>Average Utilization</span>

            <strong>
              {formatPercentage(
                workforceSummary.averageUtilization,
              )}
            </strong>

            <small>
              Across current workforce
            </small>
          </div>
        </div>
      </div>

      <div className="employee-workspace">
        <div className="employee-directory-card">
          <div className="employee-card-header">
            <div>
              <span className="card-eyebrow">
                EMPLOYEE DIRECTORY
              </span>

              <h3>Workforce</h3>

              <p>
                Current employees and their capacity
                position.
              </p>
            </div>

            <div className="employee-selector">
              <label htmlFor="employee-select">
                Selected employee
              </label>

              <select
                id="employee-select"
                value={selectedEmployeeId}
                onChange={(event) =>
                  setSelectedEmployeeId(
                    event.target.value,
                  )
                }
              >
                {employees.map((employee) => (
                  <option
                    key={employee.employee_id}
                    value={employee.employee_id}
                  >
                    {employee.employee_code} —{' '}
                    {employee.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="employee-table-wrapper">
            <table className="employee-table">
              <thead>
                <tr>
                  <th>Employee</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Availability</th>
                  <th>Utilization</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {employees.map((employee) => (
                  <tr
                    key={employee.employee_id}
                    className={
                      employee.employee_id ===
                      selectedEmployeeId
                        ? 'selected'
                        : ''
                    }
                    onClick={() =>
                      setSelectedEmployeeId(
                        employee.employee_id,
                      )
                    }
                  >
                    <td>
                      <div className="employee-table-person">
                        <div className="employee-table-avatar">
                          {employee.name
                            .charAt(0)
                            .toUpperCase()}
                        </div>

                        <div>
                          <strong>
                            {employee.name}
                          </strong>

                          <small>
                            {employee.employee_code}
                          </small>
                        </div>
                      </div>
                    </td>

                    <td>
                      {employee.designation ?? '—'}
                    </td>

                    <td>
                      {employee.department ?? '—'}
                    </td>

                    <td>
                      <span className="employee-status-pill">
                        {employee.availability_status}
                      </span>
                    </td>

                    <td>
                      <div className="employee-utilization-cell">
                        <span>
                          {
                            employee.utilization_percentage
                          }
                          %
                        </span>

                        <div className="employee-utilization-track">
                          <div
                            className="employee-utilization-fill"
                            style={{
                              width: `${Math.min(
                                Math.max(
                                  employee.utilization_percentage,
                                  0,
                                ),
                                100,
                              )}%`,
                            }}
                          />
                        </div>
                      </div>
                    </td>

                    <td>
                      <span className="employee-status-badge">
                        {employee.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="employee-detail-card">
          {loadingDetails ? (
            <div className="employee-detail-loading">
              Loading employee details...
            </div>
          ) : selectedEmployee && utilization ? (
            <>
              <div className="employee-detail-header">
                <div className="employee-detail-avatar">
                  {selectedEmployee.name
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <div>
                  <span className="card-eyebrow">
                    SELECTED EMPLOYEE
                  </span>

                  <h3>
                    {selectedEmployee.name}
                  </h3>

                  <p>
                    {selectedEmployee.designation ??
                      '—'}
                  </p>
                </div>
              </div>

              <div className="employee-detail-status-row">
                <span className="employee-status-badge">
                  {selectedEmployee.status}
                </span>

                <span className="employee-status-pill">
                  {
                    selectedEmployee.availability_status
                  }
                </span>
              </div>

              <div className="employee-detail-utilization">
                <div>
                  <span>
                    Current utilization
                  </span>

                  <strong>
                    {utilization.utilization_percentage}
                    %
                  </strong>
                </div>

                <div className="employee-detail-utilization-track">
                  <div
                    className="employee-detail-utilization-fill"
                    style={{
                      width: `${Math.min(
                        Math.max(
                          utilization.utilization_percentage,
                          0,
                        ),
                        100,
                      )}%`,
                    }}
                  />
                </div>

                <div className="employee-detail-utilization-caption">
                  <span>Allocated</span>

                  <span>
                    {utilization.available_percentage}%
                    {' '}
                    available
                  </span>
                </div>
              </div>

              <div className="employee-detail-grid">
                <div>
                  <span>Employee Code</span>

                  <strong>
                    {selectedEmployee.employee_code}
                  </strong>
                </div>

                <div>
                  <span>Email</span>

                  <strong>
                    {selectedEmployee.email}
                  </strong>
                </div>

                <div>
                  <span>Department</span>

                  <strong>
                    {selectedEmployee.department ??
                      '—'}
                  </strong>
                </div>

                <div>
                  <span>Experience</span>

                  <strong>
                    {selectedEmployee.experience_years}{' '}
                    yrs
                  </strong>
                </div>

                <div>
                  <span>Location</span>

                  <strong>
                    {selectedEmployee.location ?? '—'}
                  </strong>
                </div>

                <div>
                  <span>Available Capacity</span>

                  <strong>
                    {utilization.available_percentage}%
                  </strong>
                </div>
              </div>
            </>
          ) : (
            <div className="employee-detail-empty">
              Select an employee to view their current
              workforce details.
            </div>
          )}
        </aside>
      </div>

      {error && employees.length > 0 && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
    </section>
  )
}

export default EmployeesPage