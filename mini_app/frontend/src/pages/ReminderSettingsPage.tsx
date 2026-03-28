import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getReminderSettings, updateReminderSettings, type ReminderSettings } from '../api/user'
import { Header } from '../components/Header'
import { Section } from '../components/Section'
import { Toggle } from '../components/Toggle'
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
  const navigate = useNavigate()
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
      setError(err instanceof Error ? err.message : 'Не удалось загрузить настройки')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSettings()
  }, [fetchSettings])

  const handleToggle = useCallback(async (key: string) => {
    if (!settings) return
    const prev = settings
    const newSettings = { ...settings, [key]: !settings[key] }
    setSettings(newSettings)
    try {
      await updateReminderSettings({ [key]: newSettings[key] })
    } catch {
      setSettings(prev)
    }
  }, [settings])

  if (loading) return (
    <>
      <Header title="Напоминания" showBack onBack={() => navigate(-1)} />
      <LoadingView />
    </>
  )

  if (error && !settings) return (
    <>
      <Header title="Напоминания" showBack onBack={() => navigate(-1)} />
      <ErrorView message={error} onRetry={fetchSettings} />
    </>
  )

  if (!settings) return null

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title="Напоминания" showBack onBack={() => navigate(-1)} />

      <Section title="Интервалы напоминаний">
        {REMINDER_OPTIONS.map(({ key, label }, i) => (
          <div key={key}>
            {i > 0 && <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 16 }} />}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 16px',
            }}>
              <span style={{ fontSize: 15, color: 'var(--text-primary)' }}>{label}</span>
              <Toggle on={!!settings[key]} onToggle={() => handleToggle(key)} />
            </div>
          </div>
        ))}
      </Section>

      <div style={{
        padding: '8px 16px', fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5,
      }}>
        Настройки применяются ко всем новым событиям во всех пространствах.
        Уже созданные напоминания не изменятся.
      </div>
    </div>
  )
}
