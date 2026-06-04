import { api } from './client'
import type { Person, PersonCreate } from './types'

export function getPersons(): Promise<Person[]> {
  return api<Person[]>('/persons/')
}

export function createPerson(data: PersonCreate): Promise<Person> {
  return api<Person>('/persons/', { method: 'POST', body: JSON.stringify(data) })
}
