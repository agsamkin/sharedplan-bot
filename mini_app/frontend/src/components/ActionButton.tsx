import { type ReactNode } from 'react';

interface ActionButtonProps {
  icon: ReactNode;
  label: string;
  color?: string;
  onClick?: () => void;
}

export function ActionButton({ icon, label, color = 'var(--accent-blue)', onClick }: ActionButtonProps) {
  return (
    <button onClick={onClick} style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
      background: 'none', border: 'none', cursor: 'pointer', padding: '8px 4px',
      minWidth: 64, fontFamily: 'inherit',
    }}>
      <div style={{
        width: 44, height: 44, borderRadius: 12,
        position: 'relative',
        display: 'flex', alignItems: 'center', justifyContent: 'center', color,
      }}>
        <div style={{
          position: 'absolute', inset: 0, borderRadius: 12,
          background: color, opacity: 0.08,
        }} />
        <div style={{ position: 'relative' }}>{icon}</div>
      </div>
      <span style={{ fontSize: 11, color, fontWeight: 500 }}>{label}</span>
    </button>
  );
}
