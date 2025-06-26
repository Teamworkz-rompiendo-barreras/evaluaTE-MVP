import { configureStore, combineReducers, createSlice, PayloadAction } from "@reduxjs/toolkit"
import { persistStore, persistReducer } from "redux-persist"
import storage from "redux-persist/lib/storage"
import accessibilityReducer, { toggleContrast, setFontScale } from "./accessibilitySlice"
import { scenesApi } from "../features/games/scenesApi"
import personalReducer, { saveContact, savePreferences, saveCvAnalysis } from "../features/personal/personalSlice"

// CV analysis interface left as-is
export interface CvAnalysis { score: number; strengths: string[]; weaknesses: string[] }

// Progress slice
interface ProgressState { completed: Record<number, boolean> }
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

// Root reducer
const rootReducer = combineReducers({
  progress: progressSlice.reducer,
  accessibility: accessibilityReducer,
  personal: personalReducer,
  [scenesApi.reducerPath]: scenesApi.reducer,
})

// Persist config
const persistConfig = { key: "root", storage, whitelist: ["progress", "accessibility", "personal"] }
const persistedReducer = persistReducer(persistConfig, rootReducer)

// Store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({ serializableCheck: false }).concat(scenesApi.middleware),
})
export const persistor = persistStore(store)

// Exports
export const { markComplete } = progressSlice.actions
export { saveContact, savePreferences, saveCvAnalysis }
export { toggleContrast, setFontScale }

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
