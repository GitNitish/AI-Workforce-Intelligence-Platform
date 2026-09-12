import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Project } from '../types/project'
import type { StaffingRequirement } from '../types/staffingRequirement'
import { getProjects } from '../services/projects'
import { getProjectRequirements } from '../services/requirements'

function RequirementsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState('')
  const [requirements, setRequirements] = useState<StaffingRequirement[]>([])
  const [loadingProjects, setLoadingProjects] = useState(true)
  const [loadingRequirements, setLoadingRequirements] = useState(false)
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

        const data = await getProjectRequirements(selectedProjectId)
        setRequirements(data)
      } catch (requestError) {
        const message =
          requestError instanceof Error
            ? requestError.message
            : 'Unable to load staffing requirements.'

        setError(message)
        setRequirements([])
      } finally {
        setLoadingRequirements(false)
      }
    }

    void loadRequirements()
  }, [selectedProjectId])

  return (
    <section className="page">
      <div className="page-header">
        <h2>Staffing Requirements</h2>
        <p>
          View staffing requirements associated with each project.
        </p>
      </div>

      {loadingProjects && (
        <div className="loading-message">
          Loading projects...
        </div>
      )}

      {!loadingProjects && projects.length === 0 && !error && (
        <div className="empty-message">
          No projects found. Staffing requirements cannot be loaded without a
          project.
        </div>
      )}

      {!loadingProjects && projects.length > 0 && (
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
      )}

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {loadingRequirements && (
        <div className="loading-message">
          Loading staffing requirements...
        </div>
      )}

      {!loadingRequirements &&
        !error &&
        selectedProjectId &&
        requirements.length === 0 && (
          <div className="empty-message">
            No staffing requirements found for the selected project.
          </div>
        )}

      {!loadingRequirements && requirements.length > 0 && (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Role</th>
                <th>Quantity</th>
                <th>Experience</th>
                <th>Proficiency</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {requirements.map((requirement) => (
                <tr key={requirement.staffing_requirement_id}>
                  <td>{requirement.role_name}</td>
                  <td>{requirement.required_quantity}</td>
                  <td>{requirement.required_experience} yrs</td>
                  <td>{requirement.required_proficiency ?? '—'}</td>
                  <td>{requirement.priority}</td>
                  <td>{requirement.status}</td>
                  <td>{requirement.start_date ?? '—'}</td>
                  <td>{requirement.end_date ?? '—'}</td>
                  <td>
                    <Link
                      to={`/recommendations?requirementId=${encodeURIComponent(
                        requirement.staffing_requirement_id,
                      )}`}
                    >
                      Generate Recommendations
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default RequirementsPage