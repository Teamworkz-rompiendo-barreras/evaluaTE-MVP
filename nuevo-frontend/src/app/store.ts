import { configureStore, combineReducers } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import localforage from 'localforage'; // Usa IndexedDB (50MB+), no localStorage (5MB)

import personalReducer from '../features/personal/personalSlice';
import gameReducer from '../features/games/gameSlice';
import accessibilityReducer from './accessibilitySlice';

const rootReducer = combineReducers({
  personal: personalReducer,
  game: gameReducer,
  accessibility: accessibilityReducer,
});

const persistConfig = {
  key: 'root',
  storage: localforage, // <- Crítico para que la app no colapse
  whitelist: ['personal', 'game', 'accessibility'], 
};

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, 
    }),
});

export const persistor = persistStore(store);
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;