// src/app/store.ts
import { configureStore, combineReducers, createSlice, PayloadAction } from "@reduxjs/toolkit"
import { persistStore, persistReducer } from "redux-persist"
import storage from "redux-persist/lib/storage"    // localStorage
import accessibilityReducer, {
  toggleContrast,
  setFontScale,
} from "./accessibilitySlice"
import { scenesApi } from "../features/games/scenesApi"  // 1) Importa tu API slice

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

// 3) Slice “personal” con cvAnalysis Y PROGRESO DE MINIJUEGOS
interface PersonalState {
  firstName: string
  lastName: string
  email: string
  whatsapp: string
  jobPreferences: string
  workMode: "remoto" | "presencial" | "híbrido"
  availability: "mañana" | "tarde" | "completa"
  startDate: "inmediata" | "15_días" | "1_mes" | "más_de_1_mes"
  willingToRelocate: boolean
  hasDisabilityCert: boolean

  // Campo opcional de análisis de CV
  cvAnalysis?: CvAnalysis

  // Campo para el progreso de minijuegos
  unlockedGames: number
}

const initialPersonal: PersonalState = {
  firstName: "",
  lastName: "",
  email: "",
  whatsapp: "",
  jobPreferences: "",
  workMode: "remoto",
  availability: "completa",
  startDate: "inmediata",
  willingToRelocate: false,
  hasDisabilityCert: false,

  cvAnalysis: undefined,
  unlockedGames: 1, // Solo el primer minijuego desbloqueado al inicio
}

const personalSlice = createSlice({
  name: "personal",
  initialState: initialPersonal,
  reducers: {
    saveContact(
      state,
      action: PayloadAction<
        Pick<PersonalState, "firstName" | "lastName" | "email" | "whatsapp">
      >
    ) {
      Object.assign(state, action.payload)
    },
    savePreferences(
      state,
      action: PayloadAction<
        Pick<
          PersonalState,
          | "jobPreferences"
          | "workMode"
          | "availability"
          | "startDate"
          | "willingToRelocate"
          | "hasDisabilityCert"
        >
      >
    ) {
      Object.assign(state, action.payload)
    },
    // Reducer para poblar el análisis del CV
    saveCvAnalysis(state, action: PayloadAction<CvAnalysis>) {
      state.cvAnalysis = action.payload
    },
    // Reducer para desbloquear el siguiente minijuego
    unlockNextGame(state) {
      if (state.unlockedGames < 10) {
        state.unlockedGames += 1;
      }
    },
  },
})

// ────────────────────────────────────────────────────────────────
// 5) Combinamos todos los reducers, incluido el de RTK Query
const rootReducer = combineReducers({
  progress:      progressSlice.reducer,
  accessibility: accessibilityReducer,
  personal:      personalSlice.reducer,
  [scenesApi.reducerPath]: scenesApi.reducer,
})

// 6) Configuración de persistencia
const persistConfig = {
  key: "root",
  storage,
  whitelist: ["progress", "accessibility", "personal"],
}

// 7) Reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer)

// 8) Configuramos el store, engancha el middleware de RTK Query
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // para Redux Persist
    }).concat(scenesApi.middleware),
})

// 9) Creamos el persistor
export const persistor = persistStore(store)

// 10) Exportamos las actions
export const { markComplete } = progressSlice.actions
export const { saveContact, savePreferences, saveCvAnalysis, unlockNextGame } = personalSlice.actions
export { toggleContrast, setFontScale }

// 11) Exportamos los tipos para usar en useSelector / useDispatch
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
