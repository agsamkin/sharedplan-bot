import { get, put, del } from './client'

export interface SpaceEvent {
  id: string
  title: string
  event_date: string
  event_time: string | null
  created_by: number
  creator_name: string
  is_owner: boolean
  space_id?: string
  space_name?: string
}

export interface EventDetailResponse extends SpaceEvent {}

export interface EventUpdateData {
  title: string
  event_date: string
  event_time: string | null
}

export function getSpaceEvents(spaceId: string): Promise<SpaceEvent[]> {
  return get<SpaceEvent[]>(`/api/spaces/${spaceId}/events`)
}

export function getEvent(id: string): Promise<EventDetailResponse> {
  return get<EventDetailResponse>(`/api/events/${id}`)
}

export function updateEvent(id: string, data: EventUpdateData): Promise<EventDetailResponse> {
  return put<EventDetailResponse>(`/api/events/${id}`, data)
}

export function deleteEvent(id: string): Promise<void> {
  return del<void>(`/api/events/${id}`)
}
