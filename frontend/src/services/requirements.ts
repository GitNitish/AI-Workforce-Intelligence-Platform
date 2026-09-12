import type { StaffingRequirement } from '../types/staffingRequirement'
import { apiRequest } from './api'

export async function getProjectRequirements(
  projectId: string,
): Promise<StaffingRequirement[]> {
  return apiRequest<StaffingRequirement[]>(
    `/projects/${projectId}/requirements`,
  )
}