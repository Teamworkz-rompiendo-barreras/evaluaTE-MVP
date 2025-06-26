// src/App.tsx
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

// Páginas
import DatosPersonalesPage from './pages/DatosPersonalesPage'
import PreferencesStep      from './features/personal/PreferencesStep'
import GameDashboardPage    from './pages/GameDashboardPage'
import GameScenePage        from './pages/GameScenePage'
import UploadCVPage         from './pages/UploadCVPage'
import ResultadosPage       from './pages/ResultadosPage'

// Componentes
import ProtectedRoute from './components/ProtectedRoute'
import { Toaster }    from 'react-hot-toast'

export default function App() {
  return (
    <BrowserRouter>
      {/* Feedback global */}
      <Toaster position="top-center" />

      <Routes>
        {/* 1) Inicio → registro (datos personales) */}
        <Route path="/" element={<Navigate to="/register/contact" replace />} />
        <Route path="/register/contact" element={<DatosPersonalesPage />} />

        {/* 2) Dashboard de minijuegos */}
        <Route
          path="/games"
          element={
            <ProtectedRoute step="games">
              <GameDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/games/:id"
          element={
            <ProtectedRoute step="games">
              <GameScenePage />
            </ProtectedRoute>
          }
        />

        {/* 3) Subida de CV */}
        <Route
          path="/upload-cv"
          element={
            <ProtectedRoute step="uploadCV">
              <UploadCVPage />
            </ProtectedRoute>
          }
        />

        {/* 4) Preferencias laborales (tras CV) */}
        <Route
          path="/preferences"
          element={
            <ProtectedRoute step="preferences">
              <PreferencesStep />
            </ProtectedRoute>
          }
        />

        {/* 5) Resultados e Informe */}
        <Route
          path="/resultados"
          element={
            <ProtectedRoute step="resultados">
              <ResultadosPage />
            </ProtectedRoute>
          }
        />

        {/* 6) Cualquier otra ruta → inicio registro */}
        <Route path="*" element={<Navigate to="/register/contact" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
