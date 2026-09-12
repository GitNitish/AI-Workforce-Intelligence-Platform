import { useEffect, useState } from 'react'
import type { Employee } from '../types/employee'
import type { Project } from '../types/project'
import { getProjectEmployees } from '../services/projectEmployees'
import { getProjects } from '../services/projects'

function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState('')
  const [projectEmployees, setProjectEmployees] = useState<Employee[]>([])
  const [loadingProjects, setLoadingProjects] = useState(true)
  const [loadingEmployees, setLoadingEmployees] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadProjects() {
      try {
        setLoadingProjects(true)
        setError(null)

        const data = await getProjects()
        setProjects(data)

        if (data.length > 0) {
          setSelectedProjectId(data[0].project_id)
        }
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load projects.'

        setError(message)
      } finally {
        setLoadingProjects(false)
      }
    }

    void loadProjects()
  }, [])

  useEffect(() => {
    if (!selectedProjectId) {
      return
    }

    async function loadProjectEmployees() {
      try {
        setLoadingEmployees(true)
        setError(null)

        const data = await getProjectEmployees(selectedProjectId)
        setProjectEmployees(data)
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load project employees.'

        setError(message)
        setProjectEmployees([])
      } finally {
        setLoadingEmployees(false)
      }
    }

    void loadProjectEmployees()
  }, [selectedProjectId])

  return (
    <section className="page">
      <div className="page-header">
        <h2>Projects</h2>
        <p>View projects and the employees assigned to them.</p>
      </div>

      {loadingProjects && (
        <div className="loading-message">
          Loading projects...
        </div>
      )}

      {!loadingProjects && projects.length === 0 && !error && (
        <div className="empty-message">
          No projects found.
        </div>
      )}

      {!loadingProjects && projects.length > 0 && (
        <>
          <div className="requirement-selector">
            <label htmlFor="project-select">
              Project
            </label>

            <select
              id="project-select"
              value={selectedProjectId}
              onChange={(event) => setSelectedProjectId(event.target.value)}
            >
              {projects.map((project) => (
                <option key={project.project_id} value={project.project_id}>
                  {project.project_code} — {project.project_name}
                </option>
              ))}
            </select>
          </div>

          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Project Code</th>
                  <th>Project Name</th>
                  <th>Client</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                </tr>
              </thead>

              <tbody>
                {projects.map((project) => (
                  <tr key={project.project_id}>
                    <td>{project.project_code}</td>
                    <td>{project.project_name}</td>
                    <td>{project.client_name ?? '—'}</td>
                    <td>{project.status}</td>
                    <td>{project.priority}</td>
                    <td>{project.start_date ?? '—'}</td>
                    <td>{project.end_date ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="page-section">
            <div className="page-section-header">
              <h3>Assigned Employees</h3>
              <p>
                Employees currently associated with the selected project.
              </p>
            </div>

            {loadingEmployees && (
              <div className="loading-message">
                Loading assigned employees...
              </div>
            )}

            {!loadingEmployees && !error && projectEmployees.length === 0 && (
              <div className="empty-message">
                No employees assigned to the selected project.
              </div>
            )}

            {!loadingEmployees && projectEmployees.length > 0 && (
              <div className="data-table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Employee Code</th>
                      <th>Name</th>
                      <th>Designation</th>
                      <th>Department</th>
                      <th>Availability</th>
                      <th>Utilization</th>
                    </tr>
                  </thead>

                  <tbody>
                    {projectEmployees.map((employee) => (
                      <tr key={employee.employee_id}>
                        <td>{employee.employee_code}</td>
                        <td>{employee.name}</td>
                        <td>{employee.designation ?? '—'}</td>
                        <td>{employee.department ?? '—'}</td>
                        <td>{employee.availability_status}</td>
                        <td>{employee.utilization_percentage}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
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

export default ProjectsPage