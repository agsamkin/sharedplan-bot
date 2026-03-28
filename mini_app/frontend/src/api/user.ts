import { get, put } from './client'

export interface ReminderSettings {
  [key: string]: boolean
}

export function getReminderSettings(): Promise<ReminderSettings> {
  return get<ReminderSettings>('/api/user/reminders')
}

export function updateReminderSettings(settings: Partial<ReminderSettings>): Promise<ReminderSettings> {
  return put<ReminderSettings>('/api/user/reminders', settings)
}
