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

export interface LanguageResponse {
  language: string
}

export function getLanguage(): Promise<LanguageResponse> {
  return get<LanguageResponse>('/api/user/language')
}

export function updateLanguage(language: string): Promise<LanguageResponse> {
  return put<LanguageResponse>('/api/user/language', { language })
}
