// src/app/store.ts
import { configureStore, combineReducers, createSlice, PayloadAction } from "@reduxjs/toolkit"
import { persistStore, persistReducer } from "redux-persist"
import storage from "redux-persist/lib/storage"    // localStorage
import accessibilityReducer, {
  toggleContrast,
  setFontScale,
} from "./accessibilitySlice"
import { scenesApi } from "../features/games/scenesApi"

// IMPORTA el reducer y las acciones desde personalSlice
import personalReducer, {
  saveContact,
  savePreferences,
  saveCvAnalysis,
  unlockNextGame,
} from "../features/personal/personalSlice"

// 1) Interfaz para el análisis de CV
export interface CvAnalysis {
  score: number
  strengths: string[]
  weaknesses: string[]
}

// 2) Slice de progreso
interface ProgressState {
  completed: Record<number, boolean>
}
const initialProgress: ProgressState = { completed: {} }
const progressSlice = createSlice({
  name: "progress",
  initialState: initialProgress,
  reducers: {
    markComplete(state, action: PayloadAction<number>) {
      state.completed[action.payload] = true
    },
  },
})

// ────────────────────────────────────────────────────────────────
// 3) Combinamos todos los reducers, incluido el de RTK Query y el personal importado
const rootReducer = combineReducers({
  progress:      progressSlice.reducer,
  accessibility: accessibilityReducer,
  personal:      personalReducer,
  [scenesApi.reducerPath]: scenesApi.reducer,
})

// 4) Configuración de persistencia
const persistConfig = {
  key: "root",
  storage,
  whitelist: ["progress", "accessibility", "personal"],
}

// 5) Reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer)

// 6) Configuramos el store, engancha el middleware de RTK Query
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // para Redux Persist
    }).concat(scenesApi.middleware),
})

// 7) Creamos el persistor
export const persistor = persistStore(store)

// 8) Exportamos las actions (¡personal viene de personalSlice.ts!)
export const { markComplete } = progressSlice.actions
export { saveContact, savePreferences, saveCvAnalysis, unlockNextGame }
export { toggleContrast, setFontScale }

// 9) Exportamos los tipos para usar en useSelector / useDispatch
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
