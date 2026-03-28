interface ConfirmInlineProps {
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmInline({ message, confirmText = 'Удалить', cancelText = 'Отмена', onConfirm, onCancel }: ConfirmInlineProps) {
  return (
    <div style={{ margin: 16, padding: 16, background: 'var(--confirm-bg)', borderRadius: 12 }}>
      <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--confirm-text)', marginBottom: 12 }}>
        {message}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={onConfirm} style={{
          flex: 1, padding: '10px 0', borderRadius: 10, border: 'none',
          background: 'var(--accent-red)', color: '#fff', fontWeight: 600,
          fontSize: 14, cursor: 'pointer', fontFamily: 'inherit',
        }}>
          {confirmText}
        </button>
        <button onClick={onCancel} style={{
          flex: 1, padding: '10px 0', borderRadius: 10,
          border: '0.5px solid var(--border)',
          background: 'var(--bg-card)', color: 'var(--text-primary)',
          fontWeight: 500, fontSize: 14, cursor: 'pointer', fontFamily: 'inherit',
        }}>
          {cancelText}
        </button>
      </div>
    </div>
  );
}
