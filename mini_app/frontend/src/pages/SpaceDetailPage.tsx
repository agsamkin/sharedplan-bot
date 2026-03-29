import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSpaceEvents, type SpaceEvent } from '../api/events'
import { getSpace, deleteSpace, type SpaceDetail } from '../api/spaces'
import { formatRelativeDate, formatTime } from '../utils/dates'
import { Header } from '../components/Header'
import { Divider } from '../components/Section'
import { ListItem } from '../components/ListItem'
import { ActionButton } from '../components/ActionButton'
import { DateBadge } from '../components/DateBadge'
import { ConfirmInline } from '../components/ConfirmInline'
import { LoadingView, ErrorView, EmptyView } from '../components/StateViews'
import { useToast } from '../components/Toast'
import { ChevronRight, IconEdit, IconPeople, IconLink, IconTrash } from '../components/icons'
import { useTranslation } from '../i18n'

export function SpaceDetailPage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()
  const { t } = useTranslation()

  const [space, setSpace] = useState<SpaceDetail | null>(null)
  const [events, setEvents] = useState<SpaceEvent[]>([])
  const [totalCount, setTotalCount] = useState(0)
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
      const [spaceData, eventsResponse] = await Promise.all([
        getSpace(spaceId),
        getSpaceEvents(spaceId),
      ])
      setSpace(spaceData)
      setEvents(eventsResponse.events)
      setTotalCount(eventsResponse.total_count)
    } catch (err) {
      setError(err instanceof Error ? err.message : t.loadErrorGeneric)
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
    showToast(t.linkCopied)
  }, [space, showToast])

  const handleDeleteSpace = useCallback(async () => {
    if (!spaceId) return
    try {
      await deleteSpace(spaceId)
      showToast(t.spaceDeleted)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : t.deleteError)
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
      <ErrorView message={t.spaceNotFound} />
    </>
  )

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%', position: 'relative' }}>
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
            label={t.editAction}
            onClick={() => navigate(`/spaces/${spaceId}/edit`)}
          />
        )}
        <ActionButton
          icon={<IconPeople />}
          label={t.membersAction}
          onClick={() => navigate(`/spaces/${spaceId}/members`)}
        />
        <ActionButton
          icon={<IconLink />}
          label={t.linkAction}
          color="var(--accent-purple)"
          onClick={handleCopyLink}
        />
        {isAdmin && (
          <ActionButton
            icon={<IconTrash />}
            label={t.deleteAction}
            color="var(--accent-red)"
            onClick={() => setConfirmDelete(true)}
          />
        )}
      </div>

      {confirmDelete && (
        <ConfirmInline
          message={t.deleteSpaceConfirm.replace('{name}', space.name)}
          confirmText={t.deleteBtn}
          cancelText={t.cancelBtn}
          onConfirm={handleDeleteSpace}
          onCancel={() => setConfirmDelete(false)}
        />
      )}

      <div style={{ marginBottom: 8 }}>
        <div style={{
          fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)',
          textTransform: 'uppercase', letterSpacing: 0.8,
          padding: '20px 16px 8px',
        }}>
          {t.eventsTitle} · {totalCount}
        </div>
        <div style={{
          background: 'var(--bg-card)',
          borderTop: '0.5px solid var(--border)',
          borderBottom: '0.5px solid var(--border)',
        }}>
          {events.length === 0 ? (
            <EmptyView message={t.noEvents} />
          ) : (
            events.map((ev, i) => (
              <div key={ev.id}>
                {i > 0 && <Divider />}
                <ListItem
                  left={<DateBadge date={ev.event_date} />}
                  title={ev.title}
                  subtitle={`${formatRelativeDate(ev.event_date, t)}${ev.event_time ? ` · ${formatTime(ev.event_time, t)}` : ''} · ${ev.creator_name}`}
                  right={<ChevronRight />}
                  onClick={() => navigate(`/events/${ev.id}`)}
                />
              </div>
            ))
          )}
        </div>
      </div>

      <button onClick={() => navigate(`/spaces/${spaceId}/events/new`, { state: { events, spaceName: space.name } })} style={{
        position: 'fixed', bottom: 24, right: 20,
        width: 52, height: 52, borderRadius: 26,
        background: 'var(--accent-blue)', border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(55,138,221,0.35)',
      }}>
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 5V17M5 11H17" stroke="#fff" strokeWidth="2.2" strokeLinecap="round"/></svg>
      </button>
    </div>
  )
}
