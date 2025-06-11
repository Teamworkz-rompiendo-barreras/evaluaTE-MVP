import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { store, persistor } from "./app/store";
import { PersistGate } from "redux-persist/integration/react";
import DatosPersonalesPage from './pages/DatosPersonalesPage';
import GameDashboardPage   from './pages/GameDashboardPage';
import GameScenePage       from './pages/GameScenePage';
import UploadCVPage        from './pages/UploadCVPage';
import ResultadosPage      from './pages/ResultadosPage';
import { BrowserRouter, Routes, Route } from "react-router-dom";
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
         <Route path="/"            element={<DatosPersonalesPage />} />
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
