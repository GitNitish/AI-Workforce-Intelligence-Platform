import { useEffect, useMemo, useState } from 'react'
import type { Employee } from '../types/employee'
import type { Project } from '../types/project'
import { getProjectEmployees } from '../services/projectEmployees'
import { getProjects } from '../services/projects'
import './ProjectsPage.css'

function formatDate(value: string | null): string {
  if (!value) {
    return '—'
  }

  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatLabel(value: string): string {
  if (!value) {
    return '—'
  }

  return value
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    )
}

function getStatusClass(status: string): string {
  return status.toLowerCase() === 'active'
    ? 'project-status active'
    : 'project-status'
}

function getPriorityClass(priority: string): string {
  return priority.toLowerCase() === 'high'
    ? 'project-priority high'
    : 'project-priority'
}

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

        const data =
          await getProjectEmployees(selectedProjectId)

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

  const handleProjectChange = (
    projectId: string,
  ) => {
    setSelectedProjectId(projectId)
    setProjectEmployees([])
  }

  const selectedProject = useMemo(
    () =>
      projects.find(
        (project) =>
          project.project_id === selectedProjectId,
      ) ?? null,
    [projects, selectedProjectId],
  )

  const summary = useMemo(() => {
    const total = projects.length

    const active = projects.filter(
      (project) =>
        project.status.toLowerCase() === 'active',
    ).length

    const planned = projects.filter(
      (project) =>
        project.status.toLowerCase() === 'planned',
    ).length

    const highPriority = projects.filter(
      (project) =>
        project.priority.toLowerCase() === 'high',
    ).length

    return {
      total,
      active,
      planned,
      highPriority,
    }
  }, [projects])

  if (loadingProjects) {
    return (
      <section className="projects-page">
        <div className="projects-page-header">
          <div>
            <span className="projects-eyebrow">
              PROJECT MANAGEMENT
            </span>

            <h2>Projects</h2>

            <p>
              Monitor project portfolio status and current
              workforce assignments.
            </p>
          </div>
        </div>

        <div className="projects-message">
          Loading projects...
        </div>
      </section>
    )
  }

  if (error && projects.length === 0) {
    return (
      <section className="projects-page">
        <div className="projects-page-header">
          <div>
            <span className="projects-eyebrow">
              PROJECT MANAGEMENT
            </span>

            <h2>Projects</h2>

            <p>
              Monitor project portfolio status and current
              workforce assignments.
            </p>
          </div>
        </div>

        <div
          className="projects-message projects-error"
          role="alert"
        >
          {error}
        </div>
      </section>
    )
  }

  if (projects.length === 0) {
    return (
      <section className="projects-page">
        <div className="projects-page-header">
          <div>
            <span className="projects-eyebrow">
              PROJECT MANAGEMENT
            </span>

            <h2>Projects</h2>

            <p>
              Monitor project portfolio status and current
              workforce assignments.
            </p>
          </div>
        </div>

        <div className="projects-message">
          No projects are currently available.
        </div>
      </section>
    )
  }

  return (
    <section className="projects-page">
      <div className="projects-page-header">
        <div>
          <span className="projects-eyebrow">
            PROJECT MANAGEMENT
          </span>

          <h2>Projects</h2>

          <p>
            Monitor project portfolio status and current
            workforce assignments.
          </p>
        </div>

        <div className="projects-live-badge">
          <span />
          LIVE PROJECT DATA
        </div>
      </div>

      <div className="projects-kpi-grid">
        <div className="projects-kpi-card">
          <div className="projects-kpi-icon blue">
            ▣
          </div>

          <div>
            <span>Total Projects</span>

            <strong>{summary.total}</strong>

            <small>All projects in the system</small>
          </div>
        </div>

        <div className="projects-kpi-card">
          <div className="projects-kpi-icon green">
            ▶
          </div>

          <div>
            <span>Active Projects</span>

            <strong>{summary.active}</strong>

            <small>Currently active</small>
          </div>
        </div>

        <div className="projects-kpi-card">
          <div className="projects-kpi-icon purple">
            ▣
          </div>

          <div>
            <span>Planned Projects</span>

            <strong>{summary.planned}</strong>

            <small>Scheduled for future</small>
          </div>
        </div>

        <div className="projects-kpi-card">
          <div className="projects-kpi-icon orange">
            ↑
          </div>

          <div>
            <span>High Priority</span>

            <strong>{summary.highPriority}</strong>

            <small>Marked as high priority</small>
          </div>
        </div>
      </div>

      <div className="projects-workspace">
        <div className="projects-portfolio-card">
          <div className="projects-card-header">
            <div>
              <span className="projects-card-eyebrow">
                PROJECT PORTFOLIO
              </span>

              <h3>Current Projects</h3>

              <p>
                Select a project to review its workforce
                assignment and delivery details.
              </p>
            </div>

            <div className="projects-selector">
              <label htmlFor="project-select">
                Selected Project
              </label>

              <select
                id="project-select"
                value={selectedProjectId}
                onChange={(event) =>
                  handleProjectChange(
                    event.target.value,
                  )
                }
              >
                {projects.map((project) => (
                  <option
                    key={project.project_id}
                    value={project.project_id}
                  >
                    {project.project_code} —{' '}
                    {project.project_name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="projects-table-wrapper">
            <table className="projects-table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Client</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Start Date</th>
                  <th>End Date</th>
                </tr>
              </thead>

              <tbody>
                {projects.map((project) => (
                  <tr
                    key={project.project_id}
                    className={
                      project.project_id ===
                      selectedProjectId
                        ? 'selected'
                        : ''
                    }
                    onClick={() =>
                      handleProjectChange(
                        project.project_id,
                      )
                    }
                  >
                    <td>
                      <div className="projects-name-cell">
                        <strong>
                          {project.project_name}
                        </strong>

                        <small>
                          {project.project_code}
                        </small>
                      </div>
                    </td>

                    <td>
                      {project.client_name ?? '—'}
                    </td>

                    <td>
                      <span
                        className={getStatusClass(
                          project.status,
                        )}
                      >
                        {formatLabel(project.status)}
                      </span>
                    </td>

                    <td>
                      <span
                        className={getPriorityClass(
                          project.priority,
                        )}
                      >
                        {formatLabel(project.priority)}
                      </span>
                    </td>

                    <td>
                      {formatDate(project.start_date)}
                    </td>

                    <td>
                      {formatDate(project.end_date)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedProject && (
          <div className="projects-detail-card">
            <div className="projects-detail-header">
              <div>
                <span className="projects-card-eyebrow">
                  SELECTED PROJECT
                </span>

                <h3>
                  {selectedProject.project_name}
                </h3>

                <p>
                  {selectedProject.project_code}
                  {selectedProject.client_name
                    ? ` • ${selectedProject.client_name}`
                    : ''}
                </p>
              </div>

              <span
                className={getStatusClass(
                  selectedProject.status,
                )}
              >
                {formatLabel(selectedProject.status)}
              </span>
            </div>

            <div className="projects-detail-metrics">
              <div>
                <span>Priority</span>

                <strong>
                  {formatLabel(
                    selectedProject.priority,
                  )}
                </strong>
              </div>

              <div>
                <span>Start Date</span>

                <strong>
                  {formatDate(
                    selectedProject.start_date,
                  )}
                </strong>
              </div>

              <div>
                <span>End Date</span>

                <strong>
                  {formatDate(
                    selectedProject.end_date,
                  )}
                </strong>
              </div>

              <div>
                <span>Assigned Employees</span>

                <strong>
                  {loadingEmployees
                    ? '—'
                    : projectEmployees.length}
                </strong>
              </div>
            </div>

            <div className="projects-detail-section">
              <h4>Project Overview</h4>

              <p className="projects-detail-caption">
                Current project description from the
                workforce system.
              </p>

              <p className="projects-description">
                {selectedProject.description ??
                  'No project description is available.'}
              </p>
            </div>

            <div className="projects-detail-divider" />

            <div className="projects-detail-section">
              <div className="projects-assigned-header">
                <div>
                  <h4>Assigned Employees</h4>

                  <p className="projects-detail-caption">
                    Employees currently associated with
                    the selected project.
                  </p>
                </div>

                <span className="projects-assigned-count">
                  {loadingEmployees
                    ? 'LOADING'
                    : `${projectEmployees.length} ASSIGNED`}
                </span>
              </div>

              {loadingEmployees && (
                <div className="projects-empty-state">
                  Loading assigned employees...
                </div>
              )}

              {!loadingEmployees &&
                !error &&
                projectEmployees.length === 0 && (
                  <div className="projects-empty-state">
                    <span className="projects-empty-icon">
                      ♧
                    </span>

                    <span>
                      No employees are currently assigned
                      to this project.
                    </span>
                  </div>
                )}

              {!loadingEmployees &&
                projectEmployees.length > 0 && (
                  <div className="projects-employee-list">
                    {projectEmployees.map((employee) => (
                      <div
                        className="projects-employee-row"
                        key={employee.employee_id}
                      >
                        <div>
                          <strong>
                            {employee.name}
                          </strong>

                          <small>
                            {employee.employee_code}
                            {' • '}
                            {employee.designation ??
                              '—'}
                          </small>
                        </div>

                        <div className="projects-employee-utilization">
                          <strong>
                            {
                              employee.utilization_percentage
                            }
                            %
                          </strong>

                          <div>
                            <span
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
                      </div>
                    ))}
                  </div>
                )}
            </div>

            {error && (
              <div
                className="projects-inline-error"
                role="alert"
              >
                {error}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

export default ProjectsPage