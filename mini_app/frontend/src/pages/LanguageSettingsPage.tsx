import { useNavigate } from 'react-router-dom'
import { useTranslation, type Language } from '../i18n'
import { Header } from '../components/Header'
import { Section } from '../components/Section'

const LANGUAGES: { code: Language; label: string }[] = [
  { code: 'ru', label: 'Русский' },
  { code: 'en', label: 'English' },
]

export function LanguageSettingsPage() {
  const navigate = useNavigate()
  const { t, language, setLanguage } = useTranslation()

  return (
    <div style={{ background: 'var(--bg-primary)', minHeight: '100%' }}>
      <Header title={t.language} showBack onBack={() => navigate(-1)} />

      <Section title={t.interfaceLang}>
        {LANGUAGES.map(({ code, label }, i) => (
          <div key={code}>
            {i > 0 && <div style={{ height: 0.5, background: 'var(--border)', marginLeft: 16 }} />}
            <button
              onClick={() => setLanguage(code)}
              style={{
                display: 'flex',
                alignItems: 'center',
                width: '100%',
                padding: '14px 16px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: 15,
                fontFamily: 'inherit',
                color: 'var(--text-primary)',
              }}
            >
              <span style={{ flex: 1, fontWeight: code === language ? 600 : 400 }}>
                {label}
              </span>
              {code === language && (
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path
                    d="M4 9.5l3.5 3.5L14 5"
                    stroke="var(--accent-blue)"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </button>
          </div>
        ))}
      </Section>
    </div>
  )
}
