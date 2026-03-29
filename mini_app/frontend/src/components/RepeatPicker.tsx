import { useState } from 'react'
import { IconRepeat } from './icons'
import { useTranslation } from '../i18n'

interface RepeatPickerProps {
  value: string
  onChange: (value: string) => void
  readOnly?: boolean
}

export function RepeatPicker({ value, onChange, readOnly = false }: RepeatPickerProps) {
  const [open, setOpen] = useState(false)
  const { t } = useTranslation()
  const opts = Object.entries(t.repeatOptions)
  const current = t.repeatOptions[value] || t.repeatOptions.none

  const isActive = value && value !== 'none'

  return (
    <div>
      <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 16 }} />
      <button
        onClick={() => !readOnly && setOpen(!open)}
        style={{
          display: 'flex', alignItems: 'center', width: '100%', padding: '13px 16px',
          background: 'none', border: 'none', cursor: readOnly ? 'default' : 'pointer',
          textAlign: 'left', fontSize: 15, gap: 10, fontFamily: 'inherit',
          opacity: readOnly ? 0.8 : 1,
        }}
      >
        <div style={{ color: isActive ? 'var(--accent-purple)' : 'var(--text-secondary)' }}>
          <IconRepeat />
        </div>
        <span style={{ flex: 1, color: 'var(--text-primary)' }}>{t.repeat}</span>
        <span style={{
          fontSize: 14,
          color: isActive ? 'var(--accent-purple)' : 'var(--text-secondary)',
          fontWeight: isActive ? 500 : 400,
        }}>
          {current}
        </span>
        {!readOnly && (
          <svg width="10" height="6" viewBox="0 0 10 6" fill="none"
            style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s', marginLeft: 2 }}>
            <path d="M1 1l4 4 4-4" stroke="var(--text-tertiary)" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        )}
      </button>
      {open && !readOnly && (
        <div style={{ borderTop: '0.5px solid var(--border)' }}>
          {opts.map(([key, label], i) => (
            <div key={key}>
              {i > 0 && <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 44 }} />}
              <button
                onClick={() => { onChange(key); setOpen(false) }}
                style={{
                  display: 'flex', alignItems: 'center', width: '100%', padding: '11px 16px 11px 44px',
                  background: key === value || (key === 'none' && !value) ? 'var(--bg-primary)' : 'none',
                  border: 'none', cursor: 'pointer', textAlign: 'left', fontSize: 14,
                  fontFamily: 'inherit',
                }}
              >
                <span style={{ flex: 1, fontWeight: key === value || (key === 'none' && !value) ? 600 : 400, color: 'var(--text-primary)' }}>
                  {label}
                </span>
                {(key === value || (key === 'none' && !value)) && (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8.5l3 3L13 4" stroke="var(--accent-blue)" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
