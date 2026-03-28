import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { ToastProvider } from './components/Toast'
import './styles/theme.css'

import { SpacesPage } from './pages/SpacesPage'
import { SpaceDetailPage } from './pages/SpaceDetailPage'
import { SpaceEditPage } from './pages/SpaceEditPage'
import { MembersPage } from './pages/MembersPage'
import { EventDetailPage } from './pages/EventDetailPage'
import { ReminderSettingsPage } from './pages/ReminderSettingsPage'
import { SpaceCreatePage } from './pages/SpaceCreatePage'
import { EventCreatePage } from './pages/EventCreatePage'

function BackButtonHandler() {
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (!webApp) return

    const isRoot = location.pathname === '/'

    if (isRoot) {
      webApp.BackButton.hide()
    } else {
      webApp.BackButton.show()
    }

    const handleBack = () => {
      navigate(-1)
    }

    webApp.BackButton.onClick(handleBack)
    return () => {
      webApp.BackButton.offClick(handleBack)
    }
  }, [location.pathname, navigate])

  return null
}

function AppInner() {
  return (
    <>
      <BackButtonHandler />
      <Routes>
        <Route path="/" element={<SpacesPage />} />
        <Route path="/spaces/new" element={<SpaceCreatePage />} />
        <Route path="/spaces/:id" element={<SpaceDetailPage />} />
        <Route path="/spaces/:id/events/new" element={<EventCreatePage />} />
        <Route path="/spaces/:id/edit" element={<SpaceEditPage />} />
        <Route path="/spaces/:id/members" element={<MembersPage />} />
        <Route path="/events/:id" element={<EventDetailPage />} />
        <Route path="/settings/reminders" element={<ReminderSettingsPage />} />
      </Routes>
    </>
  )
}

export function App() {
  const [isDark, setIsDark] = useState(
    () => window.Telegram?.WebApp?.colorScheme === 'dark'
  )

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (!webApp) return

    webApp.ready()
    webApp.expand()

    const handleThemeChanged = () => {
      setIsDark(webApp.colorScheme === 'dark')
    }
    webApp.onEvent('themeChanged', handleThemeChanged)
    return () => {
      webApp.offEvent('themeChanged', handleThemeChanged)
    }
  }, [])

  return (
    <div
      data-theme={isDark ? 'dark' : 'light'}
      style={{
        background: 'var(--bg-primary)',
        minHeight: '100vh',
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        color: 'var(--text-primary)',
        WebkitFontSmoothing: 'antialiased',
      }}
    >
      <ToastProvider>
        <BrowserRouter>
          <AppInner />
        </BrowserRouter>
      </ToastProvider>
    </div>
  )
}
