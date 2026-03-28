import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Section, Cell, Button, List } from '@telegram-apps/telegram-ui'
import {
  getSpace,
  deleteSpace,
  removeMember,
  type SpaceDetail,
} from '../api/spaces'
import { LoadingView, ErrorView } from '../components/StateViews'
import { ConfirmDialog } from '../components/ConfirmDialog'

export function SpaceSettingsPage() {
  const { id: spaceId } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [space, setSpace] = useState<SpaceDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [currentUserId, setCurrentUserId] = useState<number | null>(null)

  const [deleteSpaceDialog, setDeleteSpaceDialog] = useState(false)
  const [removeMemberTarget, setRemoveMemberTarget] = useState<{
    userId: number
    name: string
  } | null>(null)

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (webApp?.initDataUnsafe) {
      const user = webApp.initDataUnsafe as { user?: { id?: number } }
      if (user.user?.id) {
        setCurrentUserId(user.user.id)
      }
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
      setError(err instanceof Error ? err.message : 'Не удалось загрузить пространство')
    } finally {
      setLoading(false)
    }
  }, [spaceId])

  useEffect(() => {
    fetchSpace()
  }, [fetchSpace])

  const handleCopyInvite = useCallback(async () => {
    if (!space) return
    const link = `https://t.me/sharedplan_bot?start=join_${space.invite_code}`
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      const textArea = document.createElement('textarea')
      textArea.value = link
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }, [space])

  const handleDeleteSpace = useCallback(async () => {
    if (!spaceId) return
    try {
      await deleteSpace(spaceId)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить пространство')
    } finally {
      setDeleteSpaceDialog(false)
    }
  }, [spaceId, navigate])

  const handleRemoveMember = useCallback(async () => {
    if (!spaceId || !removeMemberTarget) return
    try {
      await removeMember(spaceId, removeMemberTarget.userId)
      setSpace((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          members: prev.members.filter(
            (m) => m.user_id !== removeMemberTarget.userId
          ),
        }
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось удалить участника')
    } finally {
      setRemoveMemberTarget(null)
    }
  }, [spaceId, removeMemberTarget])

  if (loading) return <LoadingView />
  if (error && !space) return <ErrorView message={error} onRetry={fetchSpace} />
  if (!space) return <ErrorView message="Пространство не найдено" />

  const isAdmin = currentUserId !== null && space.created_by === currentUserId

  return (
    <>
      <List>
        <Section header={space.name}>
          <Cell
            subtitle={`https://t.me/sharedplan_bot?start=join_${space.invite_code}`}
            after={
              <Button size="s" mode="outline" onClick={handleCopyInvite}>
                {copied ? 'Скопировано!' : 'Копировать'}
              </Button>
            }
          >
            Ссылка-приглашение
          </Cell>
        </Section>

        <Section header="Участники">
          {space.members.map((member) => (
            <Cell
              key={member.user_id}
              subtitle={member.username ? `@${member.username}` : undefined}
              after={
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '13px', color: 'var(--tgui--hint_color, #999)' }}>
                    {member.role === 'admin' ? 'админ' : 'участник'}
                  </span>
                  {isAdmin && member.user_id !== currentUserId && (
                    <Button
                      size="s"
                      mode="outline"
                      onClick={(e: React.MouseEvent) => {
                        e.stopPropagation()
                        setRemoveMemberTarget({
                          userId: member.user_id,
                          name: member.first_name,
                        })
                      }}
                    >
                      ✕
                    </Button>
                  )}
                </div>
              }
            >
              {member.first_name}
            </Cell>
          ))}
        </Section>

        {error && (
          <div
            style={{
              padding: '8px 16px',
              color: 'var(--tgui--destructive_text_color, #ff3b30)',
              fontSize: '14px',
            }}
          >
            {error}
          </div>
        )}

        {isAdmin && (
          <div style={{ padding: '16px' }}>
            <Button
              size="l"
              stretched
              mode="outline"
              onClick={() => setDeleteSpaceDialog(true)}
              style={{ color: 'var(--tgui--destructive_text_color, #ff3b30)' }}
            >
              Удалить пространство
            </Button>
          </div>
        )}
      </List>

      <ConfirmDialog
        open={deleteSpaceDialog}
        title="Удалить пространство"
        message={`Удалить "${space.name}" и все его события? Это действие нельзя отменить.`}
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={handleDeleteSpace}
        onCancel={() => setDeleteSpaceDialog(false)}
      />

      <ConfirmDialog
        open={removeMemberTarget !== null}
        title="Удалить участника"
        message={
          removeMemberTarget
            ? `Удалить ${removeMemberTarget.name} из пространства?`
            : ''
        }
        confirmText="Удалить"
        cancelText="Отмена"
        onConfirm={handleRemoveMember}
        onCancel={() => setRemoveMemberTarget(null)}
      />
    </>
  )
}
