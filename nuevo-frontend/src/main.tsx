// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store, persistor } from './app/store';
import { PersistGate } from 'redux-persist/integration/react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import DatosPersonalesPage from './pages/DatosPersonalesPage';
import PreferencesStep from './features/personal/PreferencesStep';
import GameDashboardPage from './pages/GameDashboardPage';
import GameScenePage from './pages/GameScenePage';
import UploadCVPage from './pages/UploadCVPage';
import ResultadosPage from './pages/ResultadosPage';

import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
// import { AccessibilitySettings } from './components/AccessibilitySettings';
// import { CookieConsent } from './components/CookieConsent';

import { initSentry } from './sentry';

import './index.css';
import './legacy.css';

// Inicializar Sentry
initSentry();

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('No se encontró el elemento root');
const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        {/* <AccessibilitySettings /> */}
        {/* <CookieConsent /> */}
        <BrowserRouter>
          <Routes>
            {/* 1) Inicio → registro: datos personales */}
            <Route path="/" element={<Navigate to="/register/contact" replace />} />
            <Route path="/register/contact" element={<DatosPersonalesPage />} />

            {/* 2) Registro: preferencias */}
            <Route
              path="/register/preferences"
              element={
                <ProtectedRoute step="preferences">
                  <PreferencesStep />
                </ProtectedRoute>
              }
            />

            {/* 3) Dashboard de minijuegos */}
            <Route
              path="/games"
              element={
                <ProtectedRoute step="games">
                  <GameDashboardPage />
                </ProtectedRoute>
              }
            />

            {/* 4) Minijuego individual */}
            <Route
              path="/games/:id"
              element={
                <ProtectedRoute step="games">
                  <GameScenePage />
                </ProtectedRoute>
              }
            />

            {/* 5) Subida de CV (medallero → CV) */}
            <Route
              path="/upload-cv"
              element={
                <ProtectedRoute step="uploadCV">
                  <UploadCVPage />
                </ProtectedRoute>
              }
            />

            {/* 6) Resultados finales e informe */}
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
    </ErrorBoundary>
  </React.StrictMode>
);