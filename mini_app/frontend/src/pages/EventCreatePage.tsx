import { useState, useCallback, useMemo } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { createSpaceEvent, type SpaceEvent } from '../api/events'
import { Header } from '../components/Header'
import { Section } from '../components/Section'
import { useToast } from '../components/Toast'
import { RepeatPicker } from '../components/RepeatPicker'
import { useTranslation } from '../i18n'

export function EventCreatePage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { showToast } = useToast()
  const { t } = useTranslation()

  const state = location.state as { events?: SpaceEvent[]; spaceName?: string } | null
  const spaceEvents = state?.events ?? []
  const spaceName = state?.spaceName ?? ''

  const [title, setTitle] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [repeat, setRepeat] = useState('none')

  const titleTrimmed = title.trim()
  const isTitleTooLong = titleTrimmed.length > 500
  const canSave = titleTrimmed.length > 0 && !isTitleTooLong && date !== '' && time !== '' && !saving

  const isPastDate = useMemo(() => {
    if (!date) return false
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const [y, m, d] = date.split('-').map(Number)
    const selected = new Date(y, m - 1, d)
    selected.setHours(0, 0, 0, 0)
    return selected < today
  }, [date])

  const conflicts = useMemo(() => {
    if (!date || !time || spaceEvents.length === 0) return []

    const [hours, minutes] = time.split(':').map(Number)
    if (isNaN(hours) || isNaN(minutes)) return []

    const eventMinutes = hours * 60 + minutes

    return spaceEvents.filter(ev => {
      if (ev.event_date !== date || !ev.event_time) return false
      const [eh, em] = ev.event_time.split(':').map(Number)
      const evMinutes = eh * 60 + em
      return Math.abs(evMinutes - eventMinutes) <= 120
    })
  }, [date, time, spaceEvents])

  const handleSubmit = useCallback(async () => {
    if (!spaceId || !canSave) return
    setSaving(true)
    setError(null)
    try {
      await createSpaceEvent(spaceId, {
        title: titleTrimmed,
        event_date: date,
        event_time: time,
        recurrence_rule: repeat === 'none' ? null : repeat,
      })
      showToast(t.eventCreated)
      navigate(-1)
    } catch (err) {
      const msg = err instanceof Error ? err.message : t.createEventError
      setError(msg)
      showToast(msg)
    } finally {
      setSaving(false)
    }
  }, [spaceId, canSave, titleTrimmed, date, time, repeat, navigate, showToast])

  const inputStyle = {
    width: '100%', padding: '11px 14px', fontSize: 16, borderRadius: 10,
    border: '0.5px solid var(--border-input)', outline: 'none',
    background: 'var(--bg-card)', color: 'var(--text-primary)',
    boxSizing: 'border-box' as const, fontFamily: 'inherit',
  }

  const labelStyle = {
    fontSize: 12, color: 'var(--text-secondary)', fontWeight: 500 as const,
    display: 'block' as const, marginBottom: 6,
  }

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={t.newEvent} showBack onBack={() => navigate(-1)} />

      <Section title={t.eventDetails}>
        <div style={{ padding: '12px 16px' }}>
          <label style={labelStyle}>{t.title}</label>
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            style={inputStyle}
            placeholder={t.eventTitlePlaceholder}
            autoFocus
          />
          {isTitleTooLong && (
            <div style={{ fontSize: 13, color: 'var(--accent-red)', marginTop: 4 }}>
              {t.titleTooLongDetail}
            </div>
          )}
        </div>
        <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 16 }} />
        <div style={{ padding: '12px 16px', display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>{t.date}</label>
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              style={{ ...inputStyle, fontSize: 15 }}
            />
            {isPastDate && (
              <div style={{ fontSize: 13, color: 'var(--warning-text)', marginTop: 4 }}>
                {t.pastDate}
              </div>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>
              {t.time}
            </label>
            <input
              type="time"
              value={time}
              onChange={e => setTime(e.target.value)}
              style={{ ...inputStyle, fontSize: 15 }}
            />
          </div>
        </div>
        <RepeatPicker value={repeat} onChange={setRepeat} />
      </Section>

      {conflicts.length > 0 && (
        <div style={{
          margin: '0 16px 8px', padding: '12px 14px',
          background: 'var(--warning-bg)', borderRadius: 10, fontSize: 13,
          color: 'var(--warning-text)', lineHeight: 1.5,
        }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>
            {t.conflictWarning}
          </div>
          {conflicts.map(c => (
            <div key={c.id}>• {c.title}{c.event_time ? ` (${c.event_time.substring(0, 5)})` : ''}</div>
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '8px 16px', color: 'var(--accent-red)', fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={{ padding: '12px 16px' }}>
        <button onClick={handleSubmit} disabled={!canSave} style={{
          width: '100%', padding: '14px 0', borderRadius: 12, border: 'none',
          background: 'var(--accent-blue)', color: '#fff', fontSize: 16,
          fontWeight: 600, cursor: canSave ? 'pointer' : 'default', fontFamily: 'inherit',
          opacity: canSave ? 1 : 0.4,
        }}>
          {saving ? t.creating : t.createEvent}
        </button>
      </div>
      <div style={{ padding: '8px 16px', fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
        {spaceName
          ? t.eventCreateHint.replace('{name}', spaceName)
          : t.eventCreateHintGeneric
        }
      </div>
    </div>
  )
}
