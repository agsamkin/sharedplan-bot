import { useEffect, useState, useCallback } from 'react'
import { Section, Cell, Switch, List } from '@telegram-apps/telegram-ui'
import {
  getReminderSettings,
  updateReminderSettings,
  type ReminderSettings,
} from '../api/user'
import { LoadingView, ErrorView } from '../components/StateViews'

const REMINDER_OPTIONS = [
  { key: '1d', label: 'За 1 день' },
  { key: '2h', label: 'За 2 часа' },
  { key: '1h', label: 'За 1 час' },
  { key: '30m', label: 'За 30 минут' },
  { key: '15m', label: 'За 15 минут' },
  { key: '0m', label: 'В момент события' },
] as const

export function ReminderSettingsPage() {
  const [settings, setSettings] = useState<ReminderSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSettings = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getReminderSettings()
      setSettings(data)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Не удалось загрузить настройки'
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  const handleToggle = useCallback(
    async (key: string) => {
      if (!settings) return

      const newValue = !settings[key]
      const newSettings = { ...settings, [key]: newValue }
      setSettings(newSettings)

      try {
        await updateReminderSettings({ [key]: newValue })
      } catch (err) {
        setSettings(settings)
        setError(
          err instanceof Error ? err.message : 'Не удалось сохранить настройки'
        )
      }
    },
    [settings]
  )

  if (loading) return <LoadingView />
  if (error && !settings) return <ErrorView message={error} onRetry={fetchSettings} />
  if (!settings) return <ErrorView message="Не удалось загрузить настройки" />

  return (
    <List>
      <Section header="Напоминания" footer="Выберите, когда вы хотите получать напоминания о предстоящих событиях.">
        {REMINDER_OPTIONS.map(({ key, label }) => (
          <Cell
            key={key}
            Component="label"
            after={
              <Switch
                checked={!!settings[key]}
                onChange={() => handleToggle(key)}
              />
            }
          >
            {label}
          </Cell>
        ))}
      </Section>

      {error && (
        <div
          style={{
            padding: '8px 16px',
            color: 'var(--tgui--destructive_text_color, #ff3b30)',
            fontSize: '14px',
          }}
        >
          {error}
        </div>
      )}
    </List>
  )
}
