import { get, post, put, del } from './client'

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

export interface EventCreateData {
  title: string
  event_date: string
  event_time: string | null
}

export interface SpaceEventsResponse {
  events: SpaceEvent[]
  total_count: number
}

export function getSpaceEvents(spaceId: string): Promise<SpaceEventsResponse> {
  return get<SpaceEventsResponse>(`/api/spaces/${spaceId}/events`)
}

export function createSpaceEvent(spaceId: string, data: EventCreateData): Promise<SpaceEvent> {
  return post<SpaceEvent>(`/api/spaces/${spaceId}/events`, data)
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
