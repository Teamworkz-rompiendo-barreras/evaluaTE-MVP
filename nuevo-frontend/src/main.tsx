// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store, persistor } from './app/store';
import { PersistGate } from 'redux-persist/integration/react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { AuthProvider } from './context/AuthContext';

import DatosPersonalesPage from './pages/DatosPersonalesPage';
import PreferencesStep from './features/personal/PreferencesStep';
import GameDashboardPage from './pages/GameDashboardPage';
import GameScenePage from './pages/GameScenePage';
import UploadCVPage from './pages/UploadCVPage';
import ResultadosPage from './pages/ResultadosPage';
import PrivacidadPage from './pages/PrivacidadPage';

import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import CookieConsent from './components/CookieConsent';
// import { AccessibilitySettings } from './components/AccessibilitySettings';

import { initSentry } from './sentry';

import './index.css';
import './legacy.css';

// Widget simple: modo oscuro + zoom persistentes
function DarkZoomWidget() {
  const [dark, setDark] = React.useState<boolean>(() => {
    try { return localStorage.getItem('prefers-dark') === '1'; } catch { return false }
  });
  const [zoom, setZoom] = React.useState<number>(() => {
    try { return Number(localStorage.getItem('ui-zoom') || 100); } catch { return 100 }
  });
  React.useEffect(() => {
    try { localStorage.setItem('prefers-dark', dark ? '1' : '0'); } catch { /* ignore storage */ }
    const html = document.documentElement;
    if (dark) html.classList.add('dark'); else html.classList.remove('dark');
  }, [dark]);
  React.useEffect(() => {
    try { localStorage.setItem('ui-zoom', String(zoom)); } catch { /* ignore storage */ }
    document.documentElement.style.fontSize = `${Math.max(80, Math.min(160, zoom))}%`;
  }, [zoom]);
  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 bg-white/90 dark:bg-gray-800/90 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-2 shadow print-hidden">
      <button onClick={() => setDark(d => !d)} className="px-3 py-1 rounded-full text-sm bg-gray-200 dark:bg-gray-700 hover:opacity-90">{dark ? 'Modo claro' : 'Modo oscuro'}</button>
      <div className="flex items-center gap-1">
        <button onClick={() => setZoom(z => Math.max(80, z - 10))} className="px-2 py-1 rounded-full text-sm bg-gray-200 dark:bg-gray-700">-</button>
        <span className="text-sm w-10 text-center">{zoom}%</span>
        <button onClick={() => setZoom(z => Math.min(160, z + 10))} className="px-2 py-1 rounded-full text-sm bg-gray-200 dark:bg-gray-700">+</button>
      </div>
    </div>
  );
}

// Inicializar Sentry
initSentry();

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('No se encontró el elemento root');
const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <Provider store={store}>
        {/* Visual debug indicator */}
        <div style={{ position: 'fixed', top: 0, left: 0, zIndex: 9999, color: 'red', background: 'yellow', padding: '4px' }}>
          React Mounted (v2)
        </div>
        <PersistGate loading={<div style={{ padding: 20, fontSize: 24 }}>Loading Persisted State...</div>} persistor={persistor}>
          {/* <AccessibilitySettings /> */}
          <AuthProvider>
            <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
              <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100 transition-colors">
                <Routes>
                  {/* 1) Inicio → registro: datos personales */}
                  <Route path="/" element={<Navigate to="/register/contact" replace />} />
                  <Route path="/register/contact" element={<DatosPersonalesPage />} />

                  {/* Política de privacidad */}
                  <Route path="/privacidad" element={<PrivacidadPage />} />

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

                {/* Aviso de cookies - aparece en todas las pantallas */}
                <CookieConsent />
                {/* Controles de accesibilidad (modo oscuro + zoom) */}
                <DarkZoomWidget />
              </div>
            </BrowserRouter>
          </AuthProvider>
        </PersistGate>
      </Provider>
    </ErrorBoundary>
  </React.StrictMode>
);