// src/features/progress/progressSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ProgressState {
  completedGames: string[]
  cvFile: File | null
}

const initialState: ProgressState = {
  completedGames: [],
  cvFile: null,
}

const progressSlice = createSlice({
  name: 'progress',
  initialState,
  reducers: {
    markGameComplete(state, action: PayloadAction<string>) {
      if (!state.completedGames.includes(action.payload)) {
        state.completedGames.push(action.payload)
      }
    },
    saveCV(state, action: PayloadAction<File>) {
      state.cvFile = action.payload
    },
  },
})

export const {
  markGameComplete,
  saveCV
} = progressSlice.actions
export default progressSlice.reducer
