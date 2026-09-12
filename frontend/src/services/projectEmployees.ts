import type { Employee } from '../types/employee'
import { apiRequest } from './api'

export async function getProjectEmployees(
  projectId: string,
): Promise<Employee[]> {
  return apiRequest<Employee[]>(
    `/projects/${projectId}/employees`,
  )
}