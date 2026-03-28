import { type ReactNode } from 'react';

interface SectionProps {
  title?: string;
  children: ReactNode;
}

export function Section({ title, children }: SectionProps) {
  return (
    <div style={{ marginBottom: 8 }}>
      {title && (
        <div style={{
          fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)',
          textTransform: 'uppercase', letterSpacing: 0.8, padding: '20px 16px 8px',
        }}>
          {title}
        </div>
      )}
      <div style={{
        background: 'var(--bg-card)',
        borderTop: '0.5px solid var(--border)',
        borderBottom: '0.5px solid var(--border)',
      }}>
        {children}
      </div>
    </div>
  );
}

export function Divider() {
  return <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 70 }} />;
}
