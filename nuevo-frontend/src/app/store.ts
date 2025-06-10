// src/app/store.ts
import { configureStore, createSlice, PayloadAction } from "@reduxjs/toolkit";
import accessibilityReducer from "./accessibilitySlice";

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

// 2) Creamos el store con ambos reducers
export const store = configureStore({
  reducer: {
    progress: progressSlice.reducer,
    accessibility: accessibilityReducer,
  },
});

// 3) Exportamos las actions del slice de progreso
export const { markComplete } = progressSlice.actions;

// 4) Tipos para usar en useSelector/useDispatch
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
