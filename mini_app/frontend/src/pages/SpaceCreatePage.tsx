import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { createSpace } from '../api/spaces'
import { Header } from '../components/Header'
import { Section } from '../components/Section'
import { useToast } from '../components/Toast'

export function SpaceCreatePage() {
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleCreate = useCallback(async () => {
    if (!name.trim()) return
    setSaving(true)
    setError(null)
    try {
      await createSpace(name.trim())
      showToast('Пространство создано')
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось создать пространство')
    } finally {
      setSaving(false)
    }
  }, [name, navigate, showToast])

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title="Новое пространство" showBack onBack={() => navigate(-1)} />

      <Section title="Название пространства">
        <div style={{ padding: '8px 16px 12px' }}>
          <label htmlFor="space-name" style={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
            Название пространства
          </label>
          <input
            id="space-name"
            value={name}
            onChange={e => setName(e.target.value)}
            style={{
              width: '100%', padding: '12px 14px', fontSize: 16, borderRadius: 10,
              border: '0.5px solid var(--border-input)', outline: 'none',
              background: 'var(--bg-card)', color: 'var(--text-primary)',
              boxSizing: 'border-box', fontFamily: 'inherit',
            }}
            placeholder='Например, «Семья» или «Работа»'
            autoFocus
          />
        </div>
      </Section>

      {error && (
        <div role="alert" style={{ padding: '8px 16px', color: 'var(--accent-red)', fontSize: 14 }}>
          {error}
        </div>
      )}

      <div style={{ padding: '12px 16px' }}>
        <button onClick={handleCreate} disabled={!name.trim() || saving} style={{
          width: '100%', padding: '14px 0', borderRadius: 12, border: 'none',
          background: 'var(--accent-blue)', color: '#fff', fontSize: 16, fontWeight: 600,
          cursor: name.trim() && !saving ? 'pointer' : 'not-allowed',
          opacity: name.trim() && !saving ? 1 : 0.4,
          fontFamily: 'inherit',
        }}>
          {saving ? 'Создание...' : 'Создать'}
        </button>
      </div>

      <div style={{ padding: '8px 16px', fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
        Вы станете администратором. Пригласите участников по ссылке после создания.
      </div>
    </div>
  )
}
