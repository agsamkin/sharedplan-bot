import type { Translations } from '../i18n'

export function formatRelativeDate(dateStr: string, t: Translations): string {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const [year, month, day] = dateStr.split('-').map(Number)
  const target = new Date(year, month - 1, day)
  target.setHours(0, 0, 0, 0)

  const diffMs = target.getTime() - today.getTime()
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return t.today
  if (diffDays === 1) return t.tomorrow
  if (diffDays === 2) return t.dayAfter

  if (diffDays >= 3 && diffDays <= 6) {
    const dayOfWeek = target.getDay()
    return t.weekdaysAccusative[dayOfWeek]
  }

  return `${target.getDate()} ${t.monthsGenitive[target.getMonth()]}`
}

export function formatTime(time: string | null, t: Translations): string {
  if (!time) return t.allDay
  // time приходит как "HH:MM" или "HH:MM:SS"
  return time.substring(0, 5)
}
