import type { Employee } from '../types/employee'
import type { EmployeeUtilization } from '../types/utilization'
import { apiRequest } from './api'

export async function getEmployee(
  employeeId: string,
): Promise<Employee> {
  return apiRequest<Employee>(
    `/employees/${employeeId}`,
  )
}

export async function getEmployeeUtilization(
  employeeId: string,
): Promise<EmployeeUtilization> {
  return apiRequest<EmployeeUtilization>(
    `/employees/${employeeId}/utilization`,
  )
}