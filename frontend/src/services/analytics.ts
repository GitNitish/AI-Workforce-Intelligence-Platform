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

export interface EmployeeUtilizationAnalytics {
  employeeId: string
  employeeName: string
  employeeCode: string
  department: string | null
  designation: string | null
  utilizationPercentage: number
  availablePercentage: number
}

export interface UtilizationDistribution {
  bench: number
  low: number
  moderate: number
  high: number
  fullyUtilized: number
}

export interface CapacityAnalytics {
  totalCapacity: number
  allocatedCapacity: number
  availableCapacity: number
  utilizationPercentage: number
}

export interface UtilizationAnalytics {
  averageUtilization: number
  medianUtilization: number
  highestUtilization: number
  lowestUtilization: number
  benchEmployees: number
  benchPercentage: number
  distribution: UtilizationDistribution
}

export interface AnalyticsData {
  employees: Employee[]
  projects: Project[]
  allocations: Allocation[]
  staffingRequirements: StaffingRequirement[]
  employeeUtilization: EmployeeUtilizationAnalytics[]
  utilization: UtilizationAnalytics
  capacity: CapacityAnalytics
}

function calculateMedian(values: number[]): number {
  if (values.length === 0) {
    return 0
  }

  const sortedValues = [...values].sort(
    (first, second) => first - second,
  )

  const middleIndex = Math.floor(sortedValues.length / 2)

  if (sortedValues.length % 2 === 0) {
    return (
      (sortedValues[middleIndex - 1] +
        sortedValues[middleIndex]) /
      2
    )
  }

  return sortedValues[middleIndex]
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

  const activeAllocations = allocations.filter(
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

  const employeeUtilization = employees
    .map((employee) => {
      const utilizationPercentage = Math.min(
        activeAllocationByEmployee.get(employee.employee_id) ?? 0,
        100,
      )

      return {
        employeeId: employee.employee_id,
        employeeName: employee.name,
        employeeCode: employee.employee_code,
        department: employee.department,
        designation: employee.designation,
        utilizationPercentage,
        availablePercentage: Math.max(
          0,
          100 - utilizationPercentage,
        ),
      }
    })
    .sort(
      (first, second) =>
        second.utilizationPercentage -
        first.utilizationPercentage,
    )

  const utilizationValues = employeeUtilization.map(
    (employee) => employee.utilizationPercentage,
  )

  const totalEmployees = employeeUtilization.length

  const averageUtilization =
    totalEmployees > 0
      ? utilizationValues.reduce(
          (total, utilization) => total + utilization,
          0,
        ) / totalEmployees
      : 0

  const benchEmployees = utilizationValues.filter(
    (utilization) => utilization === 0,
  ).length

  const distribution: UtilizationDistribution = {
    bench: benchEmployees,
    low: utilizationValues.filter(
      (utilization) =>
        utilization >= 1 && utilization < 50,
    ).length,
    moderate: utilizationValues.filter(
      (utilization) =>
        utilization >= 50 && utilization < 80,
    ).length,
    high: utilizationValues.filter(
      (utilization) =>
        utilization >= 80 && utilization < 100,
    ).length,
    fullyUtilized: utilizationValues.filter(
      (utilization) => utilization >= 100,
    ).length,
  }

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

  const utilizationPercentage =
    totalCapacity > 0
      ? (allocatedCapacity / totalCapacity) * 100
      : 0

  return {
    employees,
    projects,
    allocations,
    staffingRequirements: requirementResponses.flat(),
    employeeUtilization,
    utilization: {
      averageUtilization,
      medianUtilization: calculateMedian(
        utilizationValues,
      ),
      highestUtilization:
        utilizationValues.length > 0
          ? Math.max(...utilizationValues)
          : 0,
      lowestUtilization:
        utilizationValues.length > 0
          ? Math.min(...utilizationValues)
          : 0,
      benchEmployees,
      benchPercentage:
        totalEmployees > 0
          ? (benchEmployees / totalEmployees) * 100
          : 0,
      distribution,
    },
    capacity: {
      totalCapacity,
      allocatedCapacity,
      availableCapacity,
      utilizationPercentage,
    },
  }
}