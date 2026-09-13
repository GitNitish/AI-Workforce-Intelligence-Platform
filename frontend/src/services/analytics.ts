import type { Employee } from '../types/employee'
import type { Project } from '../types/project'
import type { StaffingRequirement } from '../types/staffingRequirement'
import { apiRequest } from './api'

export interface Allocation {
  allocation_id: string
  employee_id: string
  project_id: string
  staffing_requirement_id: string | null
  allocation_percentage: number
  start_date: string
  end_date: string | null
  status: string
  allocated_by: string | null
  created_at: string
  updated_at: string
}

export interface AnalyticsData {
  employees: Employee[]
  projects: Project[]
  allocations: Allocation[]
  staffingRequirements: StaffingRequirement[]
}

export async function getAnalyticsData(): Promise<AnalyticsData> {
  const [employees, projects, allocations] = await Promise.all([
    apiRequest<Employee[]>('/employees'),
    apiRequest<Project[]>('/projects'),
    apiRequest<Allocation[]>('/allocations'),
  ])

  const requirementResponses = await Promise.all(
    projects.map((project) =>
      apiRequest<StaffingRequirement[]>(
        `/projects/${project.project_id}/requirements`,
      ),
    ),
  )

  return {
    employees,
    projects,
    allocations,
    staffingRequirements: requirementResponses.flat(),
  }
}