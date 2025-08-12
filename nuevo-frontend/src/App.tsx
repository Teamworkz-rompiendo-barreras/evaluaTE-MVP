// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom'

// Páginas principales
import DatosPersonalesPage from './pages/DatosPersonalesPage'
import PreferencesStep from './features/personal/PreferencesStep'
import GameDashboardPage from './pages/GameDashboardPage'
import GameScenePage from './pages/GameScenePage'
import UploadCVPage from './pages/UploadCVPage'
import ResultadosPage from './pages/ResultadosPage'
import WelcomePage from './pages/WelcomePage';

// Componentes visuales
import ProtectedRoute from './components/ProtectedRoute'
import { Toaster } from 'react-hot-toast'
import CookieConsent from './components/CookieConsent';
import React from 'react'

// Layouts compartidos
function AppLayout() {
  const [dark, setDark] = React.useState<boolean>(() => {
    try { return localStorage.getItem('prefers-dark') === '1'; } catch { return false }
  })
  const [zoom, setZoom] = React.useState<number>(() => {
    try { return Number(localStorage.getItem('ui-zoom') || 100) } catch { return 100 }
  })
  React.useEffect(() => { try { localStorage.setItem('prefers-dark', dark ? '1' : '0') } catch {} }, [dark])
  React.useEffect(() => { try { localStorage.setItem('ui-zoom', String(zoom)) } catch {} }, [zoom])

  return (
    <div className={`${dark ? 'dark' : ''}`}>
      <div className={`min-h-screen ${dark ? 'bg-gray-900 text-gray-100' : 'bg-gray-50 text-gray-900'}`} style={{ fontSize: `${Math.max(80, Math.min(160, zoom))}%` }}>
        {/* Controles de accesibilidad */}
        <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 bg-white/90 dark:bg-gray-800/90 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-2 shadow">
          <button onClick={() => setDark(d => !d)} className="px-3 py-1 rounded-full text-sm bg-gray-200 dark:bg-gray-700 hover:opacity-90">{dark ? 'Modo claro' : 'Modo oscuro'}</button>
          <div className="flex items-center gap-1">
            <button onClick={() => setZoom(z => Math.max(80, z - 10))} className="px-2 py-1 rounded-full text-sm bg-gray-200 dark:bg-gray-700">-</button>
            <span className="text-sm w-10 text-center">{zoom}%</span>
            <button onClick={() => setZoom(z => Math.min(160, z + 10))} className="px-2 py-1 rounded-full text-sm bg-gray-200 dark:bg-gray-700">+</button>
          </div>
        </div>

        {/* Contenido principal */}
        <main className="container mx-auto p-4">
          <Outlet />
        </main>

        {/* Notificaciones globales */}
        <Toaster position="top-center" />

        {/* Aviso de cookies */}
        <CookieConsent />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Layout global con accesibilidad (dark/zoom) */}
        <Route path="/" element={<AppLayout />}>
          {/* Ruta índice → redirige al registro */}
          <Route index element={<Navigate to="/register/contact" replace />} />

          {/* Registro inicial */}
          <Route path="register">
            <Route path="contact" element={<DatosPersonalesPage />} />
            <Route path="preferences" element={<PreferencesStep />} />
          </Route>

          {/* Pantalla de bienvenida a los minijuegos */}
          <Route path="welcome" element={<WelcomePage />} />

          {/* Dashboard de minijuegos */}
          <Route
            path="games"
            element={
              <ProtectedRoute step="games">
                <GameDashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Escena de minijuego específico */}
          <Route
            path="game/:id"
            element={
              <ProtectedRoute step="games">
                <GameScenePage />
              </ProtectedRoute>
            }
          />
          {/* Ruta alternativa para compatibilidad */}
          <Route
            path="games/:id"
            element={
              <ProtectedRoute step="games">
                <GameScenePage />
              </ProtectedRoute>
            }
          />

          {/* Subida de CV */}
          <Route
            path="upload-cv"
            element={
              <ProtectedRoute step="uploadCV">
                <UploadCVPage />
              </ProtectedRoute>
            }
          />

          {/* Resultados e informe final */}
          <Route
            path="resultados"
            element={
              <ProtectedRoute step="resultados">
                <ResultadosPage />
              </ProtectedRoute>
            }
          />

          {/* Ruta no encontrada */}
          <Route path="*" element={<Navigate to="/register/contact" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}