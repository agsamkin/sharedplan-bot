import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSpaces, type Space } from '../api/spaces'
import { Header } from '../components/Header'
import { Section, Divider } from '../components/Section'
import { ListItem } from '../components/ListItem'
import { Avatar } from '../components/Avatar'
import { LoadingView, ErrorView, EmptyView } from '../components/StateViews'
import { ChevronRight, IconBell, IconGlobe, IconPlus } from '../components/icons'
import { useTranslation } from '../i18n'

const AddButton = ({ onClick, ariaLabel }: { onClick: () => void; ariaLabel: string }) => (
  <button
    onClick={onClick}
    aria-label={ariaLabel}
    style={{
      width: 44, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-blue)',
      marginRight: 4, padding: 0,
    }}
  >
    <IconPlus />
  </button>
)

export function SpacesPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [spaces, setSpaces] = useState<Space[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSpaces = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getSpaces()
      setSpaces(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : t.loadError)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSpaces()
  }, [fetchSpaces])

  if (loading) return (
    <>
      <Header title={t.spaces} right={<AddButton onClick={() => navigate('/spaces/new')} ariaLabel={t.createSpaceAriaLabel} />} />
      <LoadingView />
    </>
  )

  if (error) return (
    <>
      <Header title={t.spaces} right={<AddButton onClick={() => navigate('/spaces/new')} ariaLabel={t.createSpaceAriaLabel} />} />
      <ErrorView message={error} onRetry={fetchSpaces} />
    </>
  )

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={t.spaces} right={<AddButton onClick={() => navigate('/spaces/new')} ariaLabel={t.createSpaceAriaLabel} />} />

      {spaces.length === 0 ? (
        <Section>
          <EmptyView message={t.emptySpaces} />
        </Section>
      ) : (
        <Section>
          {spaces.map((s, i) => (
            <div key={s.id}>
              {i > 0 && <Divider />}
              <ListItem
                left={<Avatar name={s.name} id={s.id} />}
                title={s.name}
                subtitle={`${s.member_count} ${t.membersUnit}`}
                right={<ChevronRight />}
                onClick={() => navigate(`/spaces/${s.id}`)}
              />
            </div>
          ))}
        </Section>
      )}

      <Section title={t.settings}>
        <ListItem
          left={
            <div style={{
              width: 42, height: 42, borderRadius: 12,
              position: 'relative',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--accent-orange)',
            }}>
              <div style={{
                position: 'absolute', inset: 0, borderRadius: 12,
                background: 'var(--accent-orange)', opacity: 0.08,
              }} />
              <div style={{ position: 'relative' }}><IconBell /></div>
            </div>
          }
          title={t.reminders}
          subtitle={t.reminderSubtitle}
          right={<ChevronRight />}
          onClick={() => navigate('/settings/reminders')}
        />
        <Divider />
        <ListItem
          left={
            <div style={{
              width: 42, height: 42, borderRadius: 12,
              position: 'relative',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--accent-blue)',
            }}>
              <div style={{
                position: 'absolute', inset: 0, borderRadius: 12,
                background: 'var(--accent-blue)', opacity: 0.08,
              }} />
              <div style={{ position: 'relative' }}><IconGlobe /></div>
            </div>
          }
          title={t.language}
          subtitle={t.langName}
          right={<ChevronRight />}
          onClick={() => navigate('/settings/language')}
        />
      </Section>
    </div>
  )
}
