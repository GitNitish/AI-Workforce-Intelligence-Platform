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

export interface StaffingDemandItem {
  label: string
  requirementCount: number
  demand: number
  percentage: number
}

export interface StaffingProjectDemand {
  projectId: string
  projectName: string
  requirementCount: number
  demand: number
  percentage: number
}

export interface StaffingRoleDemand {
  roleName: string
  requirementCount: number
  demand: number
  percentage: number
}

export interface StaffingStatusDemand {
  status: string
  requirementCount: number
  demand: number
  percentage: number
}

export interface StaffingAnalytics {
  openRequirements: number
  openDemand: number
  priorityDemand: StaffingDemandItem[]
  projectDemand: StaffingProjectDemand[]
  roleDemand: StaffingRoleDemand[]
  statusDemand: StaffingStatusDemand[]
}

export interface AnalyticsData {
  employees: Employee[]
  projects: Project[]
  allocations: Allocation[]
  staffingRequirements: StaffingRequirement[]
  employeeUtilization: EmployeeUtilizationAnalytics[]
  utilization: UtilizationAnalytics
  capacity: CapacityAnalytics
  staffing: StaffingAnalytics
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

function normalizeValue(value: string): string {
  return value.trim().toLowerCase()
}

function calculatePercentage(
  value: number,
  total: number,
): number {
  return total > 0 ? (value / total) * 100 : 0
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

  const staffingRequirements = requirementResponses.flat()

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

  const projectById = new Map(
    projects.map((project) => [
      project.project_id,
      project,
    ]),
  )

  const openRequirements = staffingRequirements.filter(
    (requirement) =>
      normalizeValue(requirement.status) === 'open',
  )

  const openDemand = openRequirements.reduce(
    (total, requirement) =>
      total + requirement.required_quantity,
    0,
  )

  const priorityMap = new Map<
    string,
    {
      requirementCount: number
      demand: number
    }
  >()

  for (const requirement of openRequirements) {
    const priority = normalizeValue(requirement.priority)

    const current = priorityMap.get(priority) ?? {
      requirementCount: 0,
      demand: 0,
    }

    priorityMap.set(priority, {
      requirementCount:
        current.requirementCount + 1,
      demand:
        current.demand + requirement.required_quantity,
    })
  }

  const priorityOrder = [
    'high',
    'medium',
    'low',
  ]

  const priorityDemand: StaffingDemandItem[] = Array.from(
    priorityMap.entries(),
  )
    .sort(([first], [second]) => {
      const firstIndex = priorityOrder.indexOf(first)
      const secondIndex = priorityOrder.indexOf(second)

      if (
        firstIndex !== -1 &&
        secondIndex !== -1
      ) {
        return firstIndex - secondIndex
      }

      if (firstIndex !== -1) {
        return -1
      }

      if (secondIndex !== -1) {
        return 1
      }

      return first.localeCompare(second)
    })
    .map(([priority, values]) => ({
      label:
        priority.charAt(0).toUpperCase() +
        priority.slice(1),
      requirementCount: values.requirementCount,
      demand: values.demand,
      percentage: calculatePercentage(
        values.demand,
        openDemand,
      ),
    }))

  const projectDemandMap = new Map<
    string,
    {
      requirementCount: number
      demand: number
    }
  >()

  for (const requirement of openRequirements) {
    const current =
      projectDemandMap.get(requirement.project_id) ?? {
        requirementCount: 0,
        demand: 0,
      }

    projectDemandMap.set(requirement.project_id, {
      requirementCount:
        current.requirementCount + 1,
      demand:
        current.demand + requirement.required_quantity,
    })
  }

  const projectDemand: StaffingProjectDemand[] =
    Array.from(projectDemandMap.entries())
      .map(([projectId, values]) => {
        const project = projectById.get(projectId)

        return {
          projectId,
          projectName:
            project?.project_name ?? 'Unknown Project',
          requirementCount: values.requirementCount,
          demand: values.demand,
          percentage: calculatePercentage(
            values.demand,
            openDemand,
          ),
        }
      })
      .sort(
        (first, second) =>
          second.demand - first.demand,
      )

  const roleDemandMap = new Map<
    string,
    {
      requirementCount: number
      demand: number
    }
  >()

  for (const requirement of openRequirements) {
    const roleName = requirement.role_name.trim()

    const current =
      roleDemandMap.get(roleName) ?? {
        requirementCount: 0,
        demand: 0,
      }

    roleDemandMap.set(roleName, {
      requirementCount:
        current.requirementCount + 1,
      demand:
        current.demand + requirement.required_quantity,
    })
  }

  const roleDemand: StaffingRoleDemand[] = Array.from(
    roleDemandMap.entries(),
  )
    .map(([roleName, values]) => ({
      roleName,
      requirementCount: values.requirementCount,
      demand: values.demand,
      percentage: calculatePercentage(
        values.demand,
        openDemand,
      ),
    }))
    .sort(
      (first, second) =>
        second.demand - first.demand,
    )

  const statusMap = new Map<
    string,
    {
      requirementCount: number
      demand: number
    }
  >()

  for (const requirement of staffingRequirements) {
    const status = requirement.status.trim()

    const current =
      statusMap.get(status) ?? {
        requirementCount: 0,
        demand: 0,
      }

    statusMap.set(status, {
      requirementCount:
        current.requirementCount + 1,
      demand:
        current.demand + requirement.required_quantity,
    })
  }

  const totalRequirementDemand =
    staffingRequirements.reduce(
      (total, requirement) =>
        total + requirement.required_quantity,
      0,
    )

  const statusDemand: StaffingStatusDemand[] =
    Array.from(statusMap.entries())
      .map(([status, values]) => ({
        status,
        requirementCount: values.requirementCount,
        demand: values.demand,
        percentage: calculatePercentage(
          values.demand,
          totalRequirementDemand,
        ),
      }))
      .sort(
        (first, second) =>
          second.demand - first.demand,
      )

  return {
    employees,
    projects,
    allocations,
    staffingRequirements,
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
    staffing: {
      openRequirements: openRequirements.length,
      openDemand,
      priorityDemand,
      projectDemand,
      roleDemand,
      statusDemand,
    },
  }
}