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
    <div className="fixed bottom-[10px] right-[10px] z-50 flex items-center gap-[6px] bg-white/90 dark:bg-gray-800/90 border border-gray-200 dark:border-gray-700 rounded-full px-[8px] py-[6px] shadow print-hidden">
      <button onClick={() => setDark(d => !d)} className="px-[10px] py-[6px] rounded-full text-[12px] bg-gray-200 dark:bg-gray-700 hover:opacity-90">{dark ? 'Modo claro' : 'Modo oscuro'}</button>
      <div className="flex items-center gap-[4px]">
        <button onClick={() => setZoom(z => Math.max(80, z - 10))} className="w-[28px] h-[28px] rounded-full text-[12px] bg-gray-200 dark:bg-gray-700 flex items-center justify-center">-</button>
        <span className="text-[12px] w-[38px] text-center">{zoom}%</span>
        <button onClick={() => setZoom(z => Math.min(160, z + 10))} className="w-[28px] h-[28px] rounded-full text-[12px] bg-gray-200 dark:bg-gray-700 flex items-center justify-center">+</button>
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
