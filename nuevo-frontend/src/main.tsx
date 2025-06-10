import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';            // ← importa Provider
import { store } from './app/store';                // ← importa store
import DatosPersonalesPage from './pages/DatosPersonalesPage';
import GameDashboardPage   from './pages/GameDashboardPage';
import GameScenePage       from './pages/GameScenePage';
import UploadCVPage        from './pages/UploadCVPage';
import ResultadosPage      from './pages/ResultadosPage';
import './index.css';
import './legacy.css';
 
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
-    <BrowserRouter>
+    <Provider store={store}>
+      <BrowserRouter>
       <Routes>
         <Route path="/"            element={<DatosPersonalesPage />} />
         <Route path="/games"       element={<GameDashboardPage />} />
         <Route path="/games/:id"   element={<GameScenePage />} />
         <Route path="/subircv"     element={<UploadCVPage />} />
         <Route path="/resultados"  element={<ResultadosPage />} />
       </Routes>
-    </BrowserRouter>
+      </BrowserRouter>
+    </Provider>
  </React.StrictMode>
);
