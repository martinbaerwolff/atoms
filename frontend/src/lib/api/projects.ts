import { api } from './client'
import type { Project, ProjectCreate } from './types'

export function getProjects(): Promise<Project[]> {
  return api<Project[]>('/projects/')
}

export function createProject(data: ProjectCreate): Promise<Project> {
  return api<Project>('/projects/', { method: 'POST', body: JSON.stringify(data) })
}
