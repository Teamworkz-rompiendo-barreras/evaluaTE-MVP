// src/app/store.ts
import { configureStore, createSlice, PayloadAction } from "@reduxjs/toolkit";

interface ProgressState {
  completed: Record<number, boolean>; // true si el minijuego con ese id está completo
}

const initialState: ProgressState = {
  completed: {},
};

const progressSlice = createSlice({
  name: "progress",
  initialState,
  reducers: {
    markComplete(state, action: PayloadAction<number>) {
      state.completed[action.payload] = true;
    },
  },
});

export const { markComplete } = progressSlice.actions;

export const store = configureStore({
  reducer: {
    progress: progressSlice.reducer,
  },
});

// Tipado para useSelector/useDispatch
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
