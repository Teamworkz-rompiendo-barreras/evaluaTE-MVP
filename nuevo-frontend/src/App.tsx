// src/App.tsx
import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

// Importa tus páginas y el guardia
import DatosPersonalesPage from './features/personal/DatosPersonalesPage'
import PreferencesStep      from './features/personal/PreferencesStep'
import GameScenePage        from './pages/GameScenePage'
import ProtectedRoute       from './components/ProtectedRoute'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Redirige la raíz al primer paso de registro */}
        <Route path="/" element={<Navigate to="/register/contact" replace />} />

        {/* Paso 1: datos personales */}
        <Route
          path="/register/contact"
          element={<DatosPersonalesPage />}
        />

        {/* Paso 2: preferencias laborales */}
        <Route
          path="/register/preferences"
          element={<PreferencesStep />}
        />

        {/* RUTA PROTEGIDA: solo usuarios que han completado el registro y tienen progreso */}
        <Route
          path="/games/:id"
          element={
            <ProtectedRoute>
              <GameScenePage />
            </ProtectedRoute>
          }
        />

        {/* Si la URL no coincide con nada, vuelve siempre al registro */}
        <Route path="*" element={<Navigate to="/register/contact" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
