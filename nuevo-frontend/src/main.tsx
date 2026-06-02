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

// Widget compacto accesibilidad — tamaños en px para no crecer con zoom de app ni de navegador
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

  const S = {
    wrap: { position: 'fixed', bottom: 16, right: 16, zIndex: 50, display: 'flex', alignItems: 'center', gap: 8, fontSize: 16 } as React.CSSProperties,
    btn: (bg: string, border: string, color: string): React.CSSProperties => ({
      width: 36, height: 36, borderRadius: '50%', background: bg, border: `1px solid ${border}`,
      boxShadow: '0 1px 4px rgba(0,0,0,.15)', display: 'flex', alignItems: 'center',
      justifyContent: 'center', cursor: 'pointer', color, flexShrink: 0,
    }),
    panel: { display: 'flex', alignItems: 'center', gap: 4, background: dark ? '#1e293b' : '#fff', border: `1px solid ${dark ? '#475569' : '#d1d5db'}`, borderRadius: 99, padding: '4px 8px', boxShadow: '0 1px 4px rgba(0,0,0,.12)' } as React.CSSProperties,
  };
  const bg = dark ? '#1e293b' : '#fff';
  const border = dark ? '#475569' : '#d1d5db';
  const color = dark ? '#e2e8f0' : '#374151';

  return (
    <div style={S.wrap} className="print-hidden">
      {zoomOpen && (
        <div style={S.panel}>
          <button style={{ ...S.btn(bg, border, color), width: 28, height: 28 }} onClick={() => setZoom(z => Math.max(80, z - 10))} title="Reducir texto" aria-label="Reducir tamaño de texto">−</button>
          <span style={{ fontSize: 11, width: 32, textAlign: 'center', color, fontWeight: 600 }}>{zoom}%</span>
          <button style={{ ...S.btn(bg, border, color), width: 28, height: 28 }} onClick={() => setZoom(z => Math.min(160, z + 10))} title="Aumentar texto" aria-label="Aumentar tamaño de texto">+</button>
        </div>
      )}
      <button style={S.btn(bg, border, color)} onClick={() => setZoomOpen(o => !o)} title="Tamaño de texto" aria-label="Ajustar tamaño de texto" aria-pressed={zoomOpen}>
        <span style={{ fontWeight: 700, fontSize: 13, letterSpacing: '-0.5px' }}>Aa</span>
      </button>

      <button
        style={{...S.btn(bg, border, color),fontSize: 18,fontWeight: 700}} onClick={() => setDark(d => !d)} title={dark ? 'Modo claro' : 'Modo oscuro'} aria-label={dark ? 'Activar modo claro' : 'Activar modo oscuro'}>
        {dark 
          ? '☀️' : '🌙'
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
