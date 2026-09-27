import type { Employee } from '../types/employee'
import { API_BASE_URL, getStoredAccessToken } from './api'

export async function getEmployees(): Promise<Employee[]> {
  const response = await fetch(`${API_BASE_URL}/employees`, {
    headers: {
      Authorization: `Bearer ${getStoredAccessToken() ?? ''}`,
    },
  })

  if (!response.ok) {
    throw new Error('Unable to load employees.')
  }

  return (await response.json()) as Employee[]
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

  const accessToken = getStoredAccessToken()

  const response = await fetch(`${API_BASE_URL}/employees/import`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken ?? ''}`,
    },
    body: formData,
  })

  if (!response.ok) {
    let detail = `Employee import failed with status ${response.status}`

    try {
      const errorBody = (await response.json()) as {
        detail?: string
      }

      if (errorBody.detail) {
        detail = errorBody.detail
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(detail)
  }

  return (await response.json()) as EmployeeImportResponse
}

export type EmployeeExportDataset =
  | 'all'
  | 'active'
  | 'inactive'
  | 'available'
  | 'partially_available'

export async function exportEmployees(
  dataset: EmployeeExportDataset,
): Promise<Blob> {
  const accessToken = getStoredAccessToken()

  const response = await fetch(
    `${API_BASE_URL}/employees/export?dataset=${encodeURIComponent(dataset)}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken ?? ''}`,
      },
    },
  )

  if (!response.ok) {
    let detail = `Employee export failed with status ${response.status}`

    try {
      const errorBody = (await response.json()) as {
        detail?: string
      }

      if (errorBody.detail) {
        detail = errorBody.detail
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(detail)
  }

  return response.blob()
}