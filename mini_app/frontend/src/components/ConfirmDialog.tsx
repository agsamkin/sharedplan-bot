import { useCallback, useEffect } from 'react'

interface ConfirmDialogProps {
  open: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const handleOverlayClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onCancel()
      }
    },
    [onCancel]
  )

  useEffect(() => {
    if (!open) return

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel()
    }
    document.addEventListener('keydown', handleEsc)
    return () => document.removeEventListener('keydown', handleEsc)
  }, [open, onCancel])

  if (!open) return null

  return (
    <div
      onClick={handleOverlayClick}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '16px',
      }}
    >
      <div
        style={{
          backgroundColor: 'var(--tgui--bg_color, #fff)',
          borderRadius: '16px',
          padding: '24px',
          maxWidth: '320px',
          width: '100%',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.15)',
        }}
      >
        <div
          style={{
            fontSize: '17px',
            fontWeight: 600,
            marginBottom: '8px',
            color: 'var(--tgui--text_color, #000)',
          }}
        >
          {title}
        </div>
        <div
          style={{
            fontSize: '15px',
            color: 'var(--tgui--hint_color, #999)',
            marginBottom: '24px',
            lineHeight: '20px',
          }}
        >
          {message}
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onCancel}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '12px',
              border: 'none',
              fontSize: '15px',
              fontWeight: 500,
              backgroundColor: 'var(--tgui--secondary_bg_color, #f0f0f0)',
              color: 'var(--tgui--text_color, #000)',
              cursor: 'pointer',
            }}
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            style={{
              flex: 1,
              padding: '12px',
              borderRadius: '12px',
              border: 'none',
              fontSize: '15px',
              fontWeight: 500,
              backgroundColor: 'var(--tgui--destructive_text_color, #ff3b30)',
              color: '#fff',
              cursor: 'pointer',
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
