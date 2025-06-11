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

// 2) Combinamos todos los reducers
const rootReducer = combineReducers({
  progress: progressSlice.reducer,
  accessibility: accessibilityReducer,
});

// 3) Configuración de persistencia
const persistConfig = {
  key: "root",
  storage,
  whitelist: ["progress", "accessibility"], // solo persistimos estos slices
};

// 4) Creamos el reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer);

// 5) Configuramos el store con el reducer persistido
export const store = configureStore({
  reducer: persistedReducer,
});

// 6) Creamos el persistor para Redux Persist
export const persistor = persistStore(store);

// 7) Exportamos las actions que vayamos a usar
export const { markComplete } = progressSlice.actions;
export { toggleContrast, setFontScale };

// 8) Exportamos los tipos para useSelector / useDispatch
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
