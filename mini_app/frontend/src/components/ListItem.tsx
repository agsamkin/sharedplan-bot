import { type ReactNode } from 'react';

interface ListItemProps {
  left?: ReactNode;
  title: ReactNode;
  subtitle?: ReactNode;
  right?: ReactNode;
  onClick?: () => void;
  danger?: boolean;
  compact?: boolean;
}

export function ListItem({ left, title, subtitle, right, onClick, danger, compact }: ListItemProps) {
  return (
    <button onClick={onClick} style={{
      display: 'flex', alignItems: 'center', gap: 12,
      padding: compact ? '10px 16px' : '14px 16px', width: '100%',
      background: 'none', border: 'none', cursor: onClick ? 'pointer' : 'default',
      textAlign: 'left', fontSize: 15, fontFamily: 'inherit', color: 'inherit',
    }}>
      {left}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontWeight: 500, color: danger ? 'var(--accent-red)' : 'var(--text-primary)',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {title}
        </div>
        {subtitle && (
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>
            {subtitle}
          </div>
        )}
      </div>
      {right}
    </button>
  );
}
