// src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider } from 'react-redux'
import { store, persistor } from './app/store'
import { PersistGate } from 'redux-persist/integration/react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import DatosPersonalesPage from './pages/DatosPersonalesPage'
import PreferencesStep      from './features/personal/PreferencesStep'
import GameDashboardPage   from './pages/GameDashboardPage'
import GameScenePage       from './pages/GameScenePage'
import UploadCVPage        from './pages/UploadCVPage'
import ResultadosPage      from './pages/ResultadosPage'

import ProtectedRoute      from './components/ProtectedRoute'
import { AccessibilitySettings } from './components/AccessibilitySettings'

import './index.css'
import './legacy.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <AccessibilitySettings />
        <BrowserRouter>
          <Routes>
            {/* raíz → Paso 1: datos personales */}
            <Route path="/" element={<Navigate to="/register/contact" replace />} />
            <Route path="/register/contact" element={<DatosPersonalesPage />} />

            {/* Paso 2: preferencias (sin protección de flujo) */}
            <Route path="/register/preferences" element={<PreferencesStep />} />

            {/* Dashboard de juegos (requiere registro) */}
            <Route
              path="/games"
              element={
                <ProtectedRoute step="games">
                  <GameDashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Minijuego individual (requiere registro) */}
            <Route
              path="/games/:id"
              element={
                <ProtectedRoute step="games">
                  <GameScenePage />
                </ProtectedRoute>
              }
            />

            {/* Subida de CV (requiere completar juegos) */}
            <Route
              path="/subircv"
              element={
                <ProtectedRoute step="uploadCV">
                  <UploadCVPage />
                </ProtectedRoute>
              }
            />

            {/* Resultados finales e informe (requiere CV + prefs) */}
            <Route
              path="/resultados"
              element={
                <ProtectedRoute step="resultados">
                  <ResultadosPage />
                </ProtectedRoute>
              }
            />

            {/* Cualquier otra ruta → vuelta al registro */}
            <Route path="*" element={<Navigate to="/register/contact" replace />} />
          </Routes>
        </BrowserRouter>
      </PersistGate>
    </Provider>
  </React.StrictMode>
)
