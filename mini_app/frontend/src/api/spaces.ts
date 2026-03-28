import { get, del, put } from './client'

export interface SpaceMember {
  user_id: number
  first_name: string
  username: string | null
  role: 'admin' | 'member'
}

export interface Space {
  id: string
  name: string
  role: 'admin' | 'member'
  member_count: number
  invite_code: string | null
}

export interface SpaceDetail {
  id: string
  name: string
  invite_code: string
  created_by: number
  members: SpaceMember[]
}

export function getSpaces(): Promise<Space[]> {
  return get<Space[]>('/api/spaces')
}

export function getSpace(id: string): Promise<SpaceDetail> {
  return get<SpaceDetail>(`/api/spaces/${id}`)
}

export function deleteSpace(id: string): Promise<void> {
  return del<void>(`/api/spaces/${id}`)
}

export function removeMember(spaceId: string, userId: number): Promise<void> {
  return del<void>(`/api/spaces/${spaceId}/members/${userId}`)
}

export function updateSpaceName(id: string, name: string): Promise<SpaceDetail> {
  return put<SpaceDetail>(`/api/spaces/${id}`, { name })
}
