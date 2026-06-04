export type AtomType = 'note' | 'thought' | 'task' | 'decision'
export type AtomStatus = 'open' | 'in_progress' | 'blocked' | 'done' | 'cancelled'
export type AtomPriority = 'high' | 'medium' | 'low'
export type AtomComplexity = 'deep' | 'shallow' | 'routine'
export type FilterBadge = 'inbox' | 'created_today' | 'updated_today' | 'overdue'

export interface Person {
  id: string
  name: string
  photo_url: string | null
  organizations: string[]
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  name: string
  color: string | null
  icon: string | null
  created_at: string
  updated_at: string
}

export interface Atom {
  id: string
  title: string
  content: string
  type: AtomType
  captured: boolean
  status: AtomStatus | null
  priority: AtomPriority | null
  complexity: AtomComplexity | null
  deadline_date: string | null
  alarm_date: string | null
  source_url: string | null
  responsible: Person[]
  participants: Person[]
  projects: Project[]
  created_at: string
  updated_at: string
  deleted_at: string | null
}

export interface AtomCreate {
  title: string
  type: AtomType
  content?: string
  captured?: boolean
  status?: AtomStatus | null
  priority?: AtomPriority | null
  complexity?: AtomComplexity | null
  deadline_date?: string | null
  alarm_date?: string | null
  source_url?: string | null
  responsible_ids?: string[]
  participant_ids?: string[]
  project_ids?: string[]
}

export interface AtomUpdate {
  title?: string
  content?: string
  type?: AtomType
  captured?: boolean
  status?: AtomStatus | null
  priority?: AtomPriority | null
  complexity?: AtomComplexity | null
  deadline_date?: string | null
  alarm_date?: string | null
  source_url?: string | null
  responsible_ids?: string[]
  participant_ids?: string[]
  project_ids?: string[]
}

export interface PersonCreate {
  name: string
  photo_url?: string | null
  organizations?: string[]
}

export interface ProjectCreate {
  name: string
  color?: string | null
  icon?: string | null
}
