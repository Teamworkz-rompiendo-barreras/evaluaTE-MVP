// src/App.tsx
import React from 'react'
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

// Layouts compartidos
function AppLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Barra de progreso opcional - TEMPORALMENTE DESHABILITADO */}
      {/* <ProgressBar current={1} total={1} /> */}

      {/* Contenido principal */}
      <main className="container mx-auto p-4">
        <Outlet />
      </main>

      {/* Notificaciones globales */}
      <Toaster position="top-center" />

      {/* Aviso de cookies */}
      <CookieConsent />

      {/* Configuración de accesibilidad - TEMPORALMENTE DESHABILITADO */}
      {/* <div className="fixed bottom-4 right-4 z-50">
        <AccessibilitySettings />
      </div> */}

      {/* Debug State - TEMPORALMENTE DESHABILITADO */}
      {/* <DebugState /> */}
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Routes>
        {/* Ruta raíz → redirige al registro */}
        <Route path="/" element={<Navigate to="/register/contact" replace />} />

        {/* Registro inicial */}
        <Route path="/register" element={<AppLayout />}>
          <Route path="contact" element={<DatosPersonalesPage />} />
          <Route path="preferences" element={<PreferencesStep />} />
        </Route>

        {/* Pantalla de bienvenida a los minijuegos */}
        <Route path="/welcome" element={<WelcomePage />} />

        {/* Dashboard de minijuegos */}
        <Route
          path="/games"
          element={
            <ProtectedRoute step="games">
              <GameDashboardPage />
            </ProtectedRoute>
          }
        />

        {/* Escena de minijuego específico */}
        <Route
          path="/game/:id"
          element={
            <ProtectedRoute step="games">
              <GameScenePage />
            </ProtectedRoute>
          }
        />

        {/* Subida de CV */}
        <Route
          path="/upload-cv"
          element={
            <ProtectedRoute step="uploadCV">
              <UploadCVPage />
            </ProtectedRoute>
          }
        />

        {/* Resultados e informe final */}
        <Route
          path="/resultados"
          element={
            <ProtectedRoute step="resultados">
              <ResultadosPage />
            </ProtectedRoute>
          }
        />

        {/* Ruta no encontrada */}
        <Route path="*" element={<Navigate to="/register/contact" replace />} />
      </Routes>
    </BrowserRouter>
  );
}