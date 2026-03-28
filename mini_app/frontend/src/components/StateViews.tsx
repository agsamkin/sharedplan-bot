interface LoadingViewProps {
  message?: string;
}

export function LoadingView({ message = 'Загрузка...' }: LoadingViewProps) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: '48px 16px', gap: 16,
    }}>
      <div style={{
        width: 32, height: 32, border: '3px solid var(--border)',
        borderTopColor: 'var(--accent-blue)', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <span style={{ fontSize: 15, color: 'var(--text-secondary)' }}>
        {message}
      </span>
    </div>
  );
}

interface ErrorViewProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorView({ message = 'Произошла ошибка', onRetry }: ErrorViewProps) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: '48px 16px', gap: 16,
      textAlign: 'center',
    }}>
      <div style={{ fontSize: 17, fontWeight: 600, color: 'var(--text-primary)' }}>
        Ошибка
      </div>
      <div style={{ fontSize: 15, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
        {message}
      </div>
      {onRetry && (
        <button onClick={onRetry} style={{
          padding: '10px 24px', borderRadius: 10,
          border: '0.5px solid var(--border)',
          background: 'var(--bg-card)', color: 'var(--accent-blue)',
          fontSize: 15, fontWeight: 500, cursor: 'pointer', fontFamily: 'inherit',
        }}>
          Повторить
        </button>
      )}
    </div>
  );
}

interface EmptyViewProps {
  message: string;
}

export function EmptyView({ message }: EmptyViewProps) {
  return (
    <div style={{
      padding: '32px 16px', textAlign: 'center',
      color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.5,
    }}>
      {message}
    </div>
  );
}
