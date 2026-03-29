import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getReminderSettings, updateReminderSettings, type ReminderSettings } from '../api/user'
import { Header } from '../components/Header'
import { Section } from '../components/Section'
import { Toggle } from '../components/Toggle'
import { LoadingView, ErrorView } from '../components/StateViews'
import { useTranslation } from '../i18n'

const REMINDER_KEYS = ['1d', '2h', '1h', '30m', '15m', '0m'] as const

export function ReminderSettingsPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
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
      setError(err instanceof Error ? err.message : t.loadError)
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
      <Header title={t.reminders} showBack onBack={() => navigate(-1)} />
      <LoadingView />
    </>
  )

  if (error && !settings) return (
    <>
      <Header title={t.reminders} showBack onBack={() => navigate(-1)} />
      <ErrorView message={error} onRetry={fetchSettings} />
    </>
  )

  if (!settings) return null

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={t.reminders} showBack onBack={() => navigate(-1)} />

      <Section title={t.reminderIntervals}>
        {REMINDER_KEYS.map((key, i) => (
          <div key={key}>
            {i > 0 && <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 16 }} />}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 16px',
            }}>
              <span style={{ fontSize: 15, color: 'var(--text-primary)' }}>{t.reminderLabels[key]}</span>
              <Toggle on={!!settings[key]} onToggle={() => handleToggle(key)} />
            </div>
          </div>
        ))}
      </Section>

      <div style={{
        padding: '8px 16px', fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5,
      }}>
        {t.reminderHint}
      </div>
    </div>
  )
}
