
import { apiRequest } from './api'
import type { Allocation } from '../types/allocation'

export interface AllocationCreatePayload {
  employee_id: string
  project_id: string
  staffing_requirement_id: string | null
  allocation_percentage: number
  start_date: string
  end_date: string | null
  status: 'active'
}

export interface AllocationUpdatePayload {
  allocation_percentage?: number
  start_date?: string
  end_date?: string | null
}

export function getAllocations(): Promise<Allocation[]> {
  return apiRequest<Allocation[]>('/allocations')
}

export function createAllocation(
  payload: AllocationCreatePayload,
): Promise<Allocation> {
  return apiRequest<Allocation>('/allocations', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateAllocation(
  allocationId: string,
  payload: AllocationUpdatePayload,
): Promise<Allocation> {
  return apiRequest<Allocation>(`/allocations/${allocationId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}


export function deallocateAllocation(allocationId: string): Promise<void> {
  return apiRequest<void>(`/allocations/${allocationId}`, {
    method: 'DELETE',
  })
}
