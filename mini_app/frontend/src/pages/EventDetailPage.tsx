import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getEvent, updateEvent, deleteEvent } from '../api/events'
import { Header } from '../components/Header'
import { Section } from '../components/Section'
import { ConfirmInline } from '../components/ConfirmInline'
import { LoadingView, ErrorView } from '../components/StateViews'
import { useToast } from '../components/Toast'
import { IconPerson } from '../components/icons'
import { useTranslation } from '../i18n'

export function EventDetailPage() {
  const { id: eventId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()
  const { t } = useTranslation()

  const [title, setTitle] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState<string | null>(null)
  const [author, setAuthor] = useState('')
  const [spaceId, setSpaceId] = useState<string | null>(null)
  const [isOwner, setIsOwner] = useState(false)

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const fetchEvent = useCallback(async () => {
    if (!eventId) return
    setLoading(true)
    setError(null)
    try {
      const event = await getEvent(eventId)
      setTitle(event.title)
      setDate(event.event_date)
      setTime(event.event_time ? event.event_time.substring(0, 5) : null)
      setAuthor(event.creator_name)
      setSpaceId(event.space_id ?? null)
      setIsOwner(!!event.is_owner)
    } catch (err) {
      setError(err instanceof Error ? err.message : t.loadEventError)
    } finally {
      setLoading(false)
    }
  }, [eventId])

  useEffect(() => {
    fetchEvent()
  }, [fetchEvent])

  const handleSave = useCallback(async () => {
    if (!eventId || !title.trim() || !date) return
    setSaving(true)
    setError(null)
    try {
      await updateEvent(eventId, {
        title: title.trim(),
        event_date: date,
        event_time: time || null,
      })
      showToast(t.eventUpdated)
      navigate(-1)
    } catch (err) {
      setError(err instanceof Error ? err.message : t.saveError)
    } finally {
      setSaving(false)
    }
  }, [eventId, title, date, time, navigate, showToast])

  const handleDelete = useCallback(async () => {
    if (!eventId) return
    setDeleting(true)
    try {
      await deleteEvent(eventId)
      showToast(t.eventDeleted)
      navigate(spaceId ? '/spaces/' + spaceId : '/', { replace: true })
    } catch (err) {
      const message = err instanceof Error ? err.message : t.deleteError
      setError(message)
      showToast(message)
      setDeleting(false)
    }
  }, [eventId, spaceId, navigate, showToast])

  if (loading) return (
    <>
      <Header title={t.event} showBack onBack={() => navigate(-1)} />
      <LoadingView />
    </>
  )

  if (error && !title) return (
    <>
      <Header title={t.event} showBack onBack={() => navigate(-1)} />
      <ErrorView message={error} onRetry={fetchEvent} />
    </>
  )

  const inputStyle = {
    width: '100%', padding: '11px 14px', fontSize: 16, borderRadius: 10,
    border: isOwner ? '0.5px solid var(--border-input)' : 'none',
    outline: 'none',
    background: 'var(--bg-card)', color: 'var(--text-primary)',
    boxSizing: 'border-box' as const, fontFamily: 'inherit',
    opacity: isOwner ? 1 : 0.8,
    cursor: isOwner ? undefined : 'default',
    pointerEvents: isOwner ? undefined : 'none' as const,
  }

  const labelStyle = {
    fontSize: 12, color: 'var(--text-secondary)', fontWeight: 500 as const,
    display: 'block' as const, marginBottom: 6,
  }

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={isOwner ? t.editing : t.event} showBack onBack={() => navigate(-1)} />

      <Section title={t.eventDetails}>
        <div style={{ padding: '12px 16px' }}>
          <label style={labelStyle}>{t.title}</label>
          <input
            value={title}
            onChange={e => setTitle(e.target.value)}
            readOnly={!isOwner}
            style={inputStyle}
          />
        </div>
        <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 16 }} />
        <div style={{ padding: '12px 16px', display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>{t.date}</label>
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              readOnly={!isOwner}
              style={{ ...inputStyle, fontSize: 15 }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>{t.time}</label>
            <input
              type="time"
              value={time || ''}
              onChange={e => setTime(e.target.value || null)}
              readOnly={!isOwner}
              style={{ ...inputStyle, fontSize: 15 }}
              placeholder="\u2014"
            />
          </div>
        </div>
      </Section>

      <Section>
        <div style={{
          padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 10,
          color: 'var(--text-secondary)',
        }}>
          <IconPerson />
          <span style={{ fontSize: 14 }}>{t.createdBy}: {author}</span>
        </div>
      </Section>

      {error && (
        <div style={{ padding: '8px 16px', color: 'var(--accent-red)', fontSize: 14 }}>
          {error}
        </div>
      )}

      {isOwner && (
        <div style={{ padding: '12px 16px', display: 'flex', gap: 10 }}>
          <button onClick={handleSave} disabled={saving || !title.trim() || !date} style={{
            flex: 1, padding: '14px 0', borderRadius: 12, border: 'none',
            background: 'var(--accent-blue)', color: '#fff', fontSize: 16,
            fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
            opacity: saving || !title.trim() || !date ? 0.4 : 1,
          }}>
            {saving ? t.saving : t.save}
          </button>
        </div>
      )}

      {isOwner && (
        <div style={{ padding: '0 16px' }}>
          <button onClick={() => setConfirmDelete(true)} style={{
            width: '100%', padding: '14px 0', borderRadius: 12,
            border: '0.5px solid var(--danger-border)',
            background: 'var(--confirm-bg)', color: 'var(--accent-red)',
            fontSize: 15, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
          }}>
            {t.deleteEvent}
          </button>
        </div>
      )}

      {isOwner && confirmDelete && (
        <ConfirmInline
          message={t.deleteEventConfirm.replace('{title}', title)}
          confirmText={deleting ? t.deleting : t.deleteBtn}
          cancelText={t.cancelBtn}
          disabled={deleting}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(false)}
        />
      )}
    </div>
  )
}
