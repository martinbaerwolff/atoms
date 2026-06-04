import { api } from './client'
import type { Atom, AtomCreate, AtomUpdate, FilterBadge } from './types'

export function getAtoms(params?: { type?: string; filter_badge?: FilterBadge }): Promise<Atom[]> {
  const q = new URLSearchParams()
  if (params?.type) q.set('type', params.type)
  if (params?.filter_badge) q.set('filter_badge', params.filter_badge)
  return api<Atom[]>(`/atoms/?${q}`)
}

export function getAtom(id: string): Promise<Atom> {
  return api<Atom>(`/atoms/${id}`)
}

export function createAtom(data: AtomCreate): Promise<Atom> {
  return api<Atom>('/atoms/', { method: 'POST', body: JSON.stringify(data) })
}

export function updateAtom(id: string, data: AtomUpdate): Promise<Atom> {
  return api<Atom>(`/atoms/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
}

export function deleteAtom(id: string): Promise<void> {
  return api<void>(`/atoms/${id}`, { method: 'DELETE' })
}
