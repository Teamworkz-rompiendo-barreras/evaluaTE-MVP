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
import PrivacidadPage from './pages/PrivacidadPage';

// Lazy-load heavy pages so their chunks are only fetched when the user reaches them.
// lazyWithRetry: on chunk load failure (e.g. after a Vercel deploy that changed the hash),
// reload the page once to pick up the new HTML/manifest, preventing a stale-chunk 404.
const lazyWithRetry = (importFn: () => Promise<{ default: React.ComponentType<any> }>) =>
  React.lazy(async () => {
    try {
      return await importFn();
    } catch {
      const key = 'lazy-chunk-refresh';
      if (!sessionStorage.getItem(key)) {
        sessionStorage.setItem(key, '1');
        window.location.reload();
        return new Promise<never>(() => {}); // page is reloading, never resolve
      }
      sessionStorage.removeItem(key);
      throw new Error('Failed to fetch dynamically imported module after reload');
    }
  });

const UploadCVPage = lazyWithRetry(() => import('./pages/UploadCVPage'));
const ResultadosPage = lazyWithRetry(() => import('./pages/ResultadosPage'));

import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import CookieConsent from './components/CookieConsent';

import { initSentry } from './sentry';

import './index.css';
import './legacy.css';

// Widget compacto: modo oscuro + zoom (iconos, sin texto que crezca con zoom)
function DarkZoomWidget() {
  const [dark, setDark] = React.useState<boolean>(() => {
    try { return localStorage.getItem('prefers-dark') === '1'; } catch { return false }
  });
  const [zoom, setZoom] = React.useState<number>(() => {
    try { return Number(localStorage.getItem('ui-zoom') || 100); } catch { return 100 }
  });
  const [zoomOpen, setZoomOpen] = React.useState(false);

  React.useEffect(() => {
    try { localStorage.setItem('prefers-dark', dark ? '1' : '0'); } catch { /* ignore */ }
    if (dark) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  }, [dark]);

  React.useEffect(() => {
    try { localStorage.setItem('ui-zoom', String(zoom)); } catch { /* ignore */ }
    document.documentElement.style.fontSize = `${Math.max(80, Math.min(160, zoom))}%`;
  }, [zoom]);

  const btnBase = "flex items-center justify-center w-9 h-9 rounded-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 shadow-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-200";

  return (
    <div className="fixed bottom-4 right-4 z-50 flex items-center gap-2 print-hidden" style={{ fontSize: '16px' }}>
      {zoomOpen && (
        <div className="flex items-center gap-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-full px-2 py-1 shadow-sm">
          <button
            onClick={() => setZoom(z => Math.max(80, z - 10))}
            className="w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 flex items-center justify-center font-bold leading-none"
            title="Reducir tamaño"
            aria-label="Reducir tamaño de texto"
          >−</button>
          <span className="text-xs w-8 text-center text-gray-700 dark:text-gray-200 font-medium">{zoom}%</span>
          <button
            onClick={() => setZoom(z => Math.min(160, z + 10))}
            className="w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 flex items-center justify-center font-bold leading-none"
            title="Aumentar tamaño"
            aria-label="Aumentar tamaño de texto"
          >+</button>
        </div>
      )}
      <button
        onClick={() => setZoomOpen(o => !o)}
        className={btnBase}
        title="Ajustar tamaño de texto"
        aria-label="Ajustar tamaño de texto"
        aria-pressed={zoomOpen}
      >
        <span style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '-0.5px' }}>Aa</span>
      </button>
      <button
        onClick={() => setDark(d => !d)}
        className={btnBase}
        title={dark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
        aria-label={dark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      >
        {dark
          ? <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
          : <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        }
      </button>
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
        <PersistGate loading={null} persistor={persistor}>
          <AuthProvider>
            <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
              <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100 transition-colors">
                <React.Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" /></div>}>
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
                </React.Suspense>

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