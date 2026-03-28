const MONTHS = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];

interface DateBadgeProps {
  date: string; // "YYYY-MM-DD"
}

export function DateBadge({ date }: DateBadgeProps) {
  const d = new Date(date + 'T00:00:00');
  return (
    <div style={{
      width: 42, height: 48, borderRadius: 10, background: 'var(--bg-primary)',
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      border: '0.5px solid var(--border)', flexShrink: 0,
    }}>
      <span style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.1, color: 'var(--text-primary)' }}>
        {d.getDate()}
      </span>
      <span style={{
        fontSize: 10, color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 500,
      }}>
        {MONTHS[d.getMonth()]}
      </span>
    </div>
  );
}
