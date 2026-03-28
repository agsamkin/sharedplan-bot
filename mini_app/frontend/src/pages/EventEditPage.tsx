import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Section, Cell, Button, Input, List } from '@telegram-apps/telegram-ui'
import { getEvent, updateEvent } from '../api/events'
import { LoadingView, ErrorView } from '../components/StateViews'

export function EventEditPage() {
  const { id: eventId } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [title, setTitle] = useState('')
  const [date, setDate] = useState('')
  const [time, setTime] = useState('')
  const [allDay, setAllDay] = useState(false)

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)

  const fetchEvent = useCallback(async () => {
    if (!eventId) return
    setLoading(true)
    setError(null)
    try {
      const event = await getEvent(eventId)
      setTitle(event.title)
      setDate(event.event_date)
      if (event.event_time) {
        setTime(event.event_time.substring(0, 5))
        setAllDay(false)
      } else {
        setTime('')
        setAllDay(true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить событие')
    } finally {
      setLoading(false)
    }
  }, [eventId])

  useEffect(() => {
    fetchEvent()
  }, [fetchEvent])

  const validate = (): boolean => {
    if (!title.trim()) {
      setValidationError('Название обязательно')
      return false
    }
    if (title.trim().length > 500) {
      setValidationError('Название не должно превышать 500 символов')
      return false
    }
    if (!date) {
      setValidationError('Дата обязательна')
      return false
    }
    setValidationError(null)
    return true
  }

  const handleSave = useCallback(async () => {
    if (!eventId || !validate()) return

    setSaving(true)
    setError(null)
    try {
      await updateEvent(eventId, {
        title: title.trim(),
        event_date: date,
        event_time: allDay ? null : time || null,
      })
      navigate(-1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить событие')
    } finally {
      setSaving(false)
    }
  }, [eventId, title, date, time, allDay, navigate])

  if (loading) return <LoadingView />
  if (error && !title) return <ErrorView message={error} onRetry={fetchEvent} />

  return (
    <List>
      <Section header="Редактирование события">
        <Cell>
          <Input
            header="Название"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Введите название события"
          />
        </Cell>
        <Cell>
          <div style={{ width: '100%' }}>
            <label
              style={{
                display: 'block',
                fontSize: '14px',
                color: 'var(--tgui--hint_color, #999)',
                marginBottom: '8px',
              }}
            >
              Дата
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                border: '1px solid var(--tgui--outline, #e0e0e0)',
                backgroundColor: 'var(--tgui--bg_color, #fff)',
                color: 'var(--tgui--text_color, #000)',
                fontSize: '16px',
                boxSizing: 'border-box',
              }}
            />
          </div>
        </Cell>
        <Cell
          Component="label"
          after={
            <input
              type="checkbox"
              checked={allDay}
              onChange={(e) => setAllDay(e.target.checked)}
              style={{ width: '20px', height: '20px' }}
            />
          }
        >
          Весь день
        </Cell>
        {!allDay && (
          <Cell>
            <div style={{ width: '100%' }}>
              <label
                style={{
                  display: 'block',
                  fontSize: '14px',
                  color: 'var(--tgui--hint_color, #999)',
                  marginBottom: '8px',
                }}
              >
                Время
              </label>
              <input
                type="time"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '12px',
                  border: '1px solid var(--tgui--outline, #e0e0e0)',
                  backgroundColor: 'var(--tgui--bg_color, #fff)',
                  color: 'var(--tgui--text_color, #000)',
                  fontSize: '16px',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </Cell>
        )}
      </Section>

      {(validationError || error) && (
        <div
          style={{
            padding: '8px 16px',
            color: 'var(--tgui--destructive_text_color, #ff3b30)',
            fontSize: '14px',
          }}
        >
          {validationError || error}
        </div>
      )}

      <div style={{ padding: '16px' }}>
        <Button
          size="l"
          stretched
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Сохранение...' : 'Сохранить'}
        </Button>
      </div>
    </List>
  )
}
