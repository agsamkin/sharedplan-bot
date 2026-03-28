const MONTHS_GENITIVE = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]

const WEEKDAYS_ACCUSATIVE = [
  'в воскресенье',
  'в понедельник',
  'во вторник',
  'в среду',
  'в четверг',
  'в пятницу',
  'в субботу',
]

export function formatRelativeDate(dateStr: string): string {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const [year, month, day] = dateStr.split('-').map(Number)
  const target = new Date(year, month - 1, day)
  target.setHours(0, 0, 0, 0)

  const diffMs = target.getTime() - today.getTime()
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'сегодня'
  if (diffDays === 1) return 'завтра'
  if (diffDays === 2) return 'послезавтра'

  if (diffDays >= 3 && diffDays <= 6) {
    const dayOfWeek = target.getDay()
    return WEEKDAYS_ACCUSATIVE[dayOfWeek]
  }

  return `${target.getDate()} ${MONTHS_GENITIVE[target.getMonth()]}`
}

export function formatTime(time: string | null): string {
  if (!time) return 'весь день'
  // time приходит как "HH:MM" или "HH:MM:SS"
  return time.substring(0, 5)
}
