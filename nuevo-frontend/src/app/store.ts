// src/app/store.ts

import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Reducers compartidos
import accessibilityReducer, {
  toggleContrast,
  setFontScale,
  toggleAudioAssistiveMode,
  setShowPictograms,
} from './accessibilitySlice';
import personalReducer, {
  saveContact,
  savePreferences,
  saveCV,
  generateFinalReport,
} from '../features/personal/personalSlice';
import progressReducer, { markGameComplete, saveCV as saveProgressCV } from '../features/progress/progressSlice';
import gameReducer from '../features/games/gameSlice';
import { scenesApi } from '../features/games/scenesApi';

// Combina todos los reducers
const rootReducer = combineReducers({
  personal: personalReducer,
  progress: progressReducer,
  accessibility: accessibilityReducer,
  game: gameReducer,
  [scenesApi.reducerPath]: scenesApi.reducer,
});

// Configuración de persistencia
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['personal', 'progress', 'accessibility', 'game'],
  version: 1,
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

// Definición del Store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    }).concat(scenesApi.middleware),
  devTools: import.meta.env.DEV,
});

// Persistor para guardar estado local
export const persistor = persistStore(store);

// Acciones exportadas – listas para usar en componentes
export {
  // Acciones de accesibilidad
  toggleContrast,
  setFontScale,
  toggleAudioAssistiveMode,
  setShowPictograms,

  // Acciones de personal
  saveContact,
  savePreferences,
  saveCV,
  generateFinalReport,

  // Acciones de progreso
  markGameComplete,
  saveProgressCV,
};

// Tipos para uso global
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;