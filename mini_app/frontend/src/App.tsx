import { useEffect } from 'react'
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { AppRoot } from '@telegram-apps/telegram-ui'
import '@telegram-apps/telegram-ui/dist/styles.css'

import { SpacesPage } from './pages/SpacesPage'
import { SpaceEventsPage } from './pages/SpaceEventsPage'
import { SpaceSettingsPage } from './pages/SpaceSettingsPage'
import { EventEditPage } from './pages/EventEditPage'
import { ReminderSettingsPage } from './pages/ReminderSettingsPage'

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
        <Route path="/spaces/:id" element={<SpaceEventsPage />} />
        <Route path="/spaces/:id/settings" element={<SpaceSettingsPage />} />
        <Route path="/events/:id/edit" element={<EventEditPage />} />
        <Route path="/settings/reminders" element={<ReminderSettingsPage />} />
      </Routes>
    </>
  )
}

export function App() {
  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (webApp) {
      webApp.ready()
      webApp.expand()
    }
  }, [])

  const appearance =
    window.Telegram?.WebApp?.colorScheme === 'dark' ? 'dark' : 'light'

  return (
    <AppRoot appearance={appearance}>
      <BrowserRouter>
        <AppInner />
      </BrowserRouter>
    </AppRoot>
  )
}
