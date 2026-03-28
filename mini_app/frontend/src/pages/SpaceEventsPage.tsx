import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Section, Cell, Button, List } from '@telegram-apps/telegram-ui'
import { getSpaceEvents, deleteEvent, type SpaceEvent } from '../api/events'
import { ApiError } from '../api/client'
import { getSpace } from '../api/spaces'
import { formatRelativeDate, formatTime } from '../utils/dates'
import { LoadingView, ErrorView, EmptyView } from '../components/StateViews'
import { ConfirmDialog } from '../components/ConfirmDialog'

export function SpaceEventsPage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [events, setEvents] = useState<SpaceEvent[]>([])
  const [spaceName, setSpaceName] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<SpaceEvent | null>(null)
  const [deleting, setDeleting] = useState(false)

  const fetchData = useCallback(async () => {
    if (!spaceId) return
    setLoading(true)
    setError(null)
    try {
      const [eventsData, spaceData] = await Promise.all([
        getSpaceEvents(spaceId),
        getSpace(spaceId),
      ])
      setEvents(eventsData)
      setSpaceName(spaceData.name)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить события')
    } finally {
      setLoading(false)
    }
  }, [spaceId])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await deleteEvent(deleteTarget.id)
      setEvents((prev) => prev.filter((e) => e.id !== deleteTarget.id))
      setDeleteTarget(null)
    } catch (err) {
      const message = err instanceof ApiError && err.status === 404
        ? 'Событие не найдено'
        : (err instanceof Error ? err.message : 'Не удалось удалить событие')
      setError(message)
      if (err instanceof ApiError && err.status === 404) {
        setEvents((prev) => prev.filter((e) => e.id !== deleteTarget.id))
      }
      setDeleteTarget(null)
    } finally {
      setDeleting(false)
    }
  }, [deleteTarget])

  if (loading) return <LoadingView />
  if (error) return <ErrorView message={error} onRetry={fetchData} />

  if (events.length === 0) {
    return (
      <EmptyView
        icon="📝"
        message="Нет предстоящих событий. Отправь текст или голосовое в бот."
      />
    )
  }

  return (
    <>
      <List>
        <Section header={spaceName || 'События'}>
          {events.map((event) => (
            <Cell
              key={event.id}
              subtitle={
                `${formatRelativeDate(event.event_date)}, ${formatTime(event.event_time)} — ${event.creator_name}`
              }
              after={
                event.is_owner && new Date(event.event_date + 'T23:59:59') >= new Date() ? (
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <Button
                      size="s"
                      mode="outline"
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        navigate(`/events/${event.id}/edit`)
                      }}
                    >
                      ✏️
                    </Button>
                    <Button
                      size="s"
                      mode="outline"
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        setDeleteTarget(event)
                      }}
                    >
                      🗑
                    </Button>
                  </div>
                ) : undefined
              }
            >
              {event.title}
            </Cell>
          ))}
        </Section>
      </List>

      <ConfirmDialog
        open={deleteTarget !== null}
        title="Удалить событие"
        message={
          deleteTarget
            ? `Удалить "${deleteTarget.title}"? Это действие нельзя отменить.`
            : ''
        }
        confirmText={deleting ? 'Удаление...' : 'Удалить'}
        cancelText="Отмена"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </>
  )
}
