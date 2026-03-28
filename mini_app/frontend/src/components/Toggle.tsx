interface ToggleProps {
  on: boolean;
  onToggle: () => void;
}

export function Toggle({ on, onToggle }: ToggleProps) {
  return (
    <button onClick={onToggle} style={{
      width: 48, height: 28, borderRadius: 14, padding: 2,
      background: on ? 'var(--accent-green)' : 'var(--border)',
      border: 'none', cursor: 'pointer',
      transition: 'background 0.2s', flexShrink: 0, position: 'relative',
    }}>
      <div style={{
        width: 24, height: 24, borderRadius: 12, background: '#fff',
        transition: 'transform 0.2s',
        transform: on ? 'translateX(20px)' : 'translateX(0)',
        boxShadow: 'var(--shadow-toggle)',
      }} />
    </button>
  );
}
