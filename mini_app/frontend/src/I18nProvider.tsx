import { useState, useEffect, useCallback, type ReactNode } from 'react'
import { I18nContext, translations, type Language } from './i18n'
import { getLanguage, updateLanguage } from './api/user'
import { LoadingView } from './components/StateViews'

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>('en')
  const [ready, setReady] = useState(false)

  useEffect(() => {
    getLanguage()
      .then(({ language: lang }) => {
        if (lang === 'ru' || lang === 'en') {
          setLanguageState(lang)
        }
      })
      .catch(() => {})
      .finally(() => setReady(true))
  }, [])

  const setLanguage = useCallback((lang: Language) => {
    const prev = language
    setLanguageState(lang)
    updateLanguage(lang).catch(() => {
      setLanguageState(prev)
    })
  }, [language])

  if (!ready) {
    return <LoadingView />
  }

  return (
    <I18nContext.Provider value={{ t: translations[language], language, setLanguage }}>
      {children}
    </I18nContext.Provider>
  )
}
