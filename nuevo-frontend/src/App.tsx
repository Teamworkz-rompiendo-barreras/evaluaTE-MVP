// src/App.tsx
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

// Páginas
import DatosPersonalesPage   from './pages/DatosPersonalesPage'
import PreferencesStep        from './features/personal/PreferencesStep'
import GameDashboardPage      from './pages/GameDashboardPage'
import GameScenePage          from './pages/GameScenePage'
import UploadCVPage           from './pages/UploadCVPage'
import ResultadosPage         from './pages/ResultadosPage'

// Componentes
import ProtectedRoute         from './components/ProtectedRoute'
import { Toaster }            from 'react-hot-toast'

export default function App() {
  return (
    <BrowserRouter>
      {/* Feedback global */}
      <Toaster position="top-center" />

      <Routes>
        {/* 1) Inicio redirige a registro */}
        <Route path="/" element={<Navigate to="/register/contact" replace />} />

        {/* 2) Registro paso 1 */}
        <Route path="/register/contact" element={<DatosPersonalesPage />} />

        {/* 3) Registro paso 2 */}
        <Route path="/register/preferences" element={<PreferencesStep />} />

        {/* 4) Dashboard de minijuegos */}
        <Route
          path="/games"
          element={
            <ProtectedRoute>
              <GameDashboardPage />
            </ProtectedRoute>
          }
        />

        {/* 5) Juego individual */}
        <Route
          path="/games/:id"
          element={
            <ProtectedRoute>
              <GameScenePage />
            </ProtectedRoute>
          }
        />

        {/* 6) Subida de CV */}
        <Route
          path="/upload-cv"
          element={
            <ProtectedRoute>
              <UploadCVPage />
            </ProtectedRoute>
          }
        />

        {/* 7) Resultados / informe */}
        <Route
          path="/resultados"
          element={
            <ProtectedRoute>
              <ResultadosPage />
            </ProtectedRoute>
          }
        />

        {/* 8) Cualquier otra ruta vuelve al registro */}
        <Route path="*" element={<Navigate to="/register/contact" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
