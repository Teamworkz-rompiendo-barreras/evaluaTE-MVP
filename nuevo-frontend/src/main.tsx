import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store, persistor } from "./app/store";
import { PersistGate } from "redux-persist/integration/react";
import DatosPersonalesPage from './pages/DatosPersonalesPage';
import GameDashboardPage   from './pages/GameDashboardPage'; // paso 1
import PreferencesStep from './features/personal/PreferencesStep'; // paso 2
import GameScenePage       from './pages/GameScenePage';
import UploadCVPage        from './pages/UploadCVPage';
import ResultadosPage      from './pages/ResultadosPage';
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"; // añadimos Navigate
import { AccessibilitySettings } from "./components/AccessibilitySettings";
import './index.css';
import './legacy.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
      <AccessibilitySettings />
      <BrowserRouter>
         <Routes>
          {/* redirige al paso 1 */}
            <Route path="/"            element={<Navigate to="/register/contact" replace />} />

            {/* paso 1: datos personales y contacto */}
            <Route path="/register/contact"    element={<DatosPersonalesPage />} />

            {/* paso 2: preferencias y resto de datos */}
            <Route path="/register/preferences" element={<PreferencesStep />} />
         <Route path="/games"       element={<GameDashboardPage />} />
         <Route path="/games/:id"   element={<GameScenePage />} />
         <Route path="/subircv"     element={<UploadCVPage />} />
         <Route path="/resultados"  element={<ResultadosPage />} />
      </Routes>
      </BrowserRouter>
     </PersistGate>
    </Provider>
  </React.StrictMode>
);
