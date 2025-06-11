// src/app/store.ts
import { configureStore, combineReducers, createSlice, PayloadAction } from "@reduxjs/toolkit";
import { persistStore, persistReducer } from "redux-persist";
import storage from "redux-persist/lib/storage"; // usa localStorage
import accessibilityReducer, {
  toggleContrast,
  setFontScale,
} from "./accessibilitySlice";

// 1) Definimos el slice de progreso
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

// 2) Definimos el slice “personal” para tus datos de registro
interface PersonalState {
  firstName: string;
  lastName: string;
  email: string;
  whatsapp: string;
  jobPreferences: string[];
  workMode: "remoto" | "presencial" | "híbrido";
  availability: "mañana" | "tarde" | "completa";
  startDate: string;
  willingToRelocate: boolean;
  hasDisabilityCert: boolean;
}
const initialPersonal: PersonalState = {
  firstName: "",
  lastName: "",
  email: "",
  whatsapp: "",
  jobPreferences: [],
  workMode: "remoto",
  availability: "completa",
  startDate: "",
  willingToRelocate: false,
  hasDisabilityCert: false,
};
const personalSlice = createSlice({
  name: "personal",
  initialState: initialPersonal,
  reducers: {
    saveContact(state, action: PayloadAction<Pick<PersonalState, "firstName" | "lastName" | "email" | "whatsapp">>) {
      Object.assign(state, action.payload);
    },
    savePreferences(state, action: PayloadAction<Pick<PersonalState, "jobPreferences" | "workMode" | "availability" | "startDate" | "willingToRelocate" | "hasDisabilityCert">>) {
      Object.assign(state, action.payload);
    },
  },
});
// ────────────────────────────────────────────────────────────────
// 3) Combinamos todos los reducers
const rootReducer = combineReducers({
  progress: progressSlice.reducer,
  accessibility: accessibilityReducer,
  personal: personalSlice.reducer, 
});

// 4) Configuración de persistencia
const persistConfig = {
  key: "root",
  storage,
  whitelist: ["progress", "accessibility", "personal"], // solo persistimos estos slices
};

// 5) Creamos el reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer);

// 6) Configuramos el store con el reducer persistido
export const store = configureStore({
  reducer: persistedReducer,
});

// 7) Creamos el persistor para Redux Persist
export const persistor = persistStore(store);

// 8) Exportamos las actions que vayamos a usar
export const { markComplete } = progressSlice.actions;
export const { saveContact, savePreferences } = personalSlice.actions;
export { toggleContrast, setFontScale };

// 9) Exportamos los tipos para useSelector / useDispatch
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
