import type { Project } from '../types/project'
import { apiRequest } from './api'

export async function getProjects(): Promise<Project[]> {
  return apiRequest<Project[]>('/projects')
}