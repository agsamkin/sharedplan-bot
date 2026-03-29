import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSpace, removeMember, type SpaceDetail } from '../api/spaces'
import { Header } from '../components/Header'
import { Section, Divider } from '../components/Section'
import { ListItem } from '../components/ListItem'
import { Avatar } from '../components/Avatar'
import { LoadingView, ErrorView } from '../components/StateViews'
import { useToast } from '../components/Toast'
import { useTranslation } from '../i18n'

export function MembersPage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { showToast } = useToast()
  const { t } = useTranslation()

  const [space, setSpace] = useState<SpaceDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (webApp?.initDataUnsafe) {
      const data = webApp.initDataUnsafe as { user?: { id?: number } }
      if (data.user?.id) setCurrentUserId(data.user.id)
    }
  }, [])

  const fetchSpace = useCallback(async () => {
    if (!spaceId) return
    setLoading(true)
    setError(null)
    try {
      const data = await getSpace(spaceId)
      setSpace(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : t.loadError)
    } finally {
      setLoading(false)
    }
  }, [spaceId])

  useEffect(() => {
    fetchSpace()
  }, [fetchSpace])

  const handleRemove = useCallback(async (userId: number, name: string) => {
    if (!spaceId) return
    try {
      await removeMember(spaceId, userId)
      setSpace(prev => {
        if (!prev) return prev
        return { ...prev, members: prev.members.filter(m => m.user_id !== userId) }
      })
      showToast(t.memberRemoved.replace('{name}', name))
    } catch (err) {
      setError(err instanceof Error ? err.message : t.deleteError)
    }
    setConfirmDelete(null)
  }, [spaceId, showToast])

  const isAdmin = currentUserId !== null && space !== null && space.created_by === currentUserId

  if (loading) return (
    <>
      <Header title={t.members} showBack onBack={() => navigate(-1)} />
      <LoadingView />
    </>
  )

  if (error && !space) return (
    <>
      <Header title={t.members} showBack onBack={() => navigate(-1)} />
      <ErrorView message={error} onRetry={fetchSpace} />
    </>
  )

  if (!space) return null

  const members = space.members

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={t.members} showBack onBack={() => navigate(-1)} />

      <Section title={t.membersCount.replace('{n}', members.length.toString())}>
        {members.map((m, i) => (
          <div key={m.user_id}>
            {i > 0 && <Divider />}
            <ListItem
              left={<Avatar name={m.first_name} size={38} id={m.user_id} />}
              title={m.first_name}
              subtitle={`@${m.username || '\u2014'}${m.role === 'admin' ? ` \u00b7 ${t.administrator}` : ''}`}
              right={
                isAdmin && m.user_id !== currentUserId ? (
                  <button
                    onClick={(e) => { e.stopPropagation(); setConfirmDelete(m.user_id); }}
                    style={{
                      padding: '5px 12px', borderRadius: 8,
                      border: '0.5px solid var(--danger-border)',
                      background: 'var(--confirm-bg)', color: 'var(--accent-red)',
                      fontSize: 12, fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                    }}
                  >
                    {t.removeMember}
                  </button>
                ) : m.role === 'admin' ? (
                  <span style={{
                    fontSize: 11, color: 'var(--accent-purple)',
                    background: 'var(--badge-admin-bg)',
                    padding: '3px 10px', borderRadius: 6, fontWeight: 600,
                  }}>
                    {t.administrator}
                  </span>
                ) : null
              }
            />
            {confirmDelete === m.user_id && (
              <div style={{ padding: '8px 16px 12px 70px' }}>
                <div style={{ padding: 12, background: 'var(--confirm-bg)', borderRadius: 10, fontSize: 13 }}>
                  <span style={{ color: 'var(--confirm-text)' }}>{t.removeMemberConfirm.replace('{name}', m.first_name)}</span>
                  <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                    <button onClick={() => handleRemove(m.user_id, m.first_name)} style={{
                      padding: '7px 16px', borderRadius: 8, border: 'none',
                      background: 'var(--accent-red)', color: '#fff', fontSize: 12,
                      fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                    }}>{t.yesRemove}</button>
                    <button onClick={() => setConfirmDelete(null)} style={{
                      padding: '7px 16px', borderRadius: 8,
                      border: '0.5px solid var(--border)',
                      background: 'var(--bg-card)', fontSize: 12, cursor: 'pointer',
                      fontFamily: 'inherit', color: 'var(--text-primary)',
                    }}>{t.cancelBtn}</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </Section>

      <div style={{
        padding: 16, fontSize: 13, color: 'var(--text-secondary)',
        textAlign: 'center', lineHeight: 1.5,
      }}>
        {t.membersInviteHint}
      </div>
    </div>
  )
}
