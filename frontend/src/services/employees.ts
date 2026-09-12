import type { Employee } from '../types/employee'
import { apiRequest } from './api'

export async function getEmployees(): Promise<Employee[]> {
  return apiRequest<Employee[]>('/employees')
}