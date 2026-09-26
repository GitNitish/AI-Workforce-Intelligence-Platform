import type { Employee } from '../types/employee'
import { apiRequest } from './api'

export async function getEmployees(): Promise<Employee[]> {
  return apiRequest<Employee[]>('/employees')
}

export interface EmployeeImportResponse {
  message?: string
  imported_count?: number
  skipped_count?: number
  errors?: string[]
}

export async function uploadEmployeeImport(
  file: File,
): Promise<EmployeeImportResponse> {
  const formData = new FormData()

  formData.append('file', file)

  return apiRequest<EmployeeImportResponse>(
    '/employees/import',
    {
      method: 'POST',
      body: formData,
    },
  )
}