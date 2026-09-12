import { useEffect, useState } from 'react'
import type { Employee } from '../types/employee'
import type { EmployeeUtilization } from '../types/utilization'
import { getEmployee, getEmployeeUtilization } from '../services/employeeDetails'
import { getEmployees } from '../services/employees'

function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [selectedEmployeeId, setSelectedEmployeeId] = useState('')
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(
    null,
  )
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

        const [employee, employeeUtilization] = await Promise.all([
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

  return (
    <section className="page">
      <div className="page-header">
        <h2>Employees</h2>
        <p>View the current workforce and employee availability.</p>
      </div>

      {loadingEmployees && (
        <div className="loading-message">
          Loading employees...
        </div>
      )}

      {!loadingEmployees && employees.length === 0 && !error && (
        <div className="empty-message">
          No employees found.
        </div>
      )}

      {!loadingEmployees && employees.length > 0 && (
        <>
          <div className="requirement-selector">
            <label htmlFor="employee-select">
              Employee
            </label>

            <select
              id="employee-select"
              value={selectedEmployeeId}
              onChange={(event) => setSelectedEmployeeId(event.target.value)}
            >
              {employees.map((employee) => (
                <option
                  key={employee.employee_id}
                  value={employee.employee_id}
                >
                  {employee.employee_code} — {employee.name}
                </option>
              ))}
            </select>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Employee Code</th>
                  <th>Name</th>
                  <th>Designation</th>
                  <th>Department</th>
                  <th>Experience</th>
                  <th>Availability</th>
                  <th>Utilization</th>
                  <th>Location</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {employees.map((employee) => (
                  <tr key={employee.employee_id}>
                    <td>{employee.employee_code}</td>
                    <td>{employee.name}</td>
                    <td>{employee.designation ?? '—'}</td>
                    <td>{employee.department ?? '—'}</td>
                    <td>{employee.experience_years} yrs</td>
                    <td>{employee.availability_status}</td>
                    <td>{employee.utilization_percentage}%</td>
                    <td>{employee.location ?? '—'}</td>
                    <td>{employee.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {loadingDetails && (
            <div className="loading-message">
              Loading employee details...
            </div>
          )}

          {!loadingDetails && selectedEmployee && utilization && (
            <div className="page-section">
              <div className="page-section-header">
                <h3>{selectedEmployee.name}</h3>
                <p>
                  Employee details and current capacity information.
                </p>
              </div>

              <div className="results-summary">
                <div>
                  <span>Employee Code</span>
                  <strong>{selectedEmployee.employee_code}</strong>
                </div>

                <div>
                  <span>Email</span>
                  <strong>{selectedEmployee.email}</strong>
                </div>

                <div>
                  <span>Designation</span>
                  <strong>
                    {selectedEmployee.designation ?? '—'}
                  </strong>
                </div>

                <div>
                  <span>Department</span>
                  <strong>
                    {selectedEmployee.department ?? '—'}
                  </strong>
                </div>

                <div>
                  <span>Utilization</span>
                  <strong>
                    {utilization.utilization_percentage}%
                  </strong>
                </div>

                <div>
                  <span>Available Capacity</span>
                  <strong>
                    {utilization.available_percentage}%
                  </strong>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
    </section>
  )
}

export default EmployeesPage