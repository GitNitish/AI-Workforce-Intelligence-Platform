
import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import type { Allocation } from '../types/allocation'
import type { Employee } from '../types/employee'
import type { Project } from '../types/project'
import type { StaffingRequirement } from '../types/staffingRequirement'
import { useAuth } from '../auth/useAuth'
import {
  createAllocation,
  deallocateAllocation,
  getAllocations,
  updateAllocation,
} from '../services/allocations'
import type {
  AllocationCreatePayload,
  AllocationUpdatePayload,
} from '../services/allocations'
import { getEmployees } from '../services/employees'
import { getProjects } from '../services/projects'
import { getProjectRequirements } from '../services/requirements'
import './AllocationsPage.css'

type RequirementLookup = Record<string, StaffingRequirement>
type FormMode = 'create' | 'edit'

interface AllocationFormState {
  employee_id: string
  project_id: string
  staffing_requirement_id: string
  allocation_percentage: string
  start_date: string
  end_date: string
}

const EMPTY_FORM: AllocationFormState = {
  employee_id: '',
  project_id: '',
  staffing_requirement_id: '',
  allocation_percentage: '',
  start_date: '',
  end_date: '',
}

function formatDate(value: string | null): string {
  if (!value) return '—'

  const date = new Date(`${value}T00:00:00`)

  if (Number.isNaN(date.getTime())) return value

  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatLabel(value: string | null | undefined): string {
  if (!value) return '—'

  return value
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

function getStatusClass(status: string): string {
  return status.toLowerCase() === 'active'
    ? 'allocations-status active'
    : 'allocations-status'
}

function AllocationsPage() {
  const { hasPermission } = useAuth()
  const canWrite = hasPermission('allocation.write')

  const [allocations, setAllocations] = useState<Allocation[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [requirements, setRequirements] = useState<RequirementLookup>({})
  const [selectedAllocationId, setSelectedAllocationId] = useState('')
  const [search, setSearch] = useState('')
  const [employeeFilter, setEmployeeFilter] = useState('all')
  const [projectFilter, setProjectFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [formMode, setFormMode] = useState<FormMode | null>(null)
  const [formState, setFormState] = useState<AllocationFormState>(EMPTY_FORM)
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [deallocationTarget, setDeallocationTarget] = useState<Allocation | null>(null)
  const [deallocating, setDeallocating] = useState(false)
  const [deallocationError, setDeallocationError] = useState<string | null>(null)

  async function refreshAllocations(selectId?: string) {
    const data = await getAllocations()
    setAllocations(data)

    if (selectId && data.some((item) => item.allocation_id === selectId)) {
      setSelectedAllocationId(selectId)
    } else if (data.length > 0) {
      setSelectedAllocationId(data[0].allocation_id)
    } else {
      setSelectedAllocationId('')
    }
  }

  useEffect(() => {
    let cancelled = false

    async function loadAllocationData() {
      try {
        setLoading(true)
        setError(null)

        const [allocationData, employeeData, projectData] =
          await Promise.all([
            getAllocations(),
            getEmployees(),
            getProjects(),
          ])

        const requirementResults = await Promise.all(
          projectData.map(async (project) => {
            try {
              return await getProjectRequirements(project.project_id)
            } catch {
              return []
            }
          }),
        )

        const requirementLookup: RequirementLookup = {}

        requirementResults.flat().forEach((requirement) => {
          requirementLookup[requirement.staffing_requirement_id] =
            requirement
        })

        if (cancelled) return

        setAllocations(allocationData)
        setEmployees(employeeData)
        setProjects(projectData)
        setRequirements(requirementLookup)

        if (allocationData.length > 0) {
          setSelectedAllocationId(allocationData[0].allocation_id)
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : 'Unable to load allocation data.',
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void loadAllocationData()

    return () => {
      cancelled = true
    }
  }, [])

  const employeeLookup = useMemo(
    () =>
      Object.fromEntries(
        employees.map((employee) => [employee.employee_id, employee]),
      ),
    [employees],
  )

  const projectLookup = useMemo(
    () =>
      Object.fromEntries(
        projects.map((project) => [project.project_id, project]),
      ),
    [projects],
  )

  const summary = useMemo(() => {
    const activeAllocations = allocations.filter(
      (allocation) => allocation.status.toLowerCase() === 'active',
    )

    return {
      total: allocations.length,
      active: activeAllocations.length,
      deallocated: allocations.filter(
        (allocation) => allocation.status.toLowerCase() === 'deallocated',
      ).length,
      employees: new Set(
        activeAllocations.map((allocation) => allocation.employee_id),
      ).size,
    }
  }, [allocations])

  const filteredAllocations = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return allocations.filter((allocation) => {
      const employee = employeeLookup[allocation.employee_id]
      const project = projectLookup[allocation.project_id]
      const requirement = allocation.staffing_requirement_id
        ? requirements[allocation.staffing_requirement_id]
        : undefined

      const matchesSearch =
        !normalizedSearch ||
        [
          employee?.name,
          employee?.employee_code,
          project?.project_name,
          project?.project_code,
          requirement?.role_name,
          allocation.allocation_id,
        ].some((value) => value?.toLowerCase().includes(normalizedSearch))

      const matchesEmployee =
        employeeFilter === 'all' ||
        allocation.employee_id === employeeFilter

      const matchesProject =
        projectFilter === 'all' ||
        allocation.project_id === projectFilter

      const matchesStatus =
        statusFilter === 'all' ||
        allocation.status.toLowerCase() === statusFilter

      return (
        matchesSearch &&
        matchesEmployee &&
        matchesProject &&
        matchesStatus
      )
    })
  }, [
    allocations,
    employeeLookup,
    projectLookup,
    requirements,
    search,
    employeeFilter,
    projectFilter,
    statusFilter,
  ])

  const selectedAllocation =
    filteredAllocations.find(
      (allocation) => allocation.allocation_id === selectedAllocationId,
    ) ?? filteredAllocations[0] ?? null

  const effectiveSelectedAllocationId =
    selectedAllocation?.allocation_id ?? ''

  const formRequirements = useMemo(
    () =>
      Object.values(requirements).filter(
        (requirement) => requirement.project_id === formState.project_id,
      ),
    [requirements, formState.project_id],
  )

  function resetFilters() {
    setSearch('')
    setEmployeeFilter('all')
    setProjectFilter('all')
    setStatusFilter('all')
  }

  function openCreateForm() {
    setFormState(EMPTY_FORM)
    setFormError(null)
    setFormMode('create')
  }

  function openEditForm(allocation: Allocation) {
    setFormState({
      employee_id: allocation.employee_id,
      project_id: allocation.project_id,
      staffing_requirement_id: allocation.staffing_requirement_id ?? '',
      allocation_percentage: String(allocation.allocation_percentage),
      start_date: allocation.start_date,
      end_date: allocation.end_date ?? '',
    })
    setFormError(null)
    setFormMode('edit')
  }

  function closeForm() {
    if (saving) return
    setFormMode(null)
    setFormError(null)
  }

  function updateFormField(
    field: keyof AllocationFormState,
    value: string,
  ) {
    setFormState((current) => {
      if (field === 'project_id') {
        return {
          ...current,
          project_id: value,
          staffing_requirement_id: '',
        }
      }

      return { ...current, [field]: value }
    })
  }

  async function handleFormSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    const percentage = Number(formState.allocation_percentage)

    if (!Number.isFinite(percentage) || percentage <= 0 || percentage > 100) {
      setFormError('Allocation percentage must be greater than 0 and at most 100.')
      return
    }

    if (!formState.start_date) {
      setFormError('Please select a start date.')
      return
    }

    if (
      formState.end_date &&
      formState.end_date < formState.start_date
    ) {
      setFormError('End date cannot be earlier than start date.')
      return
    }

    if (formMode === 'create' && (!formState.employee_id || !formState.project_id)) {
      setFormError('Please select an employee and a project.')
      return
    }

    setSaving(true)

    try {
      if (formMode === 'create') {
        const payload: AllocationCreatePayload = {
          employee_id: formState.employee_id,
          project_id: formState.project_id,
          staffing_requirement_id:
            formState.staffing_requirement_id || null,
          allocation_percentage: percentage,
          start_date: formState.start_date,
          end_date: formState.end_date || null,
          status: 'active',
        }

        const created = await createAllocation(payload)
        await refreshAllocations(created.allocation_id)
      } else if (formMode === 'edit' && selectedAllocation) {
        const payload: AllocationUpdatePayload = {
          allocation_percentage: percentage,
          start_date: formState.start_date,
          end_date: formState.end_date || null,
        }

        await updateAllocation(selectedAllocation.allocation_id, payload)
        await refreshAllocations(selectedAllocation.allocation_id)
      }

      setFormMode(null)
      setFormError(null)
    } catch (requestError) {
      setFormError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to save allocation.',
      )
    } finally {
      setSaving(false)
    }
  }

  function openDeallocationConfirmation(allocation: Allocation) {
    if (!canWrite || allocation.status.toLowerCase() !== 'active') return
    setDeallocationError(null)
    setDeallocationTarget(allocation)
  }

  function closeDeallocationConfirmation() {
    if (deallocating) return
    setDeallocationTarget(null)
    setDeallocationError(null)
  }

  async function handleDeallocation() {
    if (!deallocationTarget || !canWrite) return

    setDeallocating(true)
    setDeallocationError(null)

    try {
      await deallocateAllocation(deallocationTarget.allocation_id)
      await refreshAllocations(deallocationTarget.allocation_id)
      setDeallocationTarget(null)
    } catch (requestError) {
      setDeallocationError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to deallocate this allocation.',
      )
    } finally {
      setDeallocating(false)
    }
  }

  if (loading) {
    return (
      <section className="allocations-page">
        <div className="allocations-page-header">
          <div>
            <span className="allocations-eyebrow">WORKFORCE OPERATIONS</span>
            <h2>Allocations</h2>
            <p>Review employee assignments and allocation history.</p>
          </div>
        </div>
        <div className="allocations-message">Loading allocation records...</div>
      </section>
    )
  }

  if (error && allocations.length === 0) {
    return (
      <section className="allocations-page">
        <div className="allocations-page-header">
          <div>
            <span className="allocations-eyebrow">WORKFORCE OPERATIONS</span>
            <h2>Allocations</h2>
            <p>Review employee assignments and allocation history.</p>
          </div>
        </div>
        <div className="allocations-message allocations-error" role="alert">
          {error}
        </div>
      </section>
    )
  }

  return (
    <section className="allocations-page">
      <div className="allocations-page-header">
        <div>
          <span className="allocations-eyebrow">WORKFORCE OPERATIONS</span>
          <h2>Allocations</h2>
          <p>
            Review employee assignments, allocation percentages and
            allocation history.
          </p>
        </div>

        <div className="allocations-header-actions">
          {canWrite && (
            <button
              type="button"
              className="allocations-primary-button"
              onClick={openCreateForm}
            >
              + Create Allocation
            </button>
          )}
          <div className="allocations-live-badge">
            <span />
            LIVE ALLOCATION DATA
          </div>
        </div>
      </div>

      <div className="allocations-kpi-grid">
        <div className="allocations-kpi-card">
          <div className="allocations-kpi-icon blue">▣</div>
          <div>
            <span>Total Records</span>
            <strong>{summary.total}</strong>
            <small>All allocation records</small>
          </div>
        </div>
        <div className="allocations-kpi-card">
          <div className="allocations-kpi-icon green">✓</div>
          <div>
            <span>Active Allocations</span>
            <strong>{summary.active}</strong>
            <small>Currently active assignments</small>
          </div>
        </div>
        <div className="allocations-kpi-card">
          <div className="allocations-kpi-icon orange">↘</div>
          <div>
            <span>Deallocated Records</span>
            <strong>{summary.deallocated}</strong>
            <small>Historical assignments</small>
          </div>
        </div>
        <div className="allocations-kpi-card">
          <div className="allocations-kpi-icon purple">◉</div>
          <div>
            <span>Employees Allocated</span>
            <strong>{summary.employees}</strong>
            <small>With active allocations</small>
          </div>
        </div>
      </div>

      <div className="allocations-workspace">
        <div className="allocations-list-card">
          <div className="allocations-card-header">
            <div>
              <span className="allocations-card-eyebrow">ALLOCATION REGISTER</span>
              <h3>Allocation Records</h3>
              <p>Select a record to review its assignment details.</p>
            </div>
            <span className="allocations-record-count">
              {filteredAllocations.length} RECORDS
            </span>
          </div>

          <div className="allocations-filters">
            <label className="allocations-search">
              <span>Search</span>
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Employee, project or role..."
              />
            </label>

            <label>
              <span>Employee</span>
              <select
                value={employeeFilter}
                onChange={(event) => setEmployeeFilter(event.target.value)}
              >
                <option value="all">All employees</option>
                {employees.map((employee) => (
                  <option key={employee.employee_id} value={employee.employee_id}>
                    {employee.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Project</span>
              <select
                value={projectFilter}
                onChange={(event) => setProjectFilter(event.target.value)}
              >
                <option value="all">All projects</option>
                {projects.map((project) => (
                  <option key={project.project_id} value={project.project_id}>
                    {project.project_name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Status</span>
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
              >
                <option value="all">All statuses</option>
                <option value="active">Active</option>
                <option value="deallocated">Deallocated</option>
              </select>
            </label>

            <button
              type="button"
              className="allocations-reset-button"
              onClick={resetFilters}
            >
              Reset
            </button>
          </div>

          {filteredAllocations.length === 0 ? (
            <div className="allocations-empty-state">
              <strong>No matching allocation records</strong>
              <span>
                {allocations.length === 0
                  ? 'Create an allocation to begin assigning employees to projects.'
                  : 'Change the filters or search term to view other records.'}
              </span>
            </div>
          ) : (
            <div className="allocations-table-wrapper">
              <table className="allocations-table">
                <thead>
                  <tr>
                    <th>Employee</th>
                    <th>Project</th>
                    <th>Staffing Requirement</th>
                    <th>Allocation</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAllocations.map((allocation) => {
                    const employee = employeeLookup[allocation.employee_id]
                    const project = projectLookup[allocation.project_id]
                    const requirement = allocation.staffing_requirement_id
                      ? requirements[allocation.staffing_requirement_id]
                      : undefined

                    return (
                      <tr
                        key={allocation.allocation_id}
                        className={
                          allocation.allocation_id === effectiveSelectedAllocationId
                            ? 'selected'
                            : ''
                        }
                        onClick={() =>
                          setSelectedAllocationId(allocation.allocation_id)
                        }
                      >
                        <td>
                          <div className="allocations-name-cell">
                            <strong>{employee?.name ?? 'Unknown employee'}</strong>
                            <small>{employee?.employee_code ?? allocation.employee_id}</small>
                          </div>
                        </td>
                        <td>
                          <div className="allocations-name-cell">
                            <strong>{project?.project_name ?? 'Unknown project'}</strong>
                            <small>{project?.project_code ?? allocation.project_id}</small>
                          </div>
                        </td>
                        <td>{requirement?.role_name ?? '—'}</td>
                        <td><strong>{allocation.allocation_percentage}%</strong></td>
                        <td>{formatDate(allocation.start_date)}</td>
                        <td>{formatDate(allocation.end_date)}</td>
                        <td>
                          <span className={getStatusClass(allocation.status)}>
                            {formatLabel(allocation.status)}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {selectedAllocation && (
          <aside className="allocations-detail-card">
            <div className="allocations-detail-header">
              <div>
                <span className="allocations-card-eyebrow">SELECTED ALLOCATION</span>
                <h3>
                  {employeeLookup[selectedAllocation.employee_id]?.name ??
                    'Unknown employee'}
                </h3>
                <p>
                  {projectLookup[selectedAllocation.project_id]?.project_name ??
                    'Unknown project'}
                </p>
              </div>
              <span className={getStatusClass(selectedAllocation.status)}>
                {formatLabel(selectedAllocation.status)}
              </span>
            </div>

            <div className="allocations-detail-percentage">
              <span>Allocation percentage</span>
              <strong>{selectedAllocation.allocation_percentage}%</strong>
            </div>

            <div className="allocations-detail-grid">
              <div>
                <span>Employee Code</span>
                <strong>{employeeLookup[selectedAllocation.employee_id]?.employee_code ?? '—'}</strong>
              </div>
              <div>
                <span>Project Code</span>
                <strong>{projectLookup[selectedAllocation.project_id]?.project_code ?? '—'}</strong>
              </div>
              <div>
                <span>Staffing Requirement</span>
                <strong>
                  {selectedAllocation.staffing_requirement_id
                    ? requirements[selectedAllocation.staffing_requirement_id]?.role_name ??
                      'Requirement unavailable'
                    : 'Not linked'}
                </strong>
              </div>
              <div>
                <span>Allocated By</span>
                <strong>{selectedAllocation.allocated_by ?? '—'}</strong>
              </div>
              <div>
                <span>Start Date</span>
                <strong>{formatDate(selectedAllocation.start_date)}</strong>
              </div>
              <div>
                <span>End Date</span>
                <strong>{formatDate(selectedAllocation.end_date)}</strong>
              </div>
              <div>
                <span>Created</span>
                <strong>{new Date(selectedAllocation.created_at).toLocaleString('en-IN')}</strong>
              </div>
              <div>
                <span>Last Updated</span>
                <strong>{new Date(selectedAllocation.updated_at).toLocaleString('en-IN')}</strong>
              </div>
            </div>

            <div className="allocations-detail-id">
              <span>Allocation ID</span>
              <code>{selectedAllocation.allocation_id}</code>
            </div>

            {canWrite && selectedAllocation.status.toLowerCase() === 'active' && (
              <div className="allocations-detail-actions">
                <button
                  type="button"
                  className="allocations-secondary-button"
                  onClick={() => openEditForm(selectedAllocation)}
                >
                  Edit Allocation
                </button>
                <button
                  type="button"
                  className="allocations-secondary-button"
                  onClick={() => openDeallocationConfirmation(selectedAllocation)}
                >
                  Deallocate
                </button>
              </div>
            )}
          </aside>
        )}
      </div>

      {error && (
        <div className="allocations-inline-error" role="alert">{error}</div>
      )}

      {formMode && (
        <div className="allocations-modal-backdrop">
          <section
            className="allocations-form-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="allocations-form-title"
          >
            <div className="allocations-form-header">
              <div>
                <span className="allocations-card-eyebrow">
                  WORKFORCE OPERATIONS
                </span>
                <h3 id="allocations-form-title">
                  {formMode === 'create' ? 'Create Allocation' : 'Edit Allocation'}
                </h3>
                <p>
                  {formMode === 'create'
                    ? 'Assign an employee to an eligible project.'
                    : 'Update the allocation percentage and assignment dates.'}
                </p>
              </div>
              <button
                type="button"
                className="allocations-modal-close"
                onClick={closeForm}
                disabled={saving}
                aria-label="Close form"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleFormSubmit}>
              <div className="allocations-form-grid">
                {formMode === 'create' && (
                  <>
                    <label>
                      Employee *
                      <select
                        required
                        value={formState.employee_id}
                        onChange={(event) =>
                          updateFormField('employee_id', event.target.value)
                        }
                      >
                        <option value="">Select employee</option>
                        {employees
                          .filter((employee) => employee.status.toLowerCase() === 'active')
                          .map((employee) => (
                            <option
                              key={employee.employee_id}
                              value={employee.employee_id}
                            >
                              {employee.name} ({employee.employee_code})
                            </option>
                          ))}
                      </select>
                    </label>

                    <label>
                      Project *
                      <select
                        required
                        value={formState.project_id}
                        onChange={(event) =>
                          updateFormField('project_id', event.target.value)
                        }
                      >
                        <option value="">Select project</option>
                        {projects
                          .filter((project) =>
                            ['active', 'in_progress'].includes(
                              project.status.toLowerCase(),
                            ),
                          )
                          .map((project) => (
                            <option
                              key={project.project_id}
                              value={project.project_id}
                            >
                              {project.project_name} ({project.project_code})
                            </option>
                          ))}
                      </select>
                    </label>

                    <label className="allocations-form-full">
                      Staffing Requirement
                      <select
                        value={formState.staffing_requirement_id}
                        onChange={(event) =>
                          updateFormField(
                            'staffing_requirement_id',
                            event.target.value,
                          )
                        }
                        disabled={!formState.project_id}
                      >
                        <option value="">No requirement linked</option>
                        {formRequirements.map((requirement) => (
                          <option
                            key={requirement.staffing_requirement_id}
                            value={requirement.staffing_requirement_id}
                          >
                            {requirement.role_name}
                          </option>
                        ))}
                      </select>
                    </label>
                  </>
                )}

                {formMode === 'edit' && selectedAllocation && (
                  <div className="allocations-form-context allocations-form-full">
                    <span>Employee</span>
                    <strong>{employeeLookup[selectedAllocation.employee_id]?.name ?? 'Unknown employee'}</strong>
                    <span>Project</span>
                    <strong>{projectLookup[selectedAllocation.project_id]?.project_name ?? 'Unknown project'}</strong>
                    <small>Employee, project and staffing requirement cannot be changed when editing.</small>
                  </div>
                )}

                <label>
                  Allocation Percentage *
                  <input
                    type="number"
                    required
                    min="0.01"
                    max="100"
                    step="0.01"
                    value={formState.allocation_percentage}
                    onChange={(event) =>
                      updateFormField('allocation_percentage', event.target.value)
                    }
                    placeholder="e.g. 50"
                  />
                </label>

                <label>
                  Start Date *
                  <input
                    type="date"
                    required
                    value={formState.start_date}
                    onChange={(event) =>
                      updateFormField('start_date', event.target.value)
                    }
                  />
                </label>

                <label className="allocations-form-full">
                  End Date
                  <input
                    type="date"
                    min={formState.start_date || undefined}
                    value={formState.end_date}
                    onChange={(event) =>
                      updateFormField('end_date', event.target.value)
                    }
                  />
                  <small>Leave blank for an open-ended allocation.</small>
                </label>
              </div>

              {formError && (
                <div className="allocations-inline-error" role="alert">
                  {formError}
                </div>
              )}

              <div className="allocations-form-actions">
                <button
                  type="button"
                  className="allocations-secondary-button"
                  onClick={closeForm}
                  disabled={saving}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="allocations-primary-button"
                  disabled={saving}
                >
                  {saving
                    ? 'Saving...'
                    : formMode === 'create'
                      ? 'Create Allocation'
                      : 'Save Changes'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}

      {deallocationTarget && (
        <div className="allocations-modal-backdrop">
          <section
            className="allocations-form-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="allocations-deallocation-title"
          >
            <div className="allocations-form-header">
              <div>
                <span className="allocations-card-eyebrow">WORKFORCE OPERATIONS</span>
                <h3 id="allocations-deallocation-title">Deallocate Employee</h3>
                <p>
                  This will end the active allocation and mark the record as
                  deallocated. The allocation history will be retained.
                </p>
              </div>
              <button
                type="button"
                className="allocations-modal-close"
                onClick={closeDeallocationConfirmation}
                disabled={deallocating}
                aria-label="Close confirmation"
              >
                ×
              </button>
            </div>

            <div className="allocations-form-context">
              <span>Employee</span>
              <strong>
                {employeeLookup[deallocationTarget.employee_id]?.name ??
                  deallocationTarget.employee_id}
              </strong>
              <span>Project</span>
              <strong>
                {projectLookup[deallocationTarget.project_id]?.project_name ??
                  deallocationTarget.project_id}
              </strong>
              <span>Allocation</span>
              <strong>{deallocationTarget.allocation_percentage}%</strong>
              <span>Start Date</span>
              <strong>{formatDate(deallocationTarget.start_date)}</strong>
            </div>

            {deallocationError && (
              <div className="allocations-inline-error" role="alert">
                {deallocationError}
              </div>
            )}

            <div className="allocations-form-actions">
              <button
                type="button"
                className="allocations-secondary-button"
                onClick={closeDeallocationConfirmation}
                disabled={deallocating}
              >
                Cancel
              </button>
              <button
                type="button"
                className="allocations-primary-button"
                onClick={handleDeallocation}
                disabled={deallocating}
              >
                {deallocating ? 'Deallocating...' : 'Confirm Deallocation'}
              </button>
            </div>
          </section>
        </div>
      )}
    </section>
  )
}

export default AllocationsPage
