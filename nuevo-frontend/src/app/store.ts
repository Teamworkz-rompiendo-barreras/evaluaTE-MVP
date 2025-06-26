// src/app/store.ts
import { configureStore, combineReducers } from "@reduxjs/toolkit"
import { persistStore, persistReducer } from "redux-persist"
import storage from "redux-persist/lib/storage"

import accessibilityReducer, { toggleContrast, setFontScale } from "./accessibilitySlice"
import personalReducer, { saveContact, savePreferences, saveCvAnalysis } from "../features/personal/personalSlice"
import progressReducer from "../features/progress/progressSlice"
import { scenesApi } from "../features/games/scenesApi"

// Reducer raíz
const rootReducer = combineReducers({
  progress: progressReducer,
  accessibility: accessibilityReducer,
  personal: personalReducer,
  [scenesApi.reducerPath]: scenesApi.reducer,
})

// Persist config
const persistConfig = {
  key: "root",
  storage,
  whitelist: ["progress", "accessibility", "personal"],
}
const persistedReducer = persistReducer(persistConfig, rootReducer)

// Store y persistor
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (gDM) =>
    gDM({ serializableCheck: false }).concat(scenesApi.middleware),
})
export const persistor = persistStore(store)

// Acciones exportadas
export { markGameComplete } from "../features/progress/progressSlice"
export { saveContact, savePreferences, saveCvAnalysis }
export { toggleContrast, setFontScale }

// Tipos TS
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
