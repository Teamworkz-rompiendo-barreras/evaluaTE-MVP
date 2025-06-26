import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import DatosPersonalesPage from './pages/DatosPersonalesPage'
import PreferencesStep from './features/personal/PreferencesStep'
import GameScenePage from './pages/GameScenePage'
import GameDashboardPage from './pages/GameDashboardPage'
import ProtectedRoute from './components/ProtectedRoute'
import UploadCVPage from './pages/UploadCVPage'
import { Toaster } from 'react-hot-toast'
import ResultadosPage from './pages/ResultadosPage'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" />
      <Routes>
        <Route path="/" element={<Navigate to="/register/contact" replace />} />
        <Route path="/register/contact" element={<DatosPersonalesPage />} />
        <Route path="/register/preferences" element={<PreferencesStep />} />
        <Route path="/games" element={<Navigate to="/games/1" replace />} />
        <Route path="/games/:id" element={
          <ProtectedRoute>
            <GameScenePage />
          </ProtectedRoute>
        }/>
        <Route path="/upload-cv" element={<UploadCVPage />} />
        <Route path="/resultados" element={<ResultadosPage />} />
        <Route path="*" element={<Navigate to="/register/contact" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
