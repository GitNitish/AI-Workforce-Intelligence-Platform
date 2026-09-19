import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Project } from '../types/project'
import type { StaffingRequirement } from '../types/staffingRequirement'
import { getProjects } from '../services/projects'
import { getProjectRequirements } from '../services/requirements'
import './RequirementsPage.css'

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

function formatLabel(value: string | null | undefined): string {
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
  return status.toLowerCase() === 'open'
    ? 'requirements-status open'
    : 'requirements-status'
}

function getPriorityClass(priority: string): string {
  return priority.toLowerCase() === 'high'
    ? 'requirements-priority high'
    : 'requirements-priority'
}

function RequirementsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState('')
  const [requirements, setRequirements] = useState<
    StaffingRequirement[]
  >([])
  const [selectedRequirementId, setSelectedRequirementId] =
    useState('')
  const [loadingProjects, setLoadingProjects] =
    useState(true)
  const [loadingRequirements, setLoadingRequirements] =
    useState(false)
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

    async function loadRequirements() {
      try {
        setLoadingRequirements(true)
        setError(null)

        const data =
          await getProjectRequirements(
            selectedProjectId,
          )

        setRequirements(data)

        if (data.length > 0) {
          setSelectedRequirementId(
            data[0].staffing_requirement_id,
          )
        } else {
          setSelectedRequirementId('')
        }
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load staffing requirements.'

        setError(message)
        setRequirements([])
        setSelectedRequirementId('')
      } finally {
        setLoadingRequirements(false)
      }
    }

    void loadRequirements()
  }, [selectedProjectId])

  const handleProjectChange = (
    projectId: string,
  ) => {
    setSelectedProjectId(projectId)
    setRequirements([])
    setSelectedRequirementId('')
  }

  const selectedProject = useMemo(
    () =>
      projects.find(
        (project) =>
          project.project_id === selectedProjectId,
      ) ?? null,
    [projects, selectedProjectId],
  )

  const selectedRequirement = useMemo(
    () =>
      requirements.find(
        (requirement) =>
          requirement.staffing_requirement_id ===
          selectedRequirementId,
      ) ?? null,
    [requirements, selectedRequirementId],
  )

  const summary = useMemo(() => {
    const total = requirements.length

    const open = requirements.filter(
      (requirement) =>
        requirement.status.toLowerCase() === 'open',
    ).length

    const highPriority = requirements.filter(
      (requirement) =>
        requirement.priority.toLowerCase() === 'high',
    ).length

    const totalQuantity = requirements.reduce(
      (sum, requirement) =>
        sum + requirement.required_quantity,
      0,
    )

    return {
      total,
      open,
      highPriority,
      totalQuantity,
    }
  }, [requirements])

  if (loadingProjects) {
    return (
      <section className="requirements-page">
        <div className="requirements-page-header">
          <div>
            <span className="requirements-eyebrow">
              WORKFORCE DEMAND
            </span>

            <h2>Staffing Requirements</h2>

            <p>
              Review staffing demand associated with
              each project.
            </p>
          </div>
        </div>

        <div className="requirements-message">
          Loading projects...
        </div>
      </section>
    )
  }

  if (error && projects.length === 0) {
    return (
      <section className="requirements-page">
        <div className="requirements-page-header">
          <div>
            <span className="requirements-eyebrow">
              WORKFORCE DEMAND
            </span>

            <h2>Staffing Requirements</h2>

            <p>
              Review staffing demand associated with
              each project.
            </p>
          </div>
        </div>

        <div
          className="requirements-message requirements-error"
          role="alert"
        >
          {error}
        </div>
      </section>
    )
  }

  if (projects.length === 0) {
    return (
      <section className="requirements-page">
        <div className="requirements-page-header">
          <div>
            <span className="requirements-eyebrow">
              WORKFORCE DEMAND
            </span>

            <h2>Staffing Requirements</h2>

            <p>
              Review staffing demand associated with
              each project.
            </p>
          </div>
        </div>

        <div className="requirements-message">
          No projects found. Staffing requirements cannot
          be loaded without a project.
        </div>
      </section>
    )
  }

  return (
    <section className="requirements-page">
      <div className="requirements-page-header">
        <div>
          <span className="requirements-eyebrow">
            WORKFORCE DEMAND
          </span>

          <h2>Staffing Requirements</h2>

          <p>
            Review staffing demand associated with each
            project.
          </p>
        </div>

        <div className="requirements-live-badge">
          <span />
          LIVE REQUIREMENT DATA
        </div>
      </div>

      <div className="requirements-kpi-grid">
        <div className="requirements-kpi-card">
          <div className="requirements-kpi-icon blue">
            ▣
          </div>

          <div>
            <span>Requirements</span>

            <strong>{summary.total}</strong>

            <small>Current project demand</small>
          </div>
        </div>

        <div className="requirements-kpi-card">
          <div className="requirements-kpi-icon green">
            ✓
          </div>

          <div>
            <span>Open Requirements</span>

            <strong>{summary.open}</strong>

            <small>Currently open demand</small>
          </div>
        </div>

        <div className="requirements-kpi-card">
          <div className="requirements-kpi-icon purple">
            #
          </div>

          <div>
            <span>Required Positions</span>

            <strong>{summary.totalQuantity}</strong>

            <small>Total requested quantity</small>
          </div>
        </div>

        <div className="requirements-kpi-card">
          <div className="requirements-kpi-icon orange">
            ↑
          </div>

          <div>
            <span>High Priority</span>

            <strong>{summary.highPriority}</strong>

            <small>Marked as high priority</small>
          </div>
        </div>
      </div>

      <div className="requirements-workspace">
        <div className="requirements-portfolio-card">
          <div className="requirements-card-header">
            <div>
              <span className="requirements-card-eyebrow">
                STAFFING DEMAND
              </span>

              <h3>Current Requirements</h3>

              <p>
                Select a project to review its staffing
                demand.
              </p>
            </div>

            <div className="requirements-selector">
              <label htmlFor="requirements-project-select">
                Selected Project
              </label>

              <select
                id="requirements-project-select"
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

          {loadingRequirements && (
            <div className="requirements-message">
              Loading staffing requirements...
            </div>
          )}

          {!loadingRequirements &&
            !error &&
            requirements.length === 0 && (
              <div className="requirements-empty-state">
                <strong>
                  No staffing requirements found
                </strong>

                <span>
                  The selected project currently has no
                  recorded staffing demand.
                </span>
              </div>
            )}

          {!loadingRequirements &&
            requirements.length > 0 && (
              <div className="requirements-table-wrapper">
                <table className="requirements-table">
                  <thead>
                    <tr>
                      <th>Role</th>
                      <th>Qty</th>
                      <th>Experience</th>
                      <th>Proficiency</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Start</th>
                      <th>End</th>
                    </tr>
                  </thead>

                  <tbody>
                    {requirements.map(
                      (requirement) => (
                        <tr
                          key={
                            requirement.staffing_requirement_id
                          }
                          className={
                            requirement.staffing_requirement_id ===
                            selectedRequirementId
                              ? 'selected'
                              : ''
                          }
                          onClick={() =>
                            setSelectedRequirementId(
                              requirement.staffing_requirement_id,
                            )
                          }
                        >
                          <td>
                            <div className="requirements-role-cell">
                              <strong>
                                {requirement.role_name}
                              </strong>

                              <small>
                                {requirement.staffing_requirement_id.slice(
                                  0,
                                  8,
                                )}
                              </small>
                            </div>
                          </td>

                          <td>
                            {
                              requirement.required_quantity
                            }
                          </td>

                          <td>
                            {
                              requirement.required_experience
                            }{' '}
                            yrs
                          </td>

                          <td>
                            {formatLabel(
                              requirement.required_proficiency,
                            )}
                          </td>

                          <td>
                            <span
                              className={getPriorityClass(
                                requirement.priority,
                              )}
                            >
                              {formatLabel(
                                requirement.priority,
                              )}
                            </span>
                          </td>

                          <td>
                            <span
                              className={getStatusClass(
                                requirement.status,
                              )}
                            >
                              {formatLabel(
                                requirement.status,
                              )}
                            </span>
                          </td>

                          <td>
                            {formatDate(
                              requirement.start_date,
                            )}
                          </td>

                          <td>
                            {formatDate(
                              requirement.end_date,
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
        </div>

        {selectedRequirement && (
          <div className="requirements-detail-card">
            <div className="requirements-detail-header">
              <div>
                <span className="requirements-card-eyebrow">
                  SELECTED REQUIREMENT
                </span>

                <h3>
                  {selectedRequirement.role_name}
                </h3>

                <p>
                  {selectedProject?.project_code ??
                    'Project'}
                  {selectedProject
                    ? ` • ${selectedProject.project_name}`
                    : ''}
                </p>
              </div>

              <span
                className={getStatusClass(
                  selectedRequirement.status,
                )}
              >
                {formatLabel(
                  selectedRequirement.status,
                )}
              </span>
            </div>

            <div className="requirements-detail-metrics">
              <div>
                <span>Required Quantity</span>

                <strong>
                  {selectedRequirement.required_quantity}
                </strong>
              </div>

              <div>
                <span>Experience</span>

                <strong>
                  {
                    selectedRequirement.required_experience
                  }{' '}
                  yrs
                </strong>
              </div>

              <div>
                <span>Proficiency</span>

                <strong>
                  {formatLabel(
                    selectedRequirement.required_proficiency,
                  )}
                </strong>
              </div>

              <div>
                <span>Priority</span>

                <strong>
                  {formatLabel(
                    selectedRequirement.priority,
                  )}
                </strong>
              </div>
            </div>

            <div className="requirements-detail-section">
              <h4>Requirement Timeline</h4>

              <div className="requirements-timeline">
                <div>
                  <span>Start Date</span>

                  <strong>
                    {formatDate(
                      selectedRequirement.start_date,
                    )}
                  </strong>
                </div>

                <div>
                  <span>End Date</span>

                  <strong>
                    {formatDate(
                      selectedRequirement.end_date,
                    )}
                  </strong>
                </div>
              </div>
            </div>

            <div className="requirements-detail-divider" />

            <div className="requirements-detail-section">
              <h4>Candidate Matching</h4>

              <p className="requirements-detail-caption">
                Generate ranked candidate recommendations
                for this staffing requirement.
              </p>

              <Link
                className="requirements-action"
                to={`/recommendations?requirementId=${encodeURIComponent(
                  selectedRequirement.staffing_requirement_id,
                )}`}
              >
                Generate Recommendations
                <span>→</span>
              </Link>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div
          className="requirements-inline-error"
          role="alert"
        >
          {error}
        </div>
      )}
    </section>
  )
}

export default RequirementsPage