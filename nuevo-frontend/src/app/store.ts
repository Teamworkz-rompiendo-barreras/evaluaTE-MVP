// src/app/store.ts
import { configureStore, combineReducers, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage"; // usa localStorage

import accessibilityReducer, {
  toggleContrast,
  setFontScale,
} from "./accessibilitySlice";

import { scenesApi } from "../features/games/scenesApi"; // <-- 1) Importa tu API slice

// 1) Slice de progreso
interface ProgressState {
  completed: Record<number, boolean>;
}
const initialProgress: ProgressState = { completed: {} };
const progressSlice = createSlice({
  name: "progress",
  initialState: initialProgress,
  reducers: {
    markComplete(state, action: PayloadAction<number>) {
      state.completed[action.payload] = true;
    },
  },
});

// 2) Slice “personal”
interface PersonalState {
  firstName: string;
  lastName: string;
  email: string;
  whatsapp: string;
  jobPreferences: string;
  workMode: "remoto" | "presencial" | "híbrido";
  availability: "mañana" | "tarde" | "completa";
  startDate: "inmediata" | "15_días" | "1_mes" | "más_de_1_mes";
  willingToRelocate: boolean;
  hasDisabilityCert: boolean;
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
};
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
      Object.assign(state, action.payload);
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
      Object.assign(state, action.payload);
    },
  },
});

// ────────────────────────────────────────────────────────────────
// 3) Combinamos todos los reducers, incluyendo el de RTK Query
const rootReducer = combineReducers({
  progress: progressSlice.reducer,
  accessibility: accessibilityReducer,
  personal: personalSlice.reducer,
  [scenesApi.reducerPath]: scenesApi.reducer, // <-- 2) Añade tu API slice aquí
});

// 4) Configuración de persistencia
const persistConfig = {
  key: "root",
  storage,
  whitelist: ["progress", "accessibility", "personal"],
};

// 5) Creamos el reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer);

// 6) Configuramos el store con middleware de RTK Query
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefault) =>
    getDefault({
      serializableCheck: false, // necesario cuando usamos redux-persist
    }).concat(scenesApi.middleware), // <-- 3) Engancha el middleware de RTK Query
});

// 7) Creamos el persistor para Redux Persist
export const persistor = persistStore(store);

// 8) Exportamos las actions y helpers
export const { markComplete } = progressSlice.actions;
export { toggleContrast, setFontScale };

// 9) Exportamos los tipos para useSelector / useDispatch
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
