import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSpace, updateSpaceName } from '../api/spaces'
import { Header } from '../components/Header'
import { Section } from '../components/Section'
import { LoadingView, ErrorView } from '../components/StateViews'
import { useToast } from '../components/Toast'

export function SpaceEditPage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [name, setName] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSpace = useCallback(async () => {
    if (!spaceId) return
    setLoading(true)
    setError(null)
    try {
      const data = await getSpace(spaceId)
      setName(data.name)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить')
    } finally {
      setLoading(false)
    }
  }, [spaceId])

  useEffect(() => {
    fetchSpace()
  }, [fetchSpace])

  const handleSave = useCallback(async () => {
    if (!spaceId || !name.trim()) return
    setSaving(true)
    setError(null)
    try {
      await updateSpaceName(spaceId, name.trim())
      showToast('Сохранено')
      navigate(-1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось сохранить')
    } finally {
      setSaving(false)
    }
  }, [spaceId, name, navigate, showToast])

  if (loading) return (
    <>
      <Header title="Редактировать" showBack onBack={() => navigate(-1)} />
      <LoadingView />
    </>
  )

  if (error && !name) return (
    <>
      <Header title="Редактировать" showBack onBack={() => navigate(-1)} />
      <ErrorView message={error} onRetry={fetchSpace} />
    </>
  )

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title="Редактировать" showBack onBack={() => navigate(-1)} />

      <Section title="Название пространства">
        <div style={{ padding: '8px 16px 12px' }}>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            style={{
              width: '100%', padding: '12px 14px', fontSize: 16, borderRadius: 10,
              border: '0.5px solid var(--border-input)', outline: 'none',
              background: 'var(--bg-card)', color: 'var(--text-primary)',
              boxSizing: 'border-box', fontFamily: 'inherit',
            }}
            placeholder="Название"
            autoFocus
          />
        </div>
      </Section>

      {error && (
        <div style={{ padding: '8px 16px', color: 'var(--accent-red)', fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={{ padding: '12px 16px' }}>
        <button onClick={handleSave} disabled={!name.trim() || saving} style={{
          width: '100%', padding: '14px 0', borderRadius: 12, border: 'none',
          background: 'var(--accent-blue)', color: '#fff', fontSize: 16, fontWeight: 600,
          cursor: 'pointer', opacity: name.trim() && !saving ? 1 : 0.4,
          fontFamily: 'inherit',
        }}>
          {saving ? 'Сохранение...' : 'Сохранить'}
        </button>
      </div>
    </div>
  )
}
