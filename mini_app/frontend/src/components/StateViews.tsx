import { Spinner, Button, Placeholder } from '@telegram-apps/telegram-ui'

interface LoadingViewProps {
  message?: string
}

export function LoadingView({ message = 'Загрузка...' }: LoadingViewProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 16px',
        gap: '16px',
      }}
    >
      <Spinner size="m" />
      <span
        style={{
          fontSize: '15px',
          color: 'var(--tgui--hint_color, #999)',
        }}
      >
        {message}
      </span>
    </div>
  )
}

interface ErrorViewProps {
  message?: string
  onRetry?: () => void
}

export function ErrorView({
  message = 'Произошла ошибка',
  onRetry,
}: ErrorViewProps) {
  return (
    <Placeholder
      header="Ошибка"
      description={message}
    >
      {onRetry && (
        <Button size="m" mode="outline" onClick={onRetry}>
          Повторить
        </Button>
      )}
    </Placeholder>
  )
}

interface EmptyViewProps {
  message: string
  icon?: string
}

export function EmptyView({ message, icon = '📭' }: EmptyViewProps) {
  return (
    <Placeholder
      header={icon}
      description={message}
    />
  )
}
