const COLORS = ['#7F77DD', '#1D9E75', '#D85A30', '#D4537E', '#378ADD', '#639922', '#BA7517'];

function initials(name: string): string {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

function colorIndex(id: string | number): number {
  if (typeof id === 'number') return Math.abs(id) % COLORS.length;
  let hash = 0;
  for (let i = 0; i < id.length; i++) {
    hash = (hash * 31 + id.charCodeAt(i)) | 0;
  }
  return Math.abs(hash) % COLORS.length;
}

interface AvatarProps {
  name: string;
  size?: number;
  id?: string | number;
}

export function Avatar({ name, size = 42, id = 0 }: AvatarProps) {
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      background: COLORS[colorIndex(id)],
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: '#fff', fontSize: size * 0.35, fontWeight: 600, flexShrink: 0,
      letterSpacing: 0.5,
    }}>
      {initials(name)}
    </div>
  );
}
