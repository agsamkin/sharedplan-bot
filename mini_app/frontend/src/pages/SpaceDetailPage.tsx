import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSpaceEvents, type SpaceEvent } from '../api/events'
import { getSpace, deleteSpace, type SpaceDetail } from '../api/spaces'
import { formatRelativeDate, formatTime } from '../utils/dates'
import { Header } from '../components/Header'
import { Section, Divider } from '../components/Section'
import { ListItem } from '../components/ListItem'
import { ActionButton } from '../components/ActionButton'
import { DateBadge } from '../components/DateBadge'
import { ConfirmInline } from '../components/ConfirmInline'
import { LoadingView, ErrorView, EmptyView } from '../components/StateViews'
import { useToast } from '../components/Toast'
import { ChevronRight, IconEdit, IconPeople, IconLink, IconTrash } from '../components/icons'

export function SpaceDetailPage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [space, setSpace] = useState<SpaceDetail | null>(null)
  const [events, setEvents] = useState<SpaceEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (webApp?.initDataUnsafe) {
      const data = webApp.initDataUnsafe as { user?: { id?: number } }
      if (data.user?.id) setCurrentUserId(data.user.id)
    }
  }, [])

  const fetchData = useCallback(async () => {
    if (!spaceId) return
    setLoading(true)
    setError(null)
    try {
      const [spaceData, eventsData] = await Promise.all([
        getSpace(spaceId),
        getSpaceEvents(spaceId),
      ])
      setSpace(spaceData)
      setEvents(eventsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить данные')
    } finally {
      setLoading(false)
    }
  }, [spaceId])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const isAdmin = currentUserId !== null && space !== null && space.created_by === currentUserId

  const handleCopyLink = useCallback(async () => {
    if (!space) return
    const link = `https://t.me/sharedplan_bot?start=join_${space.invite_code}`
    try {
      await navigator.clipboard.writeText(link)
    } catch {
      const ta = document.createElement('textarea')
      ta.value = link
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    showToast('Ссылка скопирована')
  }, [space, showToast])

  const handleDeleteSpace = useCallback(async () => {
    if (!spaceId) return
    try {
      await deleteSpace(spaceId)
      showToast('Пространство удалено')
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить')
    }
    setConfirmDelete(false)
  }, [spaceId, navigate, showToast])

  if (loading) return (
    <>
      <Header title="" showBack onBack={() => navigate(-1)} />
      <LoadingView />
    </>
  )

  if (error && !space) return (
    <>
      <Header title="" showBack onBack={() => navigate(-1)} />
      <ErrorView message={error} onRetry={fetchData} />
    </>
  )

  if (!space) return (
    <>
      <Header title="" showBack onBack={() => navigate(-1)} />
      <ErrorView message="Пространство не найдено" />
    </>
  )

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={space.name} showBack onBack={() => navigate(-1)} />

      <div style={{
        display: 'flex', justifyContent: 'center', gap: 12,
        padding: '16px 16px 8px',
        background: 'var(--bg-card)',
        borderBottom: '0.5px solid var(--border)',
      }}>
        {isAdmin && (
          <ActionButton
            icon={<IconEdit />}
            label="Изменить"
            onClick={() => navigate(`/spaces/${spaceId}/edit`)}
          />
        )}
        <ActionButton
          icon={<IconPeople />}
          label="Участники"
          onClick={() => navigate(`/spaces/${spaceId}/members`)}
        />
        <ActionButton
          icon={<IconLink />}
          label="Ссылка"
          color="var(--accent-purple)"
          onClick={handleCopyLink}
        />
        {isAdmin && (
          <ActionButton
            icon={<IconTrash />}
            label="Удалить"
            color="var(--accent-red)"
            onClick={() => setConfirmDelete(true)}
          />
        )}
      </div>

      {confirmDelete && (
        <ConfirmInline
          message={`Удалить «${space.name}»? Все события и напоминания будут потеряны.`}
          onConfirm={handleDeleteSpace}
          onCancel={() => setConfirmDelete(false)}
        />
      )}

      <Section title={`События · ${events.length}`}>
        {events.length === 0 ? (
          <EmptyView message="Нет предстоящих событий. Создайте событие через бота." />
        ) : (
          events.map((ev, i) => (
            <div key={ev.id}>
              {i > 0 && <Divider />}
              <ListItem
                left={<DateBadge date={ev.event_date} />}
                title={ev.title}
                subtitle={`${formatRelativeDate(ev.event_date)}${ev.event_time ? ` · ${formatTime(ev.event_time)}` : ''} · ${ev.creator_name}`}
                right={<ChevronRight />}
                onClick={() => navigate(`/events/${ev.id}`)}
              />
            </div>
          ))
        )}
      </Section>
    </div>
  )
}
