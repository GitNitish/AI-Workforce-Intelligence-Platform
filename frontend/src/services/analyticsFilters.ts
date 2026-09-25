import type { Employee } from '../types/employee'
import type { Project } from '../types/project'
import type { StaffingRequirement } from '../types/staffingRequirement'
import type { Allocation, AnalyticsSourceData } from './analyticsTypes'

export interface AnalyticsFilters {
  department: string | null
  designation: string | null
  projectId: string | null
  projectStatus: string | null
  projectPriority: string | null
  allocationStatus: string | null
  staffingPriority: string | null
  staffingStatus: string | null
}

export interface AnalyticsFilterOptions {
  departments: string[]
  designations: string[]
  projects: Array<{
    id: string
    name: string
  }>
  projectStatuses: string[]
  projectPriorities: string[]
  allocationStatuses: string[]
  staffingPriorities: string[]
  staffingStatuses: string[]
}

export interface FilteredAnalyticsSourceData {
  employees: Employee[]
  projects: Project[]
  allocations: Allocation[]
  staffingRequirements: StaffingRequirement[]
}

export const DEFAULT_ANALYTICS_FILTERS: AnalyticsFilters = {
  department: null,
  designation: null,
  projectId: null,
  projectStatus: null,
  projectPriority: null,
  allocationStatus: null,
  staffingPriority: null,
  staffingStatus: null,
}

function normalizeValue(value: string | null | undefined): string {
  return value?.trim().toLowerCase() ?? ''
}

function matchesFilter(
  value: string | null | undefined,
  selectedValue: string | null,
): boolean {
  if (selectedValue === null) {
    return true
  }

  return normalizeValue(value) === normalizeValue(selectedValue)
}

export function filterAnalyticsSources(
  data: AnalyticsSourceData,
  filters: AnalyticsFilters,
): FilteredAnalyticsSourceData {
  const filteredProjects = data.projects.filter((project) => {
    return (
      matchesFilter(project.project_id, filters.projectId) &&
      matchesFilter(project.status, filters.projectStatus) &&
      matchesFilter(project.priority, filters.projectPriority)
    )
  })

  const filteredProjectIds = new Set(
    filteredProjects.map((project) => project.project_id),
  )

  const filteredEmployees = data.employees.filter((employee) => {
    return (
      matchesFilter(employee.department, filters.department) &&
      matchesFilter(employee.designation, filters.designation)
    )
  })

  const filteredEmployeeIds = new Set(
    filteredEmployees.map((employee) => employee.employee_id),
  )

  const filteredAllocations = data.allocations.filter((allocation) => {
    return (
      filteredProjectIds.has(allocation.project_id) &&
      filteredEmployeeIds.has(allocation.employee_id) &&
      matchesFilter(allocation.status, filters.allocationStatus)
    )
  })

  const filteredStaffingRequirements =
    data.staffingRequirements.filter((requirement) => {
      return (
        filteredProjectIds.has(requirement.project_id) &&
        matchesFilter(
          requirement.priority,
          filters.staffingPriority,
        ) &&
        matchesFilter(
          requirement.status,
          filters.staffingStatus,
        )
      )
    })

  return {
    employees: filteredEmployees,
    projects: filteredProjects,
    allocations: filteredAllocations,
    staffingRequirements: filteredStaffingRequirements,
  }
}

function getSortedUniqueValues(
  values: Array<string | null | undefined>,
): string[] {
  return Array.from(
    new Set(
      values
        .filter(
          (value): value is string =>
            typeof value === 'string' && value.trim().length > 0,
        )
        .map((value) => value.trim()),
    ),
  ).sort((first, second) =>
    first.localeCompare(second, undefined, {
      sensitivity: 'base',
    }),
  )
}

export function getAnalyticsFilterOptions(
  data: AnalyticsSourceData,
): AnalyticsFilterOptions {
  return {
    departments: getSortedUniqueValues(
      data.employees.map((employee) => employee.department),
    ),

    designations: getSortedUniqueValues(
      data.employees.map((employee) => employee.designation),
    ),

    projects: data.projects
      .map((project) => ({
        id: project.project_id,
        name: project.project_name,
      }))
      .sort((first, second) =>
        first.name.localeCompare(second.name, undefined, {
          sensitivity: 'base',
        }),
      ),

    projectStatuses: getSortedUniqueValues(
      data.projects.map((project) => project.status),
    ),

    projectPriorities: getSortedUniqueValues(
      data.projects.map((project) => project.priority),
    ),

    allocationStatuses: getSortedUniqueValues(
      data.allocations.map((allocation) => allocation.status),
    ),

    staffingPriorities: getSortedUniqueValues(
      data.staffingRequirements.map(
        (requirement) => requirement.priority,
      ),
    ),

    staffingStatuses: getSortedUniqueValues(
      data.staffingRequirements.map(
        (requirement) => requirement.status,
      ),
    ),
  }
}

export function hasActiveAnalyticsFilters(
  filters: AnalyticsFilters,
): boolean {
  return Object.values(filters).some(
    (value) => value !== null,
  )
}

export function resetAnalyticsFilters(): AnalyticsFilters {
  return { ...DEFAULT_ANALYTICS_FILTERS }
}