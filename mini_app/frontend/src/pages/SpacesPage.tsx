import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Section, Cell, Badge, List } from '@telegram-apps/telegram-ui'
import { getSpaces, type Space } from '../api/spaces'
import { LoadingView, ErrorView, EmptyView } from '../components/StateViews'

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

  if (loading) return <LoadingView />
  if (error) return <ErrorView message={error} onRetry={fetchSpaces} />

  if (spaces.length === 0) {
    return (
      <div>
        <EmptyView
          icon="📅"
          message="Нет пространств. Создай первое через бота командой /newspace"
        />
        <List>
          <Section>
            <Cell onClick={() => navigate('/settings/reminders')}>
              Настройки напоминаний
            </Cell>
          </Section>
        </List>
      </div>
    )
  }

  return (
    <List>
      <Section header="Мои пространства">
        {spaces.map((space) => (
          <Cell
            key={space.id}
            subtitle={`${space.member_count} участн.`}
            after={
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Badge type="number">
                  {space.role === 'admin' ? '👑' : '👤'}
                </Badge>
                <span
                  onClick={(e) => {
                    e.stopPropagation()
                    navigate(`/spaces/${space.id}/settings`)
                  }}
                  style={{
                    fontSize: '20px',
                    cursor: 'pointer',
                    padding: '4px',
                  }}
                >
                  ⚙️
                </span>
              </div>
            }
            onClick={() => navigate(`/spaces/${space.id}`)}
          >
            {space.name}
          </Cell>
        ))}
      </Section>

      <Section>
        <Cell onClick={() => navigate('/settings/reminders')}>
          Настройки напоминаний
        </Cell>
      </Section>
    </List>
  )
}
