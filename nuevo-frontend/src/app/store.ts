// src/app/store.ts

import { configureStore, combineReducers } from '@reduxjs/toolkit'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

// Reducers compartidos
import accessibilityReducer, {
  toggleContrast,
  setFontScale,
  setAudioAssistiveMode,
  setShowPictograms
} from './accessibilitySlice'
import personalReducer, {
  saveContact,
  savePreferences,
  saveCV,
  analyzeCV,
  generateFinalReport
} from '../features/personal/personalSlice'
import progressReducer, { unlockGame, resetProgress } from '../features/progress/progressSlice'
import { scenesApi } from '../features/games/scenesApi'

// Combina todos los reducers
const rootReducer = combineReducers({
  personal: personalReducer,
  progress: progressReducer,
  accessibility: accessibilityReducer,
  [scenesApi.reducerPath]: scenesApi.reducer,
})

// Configuración de persistencia
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['personal', 'progress', 'accessibility'],
  version: 1,
  stateReconciler: autoMergeLevel1, // Importado más abajo
}

import { autoMergeLevel1 } from 'redux-persist/es/stateReconciler/autoMergeLevel1'

const persistedReducer = persistReducer(persistConfig, rootReducer)

// Definición del Store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    }).concat(scenesApi.middleware),
  devTools: process.env.NODE_ENV !== 'production',
})

// Persistor para guardar estado local
export const persistor = persistStore(store)

// Acciones exportadas – listas para usar en componentes
export {
  // Acciones de accesibilidad
  toggleContrast,
  setFontScale,
  setAudioAssistiveMode,
  setShowPictograms,

  // Acciones de personal
  saveContact,
  savePreferences,
  saveCV,
  analyzeCV,
  generateFinalReport,

  // Acciones de progreso
  unlockGame,
  resetProgress,
} from '../features/personal/personalSlice'

// Tipos para uso global
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch