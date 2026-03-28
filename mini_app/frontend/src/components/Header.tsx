import { type ReactNode } from 'react';
import { IconBack } from './icons';

interface HeaderProps {
  title: string;
  showBack?: boolean;
  onBack?: () => void;
  right?: ReactNode;
}

export function Header({ title, showBack, onBack, right }: HeaderProps) {
  return (
    <div style={{
      height: 56, display: 'flex', alignItems: 'center', padding: '0 4px',
      borderBottom: '0.5px solid var(--border)', background: 'var(--bg-card)',
      position: 'sticky', top: 0, zIndex: 10, flexShrink: 0,
    }}>
      {showBack && (
        <button onClick={onBack} style={{
          width: 44, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-blue)',
          padding: 0,
        }}>
          <IconBack />
        </button>
      )}
      <span style={{
        flex: 1, fontSize: 17, fontWeight: 600, color: 'var(--text-primary)',
        paddingLeft: showBack ? 0 : 16,
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
      }}>
        {title}
      </span>
      {right}
    </div>
  );
}
