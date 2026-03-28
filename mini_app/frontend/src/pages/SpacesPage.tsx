import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSpaces, type Space } from '../api/spaces'
import { Header } from '../components/Header'
import { Section, Divider } from '../components/Section'
import { ListItem } from '../components/ListItem'
import { Avatar } from '../components/Avatar'
import { LoadingView, ErrorView, EmptyView } from '../components/StateViews'
import { ChevronRight, IconBell, IconPlus } from '../components/icons'

const AddButton = ({ onClick }: { onClick: () => void }) => (
  <button
    onClick={onClick}
    aria-label="Создать пространство"
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
      setError(err instanceof Error ? err.message : 'Не удалось загрузить пространства')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSpaces()
  }, [fetchSpaces])

  if (loading) return (
    <>
      <Header title="Пространства" right={<AddButton onClick={() => navigate('/spaces/new')} />} />
      <LoadingView />
    </>
  )

  if (error) return (
    <>
      <Header title="Пространства" right={<AddButton onClick={() => navigate('/spaces/new')} />} />
      <ErrorView message={error} onRetry={fetchSpaces} />
    </>
  )

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title="Пространства" right={<AddButton onClick={() => navigate('/spaces/new')} />} />

      {spaces.length === 0 ? (
        <Section>
          <EmptyView message="Нет пространств. Нажми + чтобы создать первое." />
        </Section>
      ) : (
        <Section>
          {spaces.map((s, i) => (
            <div key={s.id}>
              {i > 0 && <Divider />}
              <ListItem
                left={<Avatar name={s.name} id={s.id} />}
                title={s.name}
                subtitle={`${s.member_count} участн.`}
                right={<ChevronRight />}
                onClick={() => navigate(`/spaces/${s.id}`)}
              />
            </div>
          ))}
        </Section>
      )}

      <Section title="Настройки">
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
          title="Напоминания"
          subtitle="Настроить интервалы"
          right={<ChevronRight />}
          onClick={() => navigate('/settings/reminders')}
        />
      </Section>
    </div>
  )
}
